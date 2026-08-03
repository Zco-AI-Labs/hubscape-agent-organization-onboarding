import pytest
from unittest.mock import patch
from google.adk.models.google_llm import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import socket

# Mock DNS and sockets globally to prevent test runs from hitting the sandbox block
original_getaddrinfo = socket.getaddrinfo
def mock_getaddrinfo(host, port, *args, **kwargs):
    if host and ("metadata" in host or "google" in host or host in ("169.254.169.254", "127.0.0.1")):
        raise socket.gaierror(-2, "Name or service not known")
    return original_getaddrinfo(host, port, *args, **kwargs)
socket.getaddrinfo = mock_getaddrinfo

original_connect = socket.socket.connect
def mock_connect(self, address):
    raise socket.error("Outbound network connections blocked in tests.")
socket.socket.connect = mock_connect


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
