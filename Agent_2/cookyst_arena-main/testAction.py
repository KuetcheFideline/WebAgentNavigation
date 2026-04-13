import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from agent.prompts.prompt_constructor import NewASPromptConstructor
from browser_env.actions import create_id_based_action

# Mock LMConfig and Tokenizer
class MockLMConfig:
    def __init__(self):
        self.provider = "openai"
        self.mode = "chat"
        self.gen_config = {"max_obs_length": 1000}

class MockTokenizer:
    def encode(self, text):
        return text
    def decode(self, tokens):
        return tokens

def test_switch_tab():
    print("Testing switch_tab parsing...")
    
    # Paths to required JSONs
    instruction_path = "agent/prompts/jsons/new_action_prompt.json"
    orm_path = "agent/prompts/jsons/orm_prompt.json"
    banner_path = "agent/prompts/jsons/banner.json"
    
    # Initialize Prompt Constructor
    lm_config = MockLMConfig()
    tokenizer = MockTokenizer()
    
    try:
        prompt_constructor = NewASPromptConstructor(
            instruction_path=instruction_path,
            lm_config=lm_config,
            tokenizer=tokenizer,
            orm_path=orm_path,
            banner_path=banner_path
        )
        
        # Test Input
        llm_response = "#Thinking Process: I need to switch to the second tab.\n#Operation: switch_tab(2)"
        print(f"LLM Response: {llm_response}")
        
        # Extract Action
        extracted_action = prompt_constructor.extract_action(llm_response)
        print(f"Extracted Action String: '{extracted_action}'")
        
        # Verify Extraction
        # Expecting "page_focus [2]" or "switch_tab [2]" depending on translation
        # Based on code: translate for switch_tab is "page_focus"
        if "page_focus [2]" in extracted_action:
            print("SUCCESS: Extraction correct.")
        else:
            print(f"FAILURE: Extraction incorrect. Expected 'page_focus [2]', got '{extracted_action}'")
            
        # Create Action Object
        action_obj = create_id_based_action(extracted_action, url="https://elpais.com/subscriptions", user="test_user")
        print(f"Created Action Object: {action_obj}")
        
        # Verify Action Object
        if action_obj['action_type'].name == 'PAGE_FOCUS' and action_obj['page_number'] == 2:
             print("SUCCESS: Action object creation correct.")
        else:
             print("FAILURE: Action object creation incorrect.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_switch_tab()
