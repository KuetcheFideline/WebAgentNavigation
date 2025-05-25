import json 
from tranco import Tranco
import requests
from bs4 import BeautifulSoup
import re 
from pathlib import Path

# def get_sites_from_rank(start_rank: int) -> list:
    
#     return ["http://" + domain for domain in latest_list.top(start=start_rank)]

def get_site(n=20):
    t = Tranco(cache=True, cache_dir=".tranco")
    sites = t.list(n)
   
    urls = [f"https://{site}" for site in sites]
    return urls

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


import json

def extract_result(result, site):
    lines = result.split("\n")
    data = {}
    current_key = None

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            current_key = key.strip().lower()
            data[current_key] = value.strip()
        else:
            if current_key:
                data[current_key] += ' ' + line.strip()

    if "confidence" in data:
        try:
            data["confidence"] = int(data["confidence"])
        except ValueError:
            pass

    data['url'] = site

    with open("./results/result.json", "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    return data 



def extract_category(result,result_dir:str="results"):


        # Extract_result et save dans un fichier la categorie et et les urls associés 
        """
            model_output:  
                #Category: [category]\n#Configence: [score]\n#Url: [url]\n#Explanation: [explanation]
        """
        #create the save dir if needed
        Path(result_dir).mkdir(exist_ok=True)

        #defining the path to the json file
        category_file = Path(result_dir)/ f"{result['category']}.json"

        #initialise or load file content 

        if category_file.exists():
            with open(category_file,'r',encoding="utf-8") as f:
                try:
                    print("exist file")
                    category_data = json.load(f)
                    print(category_data["sites"])
                    print(result)
                    if result["url"] not in category_data["sites"]:
                        print("not In")
                        category_data["sites"].append(result["url"])
                    
                    else:
                         print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
                    with open(category_file, "w", encoding="utf-8") as f:
                        json.dump(category_data, f, indent=2, ensure_ascii=False)
                    return result
                    
                except json.JSONDecodeError:
                    print(f"ERROR: corrupted file {category_file}, initialising a new file")
                    category_data = {"sites":[],"tasks":[]}
        else:
            category_data = {"sites":[],"tasks":[]}
        
            if result["url"] not in category_data["sites"]:
                category_data["sites"].append(result["url"])
            else:
                print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
            
            with open(category_file, "w", encoding="utf-8") as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
            
            print(f"Succès: URL {result['url']} ajoutée à {category_file}")
            return result



