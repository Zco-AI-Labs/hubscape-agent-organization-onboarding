from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_mobile_input_widget() -> dict:
    """
    Renders the mobile number entry form widget in the user interface to request the user's mobile number.
    """
    ctx = get_context()
    return ctx.show_widget("mobile_input_widget")
