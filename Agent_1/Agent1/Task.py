from tranco import Tranco
from llms.Model import AIAgent1
import requests
from bs4 import BeautifulSoup

from utils.utils import write_on_json ,get_site ,get_site_description ,read_from_json , extract_category,extract_result

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

    



def siteCategorisation(n):
    sites = get_site(n)
    for site in sites :
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




def process_sites_in_batches(total_sites: int, batch_size: int = 20):
    for i in range(0, total_sites, batch_size):
        siteCategorisation(i + batch_size)









process_sites_in_batches(20)
