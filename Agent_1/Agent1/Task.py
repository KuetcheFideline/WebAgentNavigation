from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv
import json

from utils.utils import  get_site ,get_site_description ,read_from_json , extract_category,extract_result ,getEnd ,WriteIntervale,append_json_to_list_file

Agent1 = AIAgent1()

# def SiteDescriptionsExamples():
#     """
#     Cette fonction est utiliser pour remplir le fichier Few.shot.json
    
#     """

#     t = Tranco(cache=True,cache_dir=".tranco")
#     latest_list = t.list()
#     sites = ["http://" + x for x in latest_list.top(10)]
#     descriptions = {}
#     for site in sites :

#         try:
#             response = requests.get(site,timeout=5)
#             response.raise_for_status()
#             soup = BeautifulSoup(response.text,'html.parser')
#             meta_desc = soup.find("meta", attrs={"name": "description"})
#             if meta_desc and "content" in meta_desc.attrs:
#                 description = meta_desc["content"]
            
#             else:
#                 for tag in soup(["script", "style"]):
#                   tag.decompose()
#                   text = soup.get_text(separator=' ', strip=True)
#                   description= text[:300] + "..." if len(text) > 300 else text
#         except requests.RequestException as e:
#             descriptions[site] = f"Erreur lors de la requête : {e}"
        
#         descriptions[site]={
#             "description":description,
#             "categorie":None
#         }
        
#     write_on_json(descriptions,"./prompts/Few.shot.json")

    



def siteCategorisation(sites,file):
    for site in sites:
        print(f"Traitement du site : {site}")

        try:
            description = get_site_description(site)

            data = {
                "data": {
                    site: description
                }
            }

            prompt = Agent1.Promt_generation("Categorisation", data)
            example = read_from_json("./prompts/ExampleCategorisation.json")
            response = Agent1.call_lm(prompt, example)
            result = extract_result(response.content.luna, site)
            

        except Exception as e:
            print(f" Erreur lors du traitement du site {site} ,{file} : {e}")
            append_json_to_list_file("./results/error.json",{"file": file, "site": site, "error": str(e)})
            continue 
    return 0





def process_sites_in_batches(path:str):
    last_error_file = None
    last_error_url =  None
    
    error_data = read_from_json("./results/error.json")
    if error_data :
        last_error = error_data[0]
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






process_sites_in_batches("folder_2")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

