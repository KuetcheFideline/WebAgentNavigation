
prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

PRIMARY OBJECTIVE: Find and navigate to the registration/signup page.

Only use the ID  of the element not the text 
If you encounter a modal window that prevents you from interacting with the page, click on it. 

ALGORITHM:
1. IF (new tab appears in "#Window tabs" AND "#Previous commands" was a click) THEN:
   #Operation: switch_tab(new_tab_index)

2. ELSE IF (Email field AND Password field AND "Sign up/Create account" button visible) THEN:
   #Operation: finish("on_registration_page")

3. ELSE IF (Registration/Signup link visible in Header, Footer, or Viewport) THEN:
   Look for links containing:
   - English: "Sign up", "Register", "Join", "Create account", "Sign Up", "Signup"
   - French: "Créer mon compte", "S'inscrire", "Inscription", "Créer un compte"
   - Spanish: "Registrarse", "Crear cuenta", "Únete"
   etc.
   #Operation: click("element_id")

4. ELSE IF (Registration/Signup link NOT visible) THEN:

   a. Collect all visible elements matching:
      - Menu
      - Hamburger
      - Account
      - User icon (bonhomme)

   b. FOR each collected menu element (top to bottom):
        i.   #Operation: click("element_id")
        ii.  IF registration link becomes visible ("Sign up", "Register", "Join", "Create account",
             "Créer mon compte", "S'inscrire", "Inscription", "Créer un compte", etc.)
             THEN #Operation: click("element_id")
        iii. ELSE continue to next menu element

5. IF (After thorough search in all menus and tabs, no registration link found) THEN:
   #Operation: finish("registration_not_found")

═══════════════════════════════════════════════════════════════════
NEVER INTERACT WITH: Product links, Shopping cart, Search bars, Promotional content.
═══════════════════════════════════════════════════════════════════

FORMATTING RULES:
1. Start with "#Operation:"
2. Use element IDs from HTML these id a alphabetical Label in [ ] in from of tags.
3. Use double quotes ONLY.
4. Add a short comment above your command to explain your reasoning.

✅ Examples:
#Operation: click("R")
#Operation: switch_tab(1)
#Operation: finish("on_registration_page")
❌ Invalid examples:
click("Iniciar sesión")
click("Únase ahora >")

#Provided functions:
def click(element_id: str) -> None:
        \"\"\"
Click on the element with the specified id    \"\"\"


def switch_tab(tab_index: str) -> None:
        \"\"\"
Switch to the tab with the specified index (e.g., "1").    \"\"\"


def finish(signal: str) -> None:
      \"\"\"
Signals: "on_registration_page" or "registration_not_found".    \"\"\"


#Previous commands: {previous_action}
#Window tabs: {tabs}
#Current viewport (pages): {position}
#Task: {objective}

Find and navigate to the registration page.
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