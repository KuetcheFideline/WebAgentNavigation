from text_generation import Client  # type: ignore
from huggingface_hub import InferenceClient
import time 
from openai import OpenAI
from transformers import pipeline
import time
import base64
import os 
import requests
def generate_from_huggingface_completion(
    prompt: str,
    model_endpoint: str,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
    stop_sequences: list[str] | None = None,
) -> str:
    client = Client(model_endpoint, timeout=60)
    generation: str = client.generate(
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=max_new_tokens,
        stop_sequences=stop_sequences,
    ).generated_text

    return generation





def encode_image(url):
       image_path= os.path.join(os.getcwd(),f"output/{url}")
       with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_from_huggingface_modal(
    prompt: str,
    model_endpoint: str,
    url: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_new_tokens: int = 512,
    stop_sequences: list[str] | None = None,
):
    print("Connexion à l'endpoint...")
    
    try:
        image = encode_image(url)
        print(f"Image encodée: {len(image)} caractères")
        
        # Format correct pour Ollama avec image
        data = {
            "model": "hf.co/AXONVERTEX-AI-RESEARCH/Fara-7B-Q8-GGUF:Q8_0",
            "prompt": prompt,
            "images": [image],  # Ollama attend un tableau d'images
            "temperature": temperature,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p
            },
            "stream": False
        }
        
        print("Envoi de la requête à Ollama...")
        response = requests.post(
            "http://localhost:11434/api/generate",  # API native Ollama
            json=data,
            timeout=None
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Réponse complète:", result)
            
            answer = result.get("response", "")
            print("Réponse extraite:", answer)
            return answer
        else:
            print(f"Erreur {response.status_code}:", response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("Erreur: Impossible de se connecter à Ollama. Vérifiez que le serveur tourne sur http://localhost:11434")
        return None
    except Exception as e:
        print(f"Erreur: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
# # Fonction pour encoder l'image en base64
# def encode_image(url: str) -> str:
#     with open(url, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")
# def generate_from_huggingface_modal(
#     prompt: str,
#     model_endpoint: str,
#     url: str,
#     temperature: float = 0.7,
#     top_p: float = 0.9,
#     max_new_tokens: int = 512,
#     stop_sequences: list[str] | None = None,
# ):
#     print("Connexion à l'endpoint Hugging Face...")
    
#     try:
#         print("Encodage de l'image...")
#         image_b64 = encode_image(url)
#         print(f"Image encodée: {len(image_b64)} caractères")
        
#         # Utiliser directement l'endpoint si fourni
#         if model_endpoint:
#             print(f"Utilisation de l'endpoint: {model_endpoint}")
#             import requests
            
#             payload = {
#                 "inputs": prompt,
#                 "parameters": {
#                     "temperature": temperature,
#                     "top_p": top_p,
#                     "max_new_tokens": max_new_tokens,
#                     "return_full_text": False
#                 }
#             }
            
#             headers = {
#                 "Authorization": "Bearer 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",
#                 "Content-Type": "application/json"
#             }
            
#             response = requests.post(model_endpoint, headers=headers, json=payload)
#             response.raise_for_status()
#             result = response.json()
            
#             if isinstance(result, list) and len(result) > 0:
#                 answer = result[0].get("generated_text", "")
#             else:
#                 answer = result.get("generated_text", "")
                
#             print("Réponse HF:", answer)
#             return answer
#         else:
#             # Fallback: utiliser text-generation au lieu de chat_completion
#             print("Initialisation du client...")
#             hf_api = InferenceClient(token="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")
            
#             # Combiner le prompt avec l'information de l'image
#             full_prompt = f"{prompt}\n[Image encodée en base64 fournie]"
            
#             print("Envoi de la requête...")
#             result = hf_api.text_generation(
#                 full_prompt,
#                 model="microsoft/Fara-7B",
#                 temperature=temperature,
#                 top_p=top_p,
#                 max_new_tokens=max_new_tokens,
#                 return_full_text=False
#             )
            
#             print("Réponse HF:", result)
#             return result
        
#     except Exception as e:
#         print(f"Erreur lors de l'appel à l'API Hugging Face: {type(e).__name__}: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return None