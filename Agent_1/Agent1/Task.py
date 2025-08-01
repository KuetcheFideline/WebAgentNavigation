from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv
import json

from utils.utils import write_on_json ,get_site ,get_site_description ,read_from_json , extract_category,extract_result ,getEnd ,WriteIntervale

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

    



def siteCategorisation(sites):
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
            result = extract_result(response.content, site)
            

        except Exception as e:
            print(f" Erreur lors du traitement du site {site} : {e}")
            with open("./results/error.json", "a", encoding="utf-8") as f:
                 json.dump(site, f, ensure_ascii=False)
                 f.write("\n")

            continue 
    return 0





def process_sites_in_batches(path:str):

    fichier = [nom for nom in os.listdir(path)]
    print(len(fichier))
   
    for file  in fichier :
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
                siteCategorisation(urls)
            except Exception as e :
                print("erreur ",e)
                    






process_sites_in_batches("folder_2")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

