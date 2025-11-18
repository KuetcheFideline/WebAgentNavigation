from playwright.sync_api import sync_playwright,Locator
import argparse
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from playwright.sync_api import Page
from typing import List, Dict
from time import sleep
import asyncio
from .login_utils.sigin import detect_sigin
from .login_utils.utils import locate_robustly_without_labels,get_viewport_html
from .login_utils.google import detect_login_with_google
from .html_tools.configs.config import basic_attrs,mind2web_keep_attrs
from .html_tools.html_parser import HtmlParser
import os,logging
# Création du dossier logs/ s'il n'existe pas
os.makedirs('logs', exist_ok=True)
MAX_TOKENS_FOR_LLAMA = 7000
notsign_logger = logging.getLogger('notsign')
notsign_logger.setLevel(logging.INFO)
notsign_handler = logging.FileHandler('logs/notsignIn.log')
notsign_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
notsign_logger.addHandler(notsign_handler)

# Configuration du logger pour googleSignin.log
google_logger = logging.getLogger('googlesign')
google_logger.setLevel(logging.INFO)
google_handler = logging.FileHandler('logs/googleSignin.log')
google_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
google_logger.addHandler(google_handler)

nogoogle_logger = logging.getLogger('googlenosign')
nogoogle_logger.setLevel(logging.INFO)
nogoogle_handler = logging.FileHandler('logs/googleNoSignin.log')
nogoogle_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
nogoogle_logger.addHandler(nogoogle_handler)


locator_logger = logging.getLogger('locator')
locator_logger.setLevel(logging.INFO)
locator_handler = logging.FileHandler('logs/locator.log')
locator_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
locator_logger.addHandler(locator_handler)


content_logger = logging.getLogger('content')
content_logger.setLevel(logging.INFO)
content_handler = logging.FileHandler('logs/content.log')
content_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
content_logger.addHandler(content_handler)


def login_google_page(page: Page, email: str, password: str) -> None:
    try:
        page.fill('#identifierId', email)
        page.click('#identifierNext')
        sleep(6)  # Replaced waitForTimeout with sleep
        page.fill('input[name="Passwd"]', password)
        page.click('#passwordNext')
        sleep(5)
        page.locator('button:has-text("Continuer")').click()
    except Exception as error:
        print(f'Error during login process: {error}')


def login_google_popup(popup: Page, email: str, password: str) -> None:
    try:
        popup.wait_for_load_state('networkidle')
        popup.fill('#identifierId', email)
        popup.click('#identifierNext')
        sleep(6)
        popup.fill('input[name="Passwd"]', password)
        popup.click('#passwordNext')
        sleep(5)
        popup.locator('button:has-text("Continuer")').click()
    except Exception as error:
        print(f'Error during login process in popup: {error}')


def login_existing_account_page(page: Page) -> None:
    try:
        page.locator('li:has-text("jeanclaudetagnedonfack@gmail.com")').first.click()
        sleep(5)
        password_input = page.locator('input[type="password"][name="Passwd"]')
        if password_input.is_visible():
            password_input.fill("Jc1999!cm")
            sleep(1)
            next_button = page.locator('button:has-text("Suivant")') or page.locator('button:has-text("Next")')
            if next_button.is_visible():
                next_button.click()
                sleep(5)
                continue_button = page.locator('button:has-text("Continue")')
                if continue_button.is_visible():
                    continue_button.click()
                    sleep(3)


        else:
            print("not visible")
            continue_button = page.locator('button:has-text("Continue")')
            if continue_button.is_visible():
                continue_button.click()
                sleep(3)
    except Exception as error:
        print(f'Error during login process: {error}')


def login_existing_account_popup(popup: Page) -> None:
    try:
        popup.locator('li:has-text("jeanclaudetagnedonfack@gmail.com")').first.click()
        sleep(5)
        password_input = popup.locator('input[type="password"][name="Passwd"]')
        if password_input.is_visible():
            password_input.fill("Jc1999!cm")
            sleep(1)
            next_button = popup.locator('button:has-text("Suivant")') or popup.locator('button:has-text("Next")')
            if next_button.is_visible():
                next_button.click()
                sleep(5)
                continue_button = popup.locator('button:has-text("Continue")')
                if continue_button.is_visible():
                    continue_button.click()
                    sleep(3)



        else:
            print("not visible")
            continue_button = popup.locator('button:has-text("Continue")')
            if continue_button.is_visible():
                continue_button.click()
                sleep(3)
    except Exception as error:
        print(f'Error during login process: {error}')



