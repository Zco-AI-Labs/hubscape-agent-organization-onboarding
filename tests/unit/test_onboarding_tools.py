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
from app.scripts.show_org_details_form import show_org_details_form
from app.scripts.show_otp_verify_widget import show_otp_verify_widget
from app.scripts.show_personal_details_widget import show_personal_details_widget
from app.scripts.show_contact_form import show_contact_form
from app.scripts.submit_personal import submit_personal
from app.scripts.save_phone_details import save_phone_details

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
    
    # Default lead and session override setup for both agent IDs
    for agent_id in ["organization_subscription_agent", "organization-onboarding-agent", "sales-onboarding-agent", "sales_onboarding_agent", "default_agent"]:
        db[f"agents/{agent_id}/agent_data/platform/leads/lead_alex"] = {
            "id": "lead_alex",
            "org_name": "Apex Innovations",
            "org_description": "Robotics",
            "org_website": "apex.com",
            "user_position": "CEO",
            "status": "ASSOCIATED",
            "contact_email": "alex@apex.com",
            "contact_mobile": "5550199",
            "contact_name": "Alex Doe",
            "owner_id": "alex@apex.com",
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

    mock_client = MagicMock()
    mock_user_doc = MagicMock()
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        "first_name": "Alex",
        "last_name": "Doe",
        "email": "alex@apex.com",
        "phone": "+15550199"
    }
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_user_doc
    mock_client.document.return_value = mock_doc_ref

    with patch.object(RemoteContext, "save", new=custom_save), \
         patch.object(RemoteContext, "get", new=custom_get), \
         patch.object(RemoteContext, "list", new=custom_list), \
         patch.object(RemoteContext, "delete", new=custom_delete), \
         patch.object(RemoteContext, "_db_client", new=mock_client):
        yield db

@pytest.mark.asyncio
async def test_save_org_details() -> None:
    # Set up dummy context
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_website="apex.com",
            user_position="CEO"
        )
        assert res["status"] == "success"
        assert "org_id" in res
        
        # Verify saved via context
        leads = ctx.list(scope="platform", collection_name="leads")
        # Filter out the pre-seeded lead (lead_alex) to check the newly created one
        new_leads = [l for l in leads if l["id"] == res["org_id"]]
        assert len(new_leads) == 1
        assert new_leads[0]["org_name"] == "Apex Innovations"
        assert new_leads[0]["org_website"] == "apex.com"
        assert new_leads[0]["status"] == "UNVERIFIED"

@pytest.mark.asyncio
async def test_save_org_details_authenticated() -> None:
    # Set up auth context with a standard UUID
    ctx = RemoteContext(user_id="997075d5-ed5b-4800-8111-a675a87db800")
    ctx.show_widget = MagicMock()
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Robotics",
            org_description="Making robots",
            org_website="apexrobotics.com",
            user_position="CFO"
        )
        assert res["status"] == "success"
        assert "org_id" in res
        
        # Verify saved lead details are ASSOCIATED and pre-populated from platform_users
        leads = ctx.list(scope="platform", collection_name="leads")
        new_leads = [l for l in leads if l["id"] == res["org_id"]]
        assert len(new_leads) == 1
        created_lead = new_leads[0]
        assert created_lead["org_name"] == "Apex Robotics"
        assert created_lead["status"] == "ASSOCIATED"
        assert created_lead["contact_name"] == "Alex Doe"
        assert created_lead["contact_email"] == "alex@apex.com"
        assert created_lead["contact_mobile"] == "+15550199"
        assert created_lead["owner_id"] == "997075d5-ed5b-4800-8111-a675a87db800"
        
        # Verify org_summary_card widget was queued instead of mobile_input_widget
        ctx.show_widget.assert_called_with(
            "org_summary_card",
            data={
                "summary_name": "Apex Robotics",
                "summary_description": "Making robots",
                "summary_website": "apexrobotics.com",
                "summary_position": "CFO"
            }
        )

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
        save_res = await save_org_details("Apex", "Robotics", "apex.com", "CEO")
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
        ctx.show_widget.assert_called_with(
            "org_summary_card",
            data={
                "summary_name": "Apex",
                "summary_description": "Robotics",
                "summary_website": "apex.com",
                "summary_position": "CEO"
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
async def test_save_org_details_invalid_website() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_website="invalid_website",
            user_position="CEO"
        )
        assert res["status"] == "error"
        assert "Invalid organization website format" in res["message"]

@pytest.mark.asyncio
async def test_save_org_details_empty_website() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotic research",
            org_website="",
            user_position="CEO"
        )
        assert res["status"] == "success"
        assert "org_id" in res
        
        leads = ctx.list(scope="platform", collection_name="leads")
        new_leads = [l for l in leads if l["id"] == res["org_id"]]
        assert len(new_leads) == 1
        assert new_leads[0]["org_website"] == ""

