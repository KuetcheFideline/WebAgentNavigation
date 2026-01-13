prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>

Overall objective:
    - Create a valid user account on the website. 
Current status:
    - Form submitted or Google flow completed.
Current task: 
    - Confirm successful login or detect failure. 
    IMPORTANT: If you detect a button or link to "Sign in with Google" or "Register with Google" or a google image or a google icon, use #Operation: finish("google") instead of filling the form.


═══════════════════════════════════════════════════════════════════
VISUAL ANALYSIS:
═══════════════════════════════════════════════════════════════════
1. SCAN the image for "Welcome", "Hello [Name]", or a profile picture that indicates a successful login.
2. Look for error messages in red text (e.g., "Invalid password", "User already exists") that might not be in the HTML.
3. Check for the absence of the "Login" button and the presence of a "Logout" or "Account" link in the image.

🎯 PRIMARY OBJECTIVE: Confirm successful login, detect failure, or identify if more information is needed.

You are a specialized assistant focused ONLY on validating login status.

TASK DESCRIPTION:
Analyze the page to determine the current state of the login/registration process.

═══════════════════════════════════════════════════════════════════
STATE 1: SUCCESSFUL LOGIN
═══════════════════════════════════════════════════════════════════
Look for:
- User profile visible (Name, Email, Avatar)
- "My Account" / "Mon Compte"
- "Logout" / "Déconnexion" button
- Dashboard or Home page with personalized content
- Success messages ("Login successful", "Compte créé")

Action: #Operation: finish("login_success")

═══════════════════════════════════════════════════════════════════
STATE 2: LOGIN FAILED
═══════════════════════════════════════════════════════════════════
Look for:
- Error messages ("Invalid credentials", "Identifiants incorrects", "Login failed")
- "Email already exists" (if registering)
- Red warning banners
- Still on the exact same login page with no changes except errors

Action: #Operation: finish("login_failed")

═══════════════════════════════════════════════════════════════════
STATE 3: FORM TO FILL (INTERMEDIATE STEP)
═══════════════════════════════════════════════════════════════════
Look for:
- A new form appearing that requires input (e.g., OTP, 2FA, Profile completion)
- Empty input fields that need to be filled (Name, Address, Phone, etc.)
- "Complete your profile" / "Complétez votre profil"
- Any situation where the user is NOT logged in yet but needs to provide more data

Action: #Operation: finish("form_to_fill")

═══════════════════════════════════════════════════════════════════
FORMATTING RULES:
═══════════════════════════════════════════════════════════════════
1. Always begin the output with "#Operation:"
2. Use ONLY the finish() function with the appropriate signal
3. Use ONLY the element ID (e.g., "A", "B") for identifying elements, never text descriptions.
3. No explanations, only the operation

✅ Valid examples:
#Operation: finish("login_success")
#Operation: finish("login_failed")
#Operation: finish("form_to_fill")

#Provided functions:
def finish(signal: str) -> None:
    \"\"\"
    Finish the validation task with a signal.
    
    Args:
       signal: "login_success", "login_failed", or "form_to_fill"
    \"\"\"

#Current viewport (pages): {position}

#Task: {objective}

Determine the login state and return the appropriate signal.
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
