# Functional Requirements Specification (FRS) - Global Organization Subscription Flow (Session-First & Parallel Tracks)

This document details the functional specifications for the globally accessible **Global Subscription Agent** under the session-first parallel-track subscription model.

---

## 1. Overview & Scope
The Global Subscription Agent is accessible in platform chat to both registered and unregistered users. The subscription process evaluates user authentication first and branches into two parallel tracks:

- **Context Gate (Session Check):**
  - The agent checks if the user has an active authenticated session.
  - **YES (Authenticated Track):**
    - **Step 2a (Personalized Greeting):** Agent greets the user personally (e.g., "Hello Alex!") and retrieves registered user data.
    - **Step 3a (Collect Org Details):** Prompts for organization legal name, description, email, phone, and user's position/title.
    - **Step 4a (Store Org in DB):** Saves details to the database with status `UNVERIFIED`.
    - **Bypass:** Skips the mobile prompt and OTP verification entirely, routing straight to **Step 7 (Database Consolidation)**.
  - **NO (Guest Track):**
    - **Step 2b (Generic Greeting):** Agent welcomes the user with a generic subscription welcome message.
    - **Step 3b (Collect Org Details):** Prompts for organization legal name, description, email, phone, and user's position/title.
    - **Step 4b (Store Org in DB):** Saves details to the database with status `UNVERIFIED`.
    - **Step 5 (Ask for Mobile Number):** Prompts the user to enter their personal contact mobile number.
    - **Step 6 (Identity Resolution Gate):** Checks if the user is a registered user by looking up the phone number in the database.
      - **Existing User:** Authenticates session, sends mobile OTP, user verifies, and retrieves existing contact details (Name/Email) (Step 6a).
      - **New User:** Collects Full Name and Email, sends mobile OTP, and user verifies mobile OTP (Step 6b) (Note: Email verification is planned for a future release).

- **Database Consolidation & Linking (Step 7):** Links the verified contact details with the saved organization lead record.
- **Sales Rep Alert & Summary Card (Step 8):** Sends alert notification to Sales Representative, displays organization summary card widget, and thanks the user.

---

## Conversational & Business Rules for the Agent

1. **Handling Partial Information**:
   - If the user provides only some of the requested organization or contact details (e.g., only organization name and description, but omits email/phone), the agent must not proceed to the next step. 
   - Instead, the agent must continue to ask for the remaining missing fields step-by-step before saving the details.

2. **No Internal Action Messages in Chat**:
   - The agent must never output internal status updates or technical logs (such as "Saving organization details..." or "Associating your contact...") in the chat responses. The transition between conversational stages should be seamless and natural.

3. **Smooth Guest Transitions (No "Account Not Found" alerts)**:
   - If the mobile number entered by a guest user does not exist in the database (Scenario C), the agent must not state "Account not found" or "Unregistered user."
   - The agent should transition smoothly, saying: *"Let's collect your contact details! Please provide your Full Name and email address..."*

4. **Normalized Phone Lookup**:
   - The system must normalize all phone numbers before lookup. It must strip spaces, dashes, parentheses, and country codes (e.g. "+1" or "1") to allow matches regardless of input format (e.g., matching `+1-555-0199` to `5550199`).

---

## 2. Functional Requirements Table

