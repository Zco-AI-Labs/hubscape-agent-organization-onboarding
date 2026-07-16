import pytest
import os
import json
from unittest.mock import MagicMock, patch
from app.core.hubscape_adk import RemoteContext, context_session

# Import tools
from app.scripts.save_org_details import save_org_details
from app.scripts.check_session import check_session
from app.scripts.check_mobile_exist import check_mobile_exist
from app.scripts.send_mobile_otp import send_mobile_otp
from app.scripts.verify_mobile_otp import verify_mobile_otp
from app.scripts.associate_contact_and_alert import associate_contact_and_alert

# Mock default GCP credentials and project settings
os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

import google.auth
mock_creds = MagicMock()
mock_creds.token = "dummy_token"
mock_creds.valid = True
mock_creds.service_account_email = "dummy@google.com"
mock_creds.requires_scopes = False
google.auth.default = MagicMock(return_value=(mock_creds, "dummy-project"))

@pytest.fixture(autouse=True)
def mock_db():
    """In-memory database isolation mock for all ADK RemoteContext CRUD actions."""
    db = {}
    
    # Default registered users setup for both agent IDs
    for agent_id in ["organization_subscription_agent", "organization-onboarding-agent", "default_agent"]:
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

@pytest.mark.asyncio
async def test_save_org_details() -> None:
    # Set up dummy context
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_email="info@apex.com",
            org_phone="555-0199",
            user_position="CEO"
        )
        assert res["status"] == "success"
        assert "org_id" in res
        
        # Verify saved via context
        leads = ctx.list(scope="platform", collection_name="leads")
        assert len(leads) == 1
        assert leads[0]["org_name"] == "Apex Innovations"
        assert leads[0]["status"] == "UNVERIFIED"

@pytest.mark.asyncio
async def test_check_session_valid() -> None:
    # Set up auth context
    ctx = RemoteContext(user_id="alex@apex.com")
    with context_session(ctx):
        res = await check_session()
        assert res["session_valid"] is True
        assert res["user_data"]["email_address"] == "alex@apex.com"

@pytest.mark.asyncio
async def test_check_session_invalid() -> None:
    # Set up guest context
    ctx = RemoteContext(user_id="guest_123")
    with context_session(ctx):
        res = await check_session()
        assert res["session_valid"] is False

@pytest.mark.asyncio
async def test_check_mobile_exist_success() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await check_mobile_exist("555-0199")
        assert res["exists"] is True
        assert res["user"]["full_name"] == "Alex Doe"

@pytest.mark.asyncio
async def test_check_mobile_exist_failure() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await check_mobile_exist("555-9999")
        assert res["exists"] is False

@pytest.mark.asyncio
async def test_send_and_verify_otp() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # Send
        send_res = await send_mobile_otp("555-0199")
        assert send_res["status"] == "success"
        
        # Verify success
        verify_res = await verify_mobile_otp("555-0199", "123456")
        assert verify_res["valid"] is True
        
        # Verify failure
        verify_fail = await verify_mobile_otp("555-0199", "wrong")
        assert verify_fail["valid"] is False

@pytest.mark.asyncio
async def test_associate_contact_and_alert() -> None:
    ctx = RemoteContext(user_id="guest_user")
    # Mock show_widget
    ctx.show_widget = MagicMock()
    with context_session(ctx):
        # Save lead first
        save_res = await save_org_details("Apex", "Robotics", "info@apex.com", "555-0199", "CEO")
        org_id = save_res["org_id"]
        
        # Associate
        assoc_res = await associate_contact_and_alert(
            org_id=org_id,
            contact_email="alex@apex.com",
            contact_mobile="555-0199",
            full_name="Alex Doe"
        )
        assert assoc_res["status"] == "success"
        
        # Check DB updates
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        assert lead["status"] == "ASSOCIATED"
        assert lead["contact_email"] == "alex@apex.com"
        
        alerts = ctx.list(scope="platform", collection_name="sales_alerts")
        assert len(alerts) == 1
        
        # Verify show_widget was called
        ctx.show_widget.assert_called_once_with(
            "org_summary_card",
            data={
                "summary_name": "Apex",
                "summary_description": "Robotics",
                "summary_email": "info@apex.com",
                "summary_phone": "555-0199"
            }
        )

@pytest.mark.asyncio
async def test_mobile_normalization() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # check mobile existence with different formats
        res1 = await check_mobile_exist("+1 (555) 0199")
        assert res1["exists"] is True
        
        res2 = await check_mobile_exist("555-0199")
        assert res2["exists"] is True
        
        # verify OTP handling normalizes formatting
        send_res = await send_mobile_otp("+1 (555) 0199")
        assert send_res["status"] == "success"
        
        verify_res = await verify_mobile_otp("555-0199", "123456")
        assert verify_res["valid"] is True

@pytest.mark.asyncio
async def test_save_org_details_invalid_email() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_email="invalid_email",
            org_phone="555-0199",
            user_position="CEO"
        )
        assert res["status"] == "error"
        assert "Invalid organization email format" in res["message"]

@pytest.mark.asyncio
async def test_associate_contact_invalid_email() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # Save a valid org first
        org_res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotics",
            org_email="info@apex.com",
            org_phone="555-0199",
            user_position="CEO"
        )
        org_id = org_res["org_id"]
        
        # Call with invalid contact email
        res = await associate_contact_and_alert(
            org_id=org_id,
            contact_email="invalid_contact_email",
            contact_mobile="555-0199",
            full_name="Alex Doe"
        )
        assert res["status"] == "error"
        assert "Invalid contact email format" in res["message"]

@pytest.mark.asyncio
async def test_save_org_details_invalid_phone() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_email="info@apex.com",
            org_phone="12345",
            user_position="CEO"
        )
        assert res["status"] == "error"
        assert "Invalid organization phone format" in res["message"]

@pytest.mark.asyncio
async def test_associate_contact_invalid_phone() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # Save a valid org first
        org_res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotics",
            org_email="info@apex.com",
            org_phone="555-0199",
            user_position="CEO"
        )
        org_id = org_res["org_id"]
        
        # Call with invalid contact phone
        res = await associate_contact_and_alert(
            org_id=org_id,
            contact_email="alex@apex.com",
            contact_mobile="12345",
            full_name="Alex Doe"
        )
        assert res["status"] == "error"
        assert "Invalid contact mobile format" in res["message"]

@pytest.mark.asyncio
async def test_send_otp_invalid_phone() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await send_mobile_otp("12345")
        assert res["status"] == "error"
        assert "Invalid mobile number format" in res["message"]

@pytest.mark.asyncio
async def test_verify_otp_invalid_phone() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await verify_mobile_otp("12345", "123456")
        assert res["valid"] is False
        assert "Invalid mobile number format" in res["message"]
