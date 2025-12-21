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
        
        # Format: { "Intent Actuelle": { "Signal Reçu": "Prochaine Intent" } }
        self.workflow = {
            "Register_page": {
                "on_registration_page": "Method of LogIn",
                "registration_not_found": "STOP_FAILURE"
            },
            "Method of LogIn": {
                "google": "Google Login",
                "classic": "Form_to_fill",
                "noLoginMethod": "STOP_FAILURE"
            },
            "Google Login": {
                "googleSelection": "Verification",
                "googleError": "STOP_FAILURE"
            },
            "Form_to_fill": {
                "execute_json": "HANDLE_JSON",
                "fieldToComplete": "Form_to_fill",
                "form_filled": "Form_to_submit",
                "formOkay": "Form_to_submit",
                "form_submitted": "Verification",
                "submitNotFound": "STOP_FAILURE"
            },
            
            "login_page" :{
                "on_login_page":"Method of LogIn",
                "login_not_found":"STOP_FAILURE"

            },
            "Statut" :{
                  "user_exist" :"STOP_SUCCESS",
                  "connexion": "login_page"
              },
            
            "Method of LogIn": {
                "google" :"Google Login",
                "classic": "Form_to_fill",
                "noLoginMethod": "STOP_FAILURE"

            },

            "Verification": {
                "loginSuccess": "STOP_SUCCESS",
                "loginFailed": "Method of LogIn",
                "form_to_fill": "Method of LogIn",
                "on_login_page": "Method of LogIn"
            },
            "Form_to_submit": {
                "formSubmitted": "Verification",
                "fieldToComplete": "Form_to_fill",
                "submitNotFound": "STOP_FAILURE"
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
                    content = args[1] if len(args) > 1 else (args[0] if len(args) > 0 else "")
                    action_call = f'type_string("{label}", "{content}", True)'
                elif func_name == "select":
                    val = args[1] if len(args) > 1 else (args[0] if len(args) > 0 else "")
                    action_call = f'select("{label}", "{val}")'
                elif func_name == "check":
                    action_call = f'check("{label}")'
                elif func_name == "click":
                    action_call = f'click("{label}")'
                
                if action_call:
                    logger.info(f"[CompteParams] Action : {action_call}")
                    parsed_action = self.agent.prompt_constructor.extract_action(action_call)
                    action_obj = create_id_based_action(parsed_action, url, user)
                    obs, _, terminated, _, info = self.env.step(action_obj)
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"[CompteParams] Erreur action {action_item}: {e}")
        
        return self.env._get_obs(), self.env._get_obs_metadata()

    def run(self, obs, info, url, user, max_steps, thresholds, start_intent="Register"):
        """Boucle principale de gestion du workflow."""
        current_intent = start_intent
        form_retry_count = 0
        
        while current_intent and not current_intent.startswith("STOP_"):
            logger.info(f"\n [CompteParams] Étape : {current_intent}")

            if current_intent == "Form_to_fill":
                form_retry_count += 1
                if form_retry_count > 2:
                    logger.warning(f"[CompteParams] Limite de tentatives atteinte pour Form_to_fill (2) sur {url}")
                    return "FAILURE"
            
            trajectory, meta_data, trace = self.task_execution_command(
                obs, info, current_intent, max_steps, thresholds, self.env, self.agent, url, user
            )
            
            target_response = trace[-1]["target"]
            signal = self.continuation(target_response)
            logger.info(f"[CompteParams] Signal reçu : {signal}")
            
            if isinstance(signal, tuple) and signal[0] == "execute_json":
                obs, info = self.execute_json_form(signal[1], url, user)
                current_intent = "Form_to_fill"
                continue

            if signal == "googleSelection":
                logger.info("[CompteParams] Gestion du popup Google...")
                self.env.login_existing_account_popup()
                obs, info = self.env.oldPage()
                current_intent = "Verification"
                continue

            next_step = self.workflow.get(current_intent, {}).get(signal)
            
            if not next_step:
                logger.warning(f"!!! [CompteParams] Pas de transition pour {current_intent} avec signal {signal}")
                return "FAILURE"

            last_obs_state = trajectory[-2]
            obs = last_obs_state["observation"]
            info = last_obs_state["info"]
            
            current_intent = next_step

        return "SUCCESS" if current_intent == "STOP_SUCCESS" else "FAILURE"
