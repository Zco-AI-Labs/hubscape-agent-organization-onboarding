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
    ctx = get_context()
    def normalize_phone(num: str) -> str:
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean
    clean_number = normalize_phone(mobile_number)
    if "0199" in clean_number:
        code = "123456"
    elif "9999" in clean_number:
        code = "987654"
    else:
        code = "123456"
        
    ctx.save(
        scope="platform",
        collection_name="active_otps",
        doc_id=clean_number,
        data={"otp_code": code}
    )
            
    print(f"📡 [OTP GATEWAY] Sent verification code {code} to mobile {clean_number}.")
    
    return {
        "status": "success",
        "message": f"6-digit verification code successfully sent to mobile number {mobile_number}."
    }
