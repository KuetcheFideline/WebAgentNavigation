# writer.py
import json
import os
import random
from pathlib import Path
from utils.utils import append_json_to_list_file
import time
import logging
import re 

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("writer.log"),  
        logging.StreamHandler()  
    ]
)

def load_used_ids(filepath):
    """Charge les IDs déjà utilisés depuis le fichier id.txt."""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        # map(int, ...) est plus rapide que les compréhensions de liste pour les grandes listes
        return set(map(int, f.read().split()))

def run_writer(results_queue):
    """
    Fonction cible pour le processus d'écriture.
    Collecte les résultats, gère l'état (IDs, catégories) et écrit par lots.
    """
    logging.info("Writer process started.")
    
    # --- GESTION DE L'ÉTAT CENTRALISÉ ---
    # Le writer charge l'état une seule fois au démarrage
    used_ids = load_used_ids("./results/id.txt")
   
    # Buffers en mémoire pour l'écriture par lots
    buffers = {
        "confidence": [],
        "errors": [],
        "categories": {},
        "success": []
    }
    
    BATCH_SIZE = 100
    last_write_time = time.time()
    
    while True:
        result = results_queue.get()
        if result is None:
            break

        result_type = result.get("type")
        data = result.get("data", {})
        
        if result_type == "success":
            logging.info(f"Writer: Processing success for site {data.get('site')}")
            buffers["success"].append(data)
            # 1. Mise en buffer de la catégorie (comme avant)
            # category = data.get("category", "Uncategorized")
            # if category not in buffers["categories"]:
            #     buffers["categories"][category] = []
            # buffers["categories"][category].append(data["site"])
            
            # # 2. NOUVEAU: Création des fichiers de tâches individuels
            # if task_template:
            #     create_task_files(data, task_template, used_ids)
            
        elif result_type == "confidence_issue":
            buffers["confidence"].append(data)
        else: # request_error, processing_error, parsing_error
            buffers["errors"].append(data)

        total_buffered_items =  len(buffers["success"])
        logging.info(f"total_buffered_items: {total_buffered_items}")
        logging.info(f"Writer: Buffered items count: {total_buffered_items}")
        if total_buffered_items >= BATCH_SIZE or time.time() - last_write_time > 30:
            logging.info(f"Writer: Writing buffers to disk...")
            write_batch_to_disk(buffers=buffers, used_ids_set=used_ids)
            if data.get("site"):
                update_progress(data["origin_file"], data["site"])
            last_write_time = time.time()

    # Écriture finale des données restantes avant de quitter
    #write_buffers_to_disk(buffers, used_ids)
    logging.info("Writer process finished.")



def sanitize_filename(name: str) -> str:
    """
    Nettoie une chaîne de caractères pour qu'elle soit un nom de fichier valide.
    Remplace les caractères système réservés (comme / \ : * ? " < > |) par un underscore.
    Supprime aussi les espaces ou points en début/fin de nom qui peuvent poser problème.
    """
    if not isinstance(name, str):
        name = str(name)
        
    # Remplace les slashes et autres caractères invalides par un underscore
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    
    # Supprime les points et espaces superflus au début et à la fin
    name = name.strip('. ')
    
    # Optionnel : si le nom est vide après nettoyage, on retourne un nom par défaut
    if not name:
        return "uncategorized_invalid_name"
        
    return name
       

