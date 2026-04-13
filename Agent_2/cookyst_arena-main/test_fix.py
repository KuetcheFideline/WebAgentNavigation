
import logging
import json

# Mocking the necessary parts for testing
class MockAgent:
    class MockPromptConstructor:
        def extract_action(self, action_call):
            return action_call
    def __init__(self):
        self.prompt_constructor = self.MockPromptConstructor()

class MockEnv:
    def step(self, action_obj, get_obs=False):
        print(f"Executing step with action: {action_obj}")
        return None, None, False, False, {}

def create_id_based_action(parsed_action, url, user):
    return {"action": parsed_action, "url": url, "user": user}

# The function to test
def execute_json_form(actions_list, url, user, agent, env):
    print("Starting JSON form filling...")
    for action_item in actions_list:
        try:
            func_name = action_item.get("function")
            label = action_item.get("id")
            args = action_item.get("args", [])
            
            action_call = ""
            if func_name == "type_string":
                # The fix: use args[0]
                content = args[0] if len(args) > 0 else ""
                action_call = f'type_string("{label}", "{content}", True)'
            elif func_name == "select":
                # The fix: use args[0]
                val = args[0] if len(args) > 0 else ""
                action_call = f'select("{label}", "{val}")'
            elif func_name == "check":
                action_call = f'check("{label}")'
            elif func_name == "click":
                action_call = f'click("{label}")'
            
            if action_call:
                print(f"Action call generated: {action_call}")
                parsed_action = agent.prompt_constructor.extract_action(action_call)
                action_obj = create_id_based_action(parsed_action, url, user)
                env.step(action_obj, get_obs=False)
        except Exception as e:
            print(f"Error: {e}")

# Test case
actions = [
    {"id": "N", "function": "type_string", "args": ["ChrisMartin", False], "description": "Nom d'utilisateur"},
    {"id": "X", "function": "select", "args": ["Monsieur"], "description": "Civilité (Monsieur)"}
]

agent = MockAgent()
env = MockEnv()
execute_json_form(actions, "http://example.com", "user1", agent, env)
