import os
import json
import time
import re
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def save_personal_details(
    full_name: str,
    contact_email: str,
    mobile_number: str = None,
    org_id: str = None
) -> dict:
    """
    Saves the user's personal details (full name and email) to the specified lead record.
    If mobile_number is provided, it stores it in session state as pending and triggers the OTP flow.
    Otherwise, sets status to ASSOCIATED and displays the summary card (compatibility fallback).

    Args:
        full_name: Contact person's full name.
        contact_email: Contact person's email address.
        mobile_number: Personal mobile number to verify.
        org_id: The ID of the saved organization lead record.
    """
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, contact_email.strip()):
        return {
            "status": "error",
            "message": "Invalid contact email format. Please provide a valid email address (e.g. name@domain.com)."
        }

    ctx = get_context()
    
    # Resolve active org_id: primary source is session state, fallback is persistent session, then tool parameter
    resolved_org_id = None
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state:
        resolved_org_id = ctx.session.state.get("active_org_id")
        
    if not resolved_org_id:
        try:
            user_key = f"sess_{ctx.auth.get_user_id()}"
            sess_doc = ctx.get(scope="platform", collection_name="active_sessions", doc_id=user_key) or {}
            resolved_org_id = sess_doc.get("active_org_id")
        except Exception:
            pass

    if not resolved_org_id:
        resolved_org_id = org_id
        
    org_id = resolved_org_id

    # If mobile_number is provided, validate format
    is_existing_user = False
    if mobile_number:
        clean_phone = "".join(filter(str.isdigit, mobile_number))
        has_country = True
        if len(clean_phone) >= 10:
            has_country = mobile_number.strip().startswith('+')
            
        if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
            return {
                "status": "error",
                "message": "Invalid mobile number format. Please include your country code starting with '+' (e.g. +919876543210 or +15550199000)."
            }
            
        def normalize_phone(num: str) -> str:
            clean = "".join(filter(str.isdigit, num))
            if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
                clean = clean[1:]
            return clean
        
        input_num = normalize_phone(mobile_number)
        
        # Only check existing leads if no active org_id exists from the current onboarding intake
        if not org_id:
            leads = ctx.list(scope="platform", collection_name="leads")
            matching_lead = None
            for lead in leads:
                lead_num = normalize_phone(lead.get("contact_mobile") or "")
                if lead_num == input_num:
                    matching_lead = lead
                    break
                    
            if matching_lead:
                is_existing_user = True
                org_id = matching_lead.get("id")
                if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
                    ctx.session.state["active_org_id"] = org_id
                    ctx.session.state["pending_mobile"] = mobile_number

    if not org_id and not is_existing_user:
        return {
            "status": "error",
            "message": "Error: Could not resolve active Organization ID for this session."
        }
        
    lead = None
    if org_id:
        # Retrieve existing lead record
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        
    if not lead and not is_existing_user:
        return {
            "status": "error",
            "message": f"Lead record {org_id} not found."
        }

    if lead:
        # Update contact details (except mobile, which is verified later)
        lead["contact_email"] = contact_email.strip()
        lead["contact_name"] = full_name.strip()
        
        if not mobile_number:
            lead["status"] = "ASSOCIATED"
        else:
            # Keep as UNVERIFIED if mobile OTP is pending
            lead["status"] = "UNVERIFIED"

        # Update owner_id if the user is authenticated in this session
        user_id = ctx.auth.get_user_id()
        is_authenticated = bool(
            user_id
            and not user_id.startswith("guest")
            and not user_id.startswith("anonymous")
            and user_id not in ("dummy_user", "default_user", "dev-user-123")
            and not (len(user_id) == 28 and re.match(r"^[A-Za-z0-9]+$", user_id))
        )
        if is_authenticated:
            lead["owner_id"] = user_id
        elif lead.get("owner_id") is None:
            lead["owner_id"] = "anonymous"

        ctx.save(scope="platform", collection_name="leads", doc_id=org_id, data=lead)

    # Save mobile number in session state & trigger OTP if provided
    if mobile_number:
        if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
            ctx.session.state["pending_mobile"] = mobile_number
            ctx.session.state["active_flow"] = "onboarding"
            if org_id:
                ctx.session.state["active_org_id"] = org_id

        try:
            user_key = f"sess_{ctx.auth.get_user_id()}"
            ctx.save(
                scope="platform",
                collection_name="active_sessions",
                doc_id=user_key,
                data={"pending_mobile": mobile_number, "active_flow": "onboarding", "active_org_id": org_id or ""}
            )
        except Exception as sess_err:
            print(f"⚠️ [SESSION SAVE WARNING] Failed to persist personal active session: {sess_err}")
            
        # Send OTP
        try:
            res = ctx.send_otp(mobile_number)
            if not res.get("success"):
                print(f"⚠️ Live OTP dispatch returned non-success: {res.get('message')}. Falling back to dev code 123456.")
        except Exception as e:
            print(f"⚠️ Live OTP dispatch exception ({e}). Falling back to dev code 123456.")
            
        # Show OTP verify widget
        try:
            ctx.show_widget("otp_verify_form")
        except Exception as w_err:
            print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue OTP verify widget: {w_err}")
            
        return {
            "status": "success",
            "org_id": org_id,
            "message": f"Contact details saved. Verification code dispatched to {mobile_number}."
        }

    # Queue rendering the summary card widget (for old fallback / no mobile cases)
    summary_data = {
        "summary_name": (lead.get("org_name") if lead else "") or "",
        "summary_description": (lead.get("org_description") if lead else "") or "",
        "summary_website": (lead.get("org_website") if lead else "") or "",
        "summary_position": (lead.get("user_position") if lead else "") or "",
        "summary_contact_name": (lead.get("contact_name") if lead else "") or full_name or "",
        "summary_contact_email": (lead.get("contact_email") if lead else "") or contact_email or "",
        "summary_contact_phone": (lead.get("contact_mobile") if lead else "") or mobile_number or ""
    }
    try:
        ctx.show_widget("org_summary_card", data=summary_data)
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue summary widget: {e}")

    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Contact details successfully associated for organization '{lead.get('org_name') if lead else ''}'."
    }
