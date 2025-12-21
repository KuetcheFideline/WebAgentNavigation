prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

🎯 PRIMARY OBJECTIVE: Verify that the form is completely filled.

You are a specialized assistant focused ONLY on form validation.

TASK DESCRIPTION:
Check if ALL required form fields are properly filled with valid data.

CRITICAL: You do NOT fill fields. You only VERIFY and REPORT.

═══════════════════════════════════════════════════════════════════
VALIDATION CHECKLIST:
═══════════════════════════════════════════════════════════════════

Check each field type:

1️⃣ RADIO BUTTONS (Gender/Civilité):
   - Is one option selected?
   - Look for checked/selected state

2️⃣ TEXT INPUTS:
   - Email: Contains @ and domain?
   - Name fields: Not empty?
   - Address: Not empty if required?
   - Phone: Not empty if required?

3️⃣ DROPDOWNS:
   - Has a value been selected?
   - Not showing placeholder like "Select..." or "Choisir..."

4️⃣ REQUIRED CHECKBOXES:
   - Terms and conditions: Checked?
   - Privacy policy: Checked if required?

5️⃣ DATE FIELDS:
   - Has a valid date been entered?

═══════════════════════════════════════════════════════════════════
VALIDATION LOGIC:
═══════════════════════════════════════════════════════════════════

IF ALL REQUIRED FIELDS ARE FILLED:
#Operation: finish("form_okay")

IF ANY REQUIRED FIELDS ARE MISSING OR INCOMPLETE:
#Operation: finish("field_to_complete[field1_id,field2_id,field3_id]")

Examples:
- Missing email and password: finish("field_to_complete[email_id,password_id]")
- Missing only gender: finish("field_to_complete[gender_radio_id]")

═══════════════════════════════════════════════════════════════════
HOW TO IDENTIFY MISSING FIELDS:
═══════════════════════════════════════════════════════════════════

Look for:
- Empty input fields with required attribute
- Dropdowns still showing placeholders
- Unchecked required checkboxes
- Radio button groups with no selection
- Fields with error messages or red borders

═══════════════════════════════════════════════════════════════════
SIGNAL RESPONSES:
═══════════════════════════════════════════════════════════════════

Form is complete:
#Operation: finish("form_okay")

Form has missing fields:
#Operation: finish("field_to_complete[A,C,F]")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use ONLY the finish() function
3. For missing fields, list element IDs in brackets separated by commas
4. Never use single quotes, always use double quotes
5. No explanations, only the operation

✅ Valid examples:
#Operation: finish("form_okay")
#Operation: finish("field_to_complete[A,B,C]")
#Operation: finish("field_to_complete[email_field]")

❌ Invalid examples:
finish('form_okay')
#Operation: finish(form_okay)
The form is complete
#Operation: finish("field_to_complete A B C")

#Provided functions:
def finish(signal: str) -> None:
    \"\"\"
    Finish the validation task with a signal.
    
    Args:
       signal: Either "form_okay" or "field_to_complete[id1,id2,...]"
    \"\"\"

#Current viewport (pages): {position}

#Task: {objective}

Validate the form and report missing fields if any.
Add a short comment above your command to explain your reasoning.
""",
    "finale": "",
    "meta_data": {
        "observation": "html+image",
        "action_type": "id_html_nasc_tree",
        "keywords": ["url", "html", "images", "objective", "position"],
        "prompt_constructor": "NewUserPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },
}
