import os
import json
import re
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
            
    # Check if user has verified mobile in current session state or platform database
    verified_mobile = ""
    if hasattr(ctx, "session") and ctx.session and hasattr(ctx.session, "state") and ctx.session.state is not None:
        verified_mobile = ctx.session.state.get("verified_mobile", "")

    if not verified_mobile:
        try:
            session_id = (
                getattr(ctx.auth, "session_id", None)
                or (getattr(ctx, "raw_context", {}) or {}).get("sessionId")
                or (getattr(ctx, "raw_context", {}) or {}).get("session_id")
                or f"session_{ctx.auth.get_user_id()}_{ctx.auth.hub_id}"
            )
            v_doc = ctx.get(scope="platform", collection_name="verified_sessions", doc_id=session_id)
            if v_doc:
                verified_mobile = v_doc.get("verified_mobile", "")
        except Exception:
            pass

    # If active_session is explicitly set to True in database, or mobile is verified in session, override and force it as valid
    if mock_session == True or verified_mobile:
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
            and not (len(user_id) == 28 and re.match(r"^[A-Za-z0-9]+$", user_id))
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
        mobile_number = verified_mobile or (user_id if not "@" in user_id else "")
        
        # Try to resolve user's real name, email, and mobile from platform_users/{user_id} only if authenticated
        is_authenticated_user = bool(
            user_id 
            and not user_id.startswith("guest") 
            and not user_id.startswith("anonymous")
            and not user_id in ("dummy_user", "default_user", "dev-user-123") 
            and not (len(user_id) == 28 and re.match(r"^[A-Za-z0-9]+$", user_id))
        )
        if is_authenticated_user:
            try:
                user_doc = ctx._db_client.document(f"platform_users/{user_id}").get()
                if user_doc.exists:
                    user_data = user_doc.to_dict() or {}
                    email_address = user_data.get("email") or email_address
                    mobile_number = user_data.get("phone") or mobile_number
                    
                    first_name = user_data.get("first_name") or ""
                    last_name = user_data.get("last_name") or ""
                    full_name = f"{first_name} {last_name}".strip() or full_name
            except Exception as e:
                print(f"⚠️ [USER PROFILE RETRIEVAL WARNING] Failed to fetch platform_user details: {e}")

        clean_user_id = normalize_phone(user_id)
        clean_mobile_number = normalize_phone(mobile_number)

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
            elif lead_mobile and clean_mobile_number and normalize_phone(lead_mobile) == clean_mobile_number:
                is_match = True
                
            if is_match:
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("sales_status") or "OPEN"
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
