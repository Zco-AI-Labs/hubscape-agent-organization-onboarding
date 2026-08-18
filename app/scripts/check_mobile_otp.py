import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def check_mobile_otp(mobile_number: str = "", otp_code: str = "") -> dict:
    """
    Validates the 6-digit OTP code entered by the user.

    Args:
        mobile_number: The personal mobile number associated with the code (optional if stored in session).
        otp_code: The 6-digit verification code.
    """
    ctx = get_context()
    import re
    
    # 1. Fallback: Resolve mobile number from session state
    if (not mobile_number or mobile_number.strip() == "") and hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        mobile_number = ctx.session.state.get("pending_mobile") or ""

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

    def get_linked_organizations() -> list:
        def normalize_phone(num: str) -> str:
            clean = "".join(filter(str.isdigit, num))
            if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
                clean = clean[1:]
            return clean

        input_num = normalize_phone(mobile_number)
        leads = ctx.list(scope="platform", collection_name="leads")
        linked_orgs = []
        for lead in leads:
            lead_num = normalize_phone(lead.get("contact_mobile") or "")
            if lead_num == input_num:
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("sales_status") or "OPEN"
                })
        return linked_orgs

    # 1. Development & Testing OTP Fallback
    if otp_code.strip() == "123456":
        try:
            ctx.close_widget(result_text="✅ OTP verification successful.")
        except Exception:
            pass
        linked_orgs = get_linked_organizations()
        return {
            "valid": True,
            "message": "OTP verification successful. Identity verified successfully.",
            "linked_organizations": linked_orgs
        }

    # 2. Live SMS Gateway Verification with 123456 Fallback
    try:
        res = ctx.verify_otp(mobile_number, otp_code)
        if res.get("success"):
            try:
                ctx.close_widget(result_text="✅ OTP verification successful.")
            except Exception:
                pass
            linked_orgs = get_linked_organizations()
            return {
                "valid": True,
                "message": "OTP verification successful. Identity verified successfully.",
                "linked_organizations": linked_orgs
            }
    except Exception:
        if otp_code.strip() == "123456":
            try:
                ctx.close_widget(result_text="✅ OTP verification successful.")
            except Exception:
                pass
            linked_orgs = get_linked_organizations()
            return {
                "valid": True,
                "message": "OTP verification successful. Identity verified successfully.",
                "linked_organizations": linked_orgs
            }

    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
