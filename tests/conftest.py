import sys
import os
from unittest.mock import MagicMock, patch

# Set dummy Google Cloud project environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Mock google.auth.default to return mock credentials
import google.auth
mock_creds = MagicMock()
mock_creds.token = "dummy_token"
mock_creds.valid = True
mock_creds.service_account_email = "dummy@google.com"
mock_creds.requires_scopes = False
mock_creds.before_request = MagicMock()
google.auth.default = MagicMock(return_value=(mock_creds, "dummy-project"))

# Mock google.genai.Client to prevent external API calls to Gemini/Vertex AI
from google.genai import Client, types

def mock_gen_content(*args, **kwargs):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    parts=[types.Part.from_text(text="I want to onboard my organization. Legal Name: Apex Innovations, Description: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO.")]
                )
            )
        ]
    )

def mock_gen_content_stream(*args, **kwargs):
    yield types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    parts=[types.Part.from_text(text="Onboarding details saved.")]
                )
            )
        ]
    )

async def mock_gen_content_async(*args, **kwargs):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    parts=[types.Part.from_text(text="Onboarding details saved.")]
                )
            )
        ]
    )

async def mock_gen_content_stream_async(*args, **kwargs):
    yield types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    parts=[types.Part.from_text(text="Onboarding details saved.")]
                )
            )
        ]
    )

original_init = Client.__init__
def custom_client_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self.models.generate_content = MagicMock(side_effect=mock_gen_content)
    self.models.generate_content_stream = MagicMock(side_effect=mock_gen_content_stream)
    self.aio.models.generate_content = MagicMock(side_effect=mock_gen_content_async)
    self.aio.models.generate_content_stream = MagicMock(side_effect=mock_gen_content_stream_async)

Client.__init__ = custom_client_init

import pytest
from google.adk.models.google_llm import Gemini
from google.adk.models.llm_response import LlmResponse

async def mock_generate_content_async(self, llm_request, stream=False):
    # Determine mock output text
    text_output = "Hello! I am a mocked Gemini agent response."
    yield LlmResponse(
        content=types.Content(parts=[types.Part.from_text(text=text_output)]),
        turn_complete=True
    )

@pytest.fixture(autouse=True)
def mock_gemini_api():
    """Autouse fixture to mock Gemini API calls across all tests."""
    with patch.object(Gemini, "generate_content_async", new=mock_generate_content_async):
        yield

from app.core.hubscape_adk import RemoteContext

@pytest.fixture(autouse=False)
def mock_adk_db():
    """In-memory database isolation mock for all ADK RemoteContext CRUD actions."""
    db = {}
    
    # Default registered users setup for both agent IDs
    for agent_id in ["organization-onboarding-agent", "default_agent"]:
        db[f"agents/{agent_id}/agent_data/platform/registered_users/5550199"] = {
            "mobile_number": "555-0199",
            "full_name": "Alex Doe",
            "email_address": "alex@apex.com",
            "version": 1
        }
        db[f"agents/{agent_id}/agent_data/platform/session_config/override"] = {
            "active_session": False,
            "version": 1
        }

    def custom_save(self, scope: str, collection_name: str, doc_id: str, data: dict) -> dict:
        path = self.get_agent_db_path(scope, collection_name, doc_id)
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        user_id = self.auth.get_user_id()
        
        payload = data.copy()
        if path not in db:
            payload.update({
                "created_at": now,
                "created_by": user_id,
                "updated_at": now,
                "updated_by": user_id,
                "version": 1
            })
        else:
            current_data = db[path]
            current_version = current_data.get("version", 0)
            payload.update({
                "created_at": current_data.get("created_at"),
                "created_by": current_data.get("created_by"),
                "updated_at": now,
                "updated_by": user_id,
                "version": current_version + 1
            })
        
        db[path] = payload
        return payload

    def custom_get(self, scope: str, collection_name: str, doc_id: str) -> dict:
        path = self.get_agent_db_path(scope, collection_name, doc_id)
        return db.get(path)

    def custom_list(self, scope: str, collection_name: str) -> list:
        prefix = f"agents/{self.agent_id}/agent_data/{scope}/{collection_name}"
        results = []
        for path, val in db.items():
            if path.startswith(prefix):
                results.append(val)
        return results

    def custom_delete(self, scope: str, collection_name: str, doc_id: str) -> bool:
        path = self.get_agent_db_path(scope, collection_name, doc_id)
        if path in db:
            del db[path]
            return True
        return False

    with patch.object(RemoteContext, "save", new=custom_save), \
         patch.object(RemoteContext, "get", new=custom_get), \
         patch.object(RemoteContext, "list", new=custom_list), \
         patch.object(RemoteContext, "delete", new=custom_delete):
        yield db
