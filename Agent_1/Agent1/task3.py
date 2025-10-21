from llms.Model import AIAgent1
import requests
import os
from bs4 import BeautifulSoup
import asyncio
import json
from playwright.async_api import async_playwright, Playwright
from utils.error import read_from_json, extract_category, extract_result, getEnd, WriteIntervale, get_site_content,append_json_to_list_file
import re
import time 



async def get_playwriht(playwright: Playwright, site: str):
    chromium = playwright.chromium
    #browser = await chromuim.launch()
    browser = await chromium.launch(
    headless=True,           
    slow_mo=1000,            
    args=["--start-maximized"] 
)
    page = await browser.new_page()
    await page.goto(site)
    html_content = await page.content()  
    await browser.close()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    
    text = re.sub(r'\s+', ' ', text)
    
    return text

Agent1 = AIAgent1()

async def siteCategorisation(playwright: Playwright, sites):
    for site in sites:
        try:
            description = await get_playwriht(playwright, site)  
            data = {
                "data": {
                    site: description
                }
            }

            prompt = Agent1.Promt_generation("Categorisation", data)
            example = read_from_json("./prompts/ExampleCategorisation.json")
            response = Agent1.call_lm(prompt, example)


            try:
                result = extract_result(response.content, site)

            except Exception as e:
                 print(f" Erreur lors de l'extraction des resultats  {site}  : {e}")
                 append_json_to_list_file("./results/confidence.json", {"message":response.content ,"site": site, "error": str(e)})
            continue 
            
        except Exception as e:
            print(f"Erreur lors du traitement du site {site} : {e}")
            with open("./results100/error.json", "a", encoding="utf-8") as f:
                json.dump(site, f, ensure_ascii=False)
                f.write("\n")
            continue
    return 0

# Fonction asynchrone pour traiter les sites par lots
async def process_sites_in_batches(playwright: Playwright):
    with open("./results1000/low_confidence.json", 'r', encoding='utf_8') as file:
        data = json.loads(file.read())
    #    url = [line.strip().replace('"', '') for line in file if line.strip()]
    # print(url)
    
    url = []
   
    for elt in data :
        print(elt['site'])
    # for elt in data:
    #     for it in elt:
    #         for key, elt in it.items():
        url.append(elt['site'])
    await siteCategorisation(playwright, url)  # Passe playwright en paramètre

# Fonction principale qui démarre l'exécution
async def main():
    async with async_playwright() as playwright:
        await process_sites_in_batches(playwright)  # Passe playwright

# Lancer le programme asynchrone
asyncio.run(main())