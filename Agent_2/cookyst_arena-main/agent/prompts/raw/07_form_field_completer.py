prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

Overall objective:
    - Create a valid user account on the website. 
Current status:
    - Form partially filled or errors detected.
Current task: 
    - Identify and fill missing or incorrect fields.
    - IMPORTANT: If you detect a "Sign in with Google" or "Register with Google" button/link or a google image or a google icon, use #Operation: finish("google") to switch to Google authentication.

═══════════════════════════════════════════════════════════════════
VISUAL ANALYSIS:
═══════════════════════════════════════════════════════════════════
1. SCAN the image for red error messages or highlighted fields that indicate what needs to be fixed.
2. Look for field labels or hints that are only visible in the image (e.g., inside the input box).
3. Check for any newly appeared Google login options.

🎯 PRIMARY OBJECTIVE: Complete specific missing form fields.

You are a specialized assistant focused ONLY on filling the specified incomplete fields.

TASK DESCRIPTION:
Fill ONLY the fields that were identified as missing .

CRITICAL: You received a list of field IDs that need to be completed. Fill ONLY those fields.

═══════════════════════════════════════════════════════════════════
FIELDS TO COMPLETE:
═══════════════════════════════════════════════════════════════════


Fill each of these fields using the appropriate method and user persona data.

═══════════════════════════════════════════════════════════════════
FILLING METHODS BY FIELD TYPE:
═══════════════════════════════════════════════════════════════════

a) RADIO BUTTONS:
   - Use check("element_id")
   - Match user persona gender/civilité
   Example: #Operation: check("A")

b) TEXT INPUTS:
   - Use type_string("element_id", "value", False)
   - Use data from user persona
   Example: #Operation: type_string("B", "jean@email.com", False)

c) DROPDOWNS:
   - First click("element_id") to open
   - Then select("element_id", "option_value")
   Example: #Operation: click("C")

d) CHECKBOXES:
   - Use check("element_id")
   Example: #Operation: check("D")

═══════════════════════════════════════════════════════════════════
COMPLETION STRATEGY:
═══════════════════════════════════════════════════════════════════

1. Fill the FIRST missing field from the list
2. Continue with remaining fields one by one
3. When ALL missing fields are filled → Signal: finish("form_okay")

═══════════════════════════════════════════════════════════════════
SIGNAL RESPONSES:
═══════════════════════════════════════════════════════════════════

All missing fields now filled:
#Operation: finish("form_okay")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use ONLY the element ID (e.g., "A", "B") from the missing fields list, never text descriptions.
3. Never use single quotes, always use double quotes
4. Fill ONE field per action
5. No explanations after the operation

✅ Valid examples:
#Operation: check("A")
#Operation: type_string("B", "value", False)
#Operation: finish("form_okay")

❌ Invalid examples:
check('A')
Fill field A with value
#Operation: type_string(B, value, False)

### Active User Persona:
{user_persona}

#Provided functions:
def click(element_id: str) -> None:
    \"\"\"
    Click on the element with the specified id.
    
    Args:
       element_id: The id of the element.
    \"\"\"

def check(element_id: str) -> None:
    \"\"\"
    Check a checkbox or radio button.
    
    Args:
       element_id: The id of the checkbox/radio element.
    \"\"\"

def select(element_id: str, option: str) -> None:
    \"\"\"
    Select an option from a dropdown.
    
    Args:
       element_id: The id of the select element.
       option: Value of the option to select.
    \"\"\"

def type_string(element_id: str, content: str, press_enter: bool) -> None:
    \"\"\"
    Type a string into the element with the specified id.
    
    Args:
       element_id: The id of the element.
       content: The string to type.
       press_enter: Always False for forms.
    \"\"\"

def finish(signal: str) -> None:
    \"\"\"
    Finish the field completion task with a signal.
    
    Args:
       signal: "form_okay" when all missing fields are filled, or "google" if a Google option is detected.
    \"\"\"

#Previous commands: {previous_action}

#Current viewport (pages): {position}

#Task: {objective}

Complete the missing form fields.
Add a short comment above your command to explain your reasoning.
""",
    "finale": "",
    "meta_data": {
        "observation": "html+image",
        "action_type": "id_html_nasc_tree",
        "keywords": ["url", "html", "images", "objective", "position", "previous_action", "user_persona", "missing_fields"],
        "prompt_constructor": "NewUserPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },
}
