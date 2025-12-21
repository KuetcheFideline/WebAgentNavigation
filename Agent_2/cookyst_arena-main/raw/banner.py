prompt = {
    "intro": "You are an AI assistant that specializes in web navigation tasks.",
    "examples": [],
    "template": """
<html> {html} </html>
1. Detect if the webpage contains a cookie consent banner.
   - A cookie consent banner is a visible notification that asks the user to accept or manage cookies.
   - It usually contains buttons or links with texts like "Accept all", "Reject all", "Accept essential", "Manage preferences", "Privacy settings", etc.

2. If the banner is present, you must identify and construct two distinct navigation paths, each corresponding to a specific user choice:
   - accept_all: the sequence of element IDs to click to accept all cookies.
   - configuration: to set up the other two paths 
3. If the banner is not present, indicate that no cookie consent banner was detected.

Your response must be a JSON object with the following structure:

{{
  "banner_present": "yes" or "no",
  "click_paths": {{
    "accept_all": click('element_id'),
    "configuration": click('element_id')
  }}
}}

If "banner_present" is "no", "click_paths" should be an empty object.

Example output when banner is present:
{{
  "banner_present": "yes",
  "click_paths": {{
    "accept_all":click('element_id'),
     "configuration":click('element_id')
  }}
}}

Example output when banner is absent:
{{
  "banner_present": "no",
  "click_paths": {{}}
}}
""",
    "finale": "Please provide a valid JSON response following the described structure.",
    "meta_data": {
        "observation": "html",
        "action_type": "detect_and_build_paths",
        "keywords": ["cookie consent", "banner", "accept", "reject", "essential"],
        "action_splitter": "#"
    }
}
