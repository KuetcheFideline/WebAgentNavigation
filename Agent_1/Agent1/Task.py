from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv
import json

from utils.utils import  get_site ,get_site_description ,read_from_json , extract_category,extract_result ,getEnd ,WriteIntervale,append_json_to_list_file

Agent1 = AIAgent1()

    



def siteCategorisation(sites,file):
    for site in sites:
        print(f"Traitement du site : {site}")
        description = get_site_description(site)

        data = {
                "data": {
                    site: description
                }
            }

        prompt = Agent1.Promt_generation("Categorisation", data)
        example = read_from_json("./prompts/ExampleCategorisation.json")

        try:
            response = Agent1.call_lm3(prompt, example)
            
        except Exception as  e :
            append_json_to_list_file("./results/error.json",{"file": file, "site": site, "error": str(e)})

            raise

        try:
            result = extract_result(response, site)
            

        except Exception as e:
            print(f" Erreur lors de l'extraction des resultats  {site} ,{file} : {e}")
            append_json_to_list_file("./results/confidence.json",{"file": file, "site": site, "error": str(e)})
            continue 
    return 0





def process_sites_in_batches(path:str):
    last_error_file = None
    last_error_url =  None
    
    error_data = read_from_json("./results/error.json")
    if error_data :
        last_error = error_data[-1]
        last_error_file = last_error.get('file')
        last_error_url = last_error.get('site')
        print(f"INFO: Reprise détectée. Le script redémarrera après l'URL '{last_error_url}' dans le fichier '{last_error_file}'.")
    else:
        print("INFO: Aucun fichier d'erreur trouvé ou fichier vide. Démarrage normal depuis le début.")
    try:
        all_files_in_dir = os.listdir(path)
        sorted_csv_files = sorted([f for f in all_files_in_dir if f.endswith('.csv')])
        print(f"INFO: {len(sorted_csv_files)} fichiers CSV trouvés et triés.")
    except FileNotFoundError:
        print(f"ERREUR: Le dossier spécifié n'existe pas : {path}")
        exit() 
    start_index = 0
    if last_error_file in sorted_csv_files:
        try:
           start_index = sorted_csv_files.index(last_error_file)
        except ValueError:
          pass
    files_to_process = sorted_csv_files[start_index:]
    for file  in files_to_process :
        name = os.path.join(path, file)
        if file.endswith('.csv'):
            name = os.path.join(path,file)
            try :
                with open(name,'r',encoding='utf-8') as f :
                    cvs_file = csv.reader(f)
                    urls = []
                    for row in cvs_file:
                        if len(row) >= 2: 
                            urls.append(f"https://{row[1]}")
                        else:
                            print("Ligne ignorée (malformée) :", row)
                    if file ==last_error_file and last_error_url in urls :
                        try :
                            index= urls.index(last_error_url)
                            urls = urls[index+1:]
                            print(f"INFO: Dans {file}, reprise après '{last_error_url}'. {len(urls)} URLs restantes à traiter.")
                        except ValueError:
                          pass 
                        if urls :
                             siteCategorisation(urls,file)
                        else :
                            print(f"INFO: Aucune nouvelle URL à traiter dans {file}.")

                            
            except Exception as e :
                print("erreur ",e)
                    
    print("--- Traitement terminé ---")






process_sites_in_batches("folder_1")
                                           