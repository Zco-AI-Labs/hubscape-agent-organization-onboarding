import os
import json
import time
import datetime
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def associate_contact_and_alert(
    org_id: str,
    contact_email: str,
    contact_mobile: str,
    full_name: str = ""
) -> dict:
    """
    Associates the user's verified contact details with the saved organization lead,
    registers the user if new, triggers a Sales Rep alert, and displays the summary card.

    Args:
        org_id: The ID of the saved organization lead record.
        contact_email: Contact email address collected/retrieved.
        contact_mobile: Personal mobile number collected/retrieved.
        full_name: Full name of the contact (optional).
    """
    ctx = get_context()
    if os.path.isdir("app"):
        db_path = "app/mock_db.json"
    else:
        runtime_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(runtime_dir, "mock_db.json")
    
    if not os.path.exists(db_path):
        return {"status": "error", "message": "Database not initialized."}
        
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Find lead
    lead = None
    for l in data.get("leads", []):
        if l.get("id") == org_id:
            lead = l
            break
            
    if not lead:
        return {"status": "error", "message": f"Lead record {org_id} not found."}
        
    def normalize_phone(num: str) -> str:
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_mobile = normalize_phone(contact_mobile)

    # Update lead details
    lead["contact_email"] = contact_email
    lead["contact_mobile"] = clean_mobile
    lead["contact_name"] = full_name or lead.get("contact_name")
    lead["status"] = "ASSOCIATED"
    lead["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # If new user, add to registered_users list
    user_exists = False
    for user in data.get("registered_users", []):
        db_num = normalize_phone(user.get("mobile_number", ""))
        if db_num == clean_mobile:
            user_exists = True
            break
            
    if not user_exists:
        data["registered_users"].append({
            "mobile_number": clean_mobile,
            "full_name": full_name or "New User",
            "email_address": contact_email
        })
        
    # Add Sales Representative alert log
    alert_id = f"alert_{int(time.time())}"
    alert_msg = f"New unverified lead has arrived for organization '{lead['org_name']}'."
    data["sales_alerts"].append({
        "alert_id": alert_id,
        "lead_id": org_id,
        "message": alert_msg,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    
    # Write changes back
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    # Queue rendering the summary card widget!
    summary_data = {
        "summary_name": lead.get("org_name"),
        "summary_description": lead.get("org_description"),
        "summary_email": lead.get("org_email"),
        "summary_phone": lead.get("org_phone")
    }
    try:
        ctx.show_widget("org_summary_card", data=summary_data)
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue summary widget: {e}")
        
    return {
        "status": "success",
        "message": "Contact details successfully associated. Sales alert dispatched.",
        "org_id": org_id,
        "alert_id": alert_id
    }