@pytest.mark.asyncio
async def test_associate_contact_invalid_email() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # Save a valid org first
        org_res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotics",
            org_website="apex.com",
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
async def test_associate_contact_invalid_phone() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # Save a valid org first
        org_res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotics",
            org_website="apex.com",
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

@pytest.mark.asyncio
async def test_phone_missing_country_code_fails() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):

        res2 = await send_mobile_otp("9909990890")
        assert res2["status"] == "error"
        assert "Please include your country code starting with '+'" in res2["message"]

@pytest.mark.asyncio
async def test_phone_with_country_code_passes() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        # 10 digits with '+' prefix should pass (simulate OTP send)
        res = await send_mobile_otp("+19909990890")
        assert res["status"] == "success"

        res2 = await send_mobile_otp("+919909990890")
        assert res2["status"] == "success"

@pytest.mark.asyncio
async def test_show_widget_tools() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock(return_value={"status": "success"})
    with context_session(ctx):
        res1 = await show_org_details_form()
        ctx.show_widget.assert_called_with("org_details_form")
        assert res1["status"] == "success"

        res3 = await show_otp_verify_widget()
        ctx.show_widget.assert_called_with("otp_verify")
        assert res3["status"] == "success"

        res4 = await show_personal_details_widget()
        ctx.show_widget.assert_called_with("personal_details")
        assert res4["status"] == "success"

        res5 = await show_contact_form()
        ctx.show_widget.assert_called_with("contact_form")
        assert res5["status"] == "success"

@pytest.mark.asyncio
async def test_submit_personal_success() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    with context_session(ctx):
        # 1. Save org details first
        org_res = await save_org_details("Apex Pizza", "Best Pizza", "apex.com", "Manager")
        org_id = org_res["org_id"]
        
        # 2. Submit personal details
        res = await submit_personal("Alex Doe", "alex@apex.com", org_id=org_id)
        assert res["status"] == "success"
        
        # 3. Verify lead document is updated
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        assert lead["contact_name"] == "Alex Doe"
        assert lead["contact_email"] == "alex@apex.com"
        assert lead["status"] == "ASSOCIATED"
        
        # 4. Verify org_summary_card widget was queued
        ctx.show_widget.assert_any_call("org_summary_card", data={
            "summary_name": "Apex Pizza",
            "summary_description": "Best Pizza",
            "summary_website": "apex.com",
            "summary_position": "Manager"
        })

@pytest.mark.asyncio
async def test_submit_personal_invalid_email() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await submit_personal("Alex Doe", "invalid-email", "some_org_id")
        assert res["status"] == "error"
        assert "Invalid contact email format" in res["message"]

@pytest.mark.asyncio
async def test_submit_personal_not_found() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await submit_personal("Alex Doe", "alex@apex.com", org_id="nonexistent_org_id")
        assert res["status"] == "error"
        assert "Lead record nonexistent_org_id not found" in res["message"]

