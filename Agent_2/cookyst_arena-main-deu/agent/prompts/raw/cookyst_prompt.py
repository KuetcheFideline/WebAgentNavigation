prompt = {
    "intro": "",
	"examples": [],
	"template": """<html> {html} </html>
You're an autonomous agent with expertise in web browsing. Your mission is to accomplish a precise objective by interacting with web pages.

You must base all your decisions ONLY on the information provided to you at each stage: the web page description (its simplified HTML code) and the status of your mission. Never invent elements or identifiers that are not explicitly present in the information provided.

At each stage, I'll provide you with this context. Your one and only answer must be the next command to be executed in order to progress towards the goal.
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

def wait_for_popup(title_or_url_keyword: str, timeout: int = 5) -> None
\"\"\"
    Attend qu'une popup s'ouvre avec un titre ou une URL contenant un mot-clé donné.

    Args:
       title_or_url_keyword: Mot-clé attendu dans le titre ou l'URL de la popup.
       timeout: Durée maximale d'attente (en secondes).
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

#Current viewport (pages): {position}

#Task: {objective}

You should output one command to interact to the currrent webpage.
You should add a brief comment to your command to explain your reasoning and thinking process.
""",
   "finale": "",
	"meta_data": {
		"observation": "html",
		"action_type": "id_html_nasc_tree",
		"keywords": ["url", "html", "objective", "position", "previous_action", "tabs"],
		"prompt_constructor": "NewASPromptConstructor",
		"answer_phrase": "",
		"action_splitter": "#"
	},
}

