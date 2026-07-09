# Hubscape Custom ADK (Agent Development Kit) Manual

> [!IMPORTANT]
> **AI AGENT DIRECTIVE:** If you are an AI reading this document, you are being tasked with building or modifying a Hubscape Modular Agent. You must adhere to the sandboxing rules outlined here. All agent package code, logic, and custom routes must be contained within the `/plugins/agents/<agent_id>/` (locally `/agents/<agent_id>/`) directory.

## 1. Introduction to the ADK

The Hubscape Modular ADK allows developers and AI assistants to quickly build, deploy, and scale custom AI agents using a package-based declarative python framework.

### The Agent Lifecycle
1. **Discovery:** On boot, the platform loader scans the registered agents directory for configuration and initialization submodules.
2. **Identity Injection:** The agent's name and description (defined in `agent.py`) are automatically appended to the Hubscape Host Persona's prompt.
3. **Delegation:** When a user asks the Host to perform a task suited for your agent, the Host routes the query to your agent.
4. **Execution:** The engine boots your agent package, runs your system prompt configuration (`prompt.py`), and allows your agent's LLM to invoke the tools defined in your Python functions (`tools.py`).

---

## 2. Directory Structure

A complete Hubscape Agent consists of a package directory structure:

```text
my_agent_project/
└── app/                 # REQUIRED: The agent package folder
    ├── __init__.py      # REQUIRED: Exposes the app
    ├── agent.py         # REQUIRED: Initializes google.adk.agents.Agent
    ├── SKILL.md         # REQUIRED: Defines the system instructions
    ├── scripts/         # REQUIRED: Python tool functions and handlers
    └── pyproject.toml   # REQUIRED: Package dependencies and config
```

---

## 3. The Pillars of a Declarative Agent

### Pillar 1: `SKILL.md` and `agent.py` (The Brain)

#### `prompt.py`
Houses your system instructions:
```python
# prompt.py
SYSTEM_PROMPT = """
You are a helpful agent. Attempt to carry out user requests by calling tools in tools.py.
"""
```

#### `agent.py`
Instantiates the agent using `google.adk.agents.Agent` and registers the tools:
```python
# agent.py
from google.adk.agents import Agent
from prompt import SYSTEM_PROMPT
from .tools import create_event, delete_event

root_agent = Agent(
    name="my_custom_agent",
    model="gemini-2.5-flash",
    description="Brief summary of capabilities.",
    instruction=SYSTEM_PROMPT,
    tools=[create_event, delete_event]
)
```

---

### Pillar 3: `tools.py` (The Muscle)

This file contains standard Python functions that act as tools. The ADK automatically parses their signatures, docstrings, and type hints to construct Gemini tool schemas.

**Rules for `tools.py`:**
1. Define clear docstrings describing the tool and its parameters.
2. The context object (`ToolContext` or `HubscapeContext`) is passed if declared in your parameters.
3. Keep logic clean and return JSON-serializable dicts.

```python
# tools.py
import logging
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

async def create_event(tool_context: ToolContext, title: str, date: str) -> dict:
    """
    Creates a new calendar event.

    Args:
        title: The name/title of the event.
        date: The date format YYYY-MM-DD.
    """
    logger.info(f"Creating event: {title} on {date}")
    

        
    user_id = tool_context.auth.get_user_id()
    
    # Save to scoped DB
    saved = tool_context.save_agent_data(
        scope="user",
        collection_name="events",
        doc_id=f"evt_{title}",
        data={"title": title, "date": date}
    )
    
    return {"status": "success", "event": saved}
```

---

### Pillar 4: Inbound API Routes (Decommissioned)

GEAP agents run in sandboxed cloud containers and do not support public inbound HTTP routes (`api.py`). Any webhook, callback, or OAuth redirect must be routed directly to the central platform backend, which writes to Firestore for the agent to query via `hubscape_adk.py`.

---

## 4. Understanding the `HubscapeContext` / `ToolContext` 
[***UNDER DEVELOPMENT***]

The context object passed into tool functions and API routes is your gateway to the platform.

### `context.auth` (Authentication)
*   `context.auth.get_user_id()`: Returns the unique UUID of the active user.
*   `context.auth.name`: The user's display name.
*   `context.auth.org_id`: The Organization UUID (always available).
*   `context.auth.hub_id`: The Hub UUID (may be `None` if org-level).


### `context.client` (Modality Checks)
Use these variables to adapt layouts dynamically (e.g., text only for SMS vs visual cards for Chat UI):
*   `context.client.mode`: E.g., `"chat_pc"`, `"sms"`, `"voice_call"`.
*   `context.client.has_ui`: `True` if client supports visual rendering.
*   `context.client.is_voice`: `True` if audio modality is active.

### Standardized Database Scopes & Helpers
 Firestore paths are automatically managed by ADK context helpers:
*   **`user` Scope:** `platform_users/{user_id}/agent_data/{agent_id}/{collection_name}/`
*   **`hub` Scope:** `organizations/{org_id}/hubs/{hub_id}/agent_data/{agent_id}/{collection_name}/`
*   **`org` Scope:** `organizations/{org_id}/agent_data/{agent_id}/{collection_name}/`

#### CRUD Helpers:
*   `context.save_agent_data(scope, collection_name, doc_id, data)`: Saves/merges data and increments versioning metadata (`created_by`, `updated_at`, etc.).
*   `context.get_agent_data(scope, collection_name, doc_id)`: Retrieves a document.
*   `context.delete_agent_data(scope, collection_name, doc_id)`: Deletes a document.
*   `context.list_agent_data(scope, collection_name)`: Streams all documents in the collection.

---

## 5. Development Workflow (Step-by-Step)

1. **Scaffold Package:** Run `hubscape-adk init <agent_id>` to generate the package structure inside `agents/`.
2. **Implement Tools:** Write python tool functions inside `tools.py` and register them in `agent.py`. Add prompts inside `prompt.py`.
3. **Configure Database & Context:** Define Firestore scopes and queries inside tools/scripts using `hubscape_adk.py`.
4. **Boot Sandbox:** Execute `hubscape-adk` to launch the local Holodeck at `http://localhost:8090`.
5. **Simulate & Verify:** Talk to the mock Host AI, trigger tools, test permission overrides, and inspect logs in the Holodeck dashboard.



## 7. Model Context Protocol (MCP) & Agent-to-Agent (A2A) Connections

### Programmatic MCP calling in `tools.py`
```python
mcp_result = await context.mcp.call_tool(
    agent_id=context.auth.agent_id,
    server_name="jira_mcp",
    tool_name="create_ticket",
    arguments={"summary": "Fix bugs"},
    config=mcp_config,
    context=context
)
```

### Programmatic A2A calling in `tools.py`
```python
result = await context.agents.call_external_tool(
    ext_agent_key="salesforce_copilot",
    tool_name="get_lead_details",
    arguments={"lead_id": lead_id}
)
```