| Requirement ID | Module / Title | Description | Priority |
| :--- | :--- | :--- | :--- |
| **INT-001** | Global Agent Access | Agent is accessible globally in chat to registered/unregistered sessions. | Must Have |
| **SES-001** | Session Check Context Gate | Checks for an active session. Splits workflow into Authenticated and Guest parallel tracks. | Must Have |
| **SES-002a** | Personalized Greeting | Greets authenticated users personally using retrieved user data. | Must Have |
| **SES-002b** | Generic Greeting | Greets guest users with a generic subscription welcome message. | Must Have |
| **ORG-001a** | Authenticated Org Details | Collects organization Name, Description, Email, Phone, and user's Position under authenticated session. | Must Have |
| **ORG-001b** | Guest Org Details | Collects organization Name, Description, Email, Phone, and user's Position under guest session. | Must Have |
| **ORG-002** | Handle Partial Information | Agent prompts for missing details iteratively if user input is incomplete. | Must Have |
| **DB-001a** | Save Authenticated Org | Saves authenticated organization lead record to DB with status UNVERIFIED without logging backend actions. | Must Have |
| **DB-001b** | Save Guest Org | Saves guest organization lead record to DB with status UNVERIFIED without logging backend actions. | Must Have |
| **SES-003** | Mobile Number Prompt | Prompts guest users for their personal contact mobile number to lookup details. | Must Have |
| **DB-002** | Normalized Phone Lookup | Normalizes user-input phone numbers (stripping country codes, dashes, spaces) for query. | Must Have |
| **OTP-001** | Existing User Verification | Verifies existing registered user identity via mobile OTP only and retrieves Name/Email. | Must Have |
| **OTP-002** | New User Verification | Collects Full Name and contact email smoothly without "Account Not Found" alerts, and verifies mobile via OTP. | Must Have |
| **LNK-001** | Database Consolidation | Links user verified contact details with the saved organization lead record in the database. | Must Have |
| **ALT-001** | Internal Alert | Immediately triggers lead alert notification to Sales Representative. | Must Have |
| **ACK-001** | Agent Acknowledgment & Summary | Displays thank-you message, under-review notice, and renders the Organization Summary Card in chat. | Must Have |

---

## 3. Conversational Scenarios / Scenario-Based Examples

#### Scenario A: Active Session Found (Existing User)
*   **User:** "I want to subscribe my company."
*   **Agent:** *[Session detected for Alex (alex@apex.com)]* "Hello Alex! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User:** "Name: Apex Innovations, Desc: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO."
*   **Agent:** "Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent:** *[renders Organization Summary Card: Name: Apex Innovations | Description: Robotic research | Email: info@apex.com | Phone: 555-0199]*
*   *[SUBSCRIPTION SESSION CHAT ENDS]*
 
### Scenario B: No Session, Existing User Lookup (OTP Mobile Only)
*   **User:** "I want to subscribe my company."
*   **Agent:** *[No session detected]* "Welcome! Let's get started. Please provide organization details: Legal Name, Description, Organization Email, Organization Phone, and your Position/Title in the organization (e.g. President, CEO, IT Manager, CFO)."
*   **User:** "Name: Apex Innovations, Desc: Robotic research, Email: info@apex.com, Phone: 555-0199, Position: CEO."
*   **Agent:** "Next, please enter your mobile number so we can retrieve your contact details."
*   **User:** "+1 (555) 0199"
*   **Agent:** "Found your details! I have sent a 6-digit OTP code to your mobile number +1 (555) 0199. Please enter it here to verify your identity."
*   **User:** "123456"
*   **Agent:** "OTP verified successfully! Thank you! Your organization subscription request is under review. A Hubscape Sales Representative will reach out to you shortly."
*   **Agent:** *[renders Organization Summary Card: Name: Apex Innovations | Description: Robotic research | Email: info@apex.com | Phone: 555-0199]*
*   *[SUBSCRIPTION SESSION CHAT ENDS]*
 
### Scenario C: No Session, New User Subscribing an Organization (OTP Mobile & Email Future)
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
*   *[SUBSCRIPTION SESSION CHAT ENDS]*

---

## 4. Technical / Flow Details for Step 7: Database Consolidation

The **Database Consolidation** step (Box 7 in the flow chart) executes immediately after successful verification (or active session bypass) of the user's contact details:
1. **Identify User/Contact Info**:
   - **For Authenticated Track**: Automatically retrieves active user details (Full Name, contact email, mobile number, UUID) from the validated active session.
   - **For Guest Track (Existing User)**: Matches and retrieves the existing contact record using the verified mobile number (normalized for formatting differences).
   - **For Guest Track (New User)**: Creates a new user/contact record in the database using the collected personal details.
2. **Link Records**: Creates a mapping in the database that associates the user Mobile and Email collected with the organization lead record (which was saved with status `UNVERIFIED` in Step 4a/4b).
3. **Prepare for Review**: Prepares the associated records for the subsequent Sales Representative alert and manual review.
