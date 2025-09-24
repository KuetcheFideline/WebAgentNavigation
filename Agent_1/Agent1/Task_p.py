from concurrent.futures import ThreadPoolExecutor, as_completed
from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os
from bs4 import BeautifulSoup
import csv
import json
import queue
import threading
from pathlib import Path
from utils.utils import write_on_json, get_site, get_site_description, read_from_json, extract_category_pp, extract_result_pp, getEnd, WriteIntervale, update_progress, read_progress

Agent1 = AIAgent1()

# Créer une queue pour gérer toutes les écritures
write_queue = queue.Queue()

# Fonction du thread d'écriture
def write_worker():
    while True:
        try:
            data = write_queue.get(timeout=10)
            if data is None:  # Signal de terminaison
                break
            operation = data.get("operation")
            if operation == "category":
                result = data.get("result")
                result_dir = data.get("result_dir", "results")
                if result is not None and isinstance(result, dict):
                    extract_category_pp(result, result_dir)
                else:
                    print(f"Erreur : résultat invalide pour catégorie : {result}")
            elif operation in ("result", "confidence", "error"):
                file_path = "./results/error.json" if operation == "error" else f"./results/{operation}.json"
                new_data = data.get("data")
                if new_data is not None:
                    append_json_to_list_file(file_path, new_data)
                else:
                    print(f"Erreur : données invalides pour {operation} : {new_data}")
            elif operation == "progress":
                batch_file = data.get("batch_file")
                last_site = data.get("last_site")
                result_dir = data.get("result_dir", "results")
                update_progress(batch_file, last_site, result_dir)
            else:
                print(f"Erreur : opération inconnue : {operation}")
            write_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Erreur dans le thread d'écriture : {e}")
            write_queue.task_done()

def append_json_to_list_file(file_path, new_data):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    else:
        existing = []
    existing.append(new_data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

write_thread = threading.Thread(target=write_worker, daemon=True)
write_thread.start()

def process_single_site(site, batch_file):
    print(f"Traitement du site : {site} dans le batch {batch_file}")
    try:
        description = get_site_description(site)
        data = {"data": {site: description}}
        prompt = Agent1.Promt_generation("Categorisation", data)
        example = read_from_json("./prompts/ExampleCategorisation.json")
        response = Agent1.call_lm3(prompt, example)
        result = extract_result_pp(response, site)
        if result is not None and isinstance(result, dict):
            write_queue.put({"operation": "result", "data": result})
            if result.get("confidence", 0) > 75:
                write_queue.put({"operation": "category", "result": result, "result_dir": "results"})
            else:
                write_queue.put({"operation": "confidence", "data": result})
            write_queue.put({"operation": "progress", "batch_file": batch_file, "last_site": site, "result_dir": "results"})
            return {site: result}
        else:
            print(f"Erreur : résultat invalide pour le site {site}")
            write_queue.put({"operation": "error", "data": site})
            return None
    except Exception as e:
        print(f"Erreur lors du traitement du site {site} : {e}")
        write_queue.put({"operation": "error", "data": site})
        return None

def siteCategorisation(sites, batch_file):
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_site = {executor.submit(process_single_site, site, batch_file): site for site in sites}
        for future in as_completed(future_to_site):
            result = future.result()
            if result:
                results.update(result)
    return results

def process_sites_in_batches(path: str):
    # Lire l'état de progression
    progress = read_progress()
    last_batch = progress.get("batch_file")
    last_site = progress.get("last_site")

    fichier = [nom for nom in os.listdir(path) if nom.endswith('.csv')]
    print(f"Nombre de fichiers CSV : {len(fichier)}")

    start_processing = last_batch is None  # Si aucun batch n'a été traité, commencer au début

    for file in fichier:
        name = os.path.join(path, file)
        # Si un batch précédent a été partiellement traité, reprendre à ce batch
        if not start_processing and last_batch != file:
            continue
        start_processing = True  # Commencer à traiter à partir du batch trouvé ou le premier

        try:
            with open(name, 'r', encoding='utf-8') as f:
                cvs_file = csv.reader(f)
                urls = []
                skip_until_next = False
                for row in cvs_file:
                    if len(row) >= 2:
                        url = f"https://{row[1]}"
                        if last_batch == file and last_site and url != last_site:
                            skip_until_next = True
                            continue
                        if last_batch == file and last_site == url:
                            skip_until_next = False  # Reprendre après le dernier site traité
                            continue
                        if not skip_until_next:
                            urls.append(url)
                    else:
                        print("Ligne ignorée (malformée) :", row)

                if urls:
                    print(f"Traitement du batch {file} avec {len(urls)} URLs")
                    siteCategorisation(urls, file)
                else:
                    print(f"Aucun site à traiter dans {file} (tous déjà traités ou sautés)")

        except Exception as e:
            print(f"Erreur lors du traitement du fichier {name} : {e}")
            write_queue.put({"operation": "error", "data": f"Fichier {name}: {str(e)}"})

    write_queue.put(None)
    write_thread.join()

if __name__ == "__main__":
    process_sites_in_batches("folder_1")