# worker.py

import os
import time
import queue 
import logging
from  llms.Model import AIAgent1
from utils.utils import get_site_description, parse_llm_result, read_from_json
from bs4 import BeautifulSoup
import re 

from playwright.async_api import Playwright ,async_playwright
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(message)s')




async def get_playwright(playwright: Playwright, site: str):
    chromium = playwright.chromium
    #browser = await chromuim.launch()
    browser = await chromium.launch(
    headless=False,           
    slow_mo=1000,            
    args=["--start-maximized"] 
)
    
    try:

        page = await browser.new_page()
        await page.goto(site)
        html_content = await page.content()  
        await browser.close()
    except Exception as e :
        logging.error(f"Erreur Playwright pour le site {site}: {e}")
        return f"REQUEST_ERROR: {e}"
    finally:
        await browser.close()


    soup = BeautifulSoup(html_content, 'html.parser')
        
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    
    text = re.sub(r'\s+', ' ', text)
    
    return text


async def  run_worker(task_queue, results_queue, completion_queue) :
    """
    Fonction cible pour les processus travailleurs.
    Traite une URL, envoie le résultat au Writer, et une confirmation au Main.
    """
    logger = logging.getLogger()
    
    # Chaque worker a sa propre instance de l'agent
    try:
        agent = AIAgent1()
        examples = read_from_json("./prompts/ExampleCategorisation.json")
    except Exception as e:
        logger.error(f"Impossible d'initialiser l'agent ou de lire les exemples: {e}")
        return 

    logger.info("Worker démarré et prêt.")
    async with async_playwright () as playwright :

        while True:
            try:
                task = task_queue.get()
                if task is None:
                    break

                site, origin_file = task
                
                try:
                    logger.info(f"Traitement de {site} depuis {origin_file}")
                    description = await get_playwright(playwright,site)

                    if description.startswith("REQUEST_ERROR:"):
                        error_report = {
                            "type": "request_error",
                            "data": {"file": origin_file, "site": site, "error": description}
                        }
                        results_queue.put(error_report)
                        continue

                    data_for_prompt = {"data": {site: description}}
                    prompt_text = agent.Promt_generation("Categorisation", data_for_prompt)
                    response = agent.call_lm(prompt_text, examples)

                    parsed_result = parse_llm_result(response.content, site, origin_file)
                    results_queue.put(parsed_result)

                except Exception as e:
                    logger.error(f"Erreur inattendue lors du traitement de {site}: {e}")
                    error_report = {
                        "type": "processing_error",
                        "data": {"file": origin_file, "site": site, "error": str(e)}
                    }
                    results_queue.put(error_report)

                finally:
                    completion_queue.put(origin_file)

            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                logger.critical(f"Erreur critique dans la boucle du worker: {e}")

    logger.info("Worker terminé.")




def start_worker_process(task_queue,results_queue,completion_queue):
    asyncio.run(run_worker(task_queue,results_queue,completion_queue))