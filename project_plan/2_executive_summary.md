## 🎯 2. Executive Summary

### Core Objective
To guide users through subscribing and registering an organization on the Hubscape platform. The agent evaluates user authentication first, greeting authenticated users personally and guest users generically. For guest users, it resolves identity by performing a normalized database lookup of their mobile number, executing OTP verification, and smoothly transitioning to contact detail collection if unregistered. It then links their verified contact details to the unverified organization record and notifies a Sales Representative.

### High-Level Success Criteria
*   Successfully checks session status at startup to select the appropriate parallel track.
*   Collects full organization details, prompting step-by-step if the user inputs partial details.
*   Bypasses OTP verification for authenticated sessions.
*   Executes normalized phone number lookup and mobile OTP verification for guest sessions.
*   Transition smoothly to personal detail collection for new guest users without showing "Account Not Found" errors.
*   Quietly saves details to the mock database and triggers a Sales Representative alert notification without verbalizing internal backend actions in the chat.
