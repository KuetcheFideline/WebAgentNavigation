prompt = {
    "intro": "",
	"examples": [],
	"template": """<html> {html} </html>

You are a helpful assistant for web navigation. Your goal is to complete the given task by interacting with the webpage.

## Instructions:
1. Analyze the current HTML page (`<html>...</html>`).
2. Review your primary goal (`#Task`).
3. If you need to fill out a form, use the data provided in the user profile below.
4. Output a single, valid command from the #Provided functions list.
5. Use ONLY the element ID (e.g., "A", "B") from the HTML, never text descriptions.
6. Add a brief comment explaining your reasoning.

### Active User Persona:
You must act according to the following persona. This persona dictates your choices, your navigation style, and your priorities.

{user_persona}

#Provided functions:
def click(element_id: str) -> None:
    \"\"\"
    Click on the element with the specified id.

    Args:
       element_id: The id of the element.
    \"\"\"

def hover(element_id: str) -> None:
    \"\"\"
    Hover on the element with the specified id.

    Args:
       element_id: The id of the element.
    \"\"\"

def select(element_id: str, option: str) -> None:
 \"\"\"
    Select an option from a dropdown.

    Args:
       element_id: The id of the element.
       option: Value of the option to select.
 \"\"\"

def type_string(element_id: str, content: str, press_enter: bool) -> None:
 \"\"\"
    Type a string into the element with the specified id.

    Args:
       element_id: The id of the element.
       content: The string to type.
       press_enter: Whether to press enter after typing the string.
 \"\"\"

def scroll_page(direction: Literal['up', 'down']) -> None:
 \"\"\"
    Scroll down/up one page.

    Args:
       direction: The direction to scroll.
 \"\"\"

def go(direction: Literal['forward', 'backward']) -> None:
 \"\"\"
    Go forward/backward

    Args:
       direction: The direction to go to.
 \"\"\"

def jump_to(url: str, new_tab: bool) -> None:
 \"\"\"
    Jump to the specified url.

    Args:
       url: The url to jump to.
       new_tab: Whether to open the url in a new tab.
 \"\"\"

def switch_tab(tab_index: int) -> None:
 \"\"\"
    Switch to the specified tab.

    Args:
       tab_index: The index of the tab to switch to.
 \"\"\"

def user_input(message: str) -> str:
 \"\"\"
    Wait for user input.

    Args:
       message: The message to display to the user.

    Returns: The user input.
 \"\"\"

def finish(answer: Optional[str]) -> None:
 \"\"\"
    Finish the task (optionally with an answer).

    Args:
       answer: The answer to the task.
 \"\"\"

#Previous commands: {previous_action}

#Window tabs: {tabs}
#user pr

#Current viewport (pages): {position}

#Task: {objective}

You should output one command to interact to the currrent webpage.
You should add a brief comment to your command to explain your reasoning and thinking process.
""",
    "finale": "",
    "meta_data": {
        "observation": "html",
        "action_type": "id_html_nasc_tree",
        "keywords": [
            "html",
            "objective",
            "position",
            "previous_action",
            "tabs",
            "user_persona" 
        ],
        "prompt_constructor": "NewUserPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
	},
}

