from playwright.sync_api import sync_playwright
import os

user_data_dir = os.path.join(os.getcwd(), "unauth_all_config")

with sync_playwright() as p:
    extension_path = os.path.abspath("./Extension/auth_all/3.38_0")
    recaptcha_path= os.path.abspath("./Extension/dknlfmjaanfblgfdfebhijalfmhmjjjo/0.5.3_0")

    path_to_load = f"{extension_path},{recaptcha_path}"
    
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        viewport={'width': 1280, 'height': 800},
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--window-position=0,0',
            f"--disable-extensions-except={path_to_load}",
                f"--load-extension={path_to_load}",
                "--no-sandbox",
                "--start-maximized",
        ],
        ignore_default_args=['--enable-automation'],
        
    )
    

    page = browser.new_page()
    

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        window.navigator.chrome = {
            runtime: {},
        };
       

       
        Object.defineProperty(navigator, 'permissions', {
            query: () => Promise.resolve({ state: 'granted' }),
        });
    """)
    

    page.goto("https://reservaviajes.centraldevacaciones.com/user/signup.xhtml?keepurl=true&url=")
    
    captcha_sitekey = page.query_selector("div.g-recaptcha") 
    if captcha_sitekey:
        sitekey = captcha_sitekey.get_attribute('data-sitekey')
        print("Sitekey trouvé :", sitekey)
    else:
        print("Aucun CAPTCHA trouvé sur la page.")

        

    try:
        while True:
            page.wait_for_timeout(2000)  
    except KeyboardInterrupt:
        print("Fermeture du navigateur...")
        browser.close()
