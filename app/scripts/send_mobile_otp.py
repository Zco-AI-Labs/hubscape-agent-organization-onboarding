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
    if "0199" in clean_number:
        code = "123456"
    elif "9999" in clean_number:
        code = "987654"
    else:
        code = "123456"
        
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "active_otps" not in data:
            data["active_otps"] = {}
        data["active_otps"][clean_number] = code
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    print(f"📡 [OTP GATEWAY] Sent verification code {code} to mobile {clean_number}.")
    
    return {
        "status": "success",
        "message": f"6-digit verification code successfully sent to mobile number {mobile_number}."
    }
