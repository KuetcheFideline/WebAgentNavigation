# main_parallel.py

import multiprocessing
import os
import csv
import json
import time
import logging
import re
from worker import run_worker
from writer import run_writer

DATA_FOLDER = "../../Cookyst_CrUX_Dataset/folder_5000"
HISTORY_FILE = "total.json" 
# DATA_FOLDER = "../../Cookyst_CrUX_Dataset/folder_10000"
# HISTORY_FILE = "total.json"
NUM_WORKERS = 8

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(message)s')

def load_already_processed_urls(filepath):
    """
    Charge les URLs depuis un fichier JSON ayant la structure {"sites": ["url1", "url2", ...]}.
    Retourne un set pour une recherche ultra-rapide.
    """
    processed_set = set()
    logging.info(f"Chargement des URLs déjà traitées depuis {filepath}...")
    
    if not os.path.exists(filepath):
        logging.warning("Aucun fichier d'historique trouvé, traitement complet.")
        return processed_set

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "sites" in data and isinstance(data["sites"], list):
                processed_set = set(data["sites"])
            else:
                logging.warning(f"Le fichier {filepath} n'a pas la structure attendue {{'sites': [...]}}.")
    except Exception as e:
        logging.error(f"Erreur lors du chargement de l'historique: {e}")
    
    logging.info(f"--> {len(processed_set)} URLs déjà traitées chargées en mémoire.")
    return processed_set

def read_from_json(file):
    """Lit le fichier de progression."""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def update_progress(filename, url):
    """ Met à jour le fichier de progression. """
    try:
        with open("./results/process.json", 'w', encoding='utf-8') as f:
            json.dump({"file": filename, "url": url}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour de process.json: {e}")

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')

    manager = multiprocessing.Manager()
    tasks_queue = manager.Queue()
    results_queue = manager.Queue()
    completion_queue = manager.Queue()

    writer_proc = multiprocessing.Process(target=run_writer, args=(results_queue,), name="Writer")
    writer_proc.start()
    
    worker_pool = []
    for i in range(NUM_WORKERS):
        worker = multiprocessing.Process(
            target=run_worker,
            args=(tasks_queue, results_queue, completion_queue),
            name=f"Worker-{i+1}"
        )
        worker.start()
        worker_pool.append(worker)

    try:
        logging.info("Main: Démarrage du traitement par lots synchrones.")
        already_processed = load_already_processed_urls(HISTORY_FILE)
        last_processed = read_from_json("./results/process.json")
        start_file = last_processed.get('file') if last_processed else None

        all_files_unsorted = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
        
        def get_number_key(filename):
            match = re.search(r'(\d+)', filename)
            return int(match.group(1)) if match else -1
        all_files = sorted(all_files_unsorted, key=get_number_key)
        start_index = 0
        if start_file in all_files:
            start_index = all_files.index(start_file) + 1
            logging.info(f"Reprise détectée. Démarrage après le fichier: {start_file}")

        for filename in all_files[start_index:]:
            logging.info(f"\n--- Main: Démarrage du lot '{filename}' ---")
            
            urls_in_batch = []
            last_url_in_file = None
            filepath = os.path.join(DATA_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        url = f"https://{row[1]}"
                        if url not in already_processed:
                            urls_in_batch.append(url)
                        last_url_in_file = url
            
            if not urls_in_batch:
                logging.info(f"Main: Aucune nouvelle URL à traiter dans '{filename}'. Passage au suivant.")
                update_progress(filename, last_url_in_file)
                continue

            num_tasks_in_batch = len(urls_in_batch)
            for url in urls_in_batch:
                tasks_queue.put((url, filename))
            
            logging.info(f"Main: {num_tasks_in_batch} URLs mises en file. En attente de la complétion du lot...")

            for i in range(num_tasks_in_batch):
                completion_queue.get()
                print(f"  -> Progression du lot '{filename}': {i + 1}/{num_tasks_in_batch} tâches terminées.", end='\r')
            
            print()
            logging.info(f"Main: Lot '{filename}' entièrement confirmé par les workers.")
            
            time.sleep(5) 
            
            update_progress(filename, last_url_in_file)
            logging.info(f"--- Main: Lot '{filename}' terminé et progression sauvegardée. ---")

    except KeyboardInterrupt:
        logging.warning("\nCtrl+C détecté. Le lot en cours ne sera PAS marqué comme terminé. Arrêt des processus...")
    
    finally:
        logging.info("\nMain: Tous les lots sont terminés ou arrêt demandé. Arrêt des processus...")
        
        for _ in range(NUM_WORKERS):
            tasks_queue.put(None)
        for worker in worker_pool:
            worker.join(timeout=10) 
            if worker.is_alive():
                worker.terminate() 
        logging.info("Main: Attente finale pour le Writer...")
        time.sleep(15) 
        results_queue.put(None)
        writer_proc.join(timeout=30)
        if writer_proc.is_alive():
            writer_proc.terminate()

        logging.info("--- Traitement parallèle terminé ---")