from llms.Model import AIAgent1
from utils.utils import (
    read_from_json,
    get_category_list_from_folder,
    extract_json_from_output,
    add_task_to_category_json
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import json
import time

model = AIAgent1()

# 👇 Fonction décorée pour réessayer automatiquement en cas d'erreur (429, timeout, etc.)
@retry(
    wait=wait_exponential(multiplier=2, min=2, max=60),  
    stop=stop_after_attempt(5),                         # max 5 tentatives
    retry=retry_if_exception_type(Exception)            
)
def safe_call_lm(prompt_first, examples):
    """Appel au modèle avec retry automatique en cas d'échec temporaire."""
    return model.call_lm(PromptFirst=prompt_first, example=examples)

def process_category(category, examples):
    """Traite une seule catégorie."""
    data = {"website_category": category}

    prompt_first = model.Promt_generation("Tasks", data=data)

    # Appel au modèle avec retry automatique
    response = safe_call_lm(prompt_first, examples)

    # Extraction du JSON formaté
    format_res = extract_json_from_output(response.content)

    # Sauvegarde dans le fichier correspondant
    add_task_to_category_json(f"./results/{format_res['website_category']}.json", format_res)

    return category

def task_generation_parallel(max_workers=10):
    """Lance la génération en parallèle sur plusieurs catégories avec gestion d'erreurs."""
    examples = read_from_json("./prompts/FewShotTask.json")
    categories = get_category_list_from_folder("./results")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_category, cat, examples): cat for cat in categories}

        for future in as_completed(futures):
            cat = futures[future]
            try:
                future.result()
                print(f"✅ Catégorie traitée : {cat}")
            except Exception as e:
                print(f"❌ Erreur pour {cat} : {e}")

if __name__ == "__main__":
    task_generation_parallel(max_workers=10)
