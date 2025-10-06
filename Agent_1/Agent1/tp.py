import concurrent.futures
import time
import csv
import os
import json
from utils.utils import get_site_description, read_from_json, extract_result, append_json_to_list_file
from llms.Model import AIAgent1

Agent1 = AIAgent1()

# ⚠️ Limite de parallélisme à adapter à ta rate limit réelle
MAX_WORKERS = 10  # exemple : 50 requêtes en parallèle
RETRY_LIMIT = 3   # nombre de retries max par URL en cas d'erreur
STATE_FILE = "processing_state.json" # NOUVEAU : Nom du fichier pour sauvegarder l'état

def process_single_site(site, file):
    """
    Fonction qui traite une URL individuellement.
    Elle sera exécutée en parallèle dans le pool de threads.
    """
    try:
        description = get_site_description(site)
        data = {"data": {site: description}}
        prompt = Agent1.Promt_generation("Categorisation", data)
        example = read_from_json("./prompts/ExampleCategorisation.json")

        # Appel au modèle
        response = Agent1.call_lm(prompt, example)
        result = extract_result(response, site)
        return {"site": site, "result": result, "status": "ok"}

    except Exception as e:
        append_json_to_list_file("./results/error.json", {"file": file, "site": site, "error": str(e)})
        return {"site": site, "error": str(e), "status": "error"}


def siteCategorisation_parallel(sites, file):
    """
    Version parallèle de siteCategorisation.
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_site = {executor.submit(process_single_site, site, file): site for site in sites}

        for future in concurrent.futures.as_completed(future_to_site):
            site = future_to_site[future]
            try:
                result = future.result()
                if result["status"] == "ok":
                    print(f"✅ {site} traité avec succès")
                else:
                    print(f"❌ Erreur sur {site} : {result['error']}")
                results.append(result)
            except Exception as e:
                print(f"⚠️ Exception inattendue pour {site}: {e}")
    return results

# --- NOUVELLES FONCTIONS POUR GÉRER L'ÉTAT ---

def save_progress(filename, last_index):
    """Sauvegarde le fichier et l'index du batch en cours de traitement."""
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_processed_file": filename, "last_processed_index": last_index}, f)

def load_progress():
    """Charge le dernier état sauvegardé. Retourne (None, 0) si aucun état n'existe."""
    if not os.path.exists(STATE_FILE):
        return None, 0
    with open(STATE_FILE, 'r') as f:
        try:
            state = json.load(f)
            return state.get("last_processed_file"), state.get("last_processed_index", 0)
        except json.JSONDecodeError:
            return None, 0 # Fichier corrompu ou vide

def clear_progress():
    """Supprime le fichier d'état une fois le traitement terminé."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

# --- FONCTION PRINCIPALE MODIFIÉE ---

def process_sites_in_batches_parallel(folder_path, batch_size=500):
    """
    Lecture des CSV + envoi par batch parallèle pour éviter de saturer le modèle.
    Gère la reprise sur erreur.
    """
    all_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    
    # NOUVEAU : Chargement du point de reprise
    last_file, last_index = load_progress()
    start_processing = not last_file  # Si aucun fichier sauvegardé, on commence dès le début

    for file in all_files:
        if not start_processing and file != last_file:
            print(f"⏭️ Fichier {file} déjà traité, on passe au suivant.")
            continue
        
        # On a trouvé le fichier où reprendre, on peut commencer le traitement
        start_processing = True

        filepath = os.path.join(folder_path, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            urls = [f"https://{row[1]}" for row in reader if len(row) >= 2]

        print(f"\n📂 Fichier {file} → {len(urls)} URLs à traiter")

        # Découpage en batchs
        for i in range(0, len(urls), batch_size):
            
            # NOUVEAU : Si on est dans le bon fichier, on saute les batches déjà traités
            if file == last_file and i < last_index:
                print(f"⏭️ Batch {i//batch_size + 1} déjà traité, on passe au suivant.")
                continue

            batch = urls[i:i+batch_size]
            
            # NOUVEAU : Sauvegarde le progrès AVANT de lancer le traitement du batch
            print(f"💾 Sauvegarde du point de reprise : {file}, index {i}")
            save_progress(file, i)
            
            print(f"🚀 Traitement batch {i//batch_size + 1} / {len(urls)//batch_size + 1}")
            siteCategorisation_parallel(batch, file)
            
            # ⏸ petite pause entre batchs pour éviter rate limit
            time.sleep(1)
            
        # Réinitialise l'index pour le prochain fichier
        last_index = 0

    # NOUVEAU : Nettoyage du fichier d'état après un succès complet
    clear_progress()
    print("\n✅ Traitement terminé (parallélisé). Le fichier d'état a été nettoyé.")


# Lancement du processus
process_sites_in_batches_parallel(folder_path='folder_1')