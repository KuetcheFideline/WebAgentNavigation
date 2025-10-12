# worker.py
from llms.Model import AIAgent1 
from utils.utils import get_site_description, parse_llm_result, read_from_json
import time
import os
import json
from multiprocessing import Process, Queue, current_process
def run_worker(task_queue, results_queue):
    """
    Fonction cible pour les processus travailleurs.
    """
    # Chaque travailleur initialise son propre client LLM et charge les exemples
    agent = AIAgent1()
    examples = read_from_json("./prompts/Task_Category_examples.json")
    
    print(f"Worker {os.getpid()} started.")
    nb_urls = 0
    while True:
        task = task_queue.get()
        # Le 'None' est un signal pour arrêter le travailleur
        if task is None:
            break

        site, origin_file = task
        
        try:
            description = get_site_description(site)

            data_for_prompt = {"data": {site: description}}
            prompt_text = agent.Promt_generation("Tasks_Category", data_for_prompt)

            # Appel au modèle de langage
            response = agent.call_lm(prompt_text, examples)

            # On parse le résultat et on l'envoie à l'écrivain
            parsed_result = parse_llm_result(response.content, site, origin_file)
            nb_urls= nb_urls+1
            results_queue.put(parsed_result)
            print(f"Worker {os.getpid()} processed {nb_urls} URLs.")
        except Exception as e:
            # Gère toutes les autres erreurs potentielles (ex: erreur de l'API LLM)
            error_report = {
                "type": "processing_error",
                "data": {"file": origin_file, "site": site, "error": str(e)}
            }
            results_queue.put(error_report)
            
    print(f"Worker {os.getpid()} finished.")