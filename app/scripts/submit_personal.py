import os
import json
import time
import re
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def submit_personal(
    full_name: str,
    contact_email: str,
    org_id: str = None
) -> dict:
    """
    Saves the user's personal details (full name and email) to the specified lead record,
    sets its status to ASSOCIATED, and queues the organization summary card.

    Args:
        full_name: Contact person's full name.
        contact_email: Contact person's email address.
        org_id: The ID of the saved organization lead record.
    """
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, contact_email.strip()):
        return {
            "status": "error",
            "message": "Invalid contact email format. Please provide a valid email address (e.g. name@domain.com)."
        }

    ctx = get_context()
    
    # Resolve active org_id: primary source is session state, fallback is tool parameter
    resolved_org_id = None
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state:
        resolved_org_id = ctx.session.state.get("active_org_id")
        
    if not resolved_org_id:
        resolved_org_id = org_id
        
    org_id = resolved_org_id

    if not org_id:
        return {
            "status": "error",
            "message": "Error: Could not resolve active Organization ID for this session."
        }
        
    # Retrieve existing lead record
    lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
    if not lead:
        return {
            "status": "error",
            "message": f"Lead record {org_id} not found."
        }

    # Update contact details and set status to ASSOCIATED
    lead["contact_email"] = contact_email.strip()
    lead["contact_name"] = full_name.strip()
    lead["status"] = "ASSOCIATED"

    # Update owner_id if the user is authenticated in this session
    user_id = ctx.auth.get_user_id()
    is_authenticated = bool(
        user_id
        and not user_id.startswith("guest")
        and not user_id.startswith("anonymous")
        and user_id not in ("dummy_user", "default_user", "dev-user-123")
        and not (len(user_id) == 28 and re.match(r"^[A-Za-z0-9]+$", user_id))
    )
    if is_authenticated:
        lead["owner_id"] = user_id
    elif lead.get("owner_id") is None:
        lead["owner_id"] = "anonymous"

    ctx.save(scope="platform", collection_name="leads", doc_id=org_id, data=lead)

    # Queue rendering the summary card widget
    summary_data = {
        "summary_name": lead.get("org_name"),
        "summary_description": lead.get("org_description"),
        "summary_website": lead.get("org_website")
    }
    try:
        ctx.show_widget("org_summary_card", data=summary_data)
    except Exception as e:
        print(f"⚠️ [WIDGET QUEUE WARNING] Failed to queue summary widget: {e}")

    return {
        "status": "success",
        "org_id": org_id,
        "message": f"Contact details successfully associated for organization '{lead.get('org_name')}'."
    }
