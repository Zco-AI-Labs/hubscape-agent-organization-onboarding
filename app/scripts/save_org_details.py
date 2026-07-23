import os
import json
import time
import datetime
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def save_org_details(
    org_name: str,
    org_description: str,
    org_website: str = "",
    user_position: str = ""
) -> dict:
    """
    Saves the organization onboarding details with status set to UNVERIFIED in the local JSON mock database.

    Args:
        org_name: Legal name of the organization.
        org_description: Brief description of the organization.
        org_website: Website address of the organization (optional, e.g. www.apex.com).
        user_position: Position or title of the user onboarding the organization.
    """
    website_clean = org_website.strip() if org_website else ""
    if website_clean:
        if not ('.' in website_clean and len(website_clean) >= 4):
            return {
                "status": "error",
                "message": "Invalid organization website format. Please provide a valid URL (e.g. apex.com or www.apex.com)."
            }

    ctx = get_context()
    lead_id = f"lead_{int(time.time())}"
    
    lead_data = {
        "id": lead_id,
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
        doc_id=lead_id,
        data=lead_data
    )

    # Save lead_id in the database inside the session state variable
    session_id = ctx.raw_context.get("sessionId") or ctx.raw_context.get("session_id")
    if session_id:
        try:
            ctx.save(
                scope="user",
                collection_name="sessions",
                doc_id=session_id,
                data={
                    "lead_id": lead_id
                }
            )
        except Exception as e:
            print(f"⚠️ [SESSION SAVE WARNING] Failed to save lead_id to session document: {e}")

    # Queue rendering the personal details widget to collect contacts
    try:
        ctx.show_widget("personal_details_widget")
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue personal details widget: {e}")

    return {
        "status": "success",
        "lead_id": lead_id,
        "message": f"Organization '{org_name}' details successfully saved."
    }
