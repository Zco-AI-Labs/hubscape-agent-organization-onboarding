# Organization Subscription Agent Walkthrough - Session-First & Parallel Tracks

This document provides a step-by-step walkthrough of the Global Subscription Agent's parallel-track workflow, showing how both authenticated and guest users are routed.

---

## Workflow Steps & Explanations

- **Step 1: Subscription Initiation** - User expresses intent to subscribe/onboard an organization.
- **Step 2: Context Gate (Session Check)** - Agent checks if the user has an active authenticated session.
  - **YES (Authenticated Track)**: Routes to Step 2a.
  - **NO (Guest Track)**: Routes to Step 2b.
- **Step 2a: Personalized Greeting** - Agent greets the user by name using retrieved user data.
- **Step 2b: Generic Greeting** - Agent welcomes guest user with a generic subscription welcome message.
- **Step 3a & 3b: Collect Org Details** - Prompts for Organization details: Legal Name, Description, Org Email, Org Phone, and user's Position/Title in the organization (e.g. CEO, CFO, IT Manager).
  - *Rule (Partial Information)*: If the user leaves out any of the required details, the agent continues prompting for the missing details step-by-step before saving.
- **Step 4a & 4b: Store Org in DB** - Saves organization details to the database with status `UNVERIFIED` (performed silently in the background, without printing internal status messages).
  - **Authenticated Track Bypass**: Loops straight from Step 4a to Step 7 (Database Consolidation), completely bypassing mobile number prompt and OTP verification.
- **Step 5: Ask for Mobile Number (Guest Track Only)** - Prompts guest user to enter their personal mobile number.
- **Step 6: Identity Resolution Check** - Agent looks up the user's phone number in the database of registered users.
  - *Lookup Normalization*: Matches the number flexibly by stripping country codes (like "+1" or "1"), spaces, brackets, and dashes.
  - **Existing User (Step 6a)**: Sends mobile OTP, user verifies, and retrieves existing contact details.
  - **New User (Step 6b)**: Transitions smoothly to collecting personal contact details (Full Name, contact email) and verifies mobile OTP, without printing any "account not found" error messages.
- **Step 7: Database Consolidation** - Links verified contact details (mobile, email, UUID) with the unverified organization lead record.
- **Step 8: Alert Sales & Show Card** - Dispatches alert notification to the Sales Representative, displays the organization summary card in chat, and thanks the user.

---

## Conversational Scenario Transcripts

### Scenario A: Active Session Found (Existing User)
`[SUBSCRIPTION SESSION CHAT STARTS (SESSION VALID)]`
*   **User:** "I want to subscribe my company."
*   **Agent:** *[Session detected for Alex (alex@apex.com)]* "Hello Alex! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User:** "Name: Apex Innovations, Desc: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO."
*   **Agent:** "Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent:** *[renders Organization Summary Card: Name: Apex Innovations | Description: Robotic research | Email: info@apex.com | Phone: 555-0199]*
`[SUBSCRIPTION SESSION CHAT ENDS]`

### Scenario B: No Session, Existing User Lookup (OTP Mobile Only)
`[SUBSCRIPTION SESSION CHAT STARTS (NO SESSION, EXISTING USER)]`
*   **User:** "I want to subscribe my company."
*   **Agent:** *[No session detected]* "Welcome! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User:** "Name: Apex Innovations, Desc: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO."
*   **Agent:** "Next, please enter your mobile number so we can retrieve your contact details."
*   **User:** "+1 (555) 0199"
*   **Agent:** "Found your details! I have sent a 6-digit OTP code to your mobile number +1 (555) 0199. Please enter it here to verify your identity."
*   **User:** "123456"
*   **Agent:** "OTP verified successfully! Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent:** *[renders Organization Summary Card: Name: Apex Innovations | Description: Robotic research | Email: info@apex.com | Phone: 555-0199]*
`[SUBSCRIPTION SESSION CHAT ENDS]`

### Scenario C: No Session, New User Subscribing an Organization (OTP Mobile & Email Future)
`[SUBSCRIPTION SESSION CHAT STARTS (NO SESSION, NEW USER)]`
*   **User:** "I want to subscribe my company."
*   **Agent:** *[No session detected]* "Welcome! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User:** "Name: Apex Innovations, Desc: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO."
*   **Agent:** "Next, please enter your mobile number so we can retrieve your contact details."
*   **User:** "555-9999"
*   **Agent:** "Let's collect your contact details! Since you entered your mobile number 555-9999, please enter your remaining personal contact details: Full Name and contact email address."
*   **User:** "Alex Doe, Email: alex@apex.com"
*   **Agent:** "*(Note: Email verification is planned for a future release; we will verify your mobile number first).* Next, I have sent a 6-digit OTP code to your mobile number 555-9999. Please enter it here to verify your mobile."
*   **User:** "987654"
*   **Agent:** "Mobile OTP verified successfully! Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent:** *[renders Organization Summary Card: Name: Apex Innovations | Description: Robotics research | Email: info@apex.com | Phone: 555-0199]*
`[SUBSCRIPTION SESSION CHAT ENDS]`
