from google import genai
import os

# Remplacez par votre clé si elle n'est pas dans l'environnement
api_key = os.environ.get("GOOGLE_API_KEY") 
# Ou mettez la en dur pour tester : api_key = "AIzaSy..."

client = genai.Client(api_key=api_key)

print("--- Modèles disponibles pour votre clé ---")
try:
    for m in client.models.list():
        if "gemini" in m.name:
            print(f"Nom du modèle : {m.name}")
            print(f"  Affichage : {m.display_name}")
except Exception as e:
    print(f"Erreur lors du listage : {e}")