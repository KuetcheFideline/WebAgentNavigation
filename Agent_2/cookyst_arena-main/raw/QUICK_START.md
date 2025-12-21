# Quick Start Guide - Multi-Level Authentication System

## 📁 Files Created

### ✅ 11 Specialized Prompts
Located in: `agent/prompts/raw/`

| # | File | Purpose | Key Signals |
|---|------|---------|-------------|
| 01 | `01_account_status_detector.py` | Check if logged in | `user_exist`, `not_exist_login` |
| 02 | `02_account_page_navigator.py` | Go to login page | `on_login_page`, `login_not_found` |
| 03 | `03_login_method_detector.py` | Detect Google/Classic | `google_login`, `login_classic` |
| 04 | `04_google_login_executor.py` | Google OAuth flow | `google_login_success` |
| 05 | `05_form_filler_generic.py` | Fill all fields | `form_filled` |
| 06 | `06_form_validator.py` | Check completion | `form_okay`, `field_to_complete[...]` |
| 07 | `07_form_field_completer.py` | Fill missing fields | `form_okay` |
| 08 | `08_form_submitter.py` | Click submit | `form_submitted` |
| 09 | `09_verification_handler.py` | Email/code verify | `verification_complete` |
| 10 | `10_login_success_validator.py` | Confirm success | `login_success` |
| 11 | `11_registration_page_detector.py` | Find signup page | `on_registration_page` |

### 📚 Documentation
- `SIGNALS_REFERENCE.md` - All signals and flow patterns

## 🚀 Quick Flow Examples

### Already Logged In (1 step)
```
01 → user_exist → MAIN TASK ✓
```

### Google Login (4 steps)
```
01 → not_exist_login
02 → on_login_page
03 → google_login
04 → google_login_success
10 → login_success → MAIN TASK ✓
```

### Classic Login (6 steps)
```
01 → not_exist_login
02 → on_login_page
03 → login_classic
05 → form_filled
06 → form_okay
08 → form_submitted
09 → no_verification_needed
10 → login_success → MAIN TASK ✓
```

### Registration with Validation Loop (9 steps)
```
01 → not_exist_login
02 → login_not_found
11 → on_registration_page
03 → login_classic
05 → form_filled
06 → field_to_complete[A,B]
07 → form_okay
08 → form_submitted
09 → verification_complete
10 → login_success → MAIN TASK ✓
```

## 🎯 Key Benefits

| Before | After |
|--------|-------|
| 1 monolithic prompt (311 lines) | 11 specialized prompts (~100 lines each) |
| All actions available always | Only relevant actions per task |
| Complex context to maintain | Simple, focused context |
| Hard to debug | Easy to trace which step failed |
| Model confusion on edge cases | Clear decision points |



## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│  (Routes between prompts based on signals)                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   DETECTION   │   │  NAVIGATION   │   │ VALIDATION    │
│               │   │               │   │               │
│ 01: Status    │   │ 02: Login Pg  │   │ 06: Validator │
│ 03: Method    │   │ 11: Reg Page  │   │ 10: Success   │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │         EXECUTION LAYER               │
        │                                       │
        │  04: Google Login                    │
        │  05: Form Filler                     │
        │  07: Field Completer                 │
        │  08: Form Submitter                  │
        │  09: Verification Handler            │
        └───────────────────────────────────────┘
```

## 🎨 Design Principles

✅ **Single Responsibility** - One task per prompt  
✅ **Separation of Concerns** - Detection ≠ Execution ≠ Validation  
✅ **Explicit Signals** - Clear communication via signals  
✅ **Fail Fast** - Early error detection  
✅ **Reusability** - Shared prompts for login/registration  

