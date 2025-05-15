import json 
from tranco import Tranco
import requests
from bs4 import BeautifulSoup


# def get_sites_from_rank(start_rank: int) -> list:
    
#     return ["http://" + domain for domain in latest_list.top(start=start_rank)]

def get_site(rank: int, ) -> str:
    #   print("y")
    #   t = Tranco(cache=True, cache_dir=".tranco")
    #   print("y")
    #   list_id = t.latest_list_id()
    #   print(list_id)
    #   sites = latest_list.top("6683X")
    #   print("ok")
    
    #   domain = sites[rank - 1]
      return f"https://chatgpt.com"

# def get_sites_range(start_rank: int, count: int) -> list:
#     return ["http://" + domain for domain in latest_list.top(n=count, start=start_rank)]

def get_site_description(site:str) -> str :
        try:
            response = requests.get(site,timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text,'html.parser')
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and "content" in meta_desc.attrs:
                description = meta_desc["content"]
            
            else:
                for tag in soup(["script", "style"]):
                  tag.decompose()
                  text = soup.get_text(separator=' ', strip=True)
                  description= text[:300] + "..." if len(text) > 300 else text
        except requests.RequestException as e:
            description = f"Erreur lors de la requête : {e}"
        
        return description

def write_on_json(data,path):
    with open (path,'w',encoding='utf-8') as f :
        json.dump(data,f,ensure_ascii=False,indent=4)

def read_from_json(file):
    try:
        with open(file,'r',encoding='utf-8') as f :
            data = json.load(f)
            return data
    except FileNotFoundError :
          print(f"Fichier non trouvé : {file}")
          return None
    except json.JSONDecodeError as e :
        print(f"Erreur de décodage JSON dans {file} : {e}")
        return None

        