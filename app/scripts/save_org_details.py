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
    import re
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, org_email.strip()):
        return {
            "status": "error",
            "message": "Invalid organization email format. Please provide a valid email address (e.g. name@domain.com)."
        }
        
    clean_phone = "".join(filter(str.isdigit, org_phone))
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)):
        return {
            "status": "error",
            "message": "Invalid organization phone format. Please provide a valid phone number (e.g. 555-019-9000)."
        }

    ctx = get_context()
    org_id = f"lead_{int(time.time())}"
    
    lead_data = {
        "org_name": org_name,
        "org_description": org_description,
        "org_email": org_email,
        "org_phone": org_phone,
        "user_position": user_position,
        "status": "UNVERIFIED",
        "contact_email": None,
        "contact_mobile": None,
        "contact_name": None
    }
    
    ctx.save(
        scope="platform",
        collection_name="leads",
        doc_id=org_id,
        data=lead_data
    )
        
    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Organization '{org_name}' details successfully saved as UNVERIFIED."
    }
