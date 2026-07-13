## 🧪 8. Verification & QA Plan

*   **Automated Tests:**
    - Run unit and integration tests using pytest:
      ```bash
      uv run pytest tests/unit tests/integration
      ```
    - Check code quality:
      ```bash
      agents-cli lint
      ```

*   **Manual Verification Checklist:**
    1.  `[ ]` Verify that launching the agent immediately checks session status and performs personalized/generic greeting.
    2.  `[ ]` Verify that organization details are successfully saved to `app/mock_db.json` with status `UNVERIFIED` quietly, without printing internal backend messages in chat.
    3.  `[ ]` Verify that for active sessions, the agent bypasses mobile OTP prompts and links contact directly in `app/mock_db.json`.
    4.  `[ ]` Verify that for guest sessions, the agent prompts for mobile, does registered lookups (ignoring spaces, dashes, or country codes), sends/verifies OTP, and links contact.
    5.  `[ ]` Verify that unrecognized mobile numbers transition smoothly to collecting contact details without displaying any "Account Not Found" errors.
    6.  `[ ]` Verify that completing verification creates a Sales Rep alert entry in `app/mock_db.json`.
    7.  `[ ]` Verify that submitting partial organization info causes the agent to prompt for the missing fields iteratively.
