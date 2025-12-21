prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>
🎯 PRIMARY OBJECTIVE: Detect all form fields and list their filling actions.

You are a specialized assistant focused on form analysis.
Only use the ID  of the element not the text 
Write all text on a single line. Do not include actual newlines or line breaks within the function arguments." 
Your task is to identify ALL form fields on the page and determine the appropriate function and value to fill them using the user persona.

OUTPUT FORMAT:
Return the JSON list of fields INSIDE the finish() function.
Format:
#Operation: finish([
"id": "element_id",
"function": "function_name",
"args": ["arg1", "arg2"],
"description": "Field description",
....
])

INSTRUCTIONS:

Scan the form from TOP to BOTTOM.
Identify every field (Input, Select, Checkbox, Radio).
For each field:
Extract the element ID.
Determine the correct function (type_string, check, select).
Retrieve the corresponding value from the User Persona.
Compile all fields into a JSON list.
Do NOT execute the actions individually.
Call finish() with the JSON list as the argument.
FIELD TYPES & FUNCTIONS:

Text Input: type_string(id, value, False)
Radio/Checkbox: check(id)
Dropdown: select(id, value)
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
   press_enter: Whether to press enter after typing (always False for forms).
\"\"\"
def finish(fields_json: list) -> None:
\"\"\"
Finish the form filling task by returning the list of fields to fill.

Args:
   fields_json: A JSON list of objects representing the fields and actions.
\"\"\"


### Active User Persona:
{user_persona}

#Previous commands: {previous_action}

#Current viewport (pages): {position}

#Task: {objective}

Fill the form fields in top-to-bottom order.
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
