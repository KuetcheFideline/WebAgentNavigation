from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv


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
    # sites = get_site(start,start+2)
    for  id ,site in sites :
        print(site)

        try :
            description = get_site_description(site)
            data = {
                "data" :{
                    site:description
                }
            }
            Prompt_first = Agent1.Promt_generation("Categorisation",data)
            example = read_from_json("./prompts/ExampleCategorisation.json")
            response = Agent1.call_lm(Prompt_first,example)
            result= extract_result(response.content,site)
        
            extract_category(result)

        except Exception as e:
             print(f"Erreur lors du traitement du site {site} : {e}")
            #  WriteIntervale(start,id)
             return

        # WriteIntervale(start,start+2)
        




def process_sites_in_batches(path:str):

    fichier = [nom for nom in os.listdir(path)]
    for file  in fichier :
        print("debut ############################################################du batch ",file)                 


        if file.endswith('.csv'):
            name = os.path.join(path,file)
            try :
                with open(name,'r',encoding='utf-8') as f :
                    cvs_file = csv.reader(f)
                    siteCategorisation(cvs_file)
            except Exception as e :
                print("erreur ")
                    # for elt in cvs_file :
                    #      url = f"https://{elt}

        print("fin ############################################################du batch ",file)                 





process_sites_in_batches("folder_2")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

