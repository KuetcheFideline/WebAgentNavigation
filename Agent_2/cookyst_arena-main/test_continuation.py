import re
import json5

def Continuation(target):
    target = target.strip()
    signal_patterns = [
        r"finish\(\s*['\"]on_login_page['\"]\s*\)",
        r"finish\(\s*['\"]login_not_found['\"]\s*\)",
        r"finish\(\s*['\"]on_registration_page['\"]\s*\)",
        r"finish\(\s*['\"]registration_not_found['\"]\s*\)",
        r"finish\(\s*['\"]google_login['\"]\s*\)",
        r"finish\(\s*['\"]login_classic['\"]\s*\)",
        r"finish\(\s*['\"]no_login_method['\"]\s*\)",
        r"finish\(\s*['\"]connexion['\"]\s*\)",
        r"finish\(\s*['\"]account_selection['\"]\s*\)",
        r"finish\(\s*['\"]google_login_error['\"]\s*\)",
        r"finish\(\s*['\"]missing_data['\"]\s*\)",
        r"finish\(\s*['\"]form_to_fill['\"]\s*\)",
        r"finish\(\s*['\"]form_filled['\"]\s*\)",
        r"finish\(\s*['\"]form_okay['\"]\s*\)",
        r"finish\(\s*['\"]field_to_complete\[[^\]]+\]['\"]\s*\)",
        r"finish\(\s*['\"]form_submitted['\"]\s*\)",
        r"finish\(\s*['\"]submit_not_found['\"]\s*\)",
        r"finish\(\s*['\"]no_verification_needed['\"]\s*\)",
        r"finish\(\s*['\"]verification_complete['\"]\s*\)",
        r"finish\(\s*['\"]already_verified['\"]\s*\)",
        r"finish\(\s*['\"]login_success['\"]\s*\)",
        r"finish\(\s*['\"]login_failed['\"]\s*\)",
        r"finish\(\s*['\"]verification_pending['\"]\s*\)",
        r"finish\(\s*['\"]user_exist['\"]\s*\)",
        r"finish\(\s*['\"]google_login_success['\"]\s*\)",
        r"finish\(\s*['\"]google['\"]\s*\)",
    ]
    
    equivalence = [
        "on_login_page",
        "login_not_found",
        "on_registration_page",
        "registration_not_found",
        "google",
        "classic",
        "noLoginMethod",
        "connexion",
        "googleSelection",
        "googleError",
        "form_filled",
        "form_to_fill",
        "missingData",
        "formOkay",
        "fieldToComplete",
        "form_submitted",
        "submitNotFound",
        "noVerificationNeeded",
        "verificationComplete",
        "alreadyVerified",
        "loginSuccess",
        "loginFailed",
        "verificationPending",
        "user_exist",
        "googleSelection",
        "google",
    ]
    
    for regex, act in zip(signal_patterns, equivalence):
        match = re.search(regex, target)
        if match:
            return act
    return None

# Test cases
test_targets = [
    '#Operation: finish("google")',
    "finish('google')",
    'finish("login_success")',
    'finish("form_submitted")'
]

for t in test_targets:
    print(f"Target: {t} -> Signal: {Continuation(t)}")
