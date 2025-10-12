# main_parallel.py
import multiprocessing
import os
import csv
from utils.utils import read_from_json
from worker import run_worker
from writer import run_writer

# --- CONFIGURATION ---
DATA_FOLDER = "folder_1"
NUM_WORKERS = 16 

def read_and_queue_urls(path, task_queue):
    """
    Processus lecteur : lit les CSV, gère la reprise et alimente la task_queue.
    """
    print("Reader process started.")
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

    for filename in all_files[start_index:]:
        filepath = os.path.join(path, filename)
        urls_to_process = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    urls_to_process.append(f"https://{row[1]}")
        
        if filename == last_file and last_url in urls_to_process:
            try:
                url_index = urls_to_process.index(last_url)
                urls_to_process = urls_to_process[url_index + 1:]
            except ValueError:
                pass

        print(f"Reader: Queuing {len(urls_to_process)} URLs from {filename}")
        for url in urls_to_process:
            task_queue.put((url, filename))

    print("Reader: All files queued. Sending stop signals to workers.")
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

    # Une fois que tous les travailleurs ont terminé, envoyer le signal d'arrêt à l'écrivain
    results.put(None)
    writer_proc.join()

    print("--- Traitement parallèle terminé ---")