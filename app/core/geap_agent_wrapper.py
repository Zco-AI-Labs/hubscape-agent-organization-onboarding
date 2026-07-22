import os
import uuid
import json
import time
from google.genai import types
from google.adk.runners import Runner
from app.core import hubscape_adk

class GEAPAgentWrapper:
    def __init__(self, agent, app_name: str = None):
        self.agent = agent
        self.app_name = app_name or agent.name.replace('_', '-')
        self.runner = None

    async def query(self, question: str, context: dict = None) -> str:
        start_time = time.time()
        core_dir = os.path.dirname(os.path.abspath(__file__))
        runtime_dir = os.path.abspath(os.path.join(core_dir, ".."))

        user_id = (context or {}).get("userId") or (context or {}).get("user_id") or "anonymous_user"
        org_id = (context or {}).get("orgId") or (context or {}).get("org_id")
        hub_id = (context or {}).get("hubId") or (context or {}).get("hub_id")
        
        agent_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://github.com/Zco-AI-Labs/{self.app_name}"))
        from app.app_utils.env_resolver import get_project_id
        project_id = get_project_id()
        
        remote_ctx = hubscape_adk.RemoteContext(
            user_id=user_id, 
            agent_id=agent_uuid,
            org_id=org_id,
            hub_id=hub_id,
            project_id=project_id,
            raw_context=context
        )
        
        session_id = (context or {}).get("sessionId") or (context or {}).get("session_id") or f"session_{user_id}_{hub_id}"
        
        # --- OPENTELEMETRY CONTEXT ENRICHMENT ---
        try:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("org_id", org_id or "unknown")
                current_span.set_attribute("hub_id", hub_id or "unknown")
                current_span.set_attribute("user_id", user_id or "unknown")
                current_span.set_attribute("gen_ai.conversation_id", session_id)
                current_span.set_attribute("gen_ai.request.model", self.agent.model.model_name)
                current_span.set_attribute("provider", "vertex")
                
                depth = (context or {}).get("depth", 0)
                request_type = "a2a" if depth > 0 else "direct"
                current_span.set_attribute("gen_ai.request.type", request_type)
        except Exception:
            pass
        
        with hubscape_adk.context_session(remote_ctx):
            if not self.runner:
                from google.adk.sessions.in_memory_session_service import InMemorySessionService
                from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
                from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
                from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
                
                self.runner = Runner(
                    agent=self.agent,
                    app_name=self.app_name,
                    session_service=InMemorySessionService(),
                    artifact_service=InMemoryArtifactService(),
                    memory_service=InMemoryMemoryService(),
                    credential_service=InMemoryCredentialService(),
                    auto_create_session=True
                )

            # 1. Restore ADK session trajectory from Firestore if available
            try:
                session_doc = remote_ctx.get(scope="user", collection_name="sessions", doc_id=session_id)
                if session_doc and "adk_session" in session_doc:
                    adk_session_json = session_doc["adk_session"]
                    from google.adk.sessions import Session
                    session_obj = Session.model_validate_json(adk_session_json)
                    
                    session_service = self.runner.session_service
                    app_name = session_obj.app_name
                    uid = session_obj.user_id
                    sid = session_obj.id
                    
                    if app_name not in session_service.sessions:
                        session_service.sessions[app_name] = {}
                    if uid not in session_service.sessions[app_name]:
                        session_service.sessions[app_name][uid] = {}
                    session_service.sessions[app_name][uid][sid] = session_obj
            except Exception as restore_err:
                print(f"⚠️ Non-critical: Failed to restore session trajectory: {restore_err}")

            # Retrieve or create session and bind it to context
            try:
                session_obj = await self.runner.session_service.get_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                if not session_obj:
                    session_obj = await self.runner.session_service.create_session(
                        app_name=self.app_name,
                        user_id=user_id,
                        session_id=session_id
                    )
                if session_obj:
                    if not hasattr(session_obj, "state") or session_obj.state is None:
                        session_obj.state = {}
                    # After loading or creating the ADK session:
                    remote_ctx.session = session_obj
            except Exception as bind_err:
                print(f"⚠️ Non-critical: Failed to bind session to remote_ctx: {bind_err}")

            workspace_type = (context or {}).get("workspaceType")
            workspace_id = (context or {}).get("workspaceId")
            if not workspace_type or not workspace_id:
                is_org_scope = (hub_id == org_id) or (not hub_id) or (hub_id == "platform")
                workspace_type = "organization" if is_org_scope else "hub"
                workspace_id = org_id if is_org_scope else hub_id

            cloned_agent = hubscape_adk.filter_tools_for_scope(
                agent=self.agent,
                user_privileges=remote_ctx.user_privileges,
                workspace_type=workspace_type,
                workspace_id=workspace_id,
                org_id=org_id
            )
            
            raw_mode = (context or {}).get("interaction_mode") or (context or {}).get("mode") or "chat_pc"
            normalized_mode = "chat_pc" if raw_mode == "chat_phone" else raw_mode
            session_context = (
                f"[ACTIVE WORKSPACE CONTEXT]\n"
                f"- Interaction Mode: {normalized_mode}\n"
                f"- Workspace Type: {workspace_type}\n"
                f"- Workspace ID: {workspace_id or 'none'}\n"
                f"- Organization ID: {org_id or 'none'}\n"
            )
            cloned_agent.instruction = f"{session_context}\n{self.agent.instruction or ''}"
            
            # Temporarily attach cloned agent to runner for execution
            self.runner.agent = cloned_agent
            
            new_message = types.Content(
                parts=[types.Part.from_text(text=question)]
            )
            
            collected_outputs = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                out = getattr(event, "output", None)
                if not out and getattr(event, "content", None) and getattr(event.content, "parts", None):
                    text_parts = [p.text for p in event.content.parts if getattr(p, "text", None)]
                    if text_parts:
                        out = "\n".join(text_parts)
                if out and isinstance(out, str) and out.strip():
                    clean_out = out.strip()
                    if not collected_outputs or clean_out != collected_outputs[-1].strip():
                        collected_outputs.append(clean_out)
            
            text_response = "\n".join(collected_outputs)
            
            # 2. Persist updated ADK session state back to Firestore
            try:
                updated_session = await self.runner.session_service.get_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                if updated_session:
                    serialized_json = updated_session.model_dump_json()
                    remote_ctx.save(
                        scope="user",
                        collection_name="sessions",
                        doc_id=session_id,
                        data={
                            "adk_session": serialized_json
                        }
                    )
            except Exception as save_err:
                print(f"⚠️ Non-critical: Failed to save session trajectory: {save_err}")
                
            return text_response