@pytest.mark.asyncio
async def test_submit_personal_fallback() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    # Create mock session object
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    
    with context_session(ctx):
        # 1. Save org details first
        org_res = await save_org_details("Apex Pizza", "Best Pizza", "apex.com", "Manager")
        org_id = org_res["org_id"]
        
        # 2. Check if active_org_id was populated in session state
        assert ctx.session.state["active_org_id"] == org_id
        
        # 3. Submit personal details with org_id omitted to test fallback
        res = await submit_personal("Alex Doe", "alex@apex.com")
        assert res["status"] == "success"
        
        # 4. Verify lead document is updated
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        assert lead["contact_name"] == "Alex Doe"
        assert lead["contact_email"] == "alex@apex.com"
        assert lead["status"] == "ASSOCIATED"

@pytest.mark.asyncio
async def test_submit_personal_combined_flow() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    # Create mock session object
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    
    with context_session(ctx):
        # 1. Save org details first
        org_res = await save_org_details("Apex Pizza", "Best Pizza", "apex.com", "Manager")
        org_id = org_res["org_id"]
        
        # 2. Submit combined personal & mobile details
        res = await submit_personal("Alex Doe", "alex@apex.com", "555-9999", org_id)
        assert res["status"] == "success"
        
        # 3. Verify lead email & name are saved, status is UNVERIFIED
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        assert lead["contact_name"] == "Alex Doe"
        assert lead["contact_email"] == "alex@apex.com"
        assert lead["status"] == "UNVERIFIED"
        # Mobile number should NOT be saved to the database yet
        assert lead.get("contact_mobile") is None
        
        # 4. Verify mobile is held in session state
        assert ctx.session.state["pending_mobile"] == "555-9999"
        
        # 5. Verify otp_verify widget is queued
        ctx.show_widget.assert_any_call("otp_verify")
        
        # 6. Verify completing OTP and associate contact
        assoc_res = await associate_contact_and_alert(
            org_id=org_id,
            contact_email="alex@apex.com",
            contact_mobile="",  # Left empty to test fallback to session state
            full_name="Alex Doe"
        )
        assert assoc_res["status"] == "success"
        
        # 7. Verify lead now has mobile saved and status is ASSOCIATED
        lead_final = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        assert lead_final["contact_mobile"] == "5559999"
        assert lead_final["status"] == "ASSOCIATED"


@pytest.mark.asyncio
async def test_verify_mobile_otp_returns_linked_orgs_success() -> None:
    ctx = RemoteContext(user_id="guest_user")
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    with context_session(ctx):
        # 1. Save org details
        org_res = await save_org_details("Test Org", "Desc", "test.com", "CEO")
        org_id = org_res["org_id"]
        
        # 2. Associate contact with unverified mobile number
        await associate_contact_and_alert(
            org_id=org_id,
            contact_email="test@test.com",
            contact_mobile="+15550199000",
            full_name="Test User"
        )
        
        # 3. Verify OTP and fetch statuses
        res = await verify_mobile_otp(mobile_number="+15550199000", otp_code="123456")
        assert res["valid"] is True
        assert "Identity verified successfully" in res["message"]
        assert len(res["linked_organizations"]) > 0
        assert res["linked_organizations"][0]["org_name"] == "Test Org"
        assert res["linked_organizations"][0]["status"] == "OPEN"
        
        # 4. Check that verified_mobile is stored in session state
        assert ctx.session.state["verified_mobile"] == "+15550199000"


