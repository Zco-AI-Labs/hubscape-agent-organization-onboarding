## 💬 4. Interaction Scripts & Conversational Flows

### Scenario A: Active Session Found (Existing User)

#### Flow A: Visual Path (Chat UI with widgets)
*   **User:** "I want to subscribe my company."
*   **Agent (Behind the Scenes):** Calls `consultAgent` -> calls tool `check_session` which returns active user session.
*   **Agent UI Rendered:** Displays greeting message.
*   **Agent Message:** "Hello Alex! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User clicks button:** Submits form `org_details_form` with details: Name: `Apex Innovations`, Desc: `Robotic research`, Email: `info@apex.com`, Phone: `555-0199`, Position: `CEO`.
*   **Agent (Behind the Scenes):** Calls tool `save_org_details` and saves with status `UNVERIFIED`.
*   **Agent (Behind the Scenes):** Calls `associate_contact_and_alert` (bypassing OTP).
*   **Agent Message:** "Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent UI Rendered:** Displays Widget `org_summary_card` with organization summary.

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Subscribe Apex Innovations."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=True`.
*   **Agent Text Reply:** "Hello Alex! To subscribe, please text the details in this format: Name, Description, Org Email, Org Phone, and your Position."
*   **User (SMS):** "Apex Innovations, Robotic research, info@apex.com, 555-0199, CEO."
*   **Agent Text Reply:** "Thank you! Your organization subscription request is under review. Sales will reach out shortly."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "I want to subscribe my company Apex Innovations."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=True`.
*   **Agent Speech Reply:** "Hello Alex! Please speak the description, organization email, phone number, and your job title."
*   **User (Voice):** "Robotic research, info at apex dot com, 555-0199, CEO."
*   **Agent Speech Reply:** "Thank you! Your organization subscription request is under review. A Sales Representative will call you shortly."

---

### Scenario B: No Session, Existing User Lookup (OTP Mobile Only)

#### Flow A: Visual Path (Chat UI with widgets)
*   **User:** "I want to subscribe my company."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Message:** "*[No session detected]* Welcome! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User clicks button:** Submits `org_details_form` with details.
*   **Agent (Behind the Scenes):** Calls `save_org_details` and saves with status `UNVERIFIED`.
*   **Agent UI Rendered:** Displays Widget `mobile_input_widget`.
*   **Agent Message:** "Next, please enter your mobile number so we can retrieve your contact details."
*   **User clicks button:** Submits mobile number `+1 (555) 0199`.
*   **Agent (Behind the Scenes):** Normalizes "+1 (555) 0199" to "5550199" and calls `check_mobile_exist` which returns `exists=True`. Generates and sends OTP.
*   **Agent UI Rendered:** Displays Widget `otp_verify_widget`.
*   **Agent Message:** "Found your details! I have sent a 6-digit OTP code to your mobile number +1 (555) 0199. Please enter it here to verify your identity."
*   **User clicks button:** Submits OTP code `123456`.
*   **Agent (Behind the Scenes):** Calls `verify_otp` and then `associate_contact_and_alert`.
*   **Agent Message:** "OTP verified successfully! Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent UI Rendered:** Displays Widget `org_summary_card`.

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Subscribe Apex Innovations."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Text Reply:** "*[No session detected]* Welcome! Please text the organization details in this format: Name, Description, Org Email, Org Phone, and your Position."
*   **User (SMS):** "Apex Innovations, Robotic research, info@apex.com, 555-0199, CEO."
*   **Agent Text Reply:** "Next, please text your personal mobile number so we can retrieve your contact details."
*   **User (SMS):** "+1 (555) 0199"
*   **Agent Text Reply:** "Found your details! I texted a 6-digit code to +1 (555) 0199. Please text it back to verify."
*   **User (SMS):** "123456"
*   **Agent Text Reply:** "OTP verified! Thank you! Your organization subscription request is under review. Sales will contact you shortly."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "I want to subscribe my company."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Speech Reply:** "Welcome! Please tell me the name, description, email, phone number, and your job title."
*   **User (Voice):** "Apex Innovations, Robotic research, info at apex dot com, 555-0199, CEO."
*   **Agent Speech Reply:** "Please state your personal mobile number so we can retrieve your contact details."
*   **User (Voice):** "555-0199"
*   **Agent Speech Reply:** "Found your details! I have sent a verification code to your mobile. Please say or enter the six digit code."
*   **User (Voice):** "1 2 3 4 5 6"
*   **Agent Speech Reply:** "Verified. Thank you! Your organization subscription request is under review. A Sales Representative will contact you shortly."

---

### Scenario C: No Session, New User Subscribing an Organization (OTP Mobile & Email Future)

#### Flow A: Visual Path (Chat UI with widgets)
*   **User:** "I want to subscribe my company."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Message:** "*[No session detected]* Welcome! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User clicks button:** Submits `org_details_form`.
*   **Agent (Behind the Scenes):** Calls `save_org_details` and saves with status `UNVERIFIED`.
*   **Agent UI Rendered:** Displays Widget `mobile_input_widget`.
*   **Agent Message:** "Next, please enter your mobile number so we can retrieve your contact details."
*   **User clicks button:** Submits mobile number `555-9999`.
*   **Agent (Behind the Scenes):** Calls `check_mobile_exist` which returns `exists=False`.
*   **Agent UI Rendered:** Displays Widget `personal_details_widget`.
*   **Agent Message:** "Let's collect your contact details! Since you entered your mobile number 555-9999, please enter your remaining personal contact details: Full Name and contact email address."
*   **User clicks button:** Submits name `Alex Doe` and email `alex@apex.com`.
*   **Agent (Behind the Scenes):** Generates and sends OTP code to mobile.
*   **Agent UI Rendered:** Displays Widget `otp_verify_widget`.
*   **Agent Message:** "(Note: Email verification is planned for a future release; we will verify your mobile number first). Next, I have sent a 6-digit OTP code to your mobile number 555-9999. Please enter it here to verify your mobile."
*   **User clicks button:** Submits OTP code `987654`.
*   **Agent (Behind the Scenes):** Calls `verify_otp` and then `associate_contact_and_alert`.
*   **Agent Message:** "Mobile OTP verified successfully! Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent UI Rendered:** Displays Widget `org_summary_card`.

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Subscribe Apex Innovations."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Text Reply:** "*[No session detected]* Welcome! Please text the organization details in this format: Name, Description, Org Email, Org Phone, and your Position."
*   **User (SMS):** "Apex Innovations, Robotic research, info@apex.com, 555-0199, CEO."
*   **Agent Text Reply:** "Next, please text your personal mobile number so we can retrieve your contact details."
*   **User (SMS):** "555-9999"
*   **Agent Text Reply:** "Let's collect your contact details! Please text your Full Name and email address separated by a comma."
*   **User (SMS):** "Alex Doe, alex@apex.com"
*   **Agent Text Reply:** "(Note: Email verification is planned for a future release; we will verify your mobile first). I texted an OTP code to your mobile 555-9999. Please text it back to verify."
*   **User (SMS):** "987654"
*   **Agent Text Reply:** "Mobile OTP verified! Thank you! Your organization subscription request is under review. Sales will contact you shortly."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "I want to subscribe my company."
*   **Agent (Behind the Scenes):** Calls `check_session` which returns `session_valid=False`.
*   **Agent Speech Reply:** "Welcome! Please tell me the name, description, email, phone number, and your job title."
*   **User (Voice):** "Apex Innovations, Robotic research, info at apex dot com, 555-0199, CEO."
*   **Agent Speech Reply:** "Please state your personal mobile number so we can retrieve your contact details."
*   **User (Voice):** "555-9999"
*   **Agent Speech Reply:** "Let's collect your contact details! Please say your Full Name and contact email address."
*   **User (Voice):** "Alex Doe, alex at apex dot com."
*   **Agent Speech Reply:** "Note: Email verification is planned for a future release; we will verify your mobile first. I sent a code to your mobile. Please say or enter the six digit code."
*   **User (Voice):** "9 8 7 6 5 4"
*   **Agent Speech Reply:** "Mobile verified. Thank you! Your organization subscription request is under review. A Sales Representative will contact you shortly."
