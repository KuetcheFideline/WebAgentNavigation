prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

Overall objective:
    - Create a valid user account on the website. 
Current status:
    - Form submission failed with errors.
Current task: 
    - Fix form errors and fill missing required fields.
    - IMPORTANT: If you detect a button or link to "Sign in with Google" or "Register with Google" or a google image or a google icon, use #Operation: finish("google") instead of filling the form.

═══════════════════════════════════════════════════════════════════
VISUAL ANALYSIS:
═══════════════════════════════════════════════════════════════════
1. SCAN the image for red text or red borders around input fields indicating errors.
2. Look for specific error messages (e.g., "Email already taken", "Password too short") that are visible in the image.
3. Identify any newly visible Google login buttons.

🎯 PRIMARY OBJECTIVE: Fix form errors and fill missing required fields.


TASK DESCRIPTION:
1. Identify fields with ERROR MESSAGES (e.g., "Invalid email", "Required field", red borders).
2. Identify EMPTY REQUIRED fields that were missed.
3. Generate actions to CORRECT these specific fields using the User Persona.

⚠️ IMPORTANT:
- DO NOT re-fill fields that are already correct.
- ONLY target the problematic fields.
- Use the User Persona to get valid data.
- If you detect a "Sign in with Google" or "Register with Google" option, you can use #Operation: finish("google") to switch to Google authentication.

OUTPUT FORMAT:
Return the JSON list of correction actions INSIDE the finish() function.
Format:
#Operation: finish([
{{ "id": "element_id", "function": "type_string", "args": ["value"] }},
{{ "id": "element_id", "function": "check", "args": [] }}
])

FIELD TYPES & FUNCTIONS:
- Text Input: type_string(id, value, False)
- Radio/Checkbox: check(id)
- Dropdown: select(id, value)

#Provided functions:
def type_string(element_id: str, content: str, press_enter: bool) -> None:
    \"\"\"Type a string into the element.\"\"\"
def check(element_id: str) -> None:
    \"\"\"Check a checkbox or radio button.\"\"\"
def select(element_id: str, option: str) -> None:
    \"\"\"Select an option from a dropdown.\"\"\"
def finish(fields_json: list) -> None:
    \"\"\"Finish the correction task with the list of actions.\"\"\"

### Active User Persona:
{user_persona}

#Previous commands: {previous_action}

#Current viewport (pages): {position}

#Task: {objective}

Identify errors and missing fields. Correct them using the User Persona.
Add a short comment above your command to explain your reasoning.
""",
    "finale": "",
    "meta_data": {
        "observation": "html+image",
        "action_type": "id_html_nasc_tree",
        "keywords": ["url", "html", "images", "objective", "position", "previous_action", "user_persona"],
        "prompt_constructor": "NewUserPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },
}
