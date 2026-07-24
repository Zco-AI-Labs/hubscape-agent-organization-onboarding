from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def close_widget() -> dict:
    """
    Closes the active Generative UI Lego widget or panel.
    """
    ctx = get_context()
    ctx.close_widget(result_text="Form cancelled.")
    return {
        "status": "success",
        "message": "Widget closed."
    }
