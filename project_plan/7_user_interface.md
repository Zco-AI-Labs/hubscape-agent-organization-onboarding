## 🎨 7. User Interface & Widgets Specification

These standard Lego block widget configurations are saved inside the agent package.

### Widget 1: `org_details_form`
*   **Type:** `form`
*   **Theme Token Default:** `indigo`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/org_details_form.json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-4 bg-white rounded-lg shadow-md border border-indigo-100"
  },
  "children": [
    {
      "type": "text-input",
      "props": {
        "id": "org_name",
        "label": "Organization Legal Name",
        "placeholder": "Apex Innovations"
      }
    },
    {
      "type": "textarea",
      "props": {
        "id": "org_description",
        "label": "Brief Description",
        "placeholder": "Robotic research and development"
      }
    },
    {
      "type": "text-input",
      "props": {
        "id": "org_email",
        "label": "Organization Email",
        "placeholder": "info@apex.com"
      }
    },
    {
      "type": "text-input",
      "props": {
        "id": "org_phone",
        "label": "Organization Phone",
        "placeholder": "555-0199"
      }
    },
    {
      "type": "dropdown",
      "props": {
        "id": "user_position",
        "label": "Your Position/Title in Organization",
        "options": [
          {"label": "President", "value": "President"},
          {"label": "CEO", "value": "CEO"},
          {"label": "CFO", "value": "CFO"},
          {"label": "IT Manager", "value": "IT Manager"}
        ]
      }
    },
    {
      "type": "button",
      "props": {
        "id": "submit_org_details",
        "label": "Submit Details",
        "variant": "primary"
      }
    }
  ]
}
```

---

### Widget 2: `mobile_input_widget`
*   **Type:** `form`
*   **Theme Token Default:** `slate`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/mobile_input_widget.json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-2 p-4 bg-white rounded-lg border border-slate-200"
  },
  "children": [
    {
      "type": "text-input",
      "props": {
        "id": "mobile_number",
        "label": "Personal Contact Mobile Number",
        "placeholder": "555-0199"
      }
    },
    {
      "type": "button",
      "props": {
        "id": "submit_mobile",
        "label": "Check Account",
        "variant": "primary"
      }
    }
  ]
}
```

---

### Widget 3: `otp_verify_widget`
*   **Type:** `form`
*   **Theme Token Default:** `blue`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/otp_verify_widget.json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-2 p-4 bg-white rounded-lg border border-blue-200"
  },
  "children": [
    {
      "type": "text-input",
      "props": {
        "id": "otp_code",
        "label": "Enter 6-digit Verification Code",
        "placeholder": "123456"
      }
    },
    {
      "type": "button",
      "props": {
        "id": "submit_otp",
        "label": "Verify OTP",
        "variant": "primary"
      }
    }
  ]
}
```

---

### Widget 4: `personal_details_widget`
*   **Type:** `form`
*   **Theme Token Default:** `pink`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/personal_details_widget.json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-4 bg-white rounded-lg border border-pink-100"
  },
  "children": [
    {
      "type": "text-input",
      "props": {
        "id": "full_name",
        "label": "Contact Person Full Name",
        "placeholder": "Alex Doe"
      }
    },
    {
      "type": "text-input",
      "props": {
        "id": "email_address",
        "label": "Contact Email Address",
        "placeholder": "alex@apex.com"
      }
    },
    {
      "type": "button",
      "props": {
        "id": "submit_personal",
        "label": "Submit Contact Details",
        "variant": "primary"
      }
    }
  ]
}
```

---

### Widget 5: `org_summary_card`
*   **Type:** `detail-card`
*   **Theme Token Default:** `green`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/org_summary_card.json
{
  "type": "card",
  "props": {
    "className": "p-4 bg-green-50 rounded-lg border border-green-200"
  },
  "children": [
    {
      "type": "title",
      "props": {
        "text": "Organization Summary Card"
      }
    },
    {
      "type": "metadata-grid",
      "props": {
        "items": [
          {"label": "Legal Name", "id": "summary_name"},
          {"label": "Description", "id": "summary_description"},
          {"label": "Org Email", "id": "summary_email"},
          {"label": "Org Phone", "id": "summary_phone"}
        ]
      }
    }
  ]
}
```
