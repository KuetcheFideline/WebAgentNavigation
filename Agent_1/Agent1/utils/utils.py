import json 
from tranco import Tranco
import requests
from bs4 import BeautifulSoup
import re 
from pathlib import Path
import os
import ast
from urllib.parse import urlparse

base_dir = os.path.dirname(__file__)

def clean_domain(url):
    netloc = urlparse(url).netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    name = netloc.split('.')[0]  
    return name


def sanitize_filename(name: str) -> str:
    """
    Nettoie une chaîne de caractères pour qu'elle soit un nom de fichier valide.
    Remplace les caractères système réservés (comme / \ : * ? " < > |) par un underscore.
    Supprime aussi les espaces ou points en début/fin de nom qui peuvent poser problème.
    """
    if not isinstance(name, str):
        name = str(name)
        
    # Remplace les slashes et autres caractères invalides par un underscore
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    
    # Supprime les points et espaces superflus au début et à la fin
    name = name.strip('. ')
    
    # Optionnel : si le nom est vide après nettoyage, on retourne un nom par défaut
    if not name:
        return "uncategorized_invalid_name"
        
    return name




def parse_llm_output(llm_content):
    parts = llm_content.split("```")
    json_str = max(parts, key=len).replace("json", "").strip()

    if not json_str:
        raise ValueError("Contenu vide")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(json_str)
    except Exception as e:
        raise ValueError(f"Impossible de parser le contenu : {e}")

def parse_llm_result(llm_content: str, site: str, origin_file: str):
    """
    Parse la sortie du LLM et retourne un dictionnaire structuré pour le processus écrivain.
    Ne fait AUCUNE opération de lecture/écriture de fichier.
    """
    nb=0
    try:
        json_data = parse_llm_output(llm_content)

        for key ,value in json_data.items():
          if value.get("Confidence") <=75 or "error" in value.get("Category") :
            return {"type": "confidence_issue", "data": json_data}
          else:
            return {"type": "success", "data": json_data}
    except Exception as e:
        return {
            "type": "parsing_error",
            "data": {
                "site": site,
                "origin_file": origin_file,
                "error": str(e),
                "llm_content": llm_content
            }
        }


def append_json_to_list_file(file_path, new_data):
        
        '''
        Ajouter les donnés a un json valide 
        
        '''
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
            description = ""
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


import os
from pathlib import Path
import json
def extract_result(result, site):

    lines = result.content.split("\n")
    data = {}
    current_key = None

   
    datas = result.content
    data =json.loads(datas)
    for elt in data :
        cat = {elt :data[elt]}

        print(elt)
        print(cat)
        print( data[elt]["Confidence"])
        if data[elt]["Confidence"] <= 75:
            append_json_to_list_file("./results/confidence.json", cat)
        else:
            print("yu")

            append_json_to_list_file("./results/result.json", cat)
            print("lil")
            extract_category(cat)

            

def extract_category(result,result_dir:str="results"):


        """
            model_output:  
                #Category: [category]\n#Configence: [score]\n#Url: [url]\n#Explanation: [explanation]
        """
        Path(result_dir).mkdir(exist_ok=True)
        category_file = ""
        for elt in result :
            category_file = Path(result_dir)/ f"{result[elt]['category']}.json"
            if category_file.exists():
                with open(category_file,'r',encoding="utf-8") as f:
                    try:
                        print("exist file")
                        category_data = json.load(f)
                        #print(category_data["sites"])
                        #print(result)
                        if result[elt] not in category_data["sites"]:
                            print("not In")
                            category_data["sites"].append(result[elt])
                        
                        else:
                            print(f"Info: URL {result[elt]} déjà présente dans {category_file}, ignorée.")
                        with open(category_file, "w", encoding="utf-8") as f:
                            json.dump(category_data, f, indent=2, ensure_ascii=False)
                        return result
                        
                    except json.JSONDecodeError:
                        print(f"ERROR: corrupted file {category_file}, initialising a new file")
                        category_data = {"sites":[],"tasks":[]}
            else:
                category_data = {"sites":[],"tasks":[]}
            
                if result[elt] not in category_data["sites"]:
                    category_data["sites"].append(result[elt])
                else:
                    print(f"Info: URL {result[elt]} déjà présente dans {category_file}, ignorée.")
                
                with open(category_file, "w", encoding="utf-8") as f:
                    json.dump(category_data, f, indent=2, ensure_ascii=False)
                
                print(f"Succès: URL {result[elt]} ajoutée à {category_file}")
            return result







def extract_category_p(result, result_dir: str = "results"):
    """
    Écrit le résultat dans le fichier JSON de la catégorie correspondante.
    """
    Path(result_dir).mkdir(exist_ok=True)
    category_file = Path(result_dir) / f"{result['category']}.json"

    if category_file.exists():
        with open(category_file, 'r', encoding="utf-8") as f:
            try:
                category_data = json.load(f)
                if result["url"] not in category_data["sites"]:
                    category_data["sites"].append(result["url"])
                else:
                    print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
            except json.JSONDecodeError:
                print(f"ERROR: corrupted file {category_file}, initialising a new file")
                category_data = {"sites": [], "tasks": []}
                category_data["sites"].append(result["url"])
    else:
        category_data = {"sites": [], "tasks": []}
        category_data["sites"].append(result["url"])

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
            #print(category_data["tasks"])
            #print(res["tasks"])
            
            category_data["tasks"].append(res["tasks"])
                    
            
            with open(file, "w", encoding="utf-8") as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
                    
        except json.JSONDecodeError:
            print(f"ERROR: corrupted file ")
def extract_result_pp(result, site):
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
            data["confidence"] = 0
    else:
        data["confidence"] = 0

    data['url'] = site

    if not data or "category" not in data:
        print(f"Erreur : données incomplètes pour le site {site} : {data}")
        return None

    return data

def extract_category_pp(result, result_dir: str = "results"):
    if not isinstance(result, dict) or "category" not in result or "url" not in result:
        print(f"Erreur : données invalides pour extract_category : {result}")
        return
    Path(result_dir).mkdir(exist_ok=True)
    category_file = Path(result_dir) / f"{result['category']}.json"

    if category_file.exists():
        with open(category_file, 'r', encoding="utf-8") as f:
            try:
                category_data = json.load(f)
                if result["url"] not in category_data["sites"]:
                    category_data["sites"].append(result["url"])
                else:
                    print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
            except json.JSONDecodeError:
                print(f"ERROR: corrupted file {category_file}, initialising a new file")
                category_data = {"sites": [], "tasks": []}
                category_data["sites"].append(result["url"])
    else:
        category_data = {"sites": [], "tasks": []}
        category_data["sites"].append(result["url"])

    with open(category_file, "w", encoding="utf-8") as f:
        json.dump(category_data, f, indent=2, ensure_ascii=False)
    
    print(f"Succès: URL {result['url']} ajoutée à {category_file}")

def update_progress(batch_file: str, last_site: str, result_dir: str = "results"):
    """Met à jour le fichier de suivi avec le batch en cours et le dernier site traité."""
    progress_file = Path(result_dir) / "progress.json"
    progress_data = {"batch_file": batch_file, "last_site": last_site}
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

def read_progress(result_dir: str = "results"):
    progress_file = Path(result_dir) / "progress.json"
    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Erreur : fichier de suivi {progress_file} corrompu, réinitialisation.")
                return {"batch_file": None, "last_site": None}
    return {"batch_file": None, "last_site": None}


def append_json_to_list_file(file_path, new_data):
        
        '''
        Ajouter les donnés a un json valide 
        
        '''
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