def find_google_login_elements(page: Page) -> List[Dict]:
    matching_elements = []

    # Sélectionne tous les <button> et <a> de la page
    elements = page.query_selector_all("button, a")

    for element in elements:
        has_google_sub_element = element.evaluate("""
            el => {
                const subElements = el.querySelectorAll('img, svg');
                for (const subEl of subElements) {
                    const attributes = subEl.getAttributeNames();
                    for (const attr of attributes) {
                        const value = (subEl.getAttribute(attr) || '').toLowerCase();
                        if (value.includes('google')) {
                            return true;
                        }
                    }
                }
                return false;
            }
        """)

        text_content = (element.text_content() or "").lower()
        has_google_text = "google" in text_content

        if has_google_sub_element and has_google_text:
            matching_elements.append({
                "element": element,
                "text": element.text_content()
            })

    if matching_elements:
        print("Éléments de connexion Google trouvés :")
        for idx, item in enumerate(matching_elements):
            print(f"{idx+1}. {item['text']}")
    else:
        print("Aucun élément Google trouvé sur cette page.")

    return matching_elements

def try_google_login_elements(page:Page,locator:Locator,tag_name):
    from time import sleep
    target_element = locator
    if target_element:
        #tag_name = target_element.evaluate("e => e.tagName.toLowerCase()")
        if tag_name == 'button':
            try:
                with page.context.expect_page() as popup_info:
                    target_element.click()
                popup = popup_info.value
                login_existing_account_popup(popup)
                sleep(5)
                google_logger.info(f"Successful sign-in - URL: {page.url}")
                return True
            except:
                login_existing_account_page(page)
                sleep(5)
                google_logger.info(f"Successful sign-in - URL: {page.url}")
                return True
        else:
            target_element.click()
            page.wait_for_load_state('networkidle')
            login_existing_account_page(page)
            sleep(5)
            google_logger.info(f"Successful sign-in - URL: {page.url}")
            return True

    # matching_elements = find_google_login_elements(page)

    # for index, item in enumerate(matching_elements):
    #     target_element = item['element']
    #     print(f"\nTentative {index + 1}/{len(matching_elements)} - Élément : \"{item['text']}\"")
    #     print("Clic imminent...")

    #     if target_element:
    #         tag_name = target_element.evaluate("e => e.tagName.toLowerCase()")
    #         if tag_name == 'button':
    #             try:
    #                 with page.context.expect_page() as popup_info:
    #                     target_element.click()
    #                 popup = popup_info.value
    #                 login_existing_account_popup(popup)
    #                 sleep(5)
    #                 return True
    #             except:
    #                 login_existing_account_page(page)
    #                 sleep(5)
    #                 return True
    #         else:
    #             target_element.click()
    #             page.wait_for_load_state('networkidle')
    #             login_existing_account_page(page)
    #             sleep(5)
    #             return True
    #     else:
    #         print(" Aucun élément de connexion Google trouvé.")
    #         return False

def simplify_content(content):
    args = {
    'use_position': False,  
    'id_attr': 'id',      
    'label_generator': 'order', 
    'label_attr': 'data-testid',  
    'attr_list': mind2web_keep_attrs,     
    'prompt': 'refine_attr'            
    }
    hp = HtmlParser(content, args)
    packet = hp.parse_tree()
    simplified_home = packet['html']
    return simplified_home

