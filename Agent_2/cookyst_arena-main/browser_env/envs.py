import json
from datetime import datetime ,date
import re
import time
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union
import os
import numpy as np
import numpy.typing as npt
from beartype import beartype
from beartype.door import is_bearable
from gymnasium import Env
from gymnasium.spaces import Box, Text
from playwright.sync_api import (
    CDPSession,
    Page,
    Playwright,
    ViewportSize,
    expect,
    sync_playwright,
)

from .utils import diff_dictionaries
from .auto_login_with_google import connect_to_browser_and_login
from .actions import Action, execute_action, get_action_space
from .processors import ObservationHandler, ObservationMetadata
from .utils import (
    AccessibilityTree,
    DetachedPage,
    Observation,
    png_bytes_to_numpy,
)

import base64
from .scripts import *

@dataclass
class PlaywrightScript:
    function: str  # goto, get_by_role
    destination: str  # https://www.google.com/, combobox
    name: str | None = None  # Search, Avatar 2009
    operation: str | None = None  # click, fill, press
    value: str | None = None  # avatar movie, Enter


def parse_action(action: str) -> PlaywrightScript:
    splitted = action.strip().split(" ")
    assert len(splitted) >= 2
    match splitted[:2]:
        case ["goto", url]:
            assert len(splitted) == 2
            return PlaywrightScript("goto", url)
        case ["get_by_role", destination]:
            assert len(splitted) >= 4
            match splitted[2:]:
                case [name, operation]:
                    return PlaywrightScript(
                        "get_by_role", destination, name, operation
                    )
                case [name, operation, value]:
                    return PlaywrightScript(
                        "get_by_role", destination, name, operation, value
                    )
                case _:
                    raise ValueError("Invalid action")
        case _:
            raise ValueError(f"Invalid action {action}")


