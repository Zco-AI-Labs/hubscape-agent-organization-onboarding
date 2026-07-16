import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def check_mobile_exist(mobile_number: str) -> dict:
    """
    Checks if a personal contact mobile number exists in the registered platform users database.

    Args:
        mobile_number: The personal mobile number to check (e.g. 555-0199).
    """
    clean_phone = "".join(filter(str.isdigit, mobile_number))
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)):
        return {
            "exists": False
        }

    ctx = get_context()
    def normalize_phone(num: str) -> str:
        """
        Helper to normalize formatting by extracting digits and stripping country codes.
        """
        clean = "".join(filter(str.isdigit, num))
        if (len(clean) == 11 or len(clean) == 8) and clean.startswith("1"):
            clean = clean[1:]
        return clean
    
    input_num = normalize_phone(mobile_number)
    user = ctx.get(scope="platform", collection_name="registered_users", doc_id=input_num)
    
    if not user:
        user_records = ctx.list(scope="platform", collection_name="registered_users")
        for u in user_records:
            if normalize_phone(u.get("mobile_number", "")) == input_num:
                user = u
                break
                
    if user:
        linked_orgs = []
        leads = ctx.list(scope="platform", collection_name="leads")
        for lead in leads:
            lead_num = normalize_phone(lead.get("contact_mobile") or "")
            if lead_num == input_num or (lead.get("contact_email") and lead.get("contact_email") == user.get("email_address")):
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("status")
                })
        
        primary_org = linked_orgs[0] if linked_orgs else None
        return {
            "exists": True,
            "user": user,
            "linked_organization": primary_org,
            "linked_organizations": linked_orgs
        }
        
    return {
        "exists": False
    }
