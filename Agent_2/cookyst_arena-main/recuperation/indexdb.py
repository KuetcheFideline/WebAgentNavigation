
"""
recuperation du fichier de indexDB  : Comment ca ve se passer 


"""

import plyvel
import sqlite3
import json
import argparse
import os 
import time 
import subprocess


def chrome_comparator(key_a, key_b):
    if key_a == key_b:
        return 0
    return -1 if key_a < key_b else 1


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
            pat = os.path.join(file,elt,"indexedDB")

            os.makedirs(pat, exist_ok=True)

            for e in os.listdir(os.path.join("../browser_env/profiles",file,elt)):
                    pat = os.path.join(file,elt,"indexedDB",e)


                    os.makedirs(pat, exist_ok=True)
                    parent_path = os.path.join("../browser_env/profiles",file,elt,e,"Default","IndexedDB")
                    if os.path.exists(parent_path): 
                        datas= []
                        for site in os.listdir(parent_path):
                            data = {}

                            
                            data[site]=[]
                            index_DB = os.path.join("../browser_env/profiles",file,elt,e,"Default","IndexedDB",site)
                            result = subprocess.run(
                                    ['dfindexeddb', 'db', '-s', index_DB, '--format', 'chrome', '-o', 'jsonl'],
                                    capture_output=True,
                                    text=True
                                )
                            if result.returncode == 0:
                                lines = result.stdout.strip().splitlines()
                                for line in lines : 
                                    if line :
                                        obj = json.loads(line)
                                        valeur = obj.get('value')
                                        type = obj.get('type')
                                        if type != 0 and isinstance(valeur, dict):
                    
                                            
                                         data[site].append(valeur)
                            else:

                                print(f"Erreur: {result.stderr}")
                            
                                    
                            final =final = os.path.join(pat,f"{site}.json")
                            datas.append({"data":data})
                        with open(final, 'w', encoding='utf-8') as jsonl_file:
                                # for obj in data :
                                    jsonl_file.write(json.dumps(data, ensure_ascii=False,indent=4))

                                
                 


    






