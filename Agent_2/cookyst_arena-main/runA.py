"""Script to run end-to-end evaluation on the benchmark"""
import argparse
import glob
import json
import logging
import os
import random
import subprocess
import tempfile
import time
from pathlib import Path

from openai import OpenAIError
from tqdm import tqdm

from agent import (Agent, PromptAgent, TeacherForcingAgent,
                   construct_agent)
from agent.prompts import *
from browser_env import (Action, ActionTypes, ScriptBrowserEnv, StateInfo,
                         Trajectory, create_stop_action)
from browser_env.actions import is_equivalent
from browser_env.helper_functions import (RenderHelper,
                                          get_action_description)
from evaluation_harness import evaluator_router
from utils.utils import load_persona_from_json

# Configuration du logging
LOG_FOLDER = "log_files"
Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)
LOG_FILE_NAME = f"{LOG_FOLDER}/log_{time.strftime('%Y%m%d%H%M%S', time.localtime())}_{random.randint(0, 10000)}.log"

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

# Empêcher les handlers de s'ajouter à chaque exécution
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(LOG_FILE_NAME)
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-to-end evaluation on the benchmark")
    parser.add_argument("--render", action="store_true", help="Render the browser")
    parser.add_argument("--slow_mo", type=int, default=0, help="Slow down the browser by the specified amount")
    parser.add_argument("--action_set_tag", default="id_html_nasc_tree", help="Action type")
    parser.add_argument("--observation_type", choices=["accessibility_tree", "html", "image"], default="accessibility_tree", help="Observation type")
    parser.add_argument("--consent", choices=["all", "partial", "none"], default="all", help="consent-o-matic extension configuration")
    parser.add_argument("--persistent", action=argparse.BooleanOptionalAction, default=False, help="Launch a persistent browser context")
    parser.add_argument("--connected", type=str, default="Auth", help="Authentication status folder")
    parser.add_argument("--viewport_width", type=int, default=1920)
    parser.add_argument("--viewport_height", type=int, default=1080)
    parser.add_argument("--save_trace_enabled", action="store_true")
    parser.add_argument("--sleep_after_execution", type=float, default=0.0)
    parser.add_argument("--max_steps", type=int, default=30)
    parser.add_argument("--orm_path" ,type=str ,default="agent/prompts/jsons/orm_prompt.json")
    parser.add_argument("--banner_path",type=str ,default="agent/prompts/jsons/banner.json")
    parser.add_argument("--c", action="store_true", help="Only capture the current viewport")
    parser.add_argument("--country", type=str,choices=['FI', 'FR', 'PL', 'PT', 'ES', 'SV', 'IT', 'EN', 'NL', 'DE', 'DK'],default='FR')
    
    # Agent config
    parser.add_argument("--agent_type", type=str, default="prompt")
    parser.add_argument("--instruction_path", type=str, default="agents/prompts/state_action_agent.json")
    parser.add_argument("--parsing_failure_th", help="Consecutive parsing failure threshold", type=int, default=3)
    parser.add_argument("--repeating_action_failure_th", help="Consecutive repeating action threshold", type=int, default=3)
    
    # LM config
    parser.add_argument("--provider", type=str, default="groq")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-0613")
    parser.add_argument("--mode", type=str, default="chat")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--context_length", type=int, default=0)
    parser.add_argument("--max_tokens", type=int, default=384)
    parser.add_argument("--stop_token", type=str, default=None)
    parser.add_argument("--cuda", type=str, default='0')
    parser.add_argument("--max_retry", type=int, default=1)
    parser.add_argument("--max_obs_length", type=int, default=1920)
    parser.add_argument("--model_endpoint", help="huggingface model endpoint", type=str, default="")



    # Example config
    parser.add_argument("--user_start_idx",type= int ,default=0000)
    parser.add_argument("--user_end_idx",type= int ,default=12)

    parser.add_argument("--test_start_idx", type=int, default=0)
    parser.add_argument("--test_end_idx", type=int, default=1000)
    parser.add_argument("--sample", type=int, default=1)
    
    # Logging related
    parser.add_argument("--result_dir", type=str, default="")
    args = parser.parse_args()

    if args.action_set_tag == "id_accessibility_tree" and args.observation_type not in ["accessibility_tree", "html"]:
        raise ValueError(f"Action type {args.action_set_tag} is incompatible with observation type {args.observation_type}")

    return args


