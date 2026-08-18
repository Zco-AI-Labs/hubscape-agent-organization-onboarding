from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_phone_otp_verify_widget() -> dict:
    """
    Renders the mobile phone number verification widget in the user interface to initiate identity verification.
    """
    ctx = get_context()
    return ctx.show_widget("phone_otp_verify_widget")
