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
    ctx = get_context()
    def normalize_phone(num: str) -> str:
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_number = normalize_phone(mobile_number)
    
    otp_doc = ctx.get(scope="platform", collection_name="active_otps", doc_id=clean_number)
    saved_code = otp_doc.get("otp_code") if otp_doc else None
    
    if saved_code and saved_code == otp_code:
        ctx.delete(scope="platform", collection_name="active_otps", doc_id=clean_number)
        return {
            "valid": True,
            "message": "OTP verification successful."
        }
            
    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
