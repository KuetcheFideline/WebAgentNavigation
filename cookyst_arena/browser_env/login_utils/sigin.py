from langchain_ollama import OllamaLLM
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from ..html_tools.html_parser  import HtmlParser
from ..html_tools.configs.config import basic_attrs,mind2web_keep_attrs
from langchain_groq import ChatGroq
from groq import Groq
from llms.providers.cookyst import call_grop_llama

import requests



from langchain_ollama import OllamaLLM
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
import re 

def create_google_signin_prompt_template():
    examples = [
        {
            "html_input": '<header | ><nav | ><a | href="/login" data-testid="a" > Sign In </a><button | data-testid="b" > Register </button></nav></header>',
            "output": (
                "ACTION: click\n"
                "TAG: a\n"
                "LABEL: a\n"
                "TEXT: Sign In\n"
                "ATTRIBUTES:\n"
                "href: /login"
            )
        },
        {
            "html_input": '<div | ><p | > Welcome! </p><a | data-testid="c" class="button-primary" > Create an account </a></div>',
            "output": (
                "ACTION: click\n"
                "TAG: a\n"
                "LABEL: c\n"
                "TEXT: Create an account\n"
                "ATTRIBUTES:\n"
                "class: button-primary"
            )
        },
        {
            "html_input": '<body | ><main | ><p | > This page has no login buttons. </p></main></body>',
            "output": 'ACTION: negatif'
        }
    ]

    example_prompt = PromptTemplate(
        input_variables=["html_input", "output"],
        template="HTML:\n{html_input}\nRESPONSE:\n{output}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=(
           "You are an expert web automation assistant tasked with identifying the primary login or sign-up element in simplified HTML.\n"
            "Rules:\n"
            "1. Identify the main interactive element (e.g., <a>, <button>, <input>) for login or sign-up.\n"
            "2. Prioritize sign-up elements (e.g., 'Sign Up', 'Create an account') over login elements if both are present.\n"
            "3. Return exactly:\n"
            "   - ACTION: click (for interactive elements) or negatif (if no relevant element is found).\n"
            "   - TAG: the HTML tag name (e.g., a, button).\n"
            "   - LABEL: the data-testid attribute or a unique identifier if available.\n"
            "   - TEXT: the exact visible text of the element (no modifications).\n"
            "   - ATTRIBUTES: relevant attributes (e.g., href, class, data-testid) as key-value pairs.\n"
            "4. If no relevant element is found, return only 'ACTION: negatif'.\n"
            "5. Do not include explanations, only the structured output.\n"
            "6. Ensure the output format is consistent with the examples."
        ),
        suffix="\n\n### TASK ###\nHTML:\n{final_input}\nRESPONSE:",
        input_variables=["final_input"],
        example_separator="\n\n"
    )
    return few_shot_prompt

def parse_llm_response(response_text: str) -> dict:
    """Parse the structured text response from the LLM into a dictionary."""
    if response_text.strip() == 'ACTION: negatif':
        return {'action': 'negatif'}

    data = {'attributes': {}}
    lines = response_text.strip().split('\n')
    in_attributes_section = False

    for line in lines:
        if line.startswith('ATTRIBUTES:'):
            in_attributes_section = True
            continue
        
        if in_attributes_section:
            if ':' in line:
                match = re.match(r'\s*([^:]+):\s*(.*)', line)
                if match:
                    key, value = match.groups()
                    data['attributes'][key.strip()] = value.strip()
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().lower()] = value.strip()
                
    return data

def detect_sigin(s_html):
    try:
        #llm = OllamaLLM(base_url="http://localhost:11434", model="llama3.1:8b", temperature=1)

        # model= ChatGroq(temperature=0, groq_api_key="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", model_name="llama-3.3-70b-versatile")
        few_shot_prompt = create_google_signin_prompt_template()
        final_prompt = few_shot_prompt.format(final_input=s_html)
        #print(final_prompt)
        print("⏳ Waiting for a response...")
        response_text  = call_grop_llama(final_prompt,Groq)
        # response_text = model.invoke(final_prompt)
        
        print("\nModel Response:\n---\n" + response_text.content.strip() + "\n---")
        
        parsed_data = parse_llm_response(response_text.content)
        return parsed_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return {'action': 'error', 'details': str(e)}