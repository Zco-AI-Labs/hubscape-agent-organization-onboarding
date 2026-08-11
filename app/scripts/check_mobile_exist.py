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
    has_country = True
    if len(clean_phone) >= 10:
        has_country = mobile_number.strip().startswith('+')
        
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
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
    
    # Check leads to see if user has already entered their contact info under this number
    leads = ctx.list(scope="platform", collection_name="leads")
    matching_lead = None
    for lead in leads:
        lead_num = normalize_phone(lead.get("contact_mobile") or "")
        if lead_num == input_num:
            matching_lead = lead
            break

    if matching_lead:
        # Build registered user properties from the lead snapshot
        user = {
            "mobile_number": input_num,
            "full_name": matching_lead.get("contact_name") or "New User",
            "email_address": matching_lead.get("contact_email") or ""
        }
        
        linked_orgs = []
        for lead in leads:
            lead_num = normalize_phone(lead.get("contact_mobile") or "")
            if lead_num == input_num or (lead.get("contact_email") and lead.get("contact_email") == user.get("email_address")):
                linked_orgs.append({
                    "org_name": lead.get("org_name"),
                    "status": lead.get("sales_status") or "OPEN"
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