class ScriptBrowserEnv(Env[dict[str, Observation], Action]):
    """
    The goal of this environment is to produce a prototype of a browser environment.
    In the end, we want to support a fully configurable browser environment with wide
    range of action spaces and observation spaces, both structured and unstructured.
    But in this prototype, we just support action space specified by Playwright script,
    and observation space is the html content of the page.
    """

    @beartype
    def __init__(
        self,
        consent:str,
        connect:str,
        country:str,

        persistent:bool,
        max_page_length: int = 8192,
        headless: bool = True,
        slow_mo: int = 0,
        observation_type: str = "html",
        current_viewport_only: bool = False,
        viewport_size: ViewportSize = {"width": 1280, "height": 720},
        save_trace_enabled: bool = False,
        sleep_after_execution: float = 0.0,
    
    ):
        # TODO: make Space[Action] = ActionSpace
        self.action_space = get_action_space()  # type: ignore[assignment]
        self.headless = headless
        self.slow_mo = slow_mo
        self.current_viewport_only = current_viewport_only
        self.reset_finished = False
        self.viewport_size = viewport_size
        self.save_trace_enabled = save_trace_enabled
        self.sleep_after_execution = sleep_after_execution
        self.storage_file=""
        self.login_require=False
        #consent update
        self.consent = consent
        #login_require = persistent
        self.context = None
        self.browser = None
        self.country = country
        self.connect = connect

        match observation_type:
            case "html" | "accessibility_tree":
                self.text_observation_type = observation_type
                self.image_observation_type = ""
                self.main_observation_type = "text"
            case "image":
                self.image_observation_type = observation_type
                self.text_observation_type = ""  # type: ignore[assignment]
                self.main_observation_type = "image"
            case _:
                raise ValueError(
                    f"Unsupported observation type: {observation_type}"
                )

        self.observation_handler = ObservationHandler(
            self.main_observation_type,
            self.text_observation_type,
            self.image_observation_type,
            self.current_viewport_only,
            self.viewport_size,
        )

        self.observation_space = (
            self.observation_handler.get_observation_space()
        )
    def initialize_storage_state(self,storage_file: str) -> None:

        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        if not os.path.exists(storage_file):
            with open(storage_file, "w") as f:
                json.dump({"cookies": [], "origins": []}, f)


    def create_profil_user(self,user):
        '''
        cette fonction est utiliser pour configurer le navigateur en fonction de chaque utilsateur 
        '''

        datadir =os.path.join(os.getcwd(),f"browser_env/profiles/{self.connect.lower()}/{self.consent}/{user}")

        base= os.path.join( os.getcwd(),"Navigateur/unauth_all_config")

        if not os.path.exists(datadir):
            os.makedirs(base, exist_ok=True)

            shutil.copytree(base,datadir)
        

        return datadir            
        
    def create_account_with_google(self,start_url):
                page = connect_to_browser_and_login(self.browser,login_url=start_url)



    @beartype
    def setup(self, config_file: Path | None = None) -> None:
        self.context_manager = sync_playwright()
        self.playwright = self.context_manager.__enter__()
        """
        Ici le navigateur est lancé, donc c'est la qu'on charge les config et les extensions
        """
        langue = {
                'fr': 'fr-FR',
                'en': 'en-GB',
                'de': 'de-DE',
                'es': 'es-ES',
                'it': 'it-IT',
                'nl': 'nl-NL',
                'pt': 'pt-PT',
                'pl': 'pl-PL',
                'sv': 'sv-SE',
                'da': 'da-DK',
                'fi': 'fi-FI',
                'cs': 'cs-CZ',
                'sk': 'sk-SK',
                'ro': 'ro-RO',
                'bg': 'bg-BG',
                'el': 'el-GR'
            }
        match = re.search(r'/([A-Za-z]{2}/\d{4})',str(config_file))
        user =" test"
        if match :
            user = match.group(1)  
        user = user.replace("/","_")

        userDataDir= self.create_profil_user(user)
        if config_file:
            with open(config_file, "r") as f:
                instance_config = json.load(f)
        else:
            instance_config = {}
        

        extension_path = os.path.join(os.getcwd(),"Navigateur/Extension/auth_all/3.38_0")
        recaptcha_path= os.path.join(os.getcwd(),"Navigateur/Extension/dknlfmjaanfblgfdfebhijalfmhmjjjo/0.5.2_0")
       
        google_require = instance_config.get("google_login",False)
        path_to_load = f"{extension_path},{recaptcha_path}"
        args_commun = [
            '--disable-blink-features=AutomationControlled',
            '--start-maximized',
            '--no-sandbox',
            f"--disable-extensions-except={path_to_load}",
                f"--load-extension={path_to_load}",
                "--no-sandbox",
                "--start-maximized",
            ]
        self.browser = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=userDataDir,
                    headless=False,
                    slow_mo=self.slow_mo,
                    args=args_commun,
                    viewport=self.viewport_size,
                    locale=f"{langue[self.country]}"
                    # proxy={
                    #     "server": "brd.superproxy.io:33335",
                    #     "username": f"brd-customer-hl_efb03598-zone-residential_proxy1-country-{self.country}",
                    #     "password": "gwynyg0rp09g",
                    # },
                )

        storage_state = instance_config.get("storage_state", None)
        start_url = instance_config.get("start_url", None)
        self.context = self.browser
            # for page in self.context.pages:
            #     try:
            #         page.close()
            #     except Exception as e:
            #         print(f"Could not close page: {e}")
        
        if self.save_trace_enabled:
            self.context.tracing.start(screenshots=True, snapshots=True)

        if start_url:

            start_urls = start_url.split(" |AND| ")
            created_pages=[]
            for url in start_urls:
                if google_require :
                    page = self.context.new_page()
                    page.goto(url)

                    
                else:
                    page = self.context.new_page()
                    page.goto(url)

             
                client = page.context.new_cdp_session(
                    page
                )

                if self.text_observation_type == "accessibility_tree":
                    client.send("Accessibility.enable")
                
                page.client = client
                created_pages.append(page)

                if created_pages:
                    self.page = created_pages[-1]
                    self.page.bring_to_front()

                
           
        else:
            self.page = self.context.new_page()
            client = self.page.context.new_cdp_session(self.page)
            if self.text_observation_type == "accessibility_tree":
                client.send("Accessibility.enable")
            self.page.client = client 
        

    def get_page_client(self, page: Page) -> CDPSession:
        # #return page.context.new_cdp_session(page)
        # if login_require:
        #     #return page.context.new_cdp_session(page)
        #     return page.client
        # else:
        return page.client  # type: ignore

    def _get_obs(self) -> dict[str, Observation]:
        obs = self.observation_handler.get_observation(
            self.page, self.get_page_client(self.page)
        )
        return obs

    def _get_obs_metadata(self) -> dict[str, ObservationMetadata]:
        metadata = self.observation_handler.get_observation_metadata()
        return metadata

    @beartype
    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, str] | None = None,
    ) -> tuple[dict[str, Observation], dict[str, Any]]:
        """
        Reset the environment.
        :param options: options for the environment. The current supported options are:
            - "storage_state": the storage state of the browser. It is a file path to a json file.
        """
        super().reset(seed=seed, options=options)
        if self.reset_finished:
            self.context_manager.__exit__()

        
        if options is not None and "config_file" in options:
            config_file = Path(options["config_file"])
            if config_file.exists():

                self.setup(config_file=config_file)


           
            else:

                raise ValueError(f"Config file {config_file} does not exist.")
                
        else:

            self.setup()
        self.reset_finished = True


        
        if self.sleep_after_execution > 0:
            time.sleep(self.sleep_after_execution)
           
        images = self.modify_page()


        observation = self._get_obs()
        

        observation_metadata = self._get_obs_metadata()
        info = {
            "page": DetachedPage(self.page.url, ""),
            "fail_error": "",
            "observation_metadata": observation_metadata,
        } 

 
        return (observation, info)

    def save_trace(self, trace_path: str | Path) -> None:
        if self.save_trace_enabled:
            self.context.tracing.stop(path=trace_path)

    def close(self) -> None:
        if self.reset_finished:
            self.context_manager.__exit__()

    def step(
        self, action: Action
    ) -> tuple[dict[str, Observation], float, bool, bool, dict[str, Any]]:
        if not self.reset_finished:
            raise RuntimeError("Call reset first before calling step.")

        success = False
        fail_error = ""
        try:
            print("Executing action:", action)
            self.page = execute_action(
                action,
                self.page,
                self.context,
                self.observation_handler.action_processor,
            )
            success = True
        except Exception as e:
            fail_error = str(e)

        # hard sleep TODO[shuyanzh] suboptimal, may need to check network
        if self.sleep_after_execution > 0:
            time.sleep(self.sleep_after_execution)

        images = self.modify_page()
        
        observation = self._get_obs()
        observation_metadata = self._get_obs_metadata()

        info = {
            "page": DetachedPage(self.page.url, self.page.content()),
            "fail_error": fail_error,
            "observation_metadata": observation_metadata,
        }
        
        msg = (
            observation,
            float(success),  # reward
            False,  # terminated
            False,  # truncated
            info,
        )
        return msg

    def remove_image(self,path):
        files = os.listdir(path)
        
        marked_files = [file for file in files if file.startswith('marked')]
        
        if len(marked_files) == 3:
            if "marked3.png" in marked_files:
                os.remove(os.path.join(path, "marked3.png"))
            
            if "marked2.png" in marked_files:
                os.rename(os.path.join(path, "marked2.png"), os.path.join(path, "marked3.png"))
            
            if "marked1.png" in marked_files:
                os.rename(os.path.join(path, "marked1.png"), os.path.join(path, "marked2.png"))
            
        
        elif len(marked_files) == 2:
            if "marked2.png" in marked_files:
                os.rename(os.path.join(path, "marked2.png"), os.path.join(path, "marked3.png"))
            
            if "marked1.png" in marked_files:
                os.rename(os.path.join(path, "marked1.png"), os.path.join(path, "marked2.png"))
            
        
        elif len(marked_files) == 1:
            if "marked1.png" in marked_files:
                os.rename(os.path.join(path, "marked1.png"), os.path.join(path, "marked2.png"))
        else :
            pass
        
        print("bonjour")

        return "marked1.png"




    def modify_page(self):
        self.page.wait_for_timeout(500)
        try:
            self.page.evaluate(remove_id_script)
        except:
            pass
        
        img_bytes = self.page.screenshot(path="output/screenshot_raw.png")
        raw_image = base64.b64encode(img_bytes).decode()
        
        self.page.evaluate(mix_marker_script)
        self.page.wait_for_timeout(100)
        
        # get all clickable elements
        start_id = 0
        elem_items, start_id = self.page.evaluate(get_rect_script, {
            "selector": ".possible-clickable-element",
            "startIndex": start_id
        })
        
        # get ocr items
        ocr_items = []
        # ocr_items = page.evaluate(canva_handler_script)
        # svg_items, _ = page.evaluate(get_rect_script, {"selector": "svg", "startIndex": -1})
        # ocr_items = ocr_items + svg_items
        # ocr_items, start_id = get_canva_images(ocr_items, img_bytes, start_id)
        
        items = elem_items + ocr_items
        
        # mark our own labels and get the images
        items = self.page.evaluate(label_marker_script, items)
        path = self.remove_image("output/")


        img_bytes = self.page.screenshot(path="output/marked1.png")

        marked_image = base64.b64encode(img_bytes).decode()
        
        self.page.evaluate(remove_label_mark_script)
        
        return {
            "raw_image": raw_image,
            "marked_image": marked_image,
        }
   

    def load_cookies(self):
         return self.context.cookies()
       


       
    

    def get_session_storage(self) -> dict:
        return self.page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))")

    def get_local_storage(self) -> dict:
        return self.page.evaluate("() => Object.fromEntries(Object.entries(localStorage))")

    def get_cookies(self) -> list:
        return self.context.cookies()
    def get_all_storage_state(self) -> dict:
        return {
            "cookies": self.get_cookies(),
            "localStorage": self.get_local_storage(),
            "sessionStorage": self.get_session_storage()
        }     


    def json_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def save_storage(self, initial_state, file,url):
        """
        Compare l'état initial du stockage avec l'état final, 
        calcule la différence et la sauvegarde dans un fichier.
        """
        
        final_state = self.get_all_storage_state()

        local_storage_diff = diff_dictionaries(initial_state["localStorage"], final_state["localStorage"])
        session_storage_diff = diff_dictionaries(initial_state["sessionStorage"], final_state["sessionStorage"])

        # On crée une clé sous forme de chaîne pour identifier un cookie
        initial_cookies = { f"{c.get('name', '')}|{c.get('domain', '')}|{c.get('path', '')}": c for c in initial_state["cookies"] }
        final_cookies = { f"{c.get('name', '')}|{c.get('domain', '')}|{c.get('path', '')}": c for c in final_state["cookies"] }
        
        cookies_diff = diff_dictionaries(initial_cookies, final_cookies)

        diff_report = {
            "metadata": {
                "initial url": url,
                "final_url": self.page.url,

                "timestamp":datetime.now().isoformat()
            },
            "cookies": cookies_diff,
            "localStorage": local_storage_diff,
            "sessionStorage": session_storage_diff,
        }
        file = Path(file)
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(diff_report, f, indent=4, default=getattr(self, 'json_serializer', str))

        print(f"Rapport de différence de stockage sauvegardé dans : {file}")