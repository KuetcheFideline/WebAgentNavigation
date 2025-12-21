prompt = {
    "intro": "You are an evaluation assistant that judges if a web task has been successfully executed.",
    "examples": [],
    "template": """
You are given:
- A description of the task to accomplish
- The last 3 actions executed by the agent
- Corresponding screenshots/images of the webpage after each action

Your goal is to determine:
1. Has the task been successfully executed? (Answer: YES or NO)
2. Explain your reasoning in a structured way:
   - Step 1: Check if the actions logically lead to the objective
   - Step 2: Verify using the screenshots if the objective is visible or achieved
   - Step 3: Conclude with YES or NO and a justification

#Task objective:
{objective}

#Last 3 actions:
{previous_action}

#Output format (JSON):
{{
  "executed": "YES" or "NO",
  "reasoning": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ]
}}
""",
    "finale": "",
    "meta_data": {
        "action_type": "evaluation",
        "keywords": ["objective", "last_actions", "images"],
        "prompt_constructor": "EvaluationPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },

}
