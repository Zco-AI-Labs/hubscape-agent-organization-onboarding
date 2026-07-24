# Database Linking & Consolidation Architecture Specification

This document details the database schemas, collection relationships, and matching algorithms used by the Global Subscription Agent to link organization subscriptions to verified users.

---

## 1. Architectural Overview

In the session-first parallel-track model, each organization is subscribed under a verified user contact record. This link is established during **Step 7 (Database Consolidation)**:
- **Authenticated Track**: Bypasses OTP, matching the active user session ID (personal details) directly to the organization record.
- **Guest Track**: Matches the user's normalized phone number (verified via SMS OTP) to the organization record.

The relationship is maintained directly within the `leads` collection using `owner_id` (representing the authenticated user's `user_id` or `"anonymous"` for guests) and storing verified contact information directly on the lead document.

---

## 2. Collection Schemas & Fields

### A. `leads` Collection (Organization Subscription Leads)
Stores the details of the organization subscription request. It holds status and reference links to the contact person.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `id` | `String` | Unique lead record document identifier. |
| `org_name` | `String` | Legal name of the organization. |
| `org_description` | `String` | Description of business activities. |
| `org_email` | `String` | Primary contact email for the organization. |
| `org_phone` | `String` | Contact phone number for the organization. |
| `user_position` | `String` | Subscribing user's position in organization (e.g. CEO). |
| `status` | `String` | Current state of lead: `UNVERIFIED` / `ASSOCIATED`. |
| `contact_mobile` | `String` | Verified mobile number of the subscriber. |
| `contact_email` | `String` | Verified contact email of the subscriber. |
| `contact_name` | `String` | Full name of the verified subscriber. |
| `owner_id` | `String` | User ID of the owner (authenticated user_id or "anonymous"). |
| `created_at` | `String` | ISO timestamp of record creation. |
| `updated_at` | `String` | ISO timestamp of last update. |

### B. `active_otps` Collection (Temporary Verification Cache)
Stores temporary active OTP validation codes mapped to mobile numbers.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `mobile_number` | `String` | Normalized mobile number (digits only). |
| `otp_code` | `String` | Active 6-digit verification code. |

---

## 3. Phone Number Normalization & Matching Algorithm

To guarantee lookup flexibility (allowing lookups whether or not the user inputs country codes, spaces, dashes, or brackets), the agent normalizes all inputs before querying `leads`:

1. **Format Stripping**: Remove all non-digit characters (`+`, `-`, `(`, `)`, spaces).
   * Example: `+1 (555) 0199-23` becomes `1555019923`.
2. **Country Code Truncation**: If the resulting string starts with country code `1` and has a length of 11 digits, strip the leading `1` to isolate the 10-digit national number.
   * Example: `1555019923` becomes `555019923`.
3. **Database Match**: Perform query matching using this standardized digits-only string against `contact_mobile`.

---

## 4. Consolidation & Linking Workflow (Step 7)

Once the user's identity is verified (via active session or OTP), the database consolidation is executed:

```
                  [ leads ]                                    
                  +--------------------------------+           
                  | id: "lead_1783576317"          |           
                  | org_name: "Apex Innovations"   |           
                  | status: "ASSOCIATED"           |           
                  | owner_id: "alex@apex.com"      |
                  | contact_mobile: "5550199"      |
                  | contact_email: "alex@apex.com" |
                  | contact_name: "Alex Doe"       |
                  +--------------------------------+
```

### Steps for Consolidation:
1. **Retrieve Organization Lead**: Fetch the unverified lead document using `org_id` saved in Step 4.
2. **Determine owner_id & Contact Details**:
   - *Authenticated Track*: Set `owner_id` to the session `user_id`, and pull contact details from the verified session.
   - *Guest Track*: Keep `owner_id` as `"anonymous"`. Associate the verification details (`contact_mobile`, `contact_email`, `contact_name`) provided during the verification steps.
3. **Save Updates**: Update the organization `leads` document with the resolved `owner_id`, `contact_mobile`, `contact_email`, and `contact_name` and change status to `ASSOCIATED`.
4. **Trigger Alerts**: Log the Sales Representative alert in the database and render the UI summary card.
