from tranco import Tranco
from llms.Model import AIAgent1
import requests
import os 
from bs4 import BeautifulSoup
import csv
import json

from utils.utils import write_on_json ,get_site ,get_site_description ,read_from_json , extract_category,extract_result ,getEnd ,WriteIntervale,get_site_content

Agent1 = AIAgent1()

def siteCategorisation(sites):
    for site in sites:
        print(f"Traitement du site : {site}")

        try:
            description = get_site_content(site)

            data = {
                "data": {
                    site: description
                }
            }

            prompt = Agent1.Promt_generation("Categorisation", data)
            example = read_from_json("./prompts/ExampleCategorisation.json")
            response = Agent1.call_lm(prompt, example)
            result = extract_result(response.content, site)
            

        except Exception as e:
            print(f" Erreur lors du traitement du site {site} : {e}")
            with open("./results/error.json", "a", encoding="utf-8") as f:
                 json.dump(site, f, ensure_ascii=False)
                 f.write("\n")

            continue  

    return 0





def process_sites_in_batches():

    with open("./results/confidence.json",'r',encoding='utf_8') as file :
        data = json.load(file)
        url = []
        for elt in data:
            url.append(elt["url"])
        siteCategorisation(url)
        






process_sites_in_batches()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

