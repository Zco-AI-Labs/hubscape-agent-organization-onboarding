from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_contact_form() -> dict:
    """
    Renders the contact support form widget in the user interface.
    """
    ctx = get_context()
    return ctx.show_widget("contact_form")
