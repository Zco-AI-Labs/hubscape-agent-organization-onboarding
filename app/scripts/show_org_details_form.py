from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_org_details_form() -> dict:
    """
    Renders the organization onboarding details form widget in the user interface to collect organization info.
    """
    ctx = get_context()
    return ctx.show_widget("org_details_form")
