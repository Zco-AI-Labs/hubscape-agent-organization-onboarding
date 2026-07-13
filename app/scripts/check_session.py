import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def check_session() -> dict:
    """
    Checks if the user has an active, authenticated platform session.
    """
    ctx = get_context()
    user_id = ctx.auth.get_user_id()
    
    # If running locally or via a mock testing setup, check mock_db.json for session override
    if os.path.isdir("app"):
        db_path = "app/mock_db.json"
    else:
        runtime_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(runtime_dir, "mock_db.json")
    
    # Auto-initialize DB with default mock data if missing
    if not os.path.exists(db_path):
        initial_data = {
            "active_session": False,
            "leads": [],
            "registered_users": [
                {
                    "mobile_number": "555-0199",
                    "full_name": "Alex Doe",
                    "email_address": "alex@apex.com"
                }
            ],
            "active_otps": {},
            "sales_alerts": []
        }
        try:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
        except Exception:
            pass

    mock_session = None
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            mock_session = data.get("active_session")
            
    # If active_session is explicitly set in database, use it as the source of truth
    if mock_session is not None:
        is_valid = bool(mock_session)
    else:
        is_valid = bool(user_id and not user_id.startswith("guest") and not user_id == "dummy_user" and not user_id == "default_user")

    if is_valid:
        # Retrieve the user record from the database if matching
        full_name = "Alex"
        email_address = "alex@apex.com"
        mobile_number = "555-0199"
        
        linked_org = None
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for user in data.get("registered_users", []):
                    if user.get("email_address") == user_id or user.get("full_name") == user_id:
                        full_name = user.get("full_name")
                        email_address = user.get("email_address")
                        mobile_number = user.get("mobile_number")
                        break
                
                def normalize_phone(num: str) -> str:
                    clean = "".join(filter(str.isdigit, num))
                    if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
                        clean = clean[1:]
                    return clean
                
                clean_mobile = normalize_phone(mobile_number)
                for lead in data.get("leads", []):
                    db_num = normalize_phone(lead.get("contact_mobile") or "")
                    if db_num == clean_mobile or (lead.get("contact_email") and lead.get("contact_email") == email_address):
                        linked_org = {
                            "org_name": lead.get("org_name"),
                            "status": lead.get("status")
                        }
                        break
                        
        return {
            "session_valid": True,
            "user_data": {
                "full_name": full_name,
                "email_address": email_address,
                "mobile_number": mobile_number,
                "linked_organization": linked_org
            }
        }
        
    return {
        "session_valid": False
    }
