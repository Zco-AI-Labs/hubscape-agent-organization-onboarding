from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_personal_details_widget(org_id: str = "") -> dict:
    """
    Renders the personal contact information form widget (for name and email) in the user interface.

    Args:
        org_id: Optional organization lead ID to bind to the form.
    """
    ctx = get_context()
    return ctx.show_widget("personal_details_widget", data={"org_id": org_id})
