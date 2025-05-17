import json 
from tranco import Tranco
import requests
from bs4 import BeautifulSoup
import os
import re

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
      return f"https://feuwofranck.tech"

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


def get_category_list_from_folder(folder_path):
    
    try:
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".json")
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
