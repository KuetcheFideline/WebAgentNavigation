# writer.py

import json
import os
import random
from pathlib import Path


from utils.utils import append_json_to_list_file, sanitize_filename 
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("writer.log"),  
        logging.StreamHandler()  
    ]
)

def load_used_ids(filepath):
    """Charge les IDs déjà utilisés depuis le fichier id.txt."""
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return set()
            return set(map(int, content.split()))
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {filepath}: {e}")
        return set()

def run_writer(results_queue):
    """
    Fonction cible pour le processus d'écriture.
    Collecte les résultats, gère l'état (IDs, catégories) et écrit par lots.
    """
    logging.info("Writer process started.")
    
    used_ids = load_used_ids("./results/id.txt")

    buffers = {
        "success": [],
        "confidence": [],
        "errors": []
    }
    
    BATCH_SIZE = 50
    last_write_time = time.time()
    
    while True:
        try:
            result = results_queue.get()
            if result is None:
                logging.info("Signal de fin reçu.")
                break

            result_type = result.get("type")
            data = result.get("data", {})
            
            if result_type == "success":
                buffers["success"].append(data)
            elif result_type == "confidence_issue":
                buffers["confidence"].append(data)
            else: # request_error, processing_error, parsing_error
                buffers["errors"].append(data)

            total_buffered_items = sum(len(b) for b in buffers.values())
            
            if total_buffered_items >= BATCH_SIZE: 
                logging.info(f"Seuil de batch atteint ({total_buffered_items} items). Écriture sur le disque...")
                write_batch_to_disk(buffers=buffers, used_ids_set=used_ids)
                last_write_time = time.time()
        
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            logging.critical(f"Erreur critique dans la boucle du writer: {e}")


    logging.info("Fin de la boucle, exécution de l'écriture finale...")
    write_batch_to_disk(buffers=buffers, used_ids_set=used_ids)
    logging.info("Writer process finished.")


def create_task_files(data, template, used_ids_set):
    """
    Prend les données d'un résultat 'success' et crée les fichiers .json de tâches.
    """
    site = data["site"]
    base_folder = "./results"
    
    combined_tasks = []
    for task_intent in data.get("unauth_task", []):
        combined_tasks.append({"is_auth": False, "intent": task_intent})
    for task_intent in data.get("auth_task", []):
        combined_tasks.append({"is_auth": True, "intent": task_intent})

    for task_info in combined_tasks:
        task_id = random.randint(1, 500000)
        while task_id in used_ids_set:
            task_id = random.randint(1, 500000)
        used_ids_set.add(task_id)

        folder_name = "auth" if task_info["is_auth"] else "unAuth"
        output_folder = os.path.join(base_folder, folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        task_data = template.copy()
        task_data["task_id"] = task_id
        task_data["require_login"] = task_info["is_auth"]
        task_data["site"] = site
        task_data["intent"] = task_info["intent"]
        task_data["start_url"] = site

        output_file = os.path.join(output_folder, f"{task_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(task_data, f_out, indent=4, ensure_ascii=False)


def write_batch_to_disk(buffers, used_ids_set):
    """
    Fonction unique qui écrit TOUT un batch : logs, journal des succès, catégories et tâches.
    """
    logger = logging.getLogger(__name__)
    total_items = sum(len(b) for b in buffers.values())
    if total_items == 0:
        return 

    logger.info(f"Écriture d'un lot de {total_items} items sur le disque...")

    try:
        if buffers["confidence"]:
            append_json_to_list_file("./results/confidence.json", buffers["confidence"])
        if buffers["errors"]:
            append_json_to_list_file("./results/errors.json", buffers["errors"])
    except Exception as e:
        logger.error(f"CRITIQUE: Échec de l'écriture des logs confidence/errors: {e}")

    try:
        if buffers["success"]:
            with open("./results/success_log.jsonl", "a", encoding="utf-8") as f:
                for success_data in buffers["success"]:
                    f.write(json.dumps(success_data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"CRITIQUE: Échec de l'écriture dans success_log.jsonl: {e}")

    for data in buffers["success"]:

        for key ,value in data.items():
                
            site = key
            
            try:
                category = sanitize_filename(value.get("Category", "Uncategorized"))
                if not category:
                    logger.warning(f"Catégorie invalide/vide pour le site {site}, ignorée.")
                    continue

                category_file = Path("./results") / f"{category}.json"
                category_file.parent.mkdir(parents=True, exist_ok=True)
                
                category_data = {"sites": []}
                if category_file.exists():
                    with open(category_file, 'r', encoding="utf-8") as f:
                        try:
                            category_data = json.load(f)
                            if "sites" not in category_data or not isinstance(category_data["sites"], list):
                                category_data["sites"] = []
                        except json.JSONDecodeError:
                            category_data = {"sites": []}

                if site not in category_data["sites"]:
                    category_data["sites"].append(site)
                
                with open(category_file, "w", encoding="utf-8") as f:
                    json.dump(category_data, f, indent=2, ensure_ascii=False)

            except Exception as e:
                logger.error(f"Échec de l'écriture de la catégorie pour le site {site}: {e}")
    try:
        with open("./results/id.txt", 'w', encoding='utf-8') as f:
            f.write(" ".join(map(str, sorted(list(used_ids_set)))))
    except Exception as e:
        logger.error(f"CRITIQUE: Échec de l'écriture de id.txt: {e}")

    for buffer_list in buffers.values():
        buffer_list.clear()
        
    logger.info("Lot écrit et buffers vidés.")

