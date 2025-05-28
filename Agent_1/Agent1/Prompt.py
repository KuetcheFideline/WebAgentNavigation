
from utils.utils import get_category_list_from_folder ,clean_domain
import os 
from jinja2 import Template
import  json

def formatage_Prompt(Path,data):
    values = {
    "site": "wikipedia",
    "task_id": 811,
    "start_url": "https://en.wikipedia.org",
    "topic": "quantum computing",
    "intent_template_id": 1000
}
    with open(Path,'r',encoding="utf-8") as f :
        template_format = f.read()
        template = Template(template_format)
        rendu = template.render(data)

        return json.loads(rendu)
        






def Generate_Prompt():
    categories = get_category_list_from_folder("./results")
    for elt in categories:
        folder = os.path.join('./results',elt)
        os.makedirs(folder,exist_ok=True)
        

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
                                response = formatage_Prompt("./prompts/template.json",{"site":domaine,"start_url":site,"task_id":task_id,"topic":resources_elt,"intent_template":task_elt['task'].split(':')[0].strip(),"intent":task_elt['task'].split(':')[0].strip()+resources_elt,"require_login":False})
                                filename = f"{elt}_task{task_id}_{domaine}_{file}.json"
                                response_file = os.path.join(folder, filename)
                      
                                with open(response_file, 'w', encoding="utf-8") as f:
                                    json.dump(response, f, ensure_ascii=False, indent=2)
                    for task_elt in aut_Task :
                        task_id +=1 
                        file =0
                        for resources_elt  in task_elt['resources'] :
                            for site in sites :
                                file+=1
                                domaine = clean_domain(site)
                                response = formatage_Prompt("./prompts/template.json",{"site":domaine,"start_url":site,"task_id":task_id,"topic":resources_elt,"intent_template":task_elt['task'].split(':')[0].strip(),"intent":task_elt['task'].split(':')[0].strip()+resources_elt,"require_login":True})
                                filename = f"{elt}_task{task_id}_{domaine}_{file}.json"
                                response_file = os.path.join(folder, filename)
                      
                                with open(response_file, 'w', encoding="utf-8") as f:
                                    json.dump(response, f, ensure_ascii=False, indent=2)
        




Generate_Prompt()