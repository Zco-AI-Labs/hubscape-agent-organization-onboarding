import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def verify_mobile_otp(mobile_number: str, otp_code: str) -> dict:
    """
    Validates the 6-digit OTP code entered by the user.

    Args:
        mobile_number: The personal mobile number associated with the code.
        otp_code: The 6-digit verification code.
    """
    clean_phone = "".join(filter(str.isdigit, mobile_number))
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)):
        return {
            "valid": False,
            "message": "Invalid mobile number format. Please provide a valid phone number (e.g. 555-019-9000)."
        }

    ctx = get_context()
    res = ctx.verify_otp(mobile_number, otp_code)
    
    if res.get("success"):
        return {
            "valid": True,
            "message": "OTP verification successful."
        }
            
    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
