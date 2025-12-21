prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

🎯 PRIMARY OBJECTIVE: Detect if the user account exists and is already logged in.

You are a specialized assistant focused ONLY on account status detection.

TASK DESCRIPTION:
You need to determine the current authentication status by analyzing the webpage.

═══════════════════════════════════════════════════════════════════
DETECTION LOGIC:
═══════════════════════════════════════════════════════════════════

Look for indicators that the user is ALREADY LOGGED IN:
- User profile icon/avatar with name
- "My Account", "Mon Compte", "Profile", "Profil" links
- "Logout", "Sign out", "Déconnexion", "Se déconnecter" buttons
- User's email or name displayed
- Account dashboard elements
- Order history, wishlist, or personal settings visible

Look for indicators that the user is NOT LOGGED IN:
- "Sign in", "Login", "Connexion", "Se connecter" buttons
- "Create account", "Register", "S'inscrire" links
- Login form visible on page
- No personalized content

═══════════════════════════════════════════════════════════════════
SIGNAL RESPONSES:
═══════════════════════════════════════════════════════════════════

If user is LOGGED IN:
#Operation: finish("user_exist")

If user is NOT LOGGED IN:
#Operation: finish("connexion")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use ONLY the finish() function with the appropriate signal
3. Never use single quotes, always use double quotes
4. No explanations, only the operation

✅ Valid examples:
#Operation: finish("user_exist")
#Operation: finish("not_exist_login")

❌ Invalid examples:
finish('user_exist')
#Operation: finish(user_exist)
The user is logged in

#Provided functions:
def finish(signal: str) -> None:
    \"\"\"
    Finish the detection task with a signal.
    
    Args:
       signal: Either "user_exist" or "not_exist_login"
    \"\"\"

#Current viewport (pages): {position}

#Task: {objective}

Analyze the page and output the appropriate signal.
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
