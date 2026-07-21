import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def show_personal_details_widget(org_id: str = "") -> dict:
    """
    Renders the personal contact information form widget (for name and email) in the user interface.

    Args:
        org_id: Optional organization lead ID to bind to the form.
    """
    ctx = get_context()

    # Load the widget template manually to perform template parameter replacements on the backend
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(app_dir, "ui", "widgets", "personal_details_widget.json")

    with open(template_path, "r", encoding="utf-8") as f:
        widget_config = json.load(f)

    # Perform backend-side template replacements
    config_str = json.dumps(widget_config).replace("{{agent_id}}", ctx.agent_id)
    config_str = config_str.replace("{{org_id}}", org_id)
    widget_config = json.loads(config_str)

    # Queue the action directly to context.actions
    action_payload = {
        "type": "OPEN_AGENT_WIDGET",
        "payload": {
            "widgetId": "personal_details_widget",
            "widgetConfig": widget_config,
            "data": {"org_id": org_id},
            "styling": ctx.raw_context.get("styling", {}),
            "userPreferences": ctx.raw_context.get("userPreferences", {})
        }
    }
    ctx.actions.append(action_payload)
    return {"status": "success", "message": "Widget 'personal_details_widget' successfully queued."}
