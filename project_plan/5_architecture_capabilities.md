## 🛠️ 5. Architecture & Capabilities

### System Instructions (`app/SKILL.md`)
```text
You are the Hubscape Global Subscription Agent. Your primary mission is to guide prospective organization creators through the subscription process.

Strictly adhere to the following sequence of steps:
1. Immediately collect organization details (Legal Name, Description, Organization Email, Organization Phone, and user's Position/Title).
   - If the user provides partial/incomplete details, continue asking for the remaining missing fields step-by-step before saving.
2. Save these details to the local JSON mock database (status: "UNVERIFIED") using the save_org_details tool. Do not print any "Saving details" status logs in chat.
3. Perform a session check using check_session.
   - If an active session is detected: greet user personally (e.g. "Hello Alex!"), retrieve registered user data, bypass OTP verification, and proceed to Step 6.
   - If no session is detected: greet guest user generically, and prompt the user for their personal mobile number.
4. Check if the entered mobile number belongs to an existing user using check_mobile_exist (lookup query is normalized to ignore spacing, dashes, and country codes).
   - If Yes (Existing User): Send and verify a mobile OTP code using send_mobile_otp and verify_mobile_otp.
   - If No (New User): Transition smoothly without saying "account not found." Prompt for remaining contact details (Full Name and contact email address), explain that email verification is a future release [Verify Email (Future)], and then send and verify a mobile OTP code using send_mobile_otp and verify_mobile_otp.
5. Create/retrieve the contact record and link it to the unverified organization record using associate_contact_and_alert. This updates status to "ASSOCIATED" and alerts the Sales Representative.
6. Display a friendly confirmation message, an under-review notice, and render the Organization Summary Card containing Name, Description, Org Email, and Org Phone.

Personal Details Rules:
- Never refer to user records as a "profile" (use "contact information" or "contact details" instead).
- Never use technical backend terms like "lead database" or "token" in conversational replies.
```

### Tool Implementations (`app/scripts/`)

#### `save_org_details.py`
```python
# app/scripts/save_org_details.py
async def save_org_details(
    tool_context: ToolContext,
    org_name: str,
    org_description: str,
    org_email: str,
    org_phone: str,
    user_position: str
) -> dict:
    """
    Saves the organization details and the user's position to the local JSON mock database under UNVERIFIED status.

    Args:
        org_name: Legal name of the organization
        org_description: Brief description of the organization
        org_email: Primary contact email for the organization
        org_phone: Contact phone number for the organization
        user_position: The position/title of the current user subscribing the organization
    """
    # Logic to load/write to app/mock_db.json
```

#### `check_session.py`
```python
# app/scripts/check_session.py
async def check_session(tool_context: ToolContext) -> dict:
    """
    Checks if the user has an active session. Returns session status and profile data if valid.
    """
    # Logic to check mock session status
```

#### `check_mobile_exist.py`
```python
# app/scripts/check_mobile_exist.py
async def check_mobile_exist(tool_context: ToolContext, mobile_number: str) -> dict:
    """
    Checks if the personal mobile number is already registered in the mock database.
    Normalizes the input mobile number by removing dashes, spaces, and country codes (e.g. "+1" or "1") before querying.

    Args:
        mobile_number: The personal mobile number to check
    """
    # Logic to query app/mock_db.json contacts with normalized number
```

#### `send_mobile_otp.py`
```python
# app/scripts/send_mobile_otp.py
async def send_mobile_otp(tool_context: ToolContext, mobile_number: str) -> dict:
    """
    Triggers sending a mock 6-digit OTP verification code to the mobile number.

    Args:
        mobile_number: The target mobile number
    """
    # Logic to write generated OTP code to app/mock_db.json and print/log it
```

#### `verify_mobile_otp.py`
```python
# app/scripts/verify_mobile_otp.py
async def verify_mobile_otp(tool_context: ToolContext, mobile_number: str, otp_code: str) -> dict:
    """
    Validates the 6-digit OTP code against the mock database entry.

    Args:
        mobile_number: The mobile number associated with the OTP
        otp_code: The 6-digit code to verify
    """
    # Logic to validate OTP code from app/mock_db.json
```

#### `associate_contact_and_alert.py`
```python
# app/scripts/associate_contact_and_alert.py
async def associate_contact_and_alert(
    tool_context: ToolContext,
    org_id: str,
    contact_email: str,
    contact_mobile: str,
    full_name: str = ""
) -> dict:
    """
    Associates the verified contact details with the saved organization lead in mock_db.json and logs sales alert.

    Args:
        org_id: The ID of the unverified organization lead record
        contact_email: Contact email address collected
        contact_mobile: Personal mobile number collected
        full_name: Full name of the contact (for new users)
    """
    # Logic to update mock_db.json lead association and log Sales Rep alert
```

### 🔑 Tool Privileges Matrix

| Privilege Name | Description of Granted Capabilities / Tools |
| :--- | :--- |
| `ORG_LEAD_CREATE` | Permits creating unverified organization lead records (`save_org_details`). |
| `CONTACT_VERIFY` | Permits checking sessions, mobile existence, and performing OTP checks (`check_session`, `check_mobile_exist`, `send_mobile_otp`, `verify_mobile_otp`). |
| `SALES_ALERT` | Permits linking contact details and dispatching representative alerts (`associate_contact_and_alert`). |

### Model Context Protocol (MCP) & Agent-to-Agent (A2A) Connections
None.

### Required Secrets (Agent Secrets Vault)
None.