def early_stop(trajectory: Trajectory, max_steps: int, thresholds: dict[str, int]) -> tuple[bool, str]:
    """Check whether to early stop."""
    num_steps = (len(trajectory) - 1) / 2
    if num_steps >= max_steps:
        return True, f"Reach max steps {max_steps}"

    # Case: parsing failure for k times
    k = thresholds["parsing_failure"]
    last_k_actions = trajectory[1::2][-k:]
    if len(last_k_actions) >= k and all(a["action_type"] == ActionTypes.NONE for a in last_k_actions):
        return True, f"Failed to parse actions for {k} times"

    # Case: same action for k times
    k = thresholds["repeating_action"]
    action_seq = trajectory[1::2]
    if not action_seq:
        return False, ""

    last_action = action_seq[-1]
    if last_action["action_type"] != ActionTypes.TYPE:
        last_k_actions = action_seq[-k:]
        if len(last_k_actions) >= k and all(is_equivalent(a, last_action) for a in last_k_actions):
            return True, f"Same action for {k} times"
    else:
        if sum(is_equivalent(a, last_action) for a in action_seq) >= k:
            return True, f"Same typing action for {k} times"

    return False, ""


def task_execution_command(obs, info,intent,max_steps, early_stop_thresholds,env,agent,url,user) -> tuple[Trajectory, dict, list[dict]]:
  
    user_profile = load_persona_from_json("./user/personas_final_v2.json",user)
    trajectory:Trajectory =[{"observation": obs, "info": info}]
    meta_data  = {"action_history": ["None"], "user_persona": user_profile}
    trace = []
            
    while True:
                early_stop_flag, stop_info = early_stop(trajectory, max_steps, early_stop_thresholds)
                if early_stop_flag:
                    action = create_stop_action(f"Early stop: {stop_info}")
                    
                else:
                    try:
                        prompt = agent.prompt_constructor.construct(trajectory, intent, meta_data)
                        action = agent.next_action(trajectory, intent, meta_data=meta_data,url=url)
                    except ValueError as e:
                        logger.error(f"Error during agent action generation: {e}")
                        action = create_stop_action(f"ERROR: {str(e)}")

                trajectory.append(action)

                action_str = get_action_description(
                    action,
                    trajectory[-2]["info"]["observation_metadata"],
                    action_set_tag=args.action_set_tag,
                    prompt_constructor=agent.prompt_constructor if isinstance(agent, PromptAgent) else None,
                )

                
                meta_data["action_history"].append(action_str)
                trace.append({
                    "source": prompt,
                    "target": action_str.split(' #HTML Segment')[0],
                })




                if action["action_type"] == ActionTypes.STOP:
                    break

                print("je suis l'actii a executer :", action)
                
                obs, _, terminated, _, info = env.step(action)

                trajectory.append({"observation": obs, "info": info})



                if terminated:
                    trajectory.append(create_stop_action("Terminated"))
                    break
    return trajectory ,meta_data , trace



def test(
    args: argparse.Namespace,
    agent: Agent | PromptAgent | TeacherForcingAgent,
    config_file_list: list[str],
) -> None:
    max_steps = args.max_steps
    early_stop_thresholds = {
        "parsing_failure": args.parsing_failure_th,
        "repeating_action": args.repeating_action_failure_th,
    }

    env = ScriptBrowserEnv(
        persistent=args.persistent,
        connect=args.connected,
        consent=args.consent,
        headless=not args.render,
        slow_mo=args.slow_mo,
        observation_type=args.observation_type,
        current_viewport_only=args.current_viewport_only,
        viewport_size={"width": args.viewport_width, "height": args.viewport_height},
        save_trace_enabled=args.save_trace_enabled,
        sleep_after_execution=args.sleep_after_execution,
        country=args.country.lower()
    )


    for config_file in tqdm(config_file_list):
        match = re.search(r'/([A-Za-z]{2}/\d{4})',str(config_file))
        user =" test"
        if match :
            user = match.group(1)  
        user = user.replace("/","_")



        try:
            with open(config_file) as f:
                _c = json.load(f)
                intent = _c["intent"]
                task_id = _c["task_id"]
                url = _c["start_url"]

                login = _c["require_login"]
                google_login = _c["google_login"]


            if "map" in _c.get("sites", []):
                continue
            
            logger.info(f"[Config file]: {config_file}")
            obs,info = env.reset(options= {"config_file":config_file})

            time.sleep(20)
            if  google_login :
                initial_storage_state = env.get_all_storage_state()

                login_with_google= env.create_account_with_google(url)
            
            if  login :
                    logger.info("La tache  demande une authentification")
                    logger.info("Capturing initial storage state...")
                    intentA = "Authenticate : create an account on the website . "

                    trajectoryA ,meta_dataA, traceA = task_execution_command(obs,info,intentA,max_steps, early_stop_thresholds,env,agent,url,user)

                    ormA = agent.verify_action(trajectoryA,intentA,meta_dataA)
                    response_textA = ormA.output[0].content[0].text
                    resultA = {"id": task_id, "trace": traceA,"verdict" :response_textA }
                    tracesA_dir = Path(args.result_dir) /user / "tracesA" / args.connected / args.consent
                    tracesA_dir.mkdir(parents=True, exist_ok=True)
                    with open(tracesA_dir / f"traceA_{task_id}.json", "w") as f:
                        json.dump({"id": task_id, "trace": resultA}, f, indent=4)
            logger.info("Starting main task execution...")

            logger.info(f"[Config_file]:{config_file}")
            logger.info(f"[Intent]: {intent}")
            agent.reset(config_file)


            if  not   login :
                initial_storage_state = env.get_all_storage_state()
            trajectory ,meta_data , trace= task_execution_command(obs,info,intent,max_steps, early_stop_thresholds,env,agent,url,user)
            orm = agent.verify_action(trajectory,intent,meta_data)
            response_text = orm.output[0].content[0].text
            result = {"id": task_id, "trace": trace,"verdict" :response_text }
            storage_dir = Path(args.result_dir) / user /"storage_state" / args.connected / args.consent
            diff_filepath = storage_dir / f"{task_id}.json"



            traces_dir = Path(args.result_dir)/user / "traces" / args.connected / args.consent

            traces_dir.mkdir(parents=True, exist_ok=True)
            
            


            with open(traces_dir / f"trace_{task_id}.json", "w") as f:
                json.dump(result, f, indent=4)

            fileO = os.getcwd()

            output_dir = Path(fileO) / "output"
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()  
            


            env.save_storage(initial_storage_state, diff_filepath,url)
        except OpenAIError as e:
            logger.error(f"[OpenAI Error] {repr(e)}")
        except Exception as e:
            logger.error(f"[Unhandled Error] {repr(e)} for config file {config_file}")
            import traceback
            error_file = Path(args.result_dir) / "error.txt"
            with open(error_file, "a") as f:
                f.write(f"[Config file]: {config_file}\n")
                f.write(f"[Unhandled Error] {repr(e)}\n")
                f.write(traceback.format_exc() + "\n\n")
        

    env.close()


