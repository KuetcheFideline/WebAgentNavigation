import json

def load_persona_from_json(path: str) -> dict:
    """
    Charge un persona utilisateur détaillé à partir d'un fichier JSON.

    Args:
        path (str): Le chemin vers le fichier .json.

    Returns:
        dict: Un dictionnaire Python représentant le persona complet.
        
    Raises:
        FileNotFoundError: Si le fichier n'est pas trouvé.
        json.JSONDecodeError: Si le fichier contient du JSON invalide.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)
        return persona_data
    except FileNotFoundError:
        print(f"Erreur : Le fichier persona '{path}' est introuvable.")
        raise
    except json.JSONDecodeError as e:
        print(f"Erreur de formatage dans le fichier JSON '{path}': {e}")
        raise



def cookies_collection() : 
    """ cette fonction est utiliser pour colllecter les cookies avec leur nom de domaine """

    