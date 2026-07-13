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
    if os.path.isdir("app"):
        db_path = "app/mock_db.json"
    else:
        runtime_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(runtime_dir, "mock_db.json")
    
    def normalize_phone(num: str) -> str:
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_number = normalize_phone(mobile_number)
    
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        active_otps = data.get("active_otps", {})
        saved_code = active_otps.get(clean_number)
        
        if saved_code and saved_code == otp_code:
            # Clear used code
            active_otps.pop(clean_number, None)
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return {
                "valid": True,
                "message": "OTP verification successful."
            }
            
    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
