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
    elif mock_session == False and (user_id == "default_user" or user_id == "dummy_user" or user_id == "dev-user-123" or user_id == "anonymous_user" or not user_id):
        # Force invalid for generic developer sessions when active_session is set to false
        is_valid = False
    else:
        # Fallback to standard user_id check
        is_valid = bool(
            user_id 
            and not user_id.startswith("guest") 
            and not user_id.startswith("anonymous")
            and not user_id == "dummy_user" 
            and not user_id == "default_user" 
            and not user_id == "dev-user-123"
        )

    if is_valid:
        def normalize_phone(num: str) -> str:
            """
            Helper to normalize formatting by extracting digits and stripping country codes.
            """
            clean = "".join(filter(str.isdigit, num))
            if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
                clean = clean[1:]
            return clean

        # Set default fallback values
        full_name = user_id
        email_address = user_id if "@" in user_id else ""
        mobile_number = user_id if not "@" in user_id else ""
        clean_user_id = normalize_phone(user_id)

        linked_orgs = []
        leads = ctx.list(scope="platform", collection_name="leads")
        for lead in leads:
            lead_owner = lead.get("owner_id")
            lead_email = lead.get("contact_email")
            lead_mobile = lead.get("contact_mobile")
            
            is_match = False
            if lead_owner == user_id:
                is_match = True
            elif lead_email and email_address and lead_email.strip().lower() == email_address.strip().lower():
                is_match = True
            elif lead_mobile and clean_user_id and normalize_phone(lead_mobile) == clean_user_id:
                is_match = True
                
            if is_match:
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("status")
                })
                # Populate user contact details from the matching lead if we don't have them yet
                if lead_email:
                    email_address = lead_email
                if lead_mobile:
                    mobile_number = lead_mobile
                if lead.get("contact_name"):
                    full_name = lead.get("contact_name")
        
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
