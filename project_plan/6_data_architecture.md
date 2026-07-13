## 💾 6. Data Architecture & DB Schemas

This agent utilizes a local JSON mock database file (`app/mock_db.json`) during development to simulate database read/write actions.

### Schema: `app/mock_db.json`

```json
{
  "leads": [
    {
      "id": "lead_1783576317",
      "org_name": "Apex Innovations",
      "org_description": "Robotic research",
      "org_email": "info@apex.com",
      "org_phone": "555-0199",
      "user_position": "CEO",
      "status": "UNVERIFIED",
      "contact_email": null,
      "contact_mobile": null,
      "contact_name": null,
      "created_at": "2026-07-10T10:14:39Z"
    }
  ],
  "registered_users": [
    {
      "mobile_number": "555-0199",
      "full_name": "Alex Doe",
      "email_address": "alex@apex.com"
    }
  ],
  "active_otps": {
    "555-0199": "123456"
  },
  "sales_alerts": [
    {
      "alert_id": "alert_1783576319",
      "lead_id": "lead_1783576317",
      "message": "New unverified lead has arrived for Apex Innovations",
      "timestamp": "2026-07-10T10:15:20Z"
    }
  ]
}
```

#### Lead Fields Table
| Field Name | Type | Description | Mandatory / Optional |
| :--- | :--- | :--- | :--- |
| `id` | `String` | Unique lead record document identifier | Mandatory |
| `org_name` | `String` | The legal name of the organization | Mandatory |
| `org_description` | `String` | Brief organization description | Mandatory |
| `org_email` | `String` | Primary contact email of the organization | Mandatory |
| `org_phone` | `String` | Contact phone number of the organization | Mandatory |
| `user_position` | `String` | Subscribing user's position/title in organization | Mandatory |
| `status` | `String` | Status of lead: `UNVERIFIED` / `ASSOCIATED` / `ACTIVE` | Mandatory |
| `contact_email` | `String` | Verified contact email address linked to the lead | Optional |
| `contact_mobile` | `String` | Verified personal mobile number linked to the lead | Optional |
| `contact_name` | `String` | Full name of the contact person linked to the lead | Optional |
| `created_at` | `String` | ISO timestamp of creation | Mandatory |

#### Phone Number Lookup Normalization Rule
Before checking if the user exists in `registered_users` by mobile number:
1. Strip all non-digit characters (e.g. `+`, `-`, `(`, `)`, spaces).
2. Strip leading country code `1` or `+1` if present (e.g. `+1 (555) 0199` and `555-0199` both normalize to `5550199` for exact matching against `registered_users` records).
