prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

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
5. AFTER clicking submit:
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
       signal: Either "form_submitted" or "submit_not_found"
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
