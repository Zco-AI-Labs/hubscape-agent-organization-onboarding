from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_otp_verify_widget() -> dict:
    """
    Renders the OTP verification code input widget in the user interface.
    """
    ctx = get_context()
    return ctx.show_widget("otp_verify_widget")
