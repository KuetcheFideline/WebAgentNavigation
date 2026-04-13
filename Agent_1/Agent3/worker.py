# worker.py

import os
import time
import queue 
import logging
from llms.Model import AIAgent1
from utils.utils import get_site_description, parse_llm_result, read_from_json

# Configurez un logger simple pour les workers
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(message)s')

def run_worker(task_queue, results_queue, completion_queue):
    """
    Fonction cible pour les processus travailleurs.
    Traite une URL, envoie le résultat au Writer, et une confirmation au Main.
    """
    logger = logging.getLogger()
    
    # Chaque worker a sa propre instance de l'agent
    try:
        agent = AIAgent1()
        examples = read_from_json("./prompts/Task_Category_examples.json")
    except Exception as e:
        logger.error(f"Impossible d'initialiser l'agent ou de lire les exemples: {e}")
        return 

    logger.info("Worker démarré et prêt.")

    while True:
        try:
            task = task_queue.get()
            if task is None:
                break

            site, origin_file = task
            
            try:
                logger.info(f"Traitement de {site} depuis {origin_file}")
                description = get_site_description(site)

                if description.startswith("REQUEST_ERROR:"):
                    error_report = {
                        "type": "request_error",
                        "data": {"file": origin_file, "site": site, "error": description}
                    }
                    results_queue.put(error_report)
                    continue

                data_for_prompt = {"data": {site: description}}
                prompt_text = agent.Promt_generation("Task_category_France", data_for_prompt)
                response = agent.call_lm(prompt_text, examples)

                parsed_result = parse_llm_result(response.content, site, origin_file)
                results_queue.put(parsed_result)

            except Exception as e:
                logger.error(f"Erreur inattendue lors du traitement de {site}: {e}")
                error_report = {
                    "type": "processing_error",
                    "data": {"file": origin_file, "site": site, "error": str(e)}
                }
                results_queue.put(error_report)

            finally:
                completion_queue.put(origin_file)

        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            logger.critical(f"Erreur critique dans la boucle du worker: {e}")

    logger.info("Worker terminé.")