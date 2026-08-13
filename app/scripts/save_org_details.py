import os
import json
import time
import datetime
import re
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
    
    # Determine if user is authenticated/verified or guest (checking for 28-char alphanumeric Firebase guest UIDs)
    is_authenticated = bool(
        user_id
        and not user_id.startswith("guest")
        and not user_id.startswith("anonymous")
        and user_id not in ("dummy_user", "default_user", "dev-user-123")
        and not (len(user_id) == 28 and re.match(r"^[A-Za-z0-9]+$", user_id))
    )
    owner_id = user_id if is_authenticated else "anonymous"
    
    contact_email = None
    contact_mobile = None
    contact_name = None
    
    if is_authenticated:
        try:
            user_doc = ctx._db_client.document(f"platform_users/{user_id}").get()
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                contact_email = user_data.get("email")
                contact_mobile = user_data.get("phone")
                
                first_name = user_data.get("first_name") or ""
                last_name = user_data.get("last_name") or ""
                contact_name = f"{first_name} {last_name}".strip() or None
        except Exception as e:
            print(f"⚠️ [USER PROFILE RETRIEVAL WARNING] Failed to fetch platform_user details: {e}")
            
    lead_data = {
        "id": org_id,
        "org_name": org_name,
        "org_description": org_description,
        "org_website": website_clean,
        "user_position": user_position,
        "status": "ASSOCIATED" if is_authenticated else "UNVERIFIED",
        "sales_status": "OPEN",
        "contact_email": contact_email,
        "contact_mobile": contact_mobile,
        "contact_name": contact_name,
        "owner_id": owner_id
    }
    
    ctx.save(
        scope="platform",
        collection_name="leads",
        doc_id=org_id,
        data=lead_data
    )

    if is_authenticated:
        try:
            alert_id = f"alert_{int(time.time())}"
            alert_msg = f"New unverified lead has arrived for organization '{org_name}'."
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
        except Exception as e:
            print(f"⚠️ [ALERT WARNING] Failed to create sales alert: {e}")

    # Save generated ID to session state for multi-turn access
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        ctx.session.state["active_org_id"] = org_id

    # Queue rendering the appropriate widget based on auth track
    try:
        if is_authenticated:
            summary_data = {
                "summary_name": org_name,
                "summary_description": org_description,
                "summary_website": website_clean,
                "summary_position": user_position
            }
            ctx.show_widget("org_summary_card", data=summary_data)
        else:
            ctx.show_widget("mobile_input_widget")
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue widget: {e}")

    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Organization '{org_name}' details successfully saved with org_id: {org_id}."
    }
