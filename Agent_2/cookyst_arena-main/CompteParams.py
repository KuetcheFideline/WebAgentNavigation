import time
import logging
from browser_env.actions import create_id_based_action

logger = logging.getLogger("logger")

class CompteParams:
    def __init__(self, env, agent, task_execution_func, continuation_func):
        self.env = env
        self.agent = agent
        self.task_execution_command = task_execution_func
        self.continuation = continuation_func
        
        self.workflow = {
            "Unified_Account_Creation": {
                "google": "Google Login SignIn",
                "form_submitted": "Verification_SignIn",
                "user_exist": "STOP_SUCCESS",
                "registration_not_found": "STOP_FAILURE",
                "noLoginMethod": "STOP_FAILURE"
            },
            "Google Login SignIn": {
                "googleSelection": "STOP_SUCCESS",
                "googleError": "STOP_FAILURE"
            },
            "Verification_SignIn": {
                "loginSuccess": "STOP_SUCCESS",
                "loginFailed": "Unified_Account_Creation", 
                "form_to_fill": "Unified_Account_Creation", 
                "on_login_page": "Unified_Account_Creation",
                "user_exist": "STOP_SUCCESS",
                "google": "Google Login SignIn"
            },
            "Statut": {
                "user_exist": "STOP_SUCCESS",
                "connexion": "Unified_Account_Creation"
            }
        }

    def execute_json_form(self, actions_list, url, user):
        """Exécute une liste d'actions Playwright formatées en JSON.""" 
        logger.info("[CompteParams] Début du remplissage de formulaire JSON...")
        for action_item in actions_list:
            try:
                func_name = action_item.get("function")
                label = action_item.get("id")
                args = action_item.get("args", [])
                
                action_call = ""
                if func_name == "type_string":
                    content = ""
                    press_enter = False
                    if len(args) == 1:
                        content = args[0]
                    elif len(args) == 2:
                        if isinstance(args[1], bool):
                            content = args[0]
                            press_enter = args[1]
                        elif str(args[0]) == str(label):
                            content = args[1]
                        elif str(args[1]) == str(label):
                            content = args[0]
                        else:
                            content = args[1]
                    elif len(args) >= 3:
                        content = args[1]
                        press_enter = args[2]
                    
                    action_call = f'type_string("{label}", "{content}", {press_enter})'
                elif func_name == "select":
                    val = ""
                    if len(args) == 1:
                        val = args[0]
                    elif len(args) >= 2:
                        if str(args[0]) == str(label):
                            val = args[1]
                        elif str(args[1]) == str(label):
                            val = args[0]
                        else:
                            val = args[1]
                    action_call = f'select("{label}", "{val}")'
                elif func_name == "check":
                    action_call = f'check("{label}")'
                elif func_name == "click":
                    action_call = f'click("{label}")'
                
                if action_call:
                    logger.info(f"[CompteParams] Action : {action_call}")
                    parsed_action = self.agent.prompt_constructor.extract_action(action_call)
                    action_obj = create_id_based_action(parsed_action, url, user)
                    obs, _, terminated, _, info = self.env.step(action_obj, get_obs=False)
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"[CompteParams] Erreur action {action_item}: {e}")
        
        
        return 0

    def run(self, obs, info, url, user, max_steps, thresholds, start_intent="Unified_Account_Creation"):
        """Boucle principale de gestion du workflow."""
        current_intent = start_intent
        login_method = "unknown"
        form_retry_count = 0
        multimodal_retry_count = 0
        correction_retry_count = 0
        loop_steps = 0
        all_traces = []
        
        while current_intent and not current_intent.startswith("STOP_"):
            loop_steps += 1
            if loop_steps > 20:
                logger.warning(f"[CompteParams] Global loop limit (20) reached. Force stopping with FAILURE.")
                return "FAILURE", all_traces

            logger.info(f"\n [CompteParams] Étape : {current_intent}")

            if current_intent in ["Form_SignIn", "Form_LogIn"]:
                form_retry_count += 1
                if form_retry_count > 1: 
                    logger.warning(f"[CompteParams] Limite de tentatives atteinte pour {current_intent} sur {url}. Passage au mode Multimodal.")
                    if "SignIn" in current_intent:
                        current_intent = "Multimodal_Form_SignIn"
                    else:
                        current_intent = "Multimodal_Form_LogIn"
                    form_retry_count = 0 
                    continue
            
            if "Multimodal" in current_intent:
                multimodal_retry_count += 1
                if multimodal_retry_count > 2:
                    logger.warning(f"[CompteParams] Limite de tentatives (3) atteinte pour {current_intent}. Arrêt avec FAILURE.")
                    return "FAILURE", all_traces
            
            if "Form_Correction" in current_intent:
                correction_retry_count += 1
                if correction_retry_count > 2:
                    logger.warning(f"[CompteParams] Limite de tentatives (3) atteinte pour {current_intent}. Fallback vers Multimodal.")
                    if "SignIn" in current_intent:
                        current_intent = "Multimodal_Form_SignIn"
                    else:
                        current_intent = "Multimodal_Form_LogIn"
                    correction_retry_count = 0
                    continue

            # # Reset correction counter if we successfully move past correction/submit loop
            # if current_intent not in ["Form_Correction_SignIn", "Submit_SignIn", "Form_Correction_LogIn", "Submit_LogIn"]:
            #      correction_retry_count = 0

            trajectory, meta_data, trace = self.task_execution_command(
                obs, info, current_intent, max_steps, thresholds, self.env, self.agent, url, user
            )
            all_traces.extend(trace)
            
            
            target_response = trace[-1]["target"]
            logger.info(f"[CompteParams] Réponse brute de l'agent : {target_response}")
            signal = self.continuation(target_response)
            logger.info(f"[CompteParams] Signal reçu : {signal}")

            if current_intent in ["Method of SignIn", "Method of LogIn"]:
                if signal in ["google", "classic"]:
                    login_method = signal
                    logger.info(f"[CompteParams] Login Method Selected: {login_method}")

            if signal in ["loginSuccess", "user_exist"]:
                logger.info(f"[CompteParams] Login SUCCESS with method: {login_method}")
            
            if signal in ["googleError", "loginFailed"]:
                logger.info(f"[CompteParams] Login FAILED with method: {login_method}")
            
            if isinstance(signal, tuple) and signal[0] == "execute_json":
                self.execute_json_form(signal[1], url, user)
                obs, info = self.env.oldPage()
                if "SignIn" in current_intent:
                    current_intent = "Submit_SignIn"
                else:
                    current_intent = "Submit_LogIn"
                continue

            if signal == "googleSelection":
                logger.info("[CompteParams] Gestion du popup Google...")
                self.env.login_existing_account_popup()
                obs, info = self.env.oldPage()
                current_intent = "STOP_SUCCESS"
                continue

            next_step = self.workflow.get(current_intent, {}).get(signal)
            
            if not next_step:
                if current_intent in ["Form_SignIn", "Form_LogIn", "Submit_SignIn", "Submit_LogIn", "Verification_SignIn", "Verification_LogIn"]:
                     logger.warning(f"!!! [CompteParams] Pas de transition pour {current_intent} avec signal {signal}. Tentative de fallback Multimodal.")
                     if "SignIn" in current_intent:
                         current_intent = "Multimodal_Form_SignIn"
                     else:
                         current_intent = "Multimodal_Form_LogIn"
                     continue
                
                logger.warning(f"!!! [CompteParams] Pas de transition pour {current_intent} avec signal {signal}")
                return "FAILURE", all_traces

            last_obs_state = trajectory[-2]
            obs = last_obs_state["observation"]
            info = last_obs_state["info"]
            
            current_intent = next_step

        if current_intent == "STOP_SUCCESS":
            if login_method == "google":
                result = "SUCCESS_GOOGLE"
            elif login_method == "classic":
                result = "SUCCESS_CLASSIC"
            else:
                result = "SUCCESS" 
            return result, all_traces
        
        return "FAILURE", all_traces
