import os
import json
import time
import datetime
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def save_org_details(
    org_name: str,
    org_description: str,
    org_website: str,
    user_position: str
) -> dict:
    """
    Saves the organization onboarding details with status set to UNVERIFIED in the local JSON mock database.

    Args:
        org_name: Legal name of the organization.
        org_description: Brief description of the organization.
        org_website: Website address of the organization (e.g. www.apex.com).
        user_position: Position or title of the user onboarding the organization.
    """
    website_clean = org_website.strip()
    if not ('.' in website_clean and len(website_clean) >= 4):
        return {
            "status": "error",
            "message": "Invalid organization website format. Please provide a valid URL (e.g. apex.com or www.apex.com)."
        }

    ctx = get_context()
    org_id = f"lead_{int(time.time())}"
    
    lead_data = {
        "org_name": org_name,
        "org_description": org_description,
        "org_website": website_clean,
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