def connect_to_browser_and_login(browser, login_url: str):

    page = browser.new_page()
    page.goto(login_url)

    client = page.context.new_cdp_session(page)
    viewport_size = {"width": 1280, "height": 720}
    # ================================ Call LLM 1 (Sign-in Button) =================================

    page.wait_for_load_state('domcontentloaded')
    #content_h = page.content()
    content_h = get_viewport_html(page=page, client=client, viewport_size=viewport_size)
    print("je suis de ce cote ma ")

    
    simplified_home = simplify_content(content=content_h)
    print("je suis de ce cote ma ")

    content_logger.info(f" LLM1 Content URL: {page.url} \n : {simplified_home}")

    data = detect_sigin(s_html=simplified_home)
    print("LLM 1 (Bouton Sign-In) a détecté:", data)
    timeout_click = False
    
    if data.get("action") == "negatif":
        print("Aucun bouton 'Sign In' détecté sur la page initiale.")
        notsign_logger.info(f"Not signed in - URL: {page.url}")
        return page
    else:
        try:

            initial_page_count = len(browser.pages)
            if locate_robustly_without_labels(page=page, llm_data=data) == None:
                return page
            locate_robustly_without_labels(page=page, llm_data=data).click(timeout=10000)
            sleep(2)
            if len(browser.pages) > initial_page_count:
                print("Nouvel onglet détecté, bascule vers celui-ci...")
                page = browser.pages[-1]
                page.bring_to_front()
        except PlaywrightTimeoutError:
            print("Timeout en cliquant sur le bouton 'Sign In'. Continuation...")
            timeout_click = True
        sleep(5)

    # ============================ End LLM 1 Call ===============================================

    # ============================ CALL LLM 2 (Google Button) ===================================
    
    page.wait_for_load_state('domcontentloaded')
    client = page.context.new_cdp_session(page)
    content_h = get_viewport_html(page=page, client=client, viewport_size=viewport_size)
    content_login_simplified = simplify_content(content_h)
    content_logger.info(f" LLM2 Content URL: {page.url} \n : {content_login_simplified}")
    data_g = detect_login_with_google(s_html=content_login_simplified)
    print("LLM 2 (Bouton Google - sur la page principale) a détecté:", data_g)

 
    if data_g.get("tag") == "iframe":
        locator_logger.info("Stratégie iframe activée : analyse du contenu du premier iframe de la page.")
        try:
       
            frame_locator = page.frame_locator("iframe").first
            
            frame_locator.wait_for(state="attached", timeout=10000)
            locator_logger.info("Premier iframe trouvé. Extraction de son contenu HTML.")

            iframe_content_html = frame_locator.evaluate("() => document.documentElement.outerHTML")
            simplified_iframe_content = simplify_content(iframe_content_html)

            locator_logger.info("Contenu de l'iframe extrait, envoi à l'LLM pour détection du bouton...")
            data_inside_iframe = detect_login_with_google(s_html=simplified_iframe_content)
            print("LLM 3 (Analyse de l'iframe) a détecté:", data_inside_iframe)

            if data_inside_iframe.get("action") != "negatif":
                
                locator_logger.info("Bouton détecté dans l'iframe. Tentative de clic.")
                button_locator_in_frame = locate_robustly_without_labels(
                    page=frame_locator, 
                    llm_data=data_inside_iframe
                )
                if button_locator_in_frame == None:
                    page.goto(login_url)
                    return page
                
                try_google_login_elements(
                    page=page, 
                    locator=button_locator_in_frame, 
                    tag_name=data_inside_iframe.get('tag')
                )
            else:
                locator_logger.warning(f"L'LLM a détecté un iframe mais n'a trouvé aucun bouton Google à l'intérieur sur {page.url}")

        except PlaywrightTimeoutError:
            locator_logger.error(f"Timeout : impossible de trouver ou d'analyser l'iframe sur {page.url}.")
        except Exception as e:
            locator_logger.error(f"Erreur inattendue lors du traitement de l'iframe sur {page.url}: {e}")

    elif data_g.get("action") == "negatif":
        if timeout_click:
            locator_logger.info(f"Échec de la localisation - pas de bouton Google trouvé après timeout - URL: {page.url}")
        else:
            nogoogle_logger.info(f"Échec de la localisation - l'LLM a confirmé l'absence de bouton Google - URL: {page.url}")
        pass

    else:
        locator_logger.info("Élément de connexion Google détecté directement sur la page.")
        try:
            locator = locate_robustly_without_labels(page=page, llm_data=data_g)
            if locator == None:
                page.goto(login_url)
                return page
            try_google_login_elements(page=page, locator=locator, tag_name=data_g.get('tag'))
        except PlaywrightTimeoutError:
            locator_logger.error(f"Timeout en essayant de localiser/cliquer sur l'élément direct sur {page.url}")
            pass

    return page




# if __name__=="__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--ws',type=str,help="ws endpoint to control a remote browser")
#     parser.add_argument('--url',type=str,help='login url for google connection')

#     args = parser.parse_args()
#     connect_to_browser_and_login(args.ws,args.url)
