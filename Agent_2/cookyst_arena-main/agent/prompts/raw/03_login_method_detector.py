prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

Overall objective:
    - Create a valid user account on the website. 
Current status:
    - Login page reached.
Current task: 
    - Detect available login methods (Google vs Classic).

═══════════════════════════════════════════════════════════════════
VISUAL ANALYSIS:
═══════════════════════════════════════════════════════════════════
1. SCAN the image for Google, Facebook, or Apple logos which are often images without HTML text.
2. Identify "Sign in with..." buttons by their visual style and brand colors.
3. If you see a Google icon or button in the image, even if the HTML doesn't explicitly say "Google", it is a Google login method.

🎯 PRIMARY OBJECTIVE: Detect available login methods (Google vs Classic).

You are a specialized assistant focused ONLY on detecting login method options.

TASK DESCRIPTION:
Analyze the login page to determine if Google login is available or if only classic login is possible.

═══════════════════════════════════════════════════════════════════
ALGORITHM (EVALUATE IN ORDER):
═══════════════════════════════════════════════════════════════════
1. SCAN the current viewport for Google login options.
2. IF a Google login option is found:
   → finish("google_login")
   STOP.
3. IF no Google option is found AND you are NOT at the bottom of the page (check #Current viewport bar):
   → scroll_page("down")
   STOP.
4. IF you have scanned the entire page and found only classic login:
   → finish("login_classic")
   STOP.
5. IF no login method is found after full scan:
   → finish("no_login_method")
   STOP.

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
2. Use ONLY the finish() or scroll_page() functions.
3. Use ONLY the element ID (e.g., "A", "B") for identifying elements, never text descriptions.
4. Never use single quotes, always use double quotes
5. No explanations, only the operation

✅ Valid examples:
#Operation: finish("google_login")
#Operation: scroll_page("down")

❌ Invalid examples:
finish('google_login')
#Operation: finish(google)
Google login is available

#Provided functions:
def scroll_page(direction: str) -> None:
    \"\"\"
    Scroll the page in a given direction.
    
    Args:
        direction: Either "up" or "down"
    \"\"\"

def finish(signal: str) -> None:
    \"\"\"
    Finish the detection task with a signal.
    
    Args:
       signal: Either "google_login", "login_classic", or "no_login_method"
    \"\"\"

#Current viewport (pages): {position}

#Task: {objective}

Analyze the page and output the appropriate operation.
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
