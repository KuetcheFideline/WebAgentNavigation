from playwright.sync_api import sync_playwright
import os

user_data_dir = os.path.join(os.getcwd(), "france_google_profile")

with sync_playwright() as p:

    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        viewport={'width': 1280, 'height': 800},
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--window-position=0,0',
        ],
        ignore_default_args=['--enable-automation'],
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        locale='fr-FR',
        timezone_id='Europe/Paris',
        geolocation={'latitude': 48.8566, 'longitude': 2.3522},  # Coordonnées de Paris
        permissions=['geolocation'],

    )
    

    page = browser.new_page()
    

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        window.navigator.chrome = {
            runtime: {},
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['fr-FR', 'fr', 'en-US', 'en'],
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        Object.defineProperty(navigator, 'permissions', {
            query: () => Promise.resolve({ state: 'granted' }),
        });
    """)
    

    page.goto("https://accounts.google.com/signin?hl=fr")
    
    print("Le navigateur est ouvert. Connecte-toi à ton compte Google.")
    print("Ferme ce script ou le navigateur quand tu auras terminé.")
    

    try:
        while True:
            page.wait_for_timeout(1000)  # 1 seconde
    except KeyboardInterrupt:
        print("Fermeture du navigateur...")
        browser.close()
