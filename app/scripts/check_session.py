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
    
    # Auto-initialize registered_users and session override if not present
    registered_users = ctx.list(scope="platform", collection_name="registered_users")
    if not registered_users:
        ctx.save(
            scope="platform",
            collection_name="registered_users",
            doc_id="5550199",
            data={
                "mobile_number": "555-0199",
                "full_name": "Alex Doe",
                "email_address": "alex@apex.com"
            }
        )
        
    cfg = ctx.get(scope="platform", collection_name="session_config", doc_id="override")
    if cfg is None:
        cfg = ctx.save(
            scope="platform",
            collection_name="session_config",
            doc_id="override",
            data={"active_session": False}
        )

    mock_session = cfg.get("active_session") if cfg else None
            
    # If active_session is explicitly set to True in database, override and force it as valid
    if mock_session == True:
        is_valid = True
    elif mock_session == False and (user_id == "default_user" or user_id == "dummy_user" or user_id == "dev-user-123" or not user_id):
        # Force invalid for generic developer sessions when active_session is set to false
        is_valid = False
    else:
        # Fallback to standard user_id check
        is_valid = bool(user_id and not user_id.startswith("guest") and not user_id == "dummy_user" and not user_id == "default_user" and not user_id == "dev-user-123")

    if is_valid:
        # Retrieve the user record from the database if matching
        full_name = "Alex"
        email_address = "alex@apex.com"
        mobile_number = "555-0199"
        
        linked_org = None
        user_records = ctx.list(scope="platform", collection_name="registered_users")
        for user in user_records:
            if user.get("email_address") == user_id or user.get("full_name") == user_id:
                full_name = user.get("full_name")
                email_address = user.get("email_address")
                mobile_number = user.get("mobile_number")
                break
        
        def normalize_phone(num: str) -> str:
            """
            Helper to normalize formatting by extracting digits and stripping country codes.
            """
            clean = "".join(filter(str.isdigit, num))
            if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
                clean = clean[1:]
            return clean
        
        clean_mobile = normalize_phone(mobile_number)
        linked_orgs = []
        leads = ctx.list(scope="platform", collection_name="leads")
        for lead in leads:
            db_num = normalize_phone(lead.get("contact_mobile") or "")
            if db_num == clean_mobile or (lead.get("contact_email") and lead.get("contact_email") == email_address):
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("status")
                })
        
        primary_org = linked_orgs[0] if linked_orgs else None
        return {
            "session_valid": True,
            "user_data": {
                "full_name": full_name,
                "email_address": email_address,
                "mobile_number": mobile_number,
                "linked_organization": primary_org,
                "linked_organizations": linked_orgs
            }
        }
        
    return {
        "session_valid": False
    }
