import os
import json
import time
import datetime
import re
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def associate_contact_and_alert(
    org_id: str = None,
    contact_email: str = None,
    contact_mobile: str = None,
    full_name: str = ""
) -> dict:
    """
    Associates the user's verified contact details with the saved organization lead,
    registers the user if new, triggers a Sales Rep alert, and displays the summary card.

    Args:
        org_id: The ID of the saved organization lead record.
        contact_email: Contact email address collected/retrieved.
        contact_mobile: Personal mobile number collected/retrieved.
        full_name: Full name of the contact (optional).
    """
    ctx = get_context()
    if (not org_id or org_id.strip() == "") and hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        org_id = ctx.session.state.get("active_org_id", "")

    if not org_id:
        return {"status": "error", "message": "Error: Could not resolve active Organization ID."}

    # Find lead
    lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
    if not lead:
        return {"status": "error", "message": f"Lead record {org_id} not found."}

    resolved_email = contact_email.strip() if contact_email else lead.get("contact_email") or ""
    resolved_name = full_name.strip() if full_name else lead.get("contact_name") or ""
    resolved_mobile = contact_mobile
    if not resolved_mobile and hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        resolved_mobile = ctx.session.state.get("pending_mobile") or ctx.session.state.get("verified_mobile") or ""

    if not resolved_mobile:
        return {
            "status": "error",
            "message": "Error: Contact mobile number is missing."
        }

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, resolved_email):
        return {
            "status": "error",
            "message": "Invalid contact email format. Please provide a valid email address (e.g. name@domain.com)."
        }
        
    clean_phone = "".join(filter(str.isdigit, resolved_mobile))
    has_country = True
    if len(clean_phone) >= 10:
        has_country = resolved_mobile.strip().startswith('+')
        
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
        return {
            "status": "error",
            "message": "Invalid contact mobile format. Please include your country code starting with '+' (e.g. +919876543210 or +15550199000)."
        }

    def normalize_phone(num: str) -> str:
        """
        Helper to normalize formatting by extracting digits and stripping country codes.
        """
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_mobile = normalize_phone(resolved_mobile)

    # Update lead details
    lead["contact_email"] = resolved_email
    lead["contact_mobile"] = clean_mobile
    lead["contact_name"] = resolved_name or lead.get("contact_name") or "New User"
    lead["status"] = "ASSOCIATED"
    
    # Set owner_id to user_id if authenticated; otherwise keep/set it as "anonymous"
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
        
    # Add Sales Representative alert log
    alert_id = f"alert_{int(time.time())}"
    alert_msg = f"New unverified lead has arrived for organization '{lead['org_name']}'."
    
    ctx.save(
        scope="platform",
        collection_name="sales_alerts",
        doc_id=alert_id,
        data={
            "lead_id": org_id,
            "message": alert_msg,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )
        
    # Queue rendering the summary card widget!
    summary_data = {
        "summary_name": lead.get("org_name"),
        "summary_description": lead.get("org_description"),
        "summary_website": lead.get("org_website")
    }
    try:
        ctx.show_widget("org_summary_card", data=summary_data)
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue summary widget: {e}")
        
    return {
        "status": "success",
        "message": "Contact details successfully associated. Sales alert dispatched.",
        "org_id": org_id,
        "alert_id": alert_id
    }
