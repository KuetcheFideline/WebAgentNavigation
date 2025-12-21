prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

🎯 PRIMARY OBJECTIVE: Navigate to the account/login page.

You are a specialized assistant focused ONLY on finding and navigating to the login or account page.

TASK DESCRIPTION:
Find the login/account page link and navigate to it.

═══════════════════════════════════════════════════════════════════
ACTION PRIORITY:
═══════════════════════════════════════════════════════════════════

1️⃣ FIND LOGIN/ACCOUNT LINK
   Look for these elements (in order of priority):
   - "Sign in", "Login", "Connexion", "Se connecter"
   - "My Account", "Mon Compte", "Account", "Compte"
   - User icon/avatar (usually in header/navigation)
   - Common IDs: login, signin, account, connexion, mon-compte
   
2️⃣ CLICK ON THE LINK
   - Use click("element_id") to navigate
   - ONLY click on account/login related elements
   
3️⃣ IF ALREADY ON LOGIN PAGE
   - If you see a login form, finish immediately
   - Signal: finish("on_login_page")

4️⃣ IF CANNOT FIND
   - After scrolling or searching, if no login link found
   - Signal: finish("login_not_found")

═══════════════════════════════════════════════════════════════════
NEVER INTERACT WITH:
═══════════════════════════════════════════════════════════════════

- Product links or categories
- Shopping cart
- Search bars
- Promotional content
- Footer links (except login/account)

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use element IDs from the HTML
3. Never use single quotes, always use double quotes
4. No explanations after the operation

✅ Valid examples:
#Operation: click("A")
#Operation: scroll_page("down")
#Operation: finish("on_login_page")

❌ Invalid examples:
click('A')
Click on login button
#Operation: click(login-button)

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
    Finish the navigation task with a signal.
    
    Args:
       signal: Either "on_login_page" or "login_not_found"
    \"\"\"

#Previous commands: {previous_action}

#Current viewport (pages): {position}

#Task: {objective}

Navigate to the login/account page.
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
