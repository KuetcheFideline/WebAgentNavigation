import json
import re
import time
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
        persistent:bool,
        max_page_length: int = 8192,
        headless: bool = False,
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

    @beartype
    def setup(self, config_file: Path | None = None) -> None:
        self.context_manager = sync_playwright()
        self.playwright = self.context_manager.__enter__()
        """
        Ici le navigateur est lancé, donc c'est la qu'on charge les config et les extensions
        """
        extensionPaths = {
            "none":"browser_env/Consent-O-Matic/config/consent-accept-none",
            "all":"browser_env/Consent-O-Matic/config/consent-accept-all",
            "partial":"browser_env/Consent-O-Matic/config/consent-accept-partial",
        }
        persistent_chromium = {
            "none":"browser_env/profiles/persistent/google-profile-none",
            "all":"browser_env/profiles/persistent/google-profile-all",
            "partial":"browser_env/profiles/persistent/google-profile-partial"
        }

        persistent_not_chromium = {
            "none":"browser_env/profiles/not_persistent/google-profile-none",
            "all":"browser_env/profiles/not_persistent/google-profile-all",
            "partial":"browser_env/profiles/not_persistent/google-profile-partial"
        }
        storage = {
            "all": {"storage_file": "state_accept_all.json"},
            "none": {"storage_file": "state_reject_all.json"},
            "partial": {"storage_file": "state_partial.json"}
        }
        selectedConset = extensionPaths[self.consent]
        storage_dir="browser_env/profiles/storage_state"
        self.storage_file = storage_file = os.path.join(storage_dir, storage[self.consent]["storage_file"])
        self.initialize_storage_state(storage_file=storage_file)

                    # Charger le storage_state s'il existe
        

        if config_file:
            with open(config_file, "r") as f:
                instance_config = json.load(f)
        else:
            instance_config = {}
        geolocation = instance_config.get("geolocation", None)
        # login with google operation
        login_require = instance_config.get("require_login",False)
        login_url = instance_config.get("login_url",None)
        login_selector = instance_config.get("login_selector",None)
        self.login_require = login_require
        if login_require:
            profile_dictionary = persistent_chromium
        else:
            profile_dictionary = persistent_not_chromium
        
        selectedContext = profile_dictionary[self.consent]

        
        

            
       
        selectedContext = profile_dictionary[self.consent]

        args_commun = [
            '--disable-blink-features=AutomationControlled',
            '--start-maximized',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            f'--disable-extensions-except={selectedConset}',
            f'--load-extension={selectedConset}'
        ]
        
       
        self.browser = self.playwright.chromium.launch_persistent_context(
            headless=False,
            slow_mo=self.slow_mo, 
            args=args_commun,
            user_data_dir=selectedContext,
            viewport=self.viewport_size,
            geolocation=geolocation,
            device_scale_factor=1,
        )


        # if config_file:
        #     with open(config_file, "r") as f:
        #         instance_config = json.load(f)
        # else:
        #     instance_config = {}
        """
        Ici se sont les config du json de la tache qui sont extraits
        """
      
        storage_state = instance_config.get("storage_state", None)
        start_url = instance_config.get("start_url", None)


        
        

        """
        Creation d'un nouveau contexte de Navigateur

        ici on rajoutera une condition pour lancer un context persistant comme on l'a fait avev gdpr_on_cookies 

        ce context contiendra le compte de jean tagne 

            - un parametre est ajouter dans ScriptBrowserEnv qui defini le type
            - dans l'env on precise la configuration de consent omatic souhaité ( consent = none | partial | all)
        """

        # Ensure all pages have a client attribute
        def initialize_page(page: Page) -> None:
            client = page.context.new_cdp_session(page)
            if self.text_observation_type == "accessibility_tree":
                client.send("Accessibility.enable")
            page.client = client 

     
        self.context = self.browser
            # for page in self.context.pages:
            #     try:
            #         page.close()
            #     except Exception as e:
            #         print(f"Could not close page: {e}")
            # if login_require:
            #     page = connect_to_browser_and_login(self.browser,login_url=login_url,login_selector=login_selector)
      
        if self.save_trace_enabled:
            self.context.tracing.start(screenshots=True, snapshots=True)
        if start_url:
            start_urls = start_url.split(" |AND| ")
            created_pages=[]
            for url in start_urls:
                if login_require :
                    
                    page = connect_to_browser_and_login(self.browser,login_url=login_url,login_selector=login_selector)
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
            self.page.client = client  # type: ignore

        

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
            "images": images,
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
            "images": images,
        }
        
        msg = (
            observation,
            float(success),  # reward
            False,  # terminated
            False,  # truncated
            info,
        )
        return msg

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
        img_bytes = self.page.screenshot(path="output/marked.png")
        marked_image = base64.b64encode(img_bytes).decode()
        
        self.page.evaluate(remove_label_mark_script)
        
        return {
            "raw_image": raw_image,
            "marked_image": marked_image,
        }
   