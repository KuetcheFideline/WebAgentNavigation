from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv
import json

from utils.utils import get_site, get_site_description, read_from_json, extract_category, extract_result, getEnd, WriteIntervale, append_json_to_list_file

Agent1 = AIAgent1()
STATE_FILE = "processing_state.json"  # Fichier pour sauvegarder la progression

def siteCategorisation(site, file):
    """
    Traite une seule URL et gère les erreurs potentielles.
    Retourne True en cas de succès, False en cas d'échec.
    """
    print(f"Traitement du site : {site}")
    try:
        description = get_site_description(site)
        data = {"data": {site: description}}
        prompt = Agent1.Promt_generation("Categorisation", data)
        example = read_from_json("./prompts/ExampleCategorisation.json")

        response = Agent1.call_lm(prompt, example)
        
        result = extract_result(response, site)
        
        return True # Succès

    except Exception as e:
        print(f"❌ Erreur sur {site} dans {file} : {e}")
        error_details = {"file": file, "site": site, "error": str(e)}
        if "confidence" in str(e).lower():
             append_json_to_list_file("./results/confidence.json", error_details)
        else:
             append_json_to_list_file("./results/error.json", error_details)
        return False 


def save_progress(filename, last_url):
    """Sauvegarde le fichier et la dernière URL traitée avec succès."""
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_processed_file": filename, "last_successful_url": last_url}, f)

def load_progress():
    """Charge le dernier état sauvegardé. Retourne (None, None) si aucun état n'existe."""
    if not os.path.exists(STATE_FILE):
        return None, None
    with open(STATE_FILE, 'r') as f:
        try:
            state = json.load(f)
            return state.get("last_processed_file"), state.get("last_successful_url")
        except (json.JSONDecodeError, AttributeError):
            # Fichier corrompu ou vide
            return None, None

def clear_progress():
    """Supprime le fichier d'état une fois le traitement terminé."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def process_sites_in_batches(path: str):
    """
    Lit les fichiers CSV, traite les URLs une par une et gère la reprise sur erreur.
    """
    try:
        all_files_in_dir = os.listdir(path)
        sorted_csv_files = sorted([f for f in all_files_in_dir if f.endswith('.csv')])
        print(f"INFO: {len(sorted_csv_files)} fichiers CSV trouvés et triés.")
    except FileNotFoundError:
        print(f"ERREUR: Le dossier spécifié n'existe pas : {path}")
        return

    resume_file, resume_url = load_progress()

    if resume_file:
        print(f"INFO: Reprise détectée. Le script redémarrera après l'URL '{resume_url}' dans le fichier '{resume_file}'.")
    else:
        print("INFO: Aucun état de reprise trouvé. Démarrage normal depuis le début.")

    start_processing = not resume_file

    for file in sorted_csv_files:
        if not start_processing and file != resume_file:
            print(f"⏭️ Fichier {file} déjà traité, on passe au suivant.")
            continue
        start_processing = True

        name = os.path.join(path, file)
        
        try:
            with open(name, 'r', encoding='utf-8') as f:
                csv_file = csv.reader(f)
                urls = [f"https://{row[1]}" for row in csv_file if len(row) >= 2]
        except Exception as e:
            print(f"ERREUR: Impossible de lire le fichier {file}. Erreur: {e}")
            continue
        urls_to_process = urls
        if file == resume_file and resume_url in urls:
            try:
                index = urls.index(resume_url)
                urls_to_process = urls[index + 1:]
                print(f"INFO: Dans {file}, reprise après '{resume_url}'. {len(urls_to_process)} URLs restantes.")
            except ValueError:
                pass # L'URL n'a pas été trouvée, on traite tout le fichier par sécurité
        
        if not urls_to_process:
            print(f"INFO: Aucune nouvelle URL à traiter dans {file}.")
            continue
        
        print(f"\n📂 Traitement du fichier {file} ({len(urls_to_process)} URLs)")

        for site_url in urls_to_process:
            if siteCategorisation(site_url, file):
                save_progress(file, site_url)

    clear_progress()
    print("\n--- ✅ Traitement terminé. Le fichier d'état a été nettoyé. ---")

process_sites_in_batches("folder_1")