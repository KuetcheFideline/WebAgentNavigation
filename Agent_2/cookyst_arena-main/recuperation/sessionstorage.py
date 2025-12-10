import plyvel
import sqlite3
import json
import argparse
import os 




def decodebyte(raw):
    data = {}
    parts =raw.split(b"\x00\x01")
    if len(parts)==2 :
        data[parts[0].decode("utf-8")]=parts[1].decode("utf-8")
    elif len(parts)==3:
        domain = parts[0].decode("utf-8")
        sub_key = parts[1].decode("utf-8")
        value = parts[2].decode("utf-8")
        if domain not in sub_key :
            data[domain]= {}
        
        data[domain][sub_key] = value
    else :
        data[parts[0].decode('utf-8')]={}
    
    return data 


for file in os.listdir("../browser_env/profiles"):
    if file=="auth" or file =="notauth":
        for elt in os.listdir(os.path.join("../browser_env/profiles",file)) :
            pat = os.path.join(file,elt,"session_storage")

            os.makedirs(pat, exist_ok=True)

            for e in os.listdir(os.path.join("../browser_env/profiles",file,elt)):
                    local_storage_DB = os.path.join("../browser_env/profiles",file,elt,e,'Default/Session Storage')
                    db = plyvel.DB(local_storage_DB)
                    final =final = os.path.join(pat, f"{e}.json")

                    with open(final, 'w', encoding='utf-8') as jsonl_file:
                        datas = []
                        
                        for key, value in db:

                            keys = decodebyte(key)  
                            data= {}

                            for domain, second in keys.items():
                                if domain not in datas:
                                    data[domain] = {}

                                if isinstance(second, str):
                                    data[domain][second] = value.decode("utf-8", errors="ignore").replace('\u0001', '')
                                else:
                                    for sub_key, k in second.items():
                                        data[domain][sub_key] = k.replace('\u0001', '')
                            datas.append(data)
                    
                        jsonl_file.write(json.dumps(datas, ensure_ascii=False,indent=4) )

                    
                 


    






