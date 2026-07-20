from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_personal_details_widget() -> dict:
    """
    Renders the personal contact information form widget (for name and email) in the user interface.
    """
    ctx = get_context()
    return ctx.show_widget("personal_details_widget")
