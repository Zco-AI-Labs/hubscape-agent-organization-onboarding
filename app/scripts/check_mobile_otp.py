import os
import json
import time
import datetime
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def check_mobile_otp(mobile_number: str = "", otp_code: str = "") -> dict:
    """
    Validates the 6-digit OTP code entered by the user.
    If in an onboarding flow, automatically associates contact details and renders the Organization Summary Card.
    If in a status check flow, returns the list of matching linked organizations.

    Args:
        mobile_number: The personal mobile number associated with the code (optional if stored in session).
        otp_code: The 6-digit verification code.
    """
    ctx = get_context()
    import re
    
    # 0. Retrieve persistent active session data from platform store
    user_key = f"sess_{ctx.auth.get_user_id()}"
    active_session_data = {}
    try:
        active_session_data = ctx.get(scope="platform", collection_name="active_sessions", doc_id=user_key) or {}
    except Exception as sess_get_err:
        print(f"⚠️ Non-critical: Failed to retrieve active session: {sess_get_err}")

    # 1. Fallback: Resolve mobile number from session state or active session document
    if not mobile_number or mobile_number.strip() == "":
        if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
            mobile_number = ctx.session.state.get("pending_mobile") or ""
        if not mobile_number:
            mobile_number = active_session_data.get("pending_mobile") or ""

    # 2. Fallback: Resolve mobile number from pending_otps collection in platform database
    if not mobile_number or mobile_number.strip() == "":
        try:
            session_id = (
                getattr(ctx.auth, "session_id", None)
                or (getattr(ctx, "raw_context", {}) or {}).get("sessionId")
                or (getattr(ctx, "raw_context", {}) or {}).get("session_id")
                or f"session_{ctx.auth.get_user_id()}_{ctx.auth.hub_id}"
            )
            otp_doc = ctx.get(scope="platform", collection_name="pending_otps", doc_id=session_id)
            if otp_doc:
                mobile_number = otp_doc.get("mobile_number") or ""
        except Exception:
            pass

    # 3. Fallback: Resolve mobile number from session event history
    if not mobile_number or mobile_number.strip() == "":
        try:
            if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "events") and ctx.session.events:
                for ev in reversed(ctx.session.events):
                    content = getattr(ev, "content", None)
                    if content and hasattr(content, "parts"):
                        for p in content.parts:
                            text = getattr(p, "text", "") or ""
                            m = re.search(r"(\+\d{10,15})", text)
                            if m:
                                mobile_number = m.group(1)
                                break
                            fc = getattr(p, "function_call", None)
                            if fc and getattr(fc, "name", "") == "send_mobile_otp":
                                args = getattr(fc, "args", {}) or {}
                                if args.get("mobile_number"):
                                    mobile_number = str(args.get("mobile_number"))
                                    break
                    if mobile_number:
                        break
        except Exception:
            pass

    clean_phone = "".join(filter(str.isdigit, mobile_number))
    has_country = True
    if len(clean_phone) >= 10:
        has_country = mobile_number.strip().startswith('+')
        
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
        return {
            "valid": False,
            "message": "Invalid mobile number format. Please include your country code starting with '+' (e.g. +919876543210 or +15550199000)."
        }

    # Verify OTP code (123456 dev code or live SMS gateway)
    is_valid = False
    if otp_code.strip() == "123456":
        is_valid = True
    else:
        try:
            res = ctx.verify_otp(mobile_number, otp_code)
            if res.get("success"):
                is_valid = True
            elif otp_code.strip() == "123456":
                is_valid = True
        except Exception:
            if otp_code.strip() == "123456":
                is_valid = True

    if not is_valid:
        return {
            "valid": False,
            "message": "Invalid verification code. Please check and try again."
        }

    # Save verified mobile number in session state & platform database
    try:
        if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
            ctx.session.state["verified_mobile"] = mobile_number
    except Exception:
        pass

    try:
        session_id = (
            getattr(ctx.auth, "session_id", None)
            or (getattr(ctx, "raw_context", {}) or {}).get("sessionId")
            or (getattr(ctx, "raw_context", {}) or {}).get("session_id")
            or f"session_{ctx.auth.get_user_id()}_{ctx.auth.hub_id}"
        )
        ctx.save(
            scope="platform",
            collection_name="verified_sessions",
            doc_id=session_id,
            data={"verified_mobile": mobile_number}
        )
    except Exception as e:
        print(f"⚠️ Non-critical: Failed to save verified session doc: {e}")

    def normalize_phone(num: str) -> str:
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_mobile = normalize_phone(mobile_number)

    def get_linked_organizations() -> list:
        input_num = clean_mobile
        leads = ctx.list(scope="platform", collection_name="leads")
        linked_orgs = []
        for l in leads:
            lead_num = normalize_phone(l.get("contact_mobile") or "")
            if lead_num == input_num:
                linked_orgs.append({
                    "org_name": l.get("org_name"),
                    "status": l.get("sales_status") or "OPEN"
                })
        return linked_orgs

    # Determine flow: check session state or active session store
    active_flow = active_session_data.get("active_flow")
    active_org_id = active_session_data.get("active_org_id")
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        if not active_flow:
            active_flow = ctx.session.state.get("active_flow")
        if not active_org_id:
            active_org_id = ctx.session.state.get("active_org_id")

    # FLOW A: SUBSCRIPTION ONBOARDING FLOW
    if (active_flow == "onboarding" or active_org_id):
        org_id = active_org_id
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id) if org_id else None
        
        if lead and lead.get("status") != "ASSOCIATED":
            lead["contact_mobile"] = clean_mobile
            lead["status"] = "ASSOCIATED"
            
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
            try:
                alert_id = f"alert_{int(time.time())}"
                alert_msg = f"New unverified lead has arrived for organization '{lead.get('org_name')}'."
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
            except Exception as a_err:
                print(f"⚠️ [ALERT WARNING] Failed to create sales alert: {a_err}")

            # Queue rendering the summary card widget!
            summary_data = {
                "summary_name": lead.get("org_name") or "",
                "summary_description": lead.get("org_description") or "",
                "summary_website": lead.get("org_website") or "",
                "summary_position": lead.get("user_position") or "",
                "summary_contact_name": lead.get("contact_name") or "",
                "summary_contact_email": lead.get("contact_email") or "",
                "summary_contact_phone": lead.get("contact_mobile") or clean_mobile or mobile_number or ""
            }
            try:
                ctx.show_widget("org_summary_card", data=summary_data)
            except Exception as w_err:
                print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue summary widget: {w_err}")

            if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
                ctx.session.state.pop("active_org_id", None)
                ctx.session.state.pop("active_flow", None)

            try:
                ctx.delete(scope="platform", collection_name="active_sessions", doc_id=user_key)
            except Exception:
                pass

            linked_orgs = get_linked_organizations()
            return {
                "valid": True,
                "flow": "onboarding",
                "org_id": org_id,
                "org_name": lead.get("org_name"),
                "message": f"Identity verified and organization '{lead.get('org_name')}' subscription request submitted successfully.",
                "linked_organizations": linked_orgs
            }

    # FLOW B: STATUS CHECK FLOW
    try:
        ctx.delete(scope="platform", collection_name="active_sessions", doc_id=user_key)
    except Exception:
        pass

    linked_orgs = get_linked_organizations()
    return {
        "valid": True,
        "flow": "status_check",
        "message": "OTP verification successful. Identity verified successfully.",
        "linked_organizations": linked_orgs
    }
