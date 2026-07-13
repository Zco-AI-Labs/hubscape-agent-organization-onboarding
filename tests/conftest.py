import sys
from unittest.mock import MagicMock, patch

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

@pytest.fixture(autouse=True)
def mock_db_file(monkeypatch):
    """Fixture to isolate mock_db.json during tests."""
    # Ensure a fresh mock_db.json is created for tests
    import json
    import os
    db_path = "app/mock_db.json"
    initial_data = {
        "leads": [],
        "registered_users": [
            {
                "mobile_number": "555-0199",
                "full_name": "Alex Doe",
                "email_address": "alex@apex.com"
            }
        ],
        "active_otps": {},
        "sales_alerts": []
    }
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, indent=2)
    yield
    # Cleanup
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
