import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def check_mobile_exist(mobile_number: str) -> dict:
    """
    Checks if a personal contact mobile number exists in the registered platform users database.

    Args:
        mobile_number: The personal mobile number to check (e.g. 555-0199).
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

    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            input_num = normalize_phone(mobile_number)
            for user in data.get("registered_users", []):
                db_num = normalize_phone(user.get("mobile_number", ""))
                if db_num == input_num:
                    linked_org = None
                    for lead in data.get("leads", []):
                        lead_num = normalize_phone(lead.get("contact_mobile") or "")
                        if lead_num == input_num or (lead.get("contact_email") and lead.get("contact_email") == user.get("email_address")):
                            linked_org = {
                                "org_name": lead.get("org_name"),
                                "status": lead.get("status")
                            }
                            break
                    return {
                        "exists": True,
                        "user": user,
                        "linked_organization": linked_org
                    }
                    
    return {
        "exists": False
    }