def create_task_files(data, template, used_ids_set):
    """
    Prend les données d'un résultat 'success' et crée les fichiers .json de tâches.
    Cette fonction est appelée uniquement par le processus Writer.
    """
    site = data["site"]
    base_folder = "./results"
    
    # Combine les tâches authentifiées et non authentifiées en une seule liste pour itérer
    combined_tasks = []
    for task_intent in data.get("unauth_task", []):
        combined_tasks.append({"is_auth": False, "intent": task_intent})
    for task_intent in data.get("auth_task", []):
        combined_tasks.append({"is_auth": True, "intent": task_intent})

    for task_info in combined_tasks:
        # Génération d'un ID unique (rapide, car tout est en mémoire)
        task_id = random.randint(80001, 100000)
        while task_id in used_ids_set:
            task_id = random.randint(80001, 100000)
        used_ids_set.add(task_id)

        # Préparation du dossier de destination
        folder_name = "auth" if task_info["is_auth"] else "unAuth"
        output_folder = os.path.join(base_folder, folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # Remplissage du template
        task_data = template.copy() # Important de copier pour ne pas modifier l'original
        task_data["task_id"] = task_id
        task_data["require_login"] = task_info["is_auth"]
        task_data["site"] = site
        task_data["intent"] = task_info["intent"]
        task_data["start_url"] = site

        # Écriture du fichier JSON de la tâche
        output_file = os.path.join(output_folder, f"{task_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(task_data, f_out, indent=4, ensure_ascii=False)

# def write_buffers_to_disk(buffers, used_ids_set):
#     """
#     Effectue les écritures sur le disque pour les fichiers de logs et de catégories.
#     Met également à jour le fichier des IDs utilisés.
#     """
#     logging.info(f"Writing buffers to disk... ({len(used_ids_set)} total unique task IDs generated)")
    
#     # Écriture des logs et des cas de faible confiance
#     append_json_to_list_file("./results/confidence.json", buffers["confidence"])
#     append_json_to_list_file("./results/errors.json", buffers["errors"])
    
#     # Écriture dans les fichiers de catégories (logique optimisée)
#     for category, sites in buffers["categories"].items():
#         if not sites: continue
#         try:
#             safe_category_name = sanitize_filename(category)
#             category_file = Path("./results") / f"{safe_category_name}.json"
            
#             existing_sites = set()
#             if category_file.exists():
#                 with open(category_file, 'r', encoding="utf-8") as f:
#                     try:
#                         category_data = json.load(f)
#                         existing_sites.update(category_data.get("sites", []))
#                     except json.JSONDecodeError: pass
            
#             existing_sites.update(sites)
            
#             with open(category_file, "w", encoding="utf-8") as f:
#                 json.dump({"sites": sorted(list(existing_sites))}, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             logging.error(f"Erreur lors de l'écriture du fichier de catégorie '{category}': {e}")

#     # NOUVEAU: Sauvegarde de l'état des IDs utilisés sur le disque
#     with open("./results/id.txt", 'w', encoding='utf-8') as f:
#         f.write(" ".join(map(str, sorted(list(used_ids_set)))))

#     # Vider les buffers après écriture
#     buffers["confidence"].clear()
#     buffers["errors"].clear()
#     buffers["categories"].clear()
#     logging.info("Finished writing.")
def write_batch_to_disk(buffers, used_ids_set):
    """
    Fonction unique qui écrit TOUT un batch : logs, catégories et tâches.
    Cette version est complète et intègre la logique de fusion pour les catégories.
    """
    logger = logging.getLogger(__name__)
    total_items = sum(len(b) for b in buffers.values())
    if total_items == 0:
        return 

    logger.info(f"Writing batch of {total_items} items to disk...")

    try:
        if buffers["confidence"]:
            append_json_to_list_file("./results/confidence.json", buffers["confidence"])
        if buffers["errors"]:
            append_json_to_list_file("./results/errors.json", buffers["errors"])
    except Exception as e:
        logger.error(f"CRITICAL: Failed to write confidence/error logs: {e}")
    try:
        if buffers["success"]:
            with open("./results/success_log.jsonl", "a", encoding="utf-8") as f:
                for success_data in buffers["success"]:
                    f.write(json.dumps(success_data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to write to success_log.jsonl: {e}")

    for data in buffers["success"]:
        site = data.get("site", "URL_INCONNUE")
        
        try:
            category = sanitize_filename(data.get("category", "Uncategorized"))
            if not category:
                logger.warning(f"Skipping category for site {site} due to invalid/empty category name.")
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
                        logger.warning(f"Corrupted JSON in {category_file}, it will be overwritten.")
                        category_data = {"sites": []}

            if site not in category_data["sites"]:
                category_data["sites"].append(site)
            
            with open(category_file, "w", encoding="utf-8") as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to write category for site {site}: {e}")
    try:
        with open("./results/id.txt", 'w', encoding='utf-8') as f:
            f.write(" ".join(map(str, sorted(list(used_ids_set)))))
    except Exception as e:
        logger.error(f"CRITICAL: Failed to write id.txt: {e}")

    for buffer_list in buffers.values():
        buffer_list.clear()
        
    logger.info("Batch written and buffers cleared.")
def update_progress(file, url):
    """ Met à jour le fichier de progression. """
    with open("./results/process.json", 'w', encoding='utf-8') as f:
        json.dump({"file": file, "url": url}, f, ensure_ascii=False, indent=2)