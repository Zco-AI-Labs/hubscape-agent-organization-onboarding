## 📂 3. Feature Checklist & Interaction Modes

### Feature 1: Session Check & Greeting Context Gate
*   **Description:** Checks active session at start. Displays personalized greeting for authenticated users and generic greeting for guest users.
*   **Visual Interaction Mode:**
    *   *Trigger:* User initiates subscription chat.
    *   *UI Rendered:* Personalized or generic greeting message based on session evaluation.
    *   *Form Actions:* None.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Agent checks session and replies with a personalized/generic greeting.
    *   *Voice/Phone Flow:* Speaks a personalized greeting or generic welcome.
    *   *Natural Language Parameters Extracted:* `session_token`.
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Happy Path - Session Exists):*
        *   **GIVEN** User session is valid.
        *   **WHEN** User starts subscription.
        *   **THEN** Agent greets user by name and routes to Authenticated Track.
    *   *Scenario B (Happy Path - Guest):*
        *   **GIVEN** User has no active session.
        *   **WHEN** User starts subscription.
        *   **THEN** Agent greets user with a generic welcome and routes to Guest Track.

---

### Feature 2: Organization Intake & DB Storage (with Partial Info Handling)
*   **Description:** Prompts for and collects Organization details (Name, Description, Org Email, Org Phone, and user's Position) and saves them under status `UNVERIFIED` without verbalizing internal backend actions.
*   **Conversational Rule:** If the user supplies incomplete information, the agent must continue to ask for the missing fields sequentially instead of saving partial records.
*   **Visual Interaction Mode:**
    *   *Trigger:* Completion of Feature 1.
    *   *UI Rendered:* Renders a form widget (`org_details_form`).
    *   *Form Actions:* Form submission maps input data to the lead collection.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Agent prompts for each organization field sequentially.
    *   *Voice/Phone Flow:* Agent speaks fields sequentially and records responses.
    *   *Natural Language Parameters Extracted:* `org_name`, `org_description`, `org_email`, `org_phone`, `user_position`.
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Happy Path):*
        *   **GIVEN** Valid organization details are provided.
        *   **WHEN** Submitting details.
        *   **THEN** Saves to DB with status `UNVERIFIED` in the background (no log messages sent to the user) and proceeds.
    *   *Scenario B (Partial Information):*
        *   **GIVEN** Incomplete organization details are provided.
        *   **WHEN** Submitting details.
        *   **THEN** Agent identifies missing fields (e.g. email) and prompts the user specifically for them.

---

### Feature 3: Guest Identity Resolution & Mobile OTP (with Flexible Lookup & Smooth Transition)
*   **Description:** Prompts guest users for their personal contact mobile number, normalizes formatting (stripping spaces, country codes, dashes), checks if registered, sends OTP, and verifies (existing users verify mobile OTP only; new users enter Full Name & Email and verify mobile OTP).
*   **Conversational Rule:** Transition smoothly to collecting contact details in Scenario C without displaying "Account Not Found" messages to the user.
*   **Visual Interaction Mode:**
    *   *Trigger:* Splitting onto the Guest Track.
    *   *UI Rendered:* Mobile input widget (`mobile_input_widget`), OTP verification form (`otp_verify_widget`), and personal details form (`personal_details_widget` for new users).
    *   *Form Actions:* Form submissions for mobile input, OTP verification, and new user personal details.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Agent prompts for mobile number, texts OTP, and verifies.
    *   *Voice/Phone Flow:* Agent speaks mobile request and verifies OTP.
    *   *Natural Language Parameters Extracted:* `mobile_number`, `otp_code`, `full_name`, `email_address`.
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Existing User Happy Path):*
        *   **GIVEN** Mobile number exists in DB (regardless of dashes, country codes, or spacing).
        *   **WHEN** Correct mobile OTP is verified.
        *   **THEN** Proceeds to Database Consolidation.
    *   *Scenario B (New User Happy Path):*
        *   **GIVEN** Mobile number is new.
        *   **WHEN** User submits Name & Email (smooth transition, no "not found" alerts) and verifies mobile OTP.
        *   **THEN** Proceeds to Database Consolidation.

---

### Feature 4: Database Consolidation & Sales Rep Alert
*   **Description:** Links verified contact details with the saved organization lead record, notifies the Sales Representative of the new unverified lead, and displays the summary card.
*   **Visual Interaction Mode:**
    *   *Trigger:* Verification completion or authenticated bypass.
    *   *UI Rendered:* Renders the final Organization Summary Card (`org_summary_card`).
    *   *Form Actions:* None.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Agent texts a plain-text confirmation and summary.
    *   *Voice/Phone Flow:* Agent verbally confirms subscription and reviews details.
    *   *Natural Language Parameters Extracted:* None.
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Happy Path):*
        *   **GIVEN** Contact information is resolved.
        *   **WHEN** Consolidation completes.
        *   **THEN** Triggers Sales Rep alert, links records, and displays Organization Summary Card.
