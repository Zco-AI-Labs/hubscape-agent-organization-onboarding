import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add root folder to pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Stub the App class to bypass validation on system Python
import google.adk.apps
google.adk.apps.App = MagicMock

# Stub the RemoteContext and get_context in app.core.hubscape_adk
import app.core.hubscape_adk

# In-memory mock database
db = {}

class MockRemoteAuth:
    def __init__(self, user_id):
        self.user_id = user_id
        self.org_id = "test-org"
        self.hub_id = "test-hub"
    def get_user_id(self):
        return self.user_id

class MockRemoteContext:
    def __init__(self, user_id):
        self.auth = MockRemoteAuth(user_id)
        self.agent_id = "sales_onboarding_agent"
        self.session = MagicMock()
        self.session.state = {}

    @property
    def _db_client(self):
        client = MagicMock()
        def get_doc(doc_path):
            doc = MagicMock()
            if doc_path == "platform_users/alex@apex.com":
                doc.exists = True
                doc.to_dict.return_value = {
                    "first_name": "Alex",
                    "last_name": "Doe",
                    "email": "alex@apex.com",
                    "phone": "+15550199"
                }
            elif doc_path == "platform_users/997075d5-ed5b-4800-8111-a675a87db800":
                doc.exists = True
                doc.to_dict.return_value = {
                    "first_name": "Raj",
                    "last_name": "Vekeria",
                    "email": "raj.vekeria@zco.com",
                    "phone": "+19787293654"
                }
            else:
                doc.exists = False
            
            ref = MagicMock()
            ref.get.return_value = doc
            return ref
            
        client.document = get_doc
        return client

    def get_agent_db_path(self, scope, collection_name, doc_id=None):
        base = f"agents/{self.agent_id}/agent_data/{scope}/{collection_name}"
        if doc_id:
            return f"{base}/{doc_id}"
        return base

    def save(self, scope, collection_name, doc_id, data):
        path = self.get_agent_db_path(scope, collection_name, doc_id)
        db[path] = data.copy()
        return db[path]

    def get(self, scope, collection_name, doc_id):
        path = self.get_agent_db_path(scope, collection_name, doc_id)
        return db.get(path)

    def list(self, scope, collection_name):
        prefix = self.get_agent_db_path(scope, collection_name)
        results = []
        for path, val in db.items():
            if path.startswith(prefix):
                val_copy = val.copy()
                val_copy["id"] = path.split("/")[-1]
                results.append(val_copy)
        return results

    def show_widget(self, widget_id, data=None):
        print(f"-> Show Widget called for '{widget_id}'")

# Monkeypatch hubscape_adk context getters
current_ctx = None

def get_context():
    global current_ctx
    if not current_ctx:
        raise RuntimeError("No active context")
    return current_ctx

app.core.hubscape_adk.get_context = get_context

class ContextSession:
    def __init__(self, ctx):
        self.ctx = ctx
    def __enter__(self):
        global current_ctx
        self.old_ctx = current_ctx
        current_ctx = self.ctx
    def __exit__(self, exc_type, exc_val, exc_tb):
        global current_ctx
        current_ctx = self.old_ctx

# Import tools after mocking get_context
from app.scripts.save_org_details import save_org_details
from app.scripts.submit_personal import submit_personal
from app.scripts.associate_contact_and_alert import associate_contact_and_alert
from app.scripts.check_session import check_session
from app.scripts.check_mobile_exist import check_mobile_exist

