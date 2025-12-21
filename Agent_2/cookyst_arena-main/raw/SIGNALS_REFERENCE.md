# Authentication System Signals Reference

## Signal Definitions

### Account Detection Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `user_exist` | 01_account_status_detector | User already logged in | Launch main task |
| `not_exist_login` | 01_account_status_detector | User needs to login | Navigate to login page |

### Navigation Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `on_login_page` | 02_account_page_navigator | Login page reached | Detect login method |
| `login_not_found` | 02_account_page_navigator | No login link found | Try registration page |
| `on_registration_page` | 11_registration_page_detector | Registration page reached | Detect login method |
| `registration_not_found` | 11_registration_page_detector | No registration link | Error handling |

### Login Method Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `google_login` | 03_login_method_detector | Google OAuth available | Execute Google login |
| `login_classic` | 03_login_method_detector | Classic form login | Fill login form |
| `no_login_method` | 03_login_method_detector | No login method found | Error handling |

### Google Login Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `google_login_success` | 04_google_login_executor | Google OAuth completed | Validate login success |
| `google_login_error` | 04_google_login_executor | Google OAuth failed | Error handling |

### Form Filling Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `form_filled` | 05_form_filler_generic | All fields filled | Validate form |
| `missing_data` | 05_form_filler_generic | Cannot fill (no data) | Error handling |
| `form_okay` | 06_form_validator | Form complete & valid | Submit form |
| `field_to_complete[ids]` | 06_form_validator | Missing fields detected | Complete missing fields |

### Form Submission Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `form_submitted` | 08_form_submitter | Form sent successfully | Handle verification |
| `submit_not_found` | 08_form_submitter | Submit button not found | Error handling |

### Verification Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `no_verification_needed` | 09_verification_handler | Direct login | Validate success |
| `verification_complete` | 09_verification_handler | Verification done | Validate success |
| `already_verified` | 09_verification_handler | Already verified | Validate success |

### Success Validation Signals
| Signal | Source | Meaning | Next Action |
|--------|--------|---------|-------------|
| `login_success` | 10_login_success_validator | Authentication successful | Launch main task |
| `login_failed` | 10_login_success_validator | Authentication failed | Error handling |
| `verification_pending` | 10_login_success_validator | Still waiting | Return to verification |

## Signal Flow Patterns

### Pattern 1: Quick Login (Already Logged In)
```
user_exist → MAIN_TASK
```

### Pattern 2: Google Login (Existing User)
```
not_exist_login → on_login_page → google_login → google_login_success → login_success → MAIN_TASK
```

### Pattern 3: Classic Login (Existing User)
```
not_exist_login → on_login_page → login_classic → form_filled → form_okay → form_submitted → no_verification_needed → login_success → MAIN_TASK
```

### Pattern 4: Registration with Form Validation Loop
```
not_exist_login → login_not_found → on_registration_page → login_classic → form_filled → field_to_complete[A,B] → form_okay → form_submitted → verification_complete → login_success → MAIN_TASK
```

## Implementation Guidelines

### Signal Format
All signals are returned using:
```python
finish("signal_name")
```

For signals with parameters:
```python
finish("field_to_complete[A,B,C]")
```

### Signal Parsing
The orchestration layer should:
1. Extract signal name from finish() call
2. Parse parameters if present (e.g., field IDs in brackets)
3. Route to appropriate next prompt based on signal
4. Pass context/parameters to next prompt

### Error Signals
Any signal ending in `_error`, `_failed`, or `_not_found` should trigger error handling:
- `google_login_error`
- `login_failed`
- `submit_not_found`
- `login_not_found`
- `registration_not_found`
- `no_login_method`
- `missing_data`
