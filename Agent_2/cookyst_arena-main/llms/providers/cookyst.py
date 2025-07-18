
from ..apikey_manager import with_api_key,   APIKeyManager
from typing import Callable
import requests

keys = [
    "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",
    "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",
]

api_manager =APIKeyManager(
    api_keys=keys,
    requests_per_window=30,  
    window_in_minutes=1   
)

manages_api_call = with_api_key(api_manager)


@manages_api_call
def call_grop_llama(prompt,model, *, api_key: str):
    client = model(api_key=api_key)
    
    # client = model(api_key = "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")
    completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": f"{prompt}"
        }
    ])
    return(completion.choices[0].message.content)

def call_webrl_llama(lm_config,prompt):
    api_url = "http://localhost:8080/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "temperature":lm_config.gen_config["temperature"],
        "top_n":lm_config.gen_config["top_p"],
        "max_new_tokens":lm_config.gen_config["max_tokens"],
        "stop_sequence": lm_config.gen_config["stop_token"]
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        prediction = response_data['generated_text'].strip()
        print(f"Sortie de l'API: {prediction}")
        return prediction

    except requests.exceptions.RequestException as e:
        print(f"Une erreur est survenue lors de l'appel à l'API : {e}")
        return ''
    except (KeyError, IndexError) as e:
        print(f"Erreur lors de l'extraction de la prédiction depuis la réponse de l'API : {e}")
        print(f"Réponse reçue : {response.text}")
        return ''