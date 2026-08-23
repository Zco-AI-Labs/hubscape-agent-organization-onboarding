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
        "placeholder": "Name"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "org_description",
        "label": "Brief Description",
        "placeholder": "Description",
        "multiline": true
      }
    },
    {
      "type": "input",
      "props": {
        "name": "org_website",
        "label": "Organization Website",
        "placeholder": "Website"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "user_position",
        "label": "Your Position/Title in Organization",
        "placeholder": "Position/Title"
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
*   **Theme Token Default:** `slate`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/org_summary_card.json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-5 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 shadow-md"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "text": "Organization Summary",
        "className": "text-slate-900 dark:text-slate-100 font-bold text-lg"
      }
    },
    {
      "type": "container",
      "props": {
        "className": "flex flex-col gap-4 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Legal Name",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_name}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Position / Title",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_position}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Description",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_description}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Website",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_website}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Full Name",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_contact_name}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Email",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_contact_email}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "flex flex-col gap-1 border-none dark:border-none bg-transparent dark:bg-transparent shadow-none p-0"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Phone",
                "className": "text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{summary_contact_phone}}",
                "className": "text-sm text-slate-800 dark:text-slate-200 font-normal"
              }
            }
          ]
        }
      ]
    }
  ]
}
```
