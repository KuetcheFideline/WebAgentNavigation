import json 
from tranco import Tranco
import requests
from bs4 import BeautifulSoup
import re 
from pathlib import Path
import os
from urllib.parse import urlparse

base_dir = os.path.dirname(__file__)

def clean_domain(url):
    netloc = urlparse(url).netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    name = netloc.split('.')[0]  
    return name


def get_site(start=0 ,end =20):
    
    cache_dir = os.path.join(base_dir, '..', '.tranco')
    t = Tranco(cache=True, cache_dir=cache_dir)
    sites = t.list(list_id='6683X')
    urls = [(i, f"https://{site}") for i, site in enumerate(sites.top(end)[start:end], start=start + 1)]
    return urls 



def getEnd():
    
    filename = os.path.join(os.path.dirname(__file__),'..','..','experimentation.txt')
    with open(filename ,'r', encoding='utf-8') as f :
        content = f.read()
        end = re.findall(r'end\s*=\s*(\d+)',content)
        if end :
            last_end = int(end[-1])
            return last_end
        else :
            raise ValueError("Aucune valeur 'end' trouvée dans le fichier.")


def WriteIntervale(start ,end ):
    filename = os.path.join(os.path.dirname(__file__),'..','..','experimentation.txt')

    with open(filename,'a',encoding='utf-8') as f :
        Intervale = f'start = {start}, end = {end}'
        f.write(Intervale)








# def get_site(rank: int, ) -> str:
#     #   print("y")
#     #   t = Tranco(cache=True, cache_dir=".tranco")
#     #   print("y")
#     #   list_id = t.latest_list_id()
#     #   print(list_id)
#     #   sites = latest_list.top("6683X")
#     #   print("ok")
    
#     #   domain = sites[rank - 1]
#       return f"https://feuwofranck.tech"

# def get_sites_range(start_rank: int, count: int) -> list:
#     return ["http://" + domain for domain in latest_list.top(n=count, start=start_rank)]


def get_site_content(site:str)->str:
    try :
        response = requests.get(site,timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text,'html.parser')
        for tag in soup (["script","style","noscript"]):
            tag.decompose
        text = soup.get_text(separator="",strip=True)

        return text 
    except Exception   as e  :
        print(f"Erreur lors de la récupération de {site} : {e}")
        return ""


       
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
    import os
    from pathlib import Path

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

    if data["confidence"] <= 75:
        append_json_to_list_file("./results/confidence.json", data)
    else:
        append_json_to_list_file("./results/result.json", data)
        extract_category(data)


def extract_category(result,result_dir:str="results"):


        """
            model_output:  
                #Category: [category]\n#Configence: [score]\n#Url: [url]\n#Explanation: [explanation]
        """
        Path(result_dir).mkdir(exist_ok=True)

        category_file = Path(result_dir)/ f"{result['category']}.json"


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



def get_category_list_from_folder(folder_path):
    
    try:
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".json")
            and os.path.splitext(f)[0] != "result"
        ]
    except FileNotFoundError:
        print(f"Folder not found: {folder_path}")
        return []
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []

def extract_json_from_output(output: str) -> dict:
    """
    Extracts a JSON object from a string containing mixed text and JSON.
    
    Args:
        output (str): The model output containing JSON and potentially other text.
        
    Returns:
        dict: The parsed JSON object, or an empty dict if no valid JSON is found.
        
    Raises:
        json.JSONDecodeError: If the extracted JSON is invalid.
    """
    try:
        # Use regex to find JSON content between ```json and ```
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, output)
        
        if not match:
            print("No JSON found within ```json ``` markers")
            return {}
            
        # Extract the JSON string from the matched group
        json_str = match.group(1)
        
        # Parse the JSON string into a Python dictionary
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}
    
def add_task_to_category_json(file,res):
    with open(file,'r',encoding="utf-8") as f:
        try:
            print("exist file")
            category_data = json.load(f)
            print(category_data["tasks"])
            print(res["tasks"])
            
            category_data["tasks"].append(res["tasks"])
                    
            
            with open(file, "w", encoding="utf-8") as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
                    
        except json.JSONDecodeError:
            print(f"ERROR: corrupted file ")
