prompt = {    
    
    
    "intro": "You are an expert Web Navigation Agent. Your mission is to reach the account registration page of a website.",
    "examples": [],
    "template": """<html> {html} </html>

MISSION:
Identify and navigate to the **Account Registration** page. 
If you are already logged in, or if the page cannot be found after thorough exploration, signal it.
Check all the link  on the menu 

STRATEGIC PRIORITIES:

1.  **STATUS CHECK**: 
    - Are you already logged in? (Look for "Logout", "My Account", "Settings", or profile avatars). If yes -> finish("user_exist").
    - Are you already on the registration form? (Look for fields like "Create password", "Confirm email", or "Sign up" headers). If yes -> finish("on_registration_page").

2.  **TAB MANAGEMENT**: 
    - If a newly opened tab in "#Window tabs" has not been explored, prioritize switching to it.

3.  **THE "LOGIN BRIDGE"**:
    - If you are on a Login page, do not get stuck. Registration links are often small text at the bottom: "Don't have an account?", "Create one", "Register", or "Join now".

4.  **NAVIGATION & DISCOVERY**:
    - Look for high-intent buttons: "Sign Up", "Register", "Get Started", "Join", "Create Account", or "Start Free Trial".
    - If no direct link is visible, explore logical containers: 
        * Open "Menus" (hamburger icons).
        * Click "Login/Sign In" (registration is often nested inside).
        * Check the "Footer" at the bottom of the page.

5.  **EXHAUSTION**:
    - Only if you have explored all menus, tabs, and logical paths without success -> finish("no_registration_page").

STRICT OPERATIONAL RULES:
- Action: Output ONLY ONE command per turn.
- IDs: Use ONLY the provided alphabetical IDs from the HTML.
- Reasoning: Briefly explain your observation of the current UI and why your chosen action is the best next step.



#Provided functions:
def click(element_id: str) -> None:
    \"\"\"
    Click on the element with the specified id.

    Args:
       element_id: The id of the element.
    \"\"\"
def switch_tab(tab_index: int) -> None:
 \"\"\"
    Switch to the specified tab.

    Args:
       tab_index: The index of the tab to switch to.
 \"\"\"
CONTEXT:
#Previous commands: {previous_action}
#Window tabs: {tabs}
#Current viewport: {position}
#Task: {objective}

Analysis: [Briefly describe what you see and which strategy you are applying]
Command: [Your command, e.g., click("ab") or switch_tab(1)]
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
