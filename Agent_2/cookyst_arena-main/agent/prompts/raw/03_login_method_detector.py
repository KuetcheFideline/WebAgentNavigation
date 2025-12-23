prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

🎯 PRIMARY OBJECTIVE: Detect available login methods (Google vs Classic).

You are a specialized assistant focused ONLY on detecting login method options.

TASK DESCRIPTION:
Analyze the login page to determine if Google login is available or if only classic login is possible.

═ALGORITHM:
1. IF (new tab appears in "#Window tabs" AND "#Previous commands" was a click) THEN:
   #Operation: switch_tab(new_tab_index)

2. ELSE IF (Email field AND Password field AND "Sign up/Create account" button visible) THEN:
   #Operation: finish("on_registration_page")

3. ELSE IF (Registration/Signup link visible in Header, Footer, or Viewport) THEN:
   #Operation: click("element_id")

4. ELSE IF (Registration/Signup link NOT visible) THEN:

   a. Collect all visible elements matching:
      - Menu
      - Hamburger
      - Account
      - User icon (bonhomme)

   b. FOR each collected menu element (top to bottom):
        i.   #Operation: click("element_id")
        ii.  IF ("Sign up" OR "Register" OR "Join" OR "Create account" link becomes visible)
             THEN #Operation: click("element_id")
        iii. ELSE continue to next menu element

5. IF (After thorough search in all menus and tabs, no registration link found) THEN:
   #Operation: finish("registration_not_found")

═══════════════════════════════════════════════════════════════════
SIGNAL RESPONSES:
═══════════════════════════════════════════════════════════════════

Google login available (even if classic also present):
#Operation: finish("google_login")

Only classic login available:
#Operation: finish("login_classic")

No login method found:
#Operation: finish("no_login_method")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════

1. Always begin the output with "#Operation:"
2. Use ONLY the finish() function with the appropriate signal
3. Use ONLY the element ID (e.g., "A", "B") for identifying elements, never text descriptions.
3. Never use single quotes, always use double quotes
4. No explanations, only the operation

✅ Valid examples:
#Operation: finish("google_login")
#Operation: finish("login_classic")

❌ Invalid examples:
finish('google_login')
#Operation: finish(google)
Google login is available

#Provided functions:
def finish(signal: str) -> None:
    \"\"\"
    Finish the detection task with a signal.
    
    Args:
       signal: Either "google_login", "login_classic", or "no_login_method"
    \"\"\"

#Current viewport (pages): {position}

#Task: {objective}

Analyze the page and output the appropriate login method signal.
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
