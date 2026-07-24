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
    org_id = f"lead_{int(time.time())}"
    
    user_id = ctx.auth.get_user_id()
    is_authenticated = bool(
        user_id
        and not user_id.startswith("guest")
        and not user_id.startswith("anonymous")
        and user_id not in ("dummy_user", "default_user", "dev-user-123")
    )
    owner_id = user_id if is_authenticated else "anonymous"
    
    lead_data = {
        "id": org_id,
        "org_name": org_name,
        "org_description": org_description,
        "org_website": website_clean,
        "user_position": user_position,
        "status": "UNVERIFIED",
        "contact_email": None,
        "contact_mobile": None,
        "contact_name": None,
        "owner_id": owner_id
    }
    
    ctx.save(
        scope="platform",
        collection_name="leads",
        doc_id=org_id,
        data=lead_data
    )

    # Save generated ID to session state for multi-turn access
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        ctx.session.state["active_org_id"] = org_id

    # Queue rendering the mobile input widget for phone identity verification
    try:
        ctx.show_widget("mobile_input_widget")
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue mobile input widget: {e}")

    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Organization '{org_name}' details successfully saved with org_id: {org_id}."
    }
