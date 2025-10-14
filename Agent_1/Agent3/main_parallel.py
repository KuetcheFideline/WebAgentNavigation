# main_parallel.py
import multiprocessing
import os
import csv
from utils.utils import read_from_json
from worker import run_worker
from writer import run_writer
import json

DATA_FOLDER = "folder_1"
NUM_WORKERS = 16 


def load_already_processed_urls(filepath):
    """
    Charge les URLs depuis un fichier JSON ayant la structure {"sites": ["url1", "url2", ...]}.
    Retourne un set pour une recherche ultra-rapide.
    """
    processed_set = set()
    print(f"Chargement des URLs déjà traitées depuis {filepath}...")
    
    if not os.path.exists(filepath):
        print("Aucun fichier d'historique trouvé, traitement complet.")
        return processed_set

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if "sites" in data and isinstance(data["sites"], list):
                processed_set = set(data["sites"])
            else:
                print(f"AVERTISSEMENT: Le fichier {filepath} n'a pas la structure attendue {{'sites': [...]}}.")

    except json.JSONDecodeError:
        print(f"ERREUR: Le fichier {filepath} n'est pas un JSON valide. Impossible de charger l'historique.")
    except Exception as e:
        print(f"Erreur inattendue lors du chargement de l'historique: {e}")
    
    print(f"--> {len(processed_set)} URLs déjà traitées chargées en mémoire.")
    return processed_set

def read_and_queue_urls(path, task_queue):
    """
    Processus lecteur : lit les CSV, gère la reprise, filtre les URLs déjà traitées,
    et alimente la task_queue.
    """
    print("Reader process started.")

    already_processed = load_already_processed_urls("total.json")
     
    last_processed = read_from_json("./results/process.json")
    last_file = last_processed.get('file') if last_processed else None
    last_url = last_processed.get('url') if last_processed else None
    
    try:
        all_files = sorted([f for f in os.listdir(path) if f.endswith('.csv')])
    except FileNotFoundError:
        print(f"ERREUR: Le dossier spécifié n'existe pas : {path}")
        return

    start_index = 0
    if last_file in all_files:
        start_index = all_files.index(last_file)

    total_skipped = 0
    total_queued = 0

    for filename in all_files[start_index:]:
        filepath = os.path.join(path, filename)
        urls_in_file = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    urls_in_file.append(f"https://{row[1]}")
        
        urls_to_process = urls_in_file
        if filename == last_file and last_url in urls_in_file:
            try:
                url_index = urls_in_file.index(last_url)
                urls_to_process = urls_in_file[url_index + 1:]
            except ValueError:
                pass

        urls_actually_queued = 0
        
        for url in urls_to_process:
            if url in already_processed:
                total_skipped += 1
                continue 
            
            task_queue.put((url, filename))
            urls_actually_queued += 1
            total_queued += 1
        
        print(f"Reader: {filename} -> {urls_actually_queued}  URLs mises en file.")

    print(f"Reader: All files queued. Total envoyé: {total_queued}. Total ignoré (déjà traité): {total_skipped}.")
    
    for _ in range(NUM_WORKERS): 
        task_queue.put(None)

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')

    manager = multiprocessing.Manager()
    tasks = manager.Queue()
    results = manager.Queue()

    reader_proc = multiprocessing.Process(target=read_and_queue_urls, args=(DATA_FOLDER, tasks))
    reader_proc.start()

    writer_proc = multiprocessing.Process(target=run_writer, args=(results,))
    writer_proc.start()
    
    worker_pool = []
    for _ in range(NUM_WORKERS):
        worker = multiprocessing.Process(target=run_worker, args=(tasks, results))
        worker.start()
        worker_pool.append(worker)

    # Attendre la fin des processus
    reader_proc.join()
    
    for worker in worker_pool:
        worker.join()

    results.put(None)
    writer_proc.join()

    print("--- Traitement parallèle terminé ---")