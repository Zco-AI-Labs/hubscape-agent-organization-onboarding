# Chapter 8: Advanced Integrations: MCP, A2A, & Secrets

This chapter outlines how custom agents communicate with third-party tools (MCP), interface with other agents (A2A), and access encrypted capabilities and secrets safely.

---

## 1. Model Context Protocol (MCP) Integration

The ADK allows agents to interact with external tools hosted on remote MCP servers (e.g. Jira, GitHub, databases) via Server-Sent Events (SSE). 

### Setup and Configuration

To register a remote MCP server and configure agent-specific characteristics (such as Google Maps or Google Search grounding toggles), define them inside the sandboxed [app/config.json](../../app/config.json) file:

```json
{
  "mcp_servers": {
    "github_mcp": {
      "url": "https://github-mcp-proxy-w3xi4ozhca-uc.a.run.app/mcp",
      "headers": {
        "Authorization": "Bearer ${OAUTH_TOKEN:github}"
      },
      "timeout": 15
    }
  },
  "google_search": true,
  "google_maps": false
}
```

### How it Works

1. **Static Loading:** At boot time, [app/agent.py](../../app/agent.py) reads the `mcp_servers` configuration block, instantiates a native `McpToolset` for each server, and registers them inside the `AdkAgent`'s tools list.
2. **Dynamic OAuth Resolution:** During request execution (in `geap_agent_wrapper.py` or `agent_runtime_app.py`), the wrapper automatically resolves token placeholders (like `${OAUTH_TOKEN:github}`) by calling `await context.get_oauth_token("github")`, injecting the active user credentials into the connection headers.
3. **Access Control Filtering:** The host platform can restrict access to specific MCP tools by sending a whitelist under `accessible_tools` in the request metadata. The wrapper applies this whitelist directly to the toolset's `tool_filter` to ensure the agent only uses approved capabilities.


---

## 2. Agent-to-Agent (A2A) Connections

A2A allows sub-agents to discover and delegate queries to other agents. An agent acts as both a **client** (making outbound requests) and a **server** (accepting inbound requests).

### Inbound A2A server endpoints:
The FastAPI server automatically mounts an inbound JSON-RPC route `/a2a/{agent_name}` using the helper `attach_a2a_routes()` defined in `[app/app_utils/a2a.py](../../app/app_utils/a2a.py)`. The platform invokes this route when delegating user requests.

### Data Isolation & Whitelisting:
To prevent unauthorized cross-tenant communication:
1. Discovery and consulting operations must work **solely** within the `accessible_agents` list injected into the context at runtime.
2. If an agent tries to discover or call a subagent not listed in `accessible_agents`, the request must fail immediately.

### Discovering Whitelisted Subagents:
Agents can search and retrieve available subagents dynamically:
* **Inside Custom Python Tools:** Call [`context.get_available_agents()`](../../app/core/hubscape_adk.py):
  ```python
  from app.core.hubscape_adk import get_context

  def find_agents(query: str = None) -> list:
      context = get_context()
      return context.get_available_agents(query=query)
  ```
* **Via System Tool:** The built-in system tool [`discover_agents.py`](../../app/core/system_tools/discover_agents.py) is registered on the root agent so Gemini can autonomously discover subagents when needed.

### Consulting Outbound Subagents:
To query a specialized subagent, invoke the built-in system tool [`consultAgent.py`](../../app/core/system_tools/consultAgent.py):
```python
# app/scripts/delegate_task.py
from app.core.system_tools.consultAgent import consultAgent

async def delegate_task(agent_id: str, query: str) -> str:
    # Invokes the remote A2A subagent and returns its response
    response = await consultAgent(agentId=agent_id, query=query)
    return response
```
Under the hood, `consultAgent` instantiates `RemoteA2aAgent` with credentials and metadata from `RemoteContext`, enforcing maximum delegation depth limits and directive parsing.

---

## 3. Platform Secrets Vault

Never hardcode credentials or secrets inside repository files.
* **Secrets Retrieval:** Secure keys are injected into the agent context dynamically. Retrieve secrets using the context raw config:
  ```python
  api_key = context.raw_context.get("secrets", {}).get("API_SECRET_KEY") or os.environ.get("API_SECRET_KEY")
  ```
  This ensures compatibility with both the cloud environment secrets vault and local `.env` mock configuration keys.

---

[Next Chapter: GEAP Developer Workflow](CHAPTER_9_GEAP_DEVELOPER_WORKFLOW.md) | [Previous Chapter: OAuth Integration & Hubscape ADK API](CHAPTER_7_OAUTH_INTEGRATION_AND_ADK_API.md)
