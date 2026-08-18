from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def save_phone_details() -> dict:
    """
    Renders the phone number collection widget in the UI to ask an unverified user for their mobile number.
    Call this tool when an unauthenticated user asks for their subscription or request status.
    You must STOP your turn after calling this tool and wait for the user to submit their phone number.
    """
    ctx = get_context()
    return ctx.show_widget("phone_details")
