
from utils.utils import get_category_list_from_folder ,clean_domain
import os 
from jinja2 import Template
import  json
import csv
from urllib.parse import urlparse
def formatage_Prompt(Path,data):

    with open(Path,'r',encoding="utf-8") as f :
        template_format = f.read()
        template = Template(template_format)
        rendu = template.render(**data)

        return json.loads(rendu)
    

def googleMatch(url) :
    googlePath = "./prompts/signinwithgoogle.csv"
    netloc_url = urlparse(url).netloc.lower()
    google_selector = ""
    try :
        with open (googlePath,'r',encoding='utf-8') as f :
            csv_data = csv.DictReader(f)
            if not {'graph_name', 'netloc', 'url', 'selector'}.issubset(csv_data.fieldnames):
                print(f"Error: CSV file {googlePath} missing required columns")
                return google_selector
            for row in csv_data :
                if row['netloc'].lower() == netloc_url:
                    google_selector = row['selector']
                    return google_selector

          
            f.seek(0)
            next(csv_data)
            for row in csv_data:
                if netloc_url in row["url"].lower() or row["url"].lower() in netloc_url:
                    google_selector = row['selector']
                    break
    except FileNotFoundError:
        print(f"Error: CSV file {googlePath} not found")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    return google_selector
        
    



def Generate_Prompt():
    categories = get_category_list_from_folder("./results")
    for elt in categories:
        folder = os.path.join('./results',"AUTH")
        folder1 = os.path.join('./results',"Non_AUTH")

        os.makedirs(folder,exist_ok=True)
        os.makedirs(folder1,exist_ok=True)

                


        file = "./results/"+ elt +".json"
        with open(file,'r',encoding='utf-8') as f :
            data = json.load(f)
            sites = data.get("sites")
            if data.get("tasks"):
                for task_group in data["tasks"]:
                    aut_Task =task_group.get("authenticated")
                    Task=task_group.get("unauthenticated")
                    task_id = 0
                    for task_elt in Task :
                        task_id +=1 
                        file =0
                        for resources_elt  in task_elt['resources'] :
                            for site in sites :

                                file+=1
                                domaine = clean_domain(site)
                                response = formatage_Prompt("./prompts/template.json",{"site":domaine,"start_url":site,"task_id":task_id,"topic":resources_elt,"intent_template":task_elt['task'].split(':')[0].strip() +" {{topic}} ","intent":task_elt['task'].split(':')[0].strip() + " " +resources_elt,"require_login":"false" })
                                filename = f"{elt}_task{task_id}_{domaine}_{file}.json"
                                response_file = os.path.join(folder1, filename)
                      
                                with open(response_file, 'w', encoding="utf-8") as f:
                                    json.dump(response, f, ensure_ascii=False, indent=2)
                    for task_elt in aut_Task :
                        task_id +=1 
                        file =0
                        for resources_elt  in task_elt['resources'] :
                            for site in sites :
                                login = googleMatch(site)

                                file+=1
                                domaine = clean_domain(site)
                                response = formatage_Prompt("./prompts/template.json",{"site":domaine,"start_url":site,"task_id":task_id,"topic":resources_elt,"intent_template":task_elt['task'].split(':')[0].strip(),"intent":task_elt['task'].split(':')[0].strip()+ " " +resources_elt,"require_login":"true","login_selector":login})
                                filename = f"{elt}_task{task_id}_{domaine}_{file}.json"
                                response_file = os.path.join(folder, filename)
                      
                                with open(response_file, 'w', encoding="utf-8") as f:
                                    json.dump(response, f, ensure_ascii=False, indent=2)
        




Generate_Prompt()