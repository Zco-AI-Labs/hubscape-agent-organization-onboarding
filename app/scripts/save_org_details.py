import os
import json
import time
import datetime
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def save_org_details(
    org_name: str,
    org_description: str,
    org_email: str,
    org_phone: str,
    user_position: str
) -> dict:
    """
    Saves the organization onboarding details with status set to UNVERIFIED in the local JSON mock database.

    Args:
        org_name: Legal name of the organization.
        org_description: Brief description of the organization.
        org_email: Primary contact email for the organization.
        org_phone: Contact phone number for the organization.
        user_position: Position or title of the user onboarding the organization.
    """
    ctx = get_context()
    if os.path.isdir("app"):
        db_path = "app/mock_db.json"
    else:
        runtime_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(runtime_dir, "mock_db.json")
    
    # Initialize DB if missing
    if not os.path.exists(db_path):
        data = {
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
    else:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
    org_id = f"lead_{int(time.time())}"
    
    new_lead = {
        "id": org_id,
        "org_name": org_name,
        "org_description": org_description,
        "org_email": org_email,
        "org_phone": org_phone,
        "user_position": user_position,
        "status": "UNVERIFIED",
        "contact_email": None,
        "contact_mobile": None,
        "contact_name": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    data["leads"].append(new_lead)
    
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Organization '{org_name}' details successfully saved as UNVERIFIED."
    }
