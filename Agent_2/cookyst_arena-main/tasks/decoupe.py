
import os
import json
import requests
import random


file = ""
result = ""

authid =[]
unAuthid= []

for file in os.listdir() :
    if  os.path.isdir(os.path.join(os.getcwd(),file)) :
        data_name = file.split("_")
        if len(data_name)>=2:
            country = file.split("_")[0]
            user = file.split("_")[1]
            
            for f in os.listdir(os.path.join(os.getcwd(),file)) :
                print(f)

                if os.path.isfile(os.path.join(os.getcwd(),file,f)) and f.endswith('.json') :
                    with open(os.path.join(os.getcwd(),file,f),'r',encoding="utf-8") as filejson:
                        data =json.load(filejson)
                        
                        Data = []
                        for elt in data["taches"] :
                            print(elt)
                            
                            if elt["require_login"]:
                                id = random.randint(0,12)
                                while id in authid :
                                    id = random.randint(0,12)
                                    
                                authid.append(id)
                                elt["task_id"]=id
                                elt["google_login"]=True

                                Folder = "AUTH/"+country +"/"+user
                            else :
                                Folder = "NotAUTH/"+country +"/"+user
                                elt["google_login"]=False

                                id = random.randint(0,12)
                                while id in unAuthid:
                                    id = random.randint(0,12)
                                   
                                unAuthid.append(id)
                                elt["task_id"]=id
                            if not os.path.exists(Folder):
                                os.makedirs(Folder)
                            filename= os.path.join(Folder,str(elt["task_id"])+".json")
                            with open (filename,'w',encoding="utf-8") as f:
                                json.dump(elt,f,ensure_ascii=False,indent=2)
            authid.clear()
            unAuthid.clear()
        
                
        else :
            print(" pas un dossier de travaille ")



                

                        