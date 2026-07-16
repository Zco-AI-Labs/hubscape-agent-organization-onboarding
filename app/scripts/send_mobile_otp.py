import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def send_mobile_otp(mobile_number: str) -> dict:
    """
    Triggers sending a 6-digit OTP verification code to the user's personal mobile number.

    Args:
        mobile_number: The personal mobile number to verify (e.g. 555-0199).
    """
    clean_phone = "".join(filter(str.isdigit, mobile_number))
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)):
        return {
            "status": "error",
            "message": "Invalid mobile number format. Please provide a valid phone number (e.g. 555-019-9000)."
        }

    ctx = get_context()
    res = ctx.send_otp(mobile_number)
    
    if not res.get("success"):
        return {
            "status": "error",
            "message": res.get("message") or "Failed to send verification code."
        }
        
    return {
        "status": "success",
        "message": f"6-digit verification code successfully sent to mobile number {mobile_number}."
    }
