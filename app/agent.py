import os
# Force regional Vertex AI routing unconditionally
os.environ.pop("GOOGLE_GENAI_USE_ENTERPRISE", None)
# os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "True":
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("GOOGLE_API_KEY", None)
import asyncio
import importlib.util
import re
from google.adk import Agent as AdkAgent
from google.adk.runners import Runner
from google.genai import types

from app.core.load_local_tools import load_local_tools

# 1. Read system prompt instructions from SKILL.md and load tools at module level
runtime_dir = os.path.dirname(os.path.abspath(__file__))
skill_md_path = os.path.join(runtime_dir, "SKILL.md")
system_instruction = "You are a highly efficient Task Manager agent."
if os.path.exists(skill_md_path):
    with open(skill_md_path, "r", encoding="utf-8") as f:
        skill_content = f.read()
    system_instruction = re.sub(r"^---.*?---", "", skill_content, flags=re.DOTALL).strip()

scripts_dir = os.path.join(runtime_dir, "scripts")
system_tools_dir = os.path.join(runtime_dir, "core", "system_tools")
tools = load_local_tools(system_tools_dir) + load_local_tools(scripts_dir)

from app.app_utils.vertex_gemini import get_model

root_agent = AdkAgent(
    model=get_model("gemini-2.5-flash"),
    name="sales_onboarding_agent",
    description="""
    The Hubscape Global Organization Subscription Agent is a specialized virtual 
    assistant designed to streamline company onboarding, subscription management, 
    and user support. It guides prospective and existing clients through registering 
    new organization details via interactive intake forms, submitting customer support 
    inquiries, and checking the real-time status of their subscription requests. To 
    protect sensitive account data, the agent enforces multi-step mobile OTP identity 
    verification before disclosing linked organization records, while automatically 
    translating raw status indicators into clear, human-friendly updates. Additionally, 
    it features multi-agent coordination capabilities to discover and consult specialized 
    assistant agents across the network for complex inquiry resolution.
    """,
    instruction=system_instruction,
    tools=tools
)

from app.core.geap_agent_wrapper import GEAPAgentWrapper

# Singleton instance used as the serialization target
agent_app = GEAPAgentWrapper(root_agent)

from google.adk.apps import App
app = App(
    root_agent=root_agent,
    name="sales-onboarding-agent",
)
