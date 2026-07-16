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
    import re
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, contact_email.strip()):
        return {
            "status": "error",
            "message": "Invalid contact email format. Please provide a valid email address (e.g. name@domain.com)."
        }
        
    clean_phone = "".join(filter(str.isdigit, contact_mobile))
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)):
        return {
            "status": "error",
            "message": "Invalid contact mobile format. Please provide a valid phone number (e.g. 555-019-9000)."
        }

    ctx = get_context()
    # Find lead
    lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
    if not lead:
        return {"status": "error", "message": f"Lead record {org_id} not found."}
        
    def normalize_phone(num: str) -> str:
        """
        Helper to normalize formatting by extracting digits and stripping country codes.
        """
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean

    clean_mobile = normalize_phone(contact_mobile)

    # Update lead details
    lead["contact_email"] = contact_email
    lead["contact_mobile"] = clean_mobile
    lead["contact_name"] = full_name or lead.get("contact_name") or "New User"
    lead["status"] = "ASSOCIATED"
    
    ctx.save(scope="platform", collection_name="leads", doc_id=org_id, data=lead)
    
    # Check if user exists in registered_users
    user_exists = ctx.get(scope="platform", collection_name="registered_users", doc_id=clean_mobile)
    if not user_exists:
        user_records = ctx.list(scope="platform", collection_name="registered_users")
        for u in user_records:
            if normalize_phone(u.get("mobile_number", "")) == clean_mobile:
                user_exists = u
                break
                
    if not user_exists:
        ctx.save(
            scope="platform",
            collection_name="registered_users",
            doc_id=clean_mobile,
            data={
                "mobile_number": clean_mobile,
                "full_name": full_name or "New User",
                "email_address": contact_email
            }
        )
        
    # Add Sales Representative alert log
    alert_id = f"alert_{int(time.time())}"
    alert_msg = f"New unverified lead has arrived for organization '{lead['org_name']}'."
    
    ctx.save(
        scope="platform",
        collection_name="sales_alerts",
        doc_id=alert_id,
        data={
            "lead_id": org_id,
            "message": alert_msg,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )
        
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
