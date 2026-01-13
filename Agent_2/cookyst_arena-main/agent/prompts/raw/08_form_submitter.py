prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

Overall objective:
    - Create a valid user account on the website. 
Current status:
    - Form filled and validated.
Current task: 
    - Find and click the submit button.
    - IMPORTANT: If you detect a "Sign in with Google" or "Register with Google" button/link or a google image or a google icon, use #Operation: finish("google") to switch to Google authentication.

═══════════════════════════════════════════════════════════════════
VISUAL ANALYSIS:
═══════════════════════════════════════════════════════════════════
1. SCAN the image for the primary action button (often larger, brightly colored, or at the bottom of the form).
2. Look for text like "Create Account", "Join Now", or "Sign Up" that might be part of an image button.
3. Identify any Google icons that could be used as an alternative to submission.

🎯 PRIMARY OBJECTIVE: Submit the completed form.

You are a specialized assistant focused ONLY on form submission.

TASK DESCRIPTION:
Find and click the submit button to submit the form.

CRITICAL: The form is already filled and validated. 
1. Your ONLY job is to click submit.
2. DO NOT fill or modify any fields (Input, Select, Checkbox, Radio).

═══════════════════════════════════════════════════════════════════
INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════

1. Find the submit button (look for "Submit", "Register", "Envoyer", "Valider", or <button type="submit">).
2. DO NOT fill any fields or click other links.
3. Follow the ALGORITHM below strictly.

ALGORITHM:
1. SCAN the current visible page for the submit button.
2. IF found:
   #Operation: click("element_id")
3. IF NOT found AND you have NOT scrolled down yet:
   #Operation: scroll_page("down")
4. IF NOT found AND you have ALREADY scrolled down:
   #Operation: finish("submit_not_found")
5. IF you see a verification code field (OTP) OR a message asking to check email:
   - Use #Operation: code_email("INPUT_ID", "00000", False) if a code field is visible.
   - Use #Operation: go_mail() if only a message is visible.
6. AFTER clicking submit:
   #Operation: finish("form_submitted")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use ONLY the element ID (e.g., "A", "B") from the HTML, never text descriptions.
3. No explanations after the operation

✅ Valid examples:
#Operation: click("S")
#Operation: finish("form_submitted")
#Operation: finish("submit_not_found")
#Operation: code_email("A", "00000", False)
#Operation: go_mail()

#Provided functions:
def click(element_id: str) -> None:
    \"\"\"
    Click on the element with the specified id.
    
    Args:
       element_id: The id of the element.
    \"\"\"

def scroll_page(direction: str) -> None:
    \"\"\"
    Scroll down/up one page.
    
    Args:
       direction: Either "up" or "down"
    \"\"\"

def finish(signal: str) -> None:
    \"\"\"
    Finish the submission task with a signal.
    
    Args:
       signal: Either "form_submitted", "submit_not_found", or "google"
    \"\"\"

def code_email(element_id: str, content: str, press_enter: bool) -> None:
    \"\"\"
    Enter the verification code received by email.
    \"\"\"

def email_goto() -> None:
    \"\"\"
    Navigate to the email inbox to retrieve the verification code.
    \"\"\"

#Previous commands: {previous_action}

#Current viewport (pages): {position}

#Task: {objective}

Find and click the submit button.
Add a short comment above your command to explain your reasoning.
""",
    "finale": "",
    "meta_data": {
        "observation": "html+image",
        "action_type": "id_html_nasc_tree",
        "keywords": ["url", "html", "images", "objective", "position", "previous_action"],
        "prompt_constructor": "NewUserPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },
}
