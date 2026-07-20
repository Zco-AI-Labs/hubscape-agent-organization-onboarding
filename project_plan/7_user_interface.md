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
      "type": "input",
      "props": {
        "name": "org_name",
        "label": "Organization Legal Name",
        "placeholder": "Apex Innovations"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "org_description",
        "label": "Brief Description",
        "placeholder": "Robotic research and development",
        "multiline": true
      }
    },
    {
      "type": "input",
      "props": {
        "name": "org_email",
        "label": "Organization Email",
        "placeholder": "info@apex.com"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "org_phone",
        "label": "Organization Phone",
        "placeholder": "555-0199"
      }
    },
    {
      "type": "select",
      "props": {
        "name": "user_position",
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
        "label": "Submit Details",
        "actionUrl": "agent://save_org_details",
        "styling": {
          "colorTheme": "indigo"
        }
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
      "type": "input",
      "props": {
        "name": "mobile_number",
        "label": "Personal Contact Mobile Number",
        "placeholder": "555-0199",
        "inputType": "text"
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Check Account",
        "actionUrl": "agent://check_mobile_exist",
        "styling": {
          "colorTheme": "slate"
        }
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
      "type": "input",
      "props": {
        "name": "otp_code",
        "label": "Enter 6-digit Verification Code",
        "placeholder": "123456",
        "inputType": "text"
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Verify OTP",
        "actionUrl": "agent://verify_mobile_otp",
        "styling": {
          "colorTheme": "blue"
        }
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
      "type": "input",
      "props": {
        "name": "full_name",
        "label": "Contact Person Full Name",
        "placeholder": "Alex Doe",
        "inputType": "text"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "contact_email",
        "label": "Contact Email Address",
        "placeholder": "alex@apex.com",
        "inputType": "text"
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Submit Contact Details",
        "actionUrl": "agent://associate_contact_and_alert",
        "styling": {
          "colorTheme": "pink"
        }
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
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-5 bg-emerald-50 dark:bg-emerald-950 rounded-xl border border-emerald-200 dark:border-emerald-800 shadow-sm"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "text": "Organization Summary Card",
        "size": "lg",
        "weight": "bold",
        "className": "text-emerald-900 dark:text-emerald-100"
      }
    },
    {
      "type": "container",
      "props": {
        "className": "grid grid-cols-2 gap-3 bg-white dark:bg-slate-900 p-4 rounded-lg border border-emerald-100 dark:border-slate-800"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Legal Name",
                "size": "xs",
                "className": "text-slate-400 dark:text-slate-500 font-medium"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_name}}",
                "size": "sm",
                "weight": "medium",
                "className": "text-slate-800 dark:text-slate-200"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Description",
                "size": "xs",
                "className": "text-slate-400 dark:text-slate-500 font-medium"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_description}}",
                "size": "sm",
                "weight": "medium",
                "className": "text-slate-800 dark:text-slate-200"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Org Email",
                "size": "xs",
                "className": "text-slate-400 dark:text-slate-500 font-medium"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_email}}",
                "size": "sm",
                "weight": "medium",
                "className": "text-slate-850 dark:text-slate-200"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Org Phone",
                "size": "xs",
                "className": "text-slate-400 dark:text-slate-500 font-medium"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_phone}}",
                "size": "sm",
                "weight": "medium",
                "className": "text-slate-850 dark:text-slate-200"
              }
            }
          ]
        }
      ]
    }
  ]
}
```
