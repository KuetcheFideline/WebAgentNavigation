from langchain_ollama import OllamaLLM
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
import re


OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1:8b"

def create_google_login_prompt_template():

    examples = [
        {
            "html_input": '<div |><button | data-testid="a" > Continue with Google </button><button | data-testid="b"> Continue with Facebook </button></div>',
            "output": (
                "ACTION: click\n"
                "TAG: button\n"
                "LABEL: a\n"
                "TEXT: Continue with Google\n"
                "ATTRIBUTES:\n"
            )
        },
        {
            "html_input": '<div | role="button" aria-label="Sign in with your Google Account" data-testid="g"><svg | >...</svg><span>Google</span></div>',
            "output": (
                "ACTION: click\n"
                "TAG: div\n"
                "LABEL: g\n"
                "TEXT: Google\n" 
                "ATTRIBUTES:\n"
                "  role: button\n"
                "  aria-label: Sign in with your Google Account" 
            )
        },
        {
            "html_input": '<div><a | data-testid="d" href="/privacy">Our policy on Google Analytics</a><button | data-testid="e">Log in with Email</button></div>',
            "output": "ACTION: negatif"
        },
        {
            "html_input": '<div><input | placeholder="Email"><input | placeholder="Password"><button | data-testid="c">Log In</button></div>',
            "output": 'ACTION: negatif'
        }
    ]

    example_prompt = PromptTemplate(
        input_variables=["html_input", "output"],
        template="HTML:\n{html_input}\nRESPONSE:\n{output}"
    )

    google_few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=(
             "You are an expert web automation assistant tasked with identifying the specific element for 'Continue with Google' or 'Sign in with Google' on a login page.\n"
            "Rules:\n"
            "1. Look for interactive elements (e.g., <a>, <button>, <div role='button'>) with explicit text like 'Continue with Google', 'Sign in with Google', or attributes (e.g., aria-label, href, alt) indicating a Google sign-in action.\n"
            "2. Consider elements associated with Google icons or images (e.g., <img alt='Google Login'>) if they are part of an interactive element.\n"
            "3. Prioritize elements with 'Sign in' or 'Continue' over generic 'Google' text, but include any Google-specific interactive element.\n"
            "4. Return exactly:\n"
            "   - ACTION: click (for interactive elements) or negatif (if no Google login element is found).\n"
            "   - TAG: the HTML tag name (e.g., a, button, div).\n"
            "   - LABEL: the data-testid attribute or a unique identifier if available.\n"
            "   - TEXT: the exact visible text of the element (no modifications).\n"
            "   - ATTRIBUTES: relevant attributes (e.g., href, class, data-testid, aria-label, role) as key-value pairs.\n"
            "5. If no Google login element is found, return only 'ACTION: negatif'.\n"
            "6. If multiple Google login options exist, choose the first one that explicitly indicates sign-in or account creation.\n"
            "7. Do not include explanations, only the structured output.\n"
            "8. Ensure the output format is consistent with the examples."
            
        ),
        suffix="\n\n### TASK ###\nHTML:\n{final_input}\nRESPONSE:",
        input_variables=["final_input"],
        example_separator="\n\n"
    )
    
    return google_few_shot_prompt

def parse_llm_response(response_text: str) -> dict:
    """
    (Réutilisable) Parse la réponse texte structurée du LLM en dictionnaire.
    """
    if 'ACTION: negatif' in response_text:
        return {'action': 'negatif'}

    data = {'attributes': {}}
    lines = response_text.strip().split('\n')
    in_attributes_section = False

    for line in lines:
        if line.startswith('ATTRIBUTES:'):
            in_attributes_section = True
            continue
        
        if in_attributes_section:
            match = re.match(r'\s*([^:]+):\s*(.*)', line)
            if match:
                key, value = match.groups()
                data['attributes'][key.strip()] = value.strip()
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().lower()] = value.strip()
                
    return data

def build_robust_selector(llm_data: dict) -> str:
    """
    (Réutilisable) Construit un sélecteur CSS robuste à partir des données du LLM.
    """
    if not llm_data or llm_data.get('action') != 'click':
        return None

    tag = llm_data.get('tag')
    label = llm_data.get('label')
    
    if not tag or not label:
        raise ValueError("TAG and LABEL are mandatory for building a selector.")
        
    selector = f"{tag}[data-testid='{label}']"

    attributes = llm_data.get('attributes', {})
    for key, value in attributes.items():
        escaped_value = value.replace("'", "\\'").replace('"', '\\"')
        selector += f"[{key}='{escaped_value}']"
        
    return selector

def detect_login_with_google(s_html: str):
    """
    Fonction principale pour détecter l'option de connexion Google et renvoyer
    les données parsées prêtes pour Playwright.
    """
    try:
        #llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=MODEL_NAME, temperature=0.0)
        model= ChatGroq(temperature=0, groq_api_key="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", model_name="llama-3.3-70b-versatile")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return {'action': 'error', 'details': f"Ollama connection failed: {e}"}

    google_prompt_template = create_google_login_prompt_template()
    final_google_prompt = google_prompt_template.format(final_input=s_html) 

    try:
        print("⏳ Searching for Google login option...")
        response_text = model.invoke(final_google_prompt)
    
        print("\n Model Response (Google Login):\n---\n" + response_text.content.strip() + "\n---")
        
        parsed_data = parse_llm_response(response_text.content)
        return parsed_data

    except Exception as e:
        print(f"An error occurred during model invocation: {e}")
        return {'action': 'error', 'details': f"Model invocation failed: {e}"}