async def run_tests():
    global db
    print("🚀 Starting Refactored Data Flow Verification tests...\n")
    
    # ---------------------------------------------------------
    # Test 1: Save Org Details - Guest Flow
    # ---------------------------------------------------------
    print("--- Test 1: save_org_details (Guest Flow) ---")
    db.clear()
    ctx = MockRemoteContext("guest_user_123")
    with ContextSession(ctx):
        res = await save_org_details(
            org_name="Apex Bikes",
            org_description="Bike shop",
            org_website="apexbikes.com",
            user_position="Owner"
        )
        assert res["status"] == "success"
        org_id = res["org_id"]
        
        # Verify saved record
        lead = db[f"agents/sales_onboarding_agent/agent_data/platform/leads/{org_id}"]
        assert lead["owner_id"] == "anonymous"
        assert lead["status"] == "UNVERIFIED"
        print("✅ Guest save_org_details owner_id is 'anonymous' as expected.")

    # ---------------------------------------------------------
    # Test 2: Save Org Details - Authenticated Flow
    # ---------------------------------------------------------
    print("\n--- Test 2: save_org_details (Authenticated Flow) ---")
    await asyncio.sleep(1.1)
    ctx = MockRemoteContext("alex@apex.com")
    with ContextSession(ctx):
        res = await save_org_details(
            org_name="Apex Innovations",
            org_description="Robotics shop",
            org_website="apex.com",
            user_position="CEO"
        )
        assert res["status"] == "success"
        auth_org_id = res["org_id"]
        
        # Verify saved record is ASSOCIATED with pre-populated user details
        lead = db[f"agents/sales_onboarding_agent/agent_data/platform/leads/{auth_org_id}"]
        assert lead["owner_id"] == "alex@apex.com"
        assert lead["status"] == "ASSOCIATED"
        assert lead["contact_name"] == "Alex Doe"
        assert lead["contact_email"] == "alex@apex.com"
        assert lead["contact_mobile"] == "+15550199"
        print("✅ Authenticated save_org_details owner_id matches user_id ('alex@apex.com') and fields are pre-populated.")

    # ---------------------------------------------------------
    # Test 3: Check Mobile Exist - Non-existent
    # ---------------------------------------------------------
    print("\n--- Test 3: check_mobile_exist (Non-existent) ---")
    ctx = MockRemoteContext("guest_user_123")
    with ContextSession(ctx):
        res = await check_mobile_exist("555-9999")
        assert res["exists"] is False
        print("✅ Correctly returned exists=False for unregistered phone.")

    # ---------------------------------------------------------
    # Test 4: Associate Guest Lead & Check Mobile Exist
    # ---------------------------------------------------------
    print("\n--- Test 4: associate_contact_and_alert & check_mobile_exist (Guest) ---")
    ctx = MockRemoteContext("guest_user_123")
    with ContextSession(ctx):
        # Associate contact info
        res = await associate_contact_and_alert(
            org_id=org_id,
            contact_email="guest@apexbikes.com",
            contact_mobile="555-0199",
            full_name="Guest User"
        )
        assert res["status"] == "success"
        
        # Verify lead updated to ASSOCIATED, owner_id remains anonymous
        lead = db[f"agents/sales_onboarding_agent/agent_data/platform/leads/{org_id}"]
        assert lead["status"] == "ASSOCIATED"
        assert lead["contact_mobile"] == "5550199"
        assert lead["owner_id"] == "anonymous"
        
        # Verify no registered_users collections were created/saved
        registered_keys = [k for k in db.keys() if "registered_users" in k]
        assert len(registered_keys) == 0, f"Error: registered_users written! Keys: {registered_keys}"
        print("✅ associate_contact_and_alert did not write to registered_users and kept owner_id='anonymous'.")

        # Verify check_mobile_exist now finds the contact from leads!
        res_exist = await check_mobile_exist("555-0199")
        assert res_exist["exists"] is True
        assert res_exist["user"]["full_name"] == "Guest User"
        assert res_exist["user"]["email_address"] == "guest@apexbikes.com"
        print("✅ check_mobile_exist successfully retrieved user details dynamically from the leads collection.")

    # ---------------------------------------------------------
    # Test 5: Check Session - Guest Track
    # ---------------------------------------------------------
    print("\n--- Test 5: check_session (Guest Track) ---")
    ctx = MockRemoteContext("guest_user_123")
    with ContextSession(ctx):
        res = await check_session()
        assert res["session_valid"] is False
        print("✅ check_session returned invalid session for guest user ID.")

    # ---------------------------------------------------------
    # Test 6: Check Session - Authenticated Track (email)
    # ---------------------------------------------------------
    print("\n--- Test 6: check_session (Authenticated Track via email) ---")
    ctx = MockRemoteContext("alex@apex.com")
    with ContextSession(ctx):
        res = await check_session()
        assert res["session_valid"] is True
        assert res["user_data"]["full_name"] == "Alex Doe"
        assert res["user_data"]["email_address"] == "alex@apex.com"
        assert len(res["user_data"]["linked_organizations"]) == 2
        assert any(org["org_name"] == "Apex Innovations" for org in res["user_data"]["linked_organizations"])
        assert any(org["org_name"] == "Apex Bikes" for org in res["user_data"]["linked_organizations"])
        print("✅ check_session resolved user details from platform_users mock document and matched by email/owner_id/phone.")

    # ---------------------------------------------------------
    # Test 7: Save Lead & Check Session - Authenticated (UUID)
    # ---------------------------------------------------------
    print("\n--- Test 7: Save Lead & Check Session (UUID) ---")
    await asyncio.sleep(1.1)
    ctx = MockRemoteContext("997075d5-ed5b-4800-8111-a675a87db800")
    with ContextSession(ctx):
        res = await save_org_details(
            org_name="Raj Vekeria Co",
            org_description="Software Consultancy",
            org_website="zco.com",
            user_position="Lead Architect"
        )
        assert res["status"] == "success"
        uuid_org_id = res["org_id"]
        
        # Verify saved record is ASSOCIATED and has correct profile details
        lead = db[f"agents/sales_onboarding_agent/agent_data/platform/leads/{uuid_org_id}"]
        assert lead["owner_id"] == "997075d5-ed5b-4800-8111-a675a87db800"
        assert lead["status"] == "ASSOCIATED"
        assert lead["contact_name"] == "Raj Vekeria"
        assert lead["contact_email"] == "raj.vekeria@zco.com"
        assert lead["contact_mobile"] == "+19787293654"
        
        # Check session
        session_res = await check_session()
        assert session_res["session_valid"] is True
        assert session_res["user_data"]["full_name"] == "Raj Vekeria"
        assert session_res["user_data"]["email_address"] == "raj.vekeria@zco.com"
        assert session_res["user_data"]["mobile_number"] == "+19787293654"
        assert len(session_res["user_data"]["linked_organizations"]) == 1
        assert session_res["user_data"]["linked_organizations"][0]["org_name"] == "Raj Vekeria Co"
        print("✅ Successfully verified UUID authentication, profile retrieval, lead creation, and session validation.")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The registered_users collection has been cleanly eliminated and owner_id is fully operational.")

if __name__ == "__main__":
    asyncio.run(run_tests())
