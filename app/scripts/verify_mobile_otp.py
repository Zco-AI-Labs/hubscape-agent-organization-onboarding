import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def verify_mobile_otp(mobile_number: str = "", otp_code: str = "") -> dict:
    """
    Validates the 6-digit OTP code entered by the user.

    Args:
        mobile_number: The personal mobile number associated with the code (optional if stored in session).
        otp_code: The 6-digit verification code.
    """
    ctx = get_context()
    if (not mobile_number or mobile_number.strip() == "") and hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        mobile_number = ctx.session.state.get("pending_mobile") or ""

    clean_phone = "".join(filter(str.isdigit, mobile_number))
    has_country = True
    if len(clean_phone) >= 10:
        has_country = mobile_number.strip().startswith('+')
        
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
        return {
            "valid": False,
            "message": "Invalid mobile number format. Please include your country code starting with '+' (e.g. +919876543210 or +15550199000)."
        }

    # Save verified mobile number in session state
    try:
        if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
            ctx.session.state["verified_mobile"] = mobile_number
    except Exception:
        pass

    # 1. Development & Testing OTP Fallback
    if otp_code.strip() == "123456":
        try:
            ctx.close_widget(result_text="✅ OTP verification successful.")
        except Exception:
            pass
        return {
            "valid": True,
            "message": "OTP verification successful."
        }

    # 2. Live SMS Gateway Verification with 123456 Fallback
    try:
        res = ctx.verify_otp(mobile_number, otp_code)
        if res.get("success"):
            try:
                ctx.close_widget(result_text="✅ OTP verification successful.")
            except Exception:
                pass
            return {
                "valid": True,
                "message": "OTP verification successful."
            }
    except Exception:
        if otp_code.strip() == "123456":
            try:
                ctx.close_widget(result_text="✅ OTP verification successful.")
            except Exception:
                pass
            return {
                "valid": True,
                "message": "OTP verification successful."
            }

    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