@pytest.mark.asyncio
async def test_verify_mobile_otp_sales_status_override() -> None:
    ctx = RemoteContext(user_id="guest_user")
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    with context_session(ctx):
        # 1. Save org details
        org_res = await save_org_details("Test Override Org", "Desc", "override.com", "CEO")
        org_id = org_res["org_id"]
        
        # 2. Associate contact details
        await associate_contact_and_alert(
            org_id=org_id,
            contact_email="test@override.com",
            contact_mobile="+15550199001",
            full_name="Override User"
        )
        
        # 3. Simulate sales update to COMPLETED in database
        lead = ctx.get(scope="platform", collection_name="leads", doc_id=org_id)
        lead["sales_status"] = "COMPLETED"
        ctx.save(scope="platform", collection_name="leads", doc_id=org_id, data=lead)
        
        # 4. Verify OTP and check returned status is COMPLETED
        res = await verify_mobile_otp(mobile_number="+15550199001", otp_code="123456")
        assert res["valid"] is True
        assert len(res["linked_organizations"]) > 0
        assert res["linked_organizations"][0]["org_name"] == "Test Override Org"
        assert res["linked_organizations"][0]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_verify_mobile_otp_invalid_code() -> None:
    ctx = RemoteContext(user_id="guest_user")
    with context_session(ctx):
        res = await verify_mobile_otp(mobile_number="+15550199000", otp_code="wrong_code")
        assert res["valid"] is False
        assert "Invalid verification code" in res["message"]


@pytest.mark.asyncio
async def test_save_phone_details() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    with context_session(ctx):
        await save_phone_details()
        ctx.show_widget.assert_called_once_with("phone_details")


@pytest.mark.asyncio
async def test_send_mobile_otp_saves_pending_mobile() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    with context_session(ctx):
        res = await send_mobile_otp("+15550199000")
        assert res["status"] == "success"
        assert ctx.session.state["pending_mobile"] == "+15550199000"
        ctx.show_widget.assert_called_once_with("otp_verify")


@pytest.mark.asyncio
async def test_verify_mobile_otp_with_session_state_fallback() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.close_widget = MagicMock()
    class MockSession:
        def __init__(self):
            self.state = {"pending_mobile": "+15550199000"}
    ctx.session = MockSession()
    with context_session(ctx):
        # Call verify_mobile_otp with only otp_code (as sent by otp_verify_widget)
        res = await verify_mobile_otp(otp_code="123456")
        assert res["valid"] is True
        assert ctx.session.state["verified_mobile"] == "+15550199000"
        ctx.close_widget.assert_called_once()


@pytest.mark.asyncio
async def test_guest_status_check_flow_after_otp_verification() -> None:
    ctx = RemoteContext(user_id="guest_user")
    ctx.show_widget = MagicMock()
    ctx.close_widget = MagicMock()
    class MockSession:
        def __init__(self):
            self.state = {}
    ctx.session = MockSession()
    with context_session(ctx):
        # Setup: Create a lead with unique phone +15550199888
        org_res = await save_org_details("Acme Corp", "Tech startup", "acme.com", "CTO")
        org_id = org_res["org_id"]
        await associate_contact_and_alert(
            org_id=org_id,
            contact_email="cto@acme.com",
            contact_mobile="+15550199888",
            full_name="Jane Doe"
        )
        
        # Step 1: Initial check_session for guest returns invalid
        init_sess = await check_session()
        assert init_sess["session_valid"] is False
        
        # Step 2: Show phone input widget using save_phone_details
        await save_phone_details()
        ctx.show_widget.assert_called_with("phone_details")
        
        # Step 3: User submits phone -> send_mobile_otp queues otp_verify
        send_res = await send_mobile_otp("+15550199888")
        assert send_res["status"] == "success"
        assert ctx.session.state["pending_mobile"] == "+15550199888"
        ctx.show_widget.assert_called_with("otp_verify")
        
        # Step 4: User submits OTP in otp_verify_widget -> calls verify_mobile_otp
        verify_res = await verify_mobile_otp(otp_code="123456")
        assert verify_res["valid"] is True
        assert ctx.session.state["verified_mobile"] == "+15550199888"
        assert "linked_organizations" in verify_res
        assert any(org["org_name"] == "Acme Corp" and org["status"] == "OPEN" for org in verify_res["linked_organizations"])
        
        # Step 5: Agent calls check_session -> session is now valid and returns Acme Corp!
        final_sess = await check_session()
        assert final_sess["session_valid"] is True
        linked = final_sess["user_data"]["linked_organizations"]
        assert any(org["org_name"] == "Acme Corp" and org["status"] == "OPEN" for org in linked)