def prepare(args: argparse.Namespace) -> None:
    """Prepare environment for the test"""
    from agent.prompts import to_json
    to_json.run()

    result_dir = args.result_dir
    if not result_dir:
        result_dir = f"cache/results_{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
    
    args.result_dir = result_dir
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Created result dir: {result_dir}")
    
    # (Path(result_dir) / "traces").mkdir(exist_ok=True)
    # (Path(result_dir) / "storage_state").mkdir(exist_ok=True)

    with open(Path(result_dir) / "log_files.txt", "a+") as f:
        f.write(f"{LOG_FILE_NAME}\n")


def get_unfinished(config_files: list[str], result_dir: str) -> list[str]:
    """Filter out tasks that have already been completed."""
    result_files = glob.glob(f"{result_dir}/traces/trace_*.json")
    completed_task_ids = {Path(f).stem.split("_")[1] for f in result_files}
    
    unfinished_configs = []
    for config_file in config_files:
        task_id = Path(config_file).stem
        if task_id not in completed_task_ids:
            unfinished_configs.append(config_file)
    return unfinished_configs


def dump_config(args: argparse.Namespace) -> None:
    """Save the configuration of the run."""
    config_file = Path(args.result_dir) / "config.json"
    if not config_file.exists():
        with open(config_file, "w") as f:
            json.dump(vars(args), f, indent=4)
        logger.info(f"Dumped config to {config_file}")


if __name__ == "__main__":
    args = config()
    args.sleep_after_execution = 2.0
    prepare(args)

    test_file_list = []
    config_dir = Path("config_files") / args.connected
    if not config_dir.exists():
        logger.error(f"Configuration directory not found: {config_dir}")
    else:
        for user in os.listdir(config_dir) :
            print(user,"je suis l'utilisateur")
            if user == args.country :
                for i in range(args.user_start_idx,args.user_end_idx):

                    for j in range(args.test_start_idx, args.test_end_idx):
                            formatted_id = f"{i:04}"
                            if j % args.sample == 0:
                                config_file = config_dir / user /formatted_id / f"{j}.json"   
                                if config_file.exists():
                                    
                                    test_file_list.append(str(config_file))

                                if "debug" not in args.result_dir:
                                    test_file_list = get_unfinished(test_file_list, args.result_dir)

        if not test_file_list:
            logger.info("No tasks left to run.")
        else:
            logger.info(f"Total tasks to run: {len(test_file_list)}")
                     # Override args for test run
            args.render = False
            args.save_trace_enabled = True
            args.current_viewport_only = True
                                        
            dump_config(args)
            agent = construct_agent(args)

            test(args, agent, test_file_list)
        