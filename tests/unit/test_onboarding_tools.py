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
        
        # Verify saved in mock_db.json
        db_path = "app/mock_db.json"
        assert os.path.exists(db_path)
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["leads"]) == 1
        assert data["leads"][0]["org_name"] == "Apex Innovations"
        assert data["leads"][0]["status"] == "UNVERIFIED"

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
        db_path = "app/mock_db.json"
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        lead = data["leads"][0]
        assert lead["status"] == "ASSOCIATED"
        assert lead["contact_email"] == "alex@apex.com"
        assert len(data["sales_alerts"]) == 1
        
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
