# Hubscape Agent Widget Closure Guide

This guide explains how to trigger widget closure actions both on the **client side** (for simple cancel/dismiss actions) and from the **agent side** (for form submit actions that send data to a subagent before closing).

---

## 📌 Summary of Closure Protocols

| Closure Type | `actionUrl` Protocol | Trigger Location | Network Call? | Best Used For |
|---|---|---|---|---|
| **Client-Side** | `client://close_widget` | Frontend Browser | No (0ms delay, no LLM) | Cancel, Dismiss, Close buttons |
| **Agent-Side** | `agent://<agent_id>/<action>` | Python Subagent Tool | Yes (POST data to agent) | Submit buttons, Save actions |

---

## 1. Pure Client-Side Closure (`client://`)

For buttons that should immediately unmount the widget without making an API request or calling a subagent tool:

### Lego Widget JSON Schema:
```json
{
  "type": "button",
  "props": {
    "label": "Cancel",
    "actionUrl": "client://close_widget?text=Form+cancelled",
    "styling": { "colorTheme": "slate" }
  }
}
```

* **Behavior**: When clicked, the frontend unmounts the active widget instantly and replaces it with `"Form cancelled"`.
* **Validation**: Bypasses all form input validation rules.

---

## 2. Subagent Form Submission + Widget Closure (`agent://`)

When a user submits a form, you typically want to:
1. Validate form fields on the client.
2. Send form payload to your subagent tool.
3. Process & save the data in Python.
4. **Close/unmount the widget upon successful processing.**

### Step 1: Lego Widget JSON Schema (Submit Button)
Set the `actionUrl` to target your subagent action endpoint:

```json
{
  "type": "container",
  "props": { "className": "flex flex-col gap-3 p-4" },
  "children": [
    {
      "type": "input",
      "props": {
        "name": "organization_name",
        "label": "Organization Name",
        "required": true
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Save & Complete",
        "actionUrl": "agent://{{agent_id}}/submit_organization",
        "styling": { "colorTheme": "blue" }
      }
    }
  ]
}
```

### Step 2: Python Subagent Tool Handler (`app/scripts/`)
Inside your Python tool implementation, call `context.close_widget()` before returning:

```python
from app.core.hubscape_adk import get_context

async def submit_organization(data: dict) -> dict:
    """Tool handler for submitting organization details."""
    context = get_context()
    
    # Extract form data sent by the widget
    org_name = data.get("organization_name")
    
    # 1. Save or process payload in backend database
    context.save(
        scope="org", 
        collection_name="organization_settings", 
        doc_id="config", 
        data={"org_name": org_name}
    )
    
    # 2. Programmatically close the active widget on the frontend UI
    context.close_widget(
        result_text=f"✅ Organization '{org_name}' saved successfully!"
    )
    
    return {
        "status": "success",
        "message": "Organization saved and widget closure directive dispatched."
    }
```

---

## 🔍 How It Works Under the Hood

When `context.close_widget(...)` is executed in Python, the Hubscape ADK registers a `CLOSE_AGENT_WIDGET` action directive in the payload returned to the host:

```json
{
  "type": "CLOSE_AGENT_WIDGET",
  "payload": {
    "messageId": null,
    "resultText": "✅ Organization saved successfully!"
  }
}
```

When the Hubscape UI receives this response, the chat engine unmounts the active widget component and updates the message stream with `resultText`.

---

## 📚 References
* **Hubscape ADK Manual**: Chapter 6 (*Lego Widgets and IFrames — Section 4: Widget Closing Protocols*)
