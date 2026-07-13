# Database Linking & Consolidation Architecture Specification

This document details the database schemas, collection relationships, and matching algorithms used by the Global Subscription Agent to link organization subscriptions to verified user phone numbers.

---

## 1. Architectural Overview

In the session-first parallel-track model, each organization is subscribed under a verified user contact record. This link is established during **Step 7 (Database Consolidation)**:
- **Authenticated Track**: Bypasses OTP, matching the active user session ID (personal details) directly to the organization record.
- **Guest Track**: Matches the user's normalized phone number (verified via SMS OTP) to the organization record.

The connection is maintained as a **Foreign Key Reference** from the `leads` collection back to the `registered_users` collection, using the normalized mobile number as the primary link.

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
| `contact_mobile` | `String` | **Foreign Key Link**: Verified mobile number of the subscriber. |
| `contact_email` | `String` | Verified contact email of the subscriber. |
| `contact_name` | `String` | Full name of the verified subscriber. |
| `created_at` | `String` | ISO timestamp of record creation. |
| `updated_at` | `String` | ISO timestamp of last update. |

### B. `registered_users` Collection (Platform Contacts)
Stores details of registered users. This is used for identity resolution.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `mobile_number` | `String` | **Primary Key Link**: Normalized phone number (digits only). |
| `full_name` | `String` | User's full name. |
| `email_address` | `String` | Personal/contact email address. |

### C. `active_otps` Collection (Temporary Verification Cache)
Stores temporary active OTP validation codes mapped to mobile numbers.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `mobile_number` | `String` | Normalized mobile number (digits only). |
| `otp_code` | `String` | Active 6-digit verification code. |

---

## 3. Phone Number Normalization & Matching Algorithm

To guarantee lookup flexibility (allowing lookups whether or not the user inputs country codes, spaces, dashes, or brackets), the agent normalizes all inputs before querying `registered_users`:

1. **Format Stripping**: Remove all non-digit characters (`+`, `-`, `(`, `)`, spaces).
   * Example: `+1 (555) 0199-23` becomes `1555019923`.
2. **Country Code Truncation**: If the resulting string starts with country code `1` and has a length of 11 digits, strip the leading `1` to isolate the 10-digit national number.
   * Example: `1555019923` becomes `555019923`.
3. **Database Match**: Perform query matching using this standardized digits-only string.

---

## 4. Consolidation & Linking Workflow (Step 7)

Once the user's identity is verified (via active session or OTP), the database consolidation is executed:

```
                  [ registered_users ]
                  +--------------------------------+
                  | mobile_number: "5550199" (PK)  | <---------+
                  | full_name: "Alex Doe"          |           |
                  | email_address: "alex@apex.com" |           |
                  +--------------------------------+           |
                                                               |
                                                               | (Linked via PK -> FK)
                                                               |
                  [ leads ]                                    |
                  +--------------------------------+           |
                  | id: "lead_1783576317"          |           |
                  | org_name: "Apex Innovations"   |           |
                  | status: "ASSOCIATED"           |           |
                  | contact_mobile: "5550199" (FK) | <---------+
                  | contact_email: "alex@apex.com" |
                  | contact_name: "Alex Doe"       |
                  +--------------------------------+
```

### Steps for Consolidation:
1. **Retrieve Organization Record**: Fetch the unverified lead document using `org_id` saved in Step 4.
2. **Look Up / Create Contact**:
   - *Authenticated Path*: Fetch user details directly from active session parameters.
   - *Guest (Existing)*: Query `registered_users` using normalized `mobile_number`.
   - *Guest (New)*: Insert a new document into `registered_users` containing `full_name`, `email_address`, and the normalized `mobile_number`.
3. **Write Foreign Keys**: Update the organization `leads` document with the verified `contact_mobile`, `contact_email`, and `contact_name` and change status to `ASSOCIATED`.
4. **Trigger Alerts**: Log the Sales alert in the database and render the UI summary card.
