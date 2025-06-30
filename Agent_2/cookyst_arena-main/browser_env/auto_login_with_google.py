from playwright.sync_api import sync_playwright
import argparse

from playwright.sync_api import Page
from typing import List, Dict
from time import sleep

import asyncio

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
        
        continue_button = page.locator('button:has-text("Continue")')
        if continue_button.is_visible():
            continue_button.click()
    except Exception as error:
        print(f'Error during login process: {error}')


def login_existing_account_popup(popup: Page) -> None:
    try:
        popup.locator('li:has-text("jeanclaudetagnedonfack@gmail.com")').first.click()
        sleep(5)
        
        continue_button = popup.locator('button:has-text("Continue")')
        if continue_button.is_visible():
            continue_button.click()
    except Exception as error:
        print(f'Error during login process in popup: {error}')


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

def try_google_login_elements(page:Page):
    from time import sleep

    matching_elements = find_google_login_elements(page)

    for index, item in enumerate(matching_elements):
        target_element = item['element']
        print(f"\nTentative {index + 1}/{len(matching_elements)} - Élément : \"{item['text']}\"")
        print("Clic imminent...")

        if target_element:
            tag_name = target_element.evaluate("e => e.tagName.toLowerCase()")
            if tag_name == 'button':
                try:
                    with page.context.expect_page() as popup_info:
                        target_element.click()
                    popup = popup_info.value
                    login_existing_account_popup(popup)
                    sleep(5)
                    return True
                except:
                    login_existing_account_page(page)
                    sleep(5)
                    return True
            else:
                target_element.click()
                page.wait_for_load_state('networkidle')
                login_existing_account_page(page)
                sleep(5)
                return True
        else:
            print(" Aucun élément de connexion Google trouvé.")
            return False


def connect_to_browser_and_login(browser,login_url:str,login_selector:str):
    #browser = p.chromium.connect_over_cdp(ws_endpoint)
   # context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = browser.new_page()
    page.goto(login_url)
    page.wait_for_load_state('networkidle')
    page.locator(login_selector).first.click()
    page.wait_for_load_state('networkidle')
    try_google_login_elements(page=page)
    #page.close()
    return page




# if __name__=="__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--ws',type=str,help="ws endpoint to control a remote browser")
#     parser.add_argument('--url',type=str,help='login url for google connection')

#     args = parser.parse_args()
#     connect_to_browser_and_login(args.ws,args.url)
