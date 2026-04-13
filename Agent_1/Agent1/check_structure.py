# import os
# import json

# # 📂 Dossier contenant les fichiers JSON
# RESULTS_DIR = "results_batch1"

# def check_json_structure(file_path):
#     """Vérifie la structure d'un fichier JSON et compte les URLs."""
#     with open(file_path, "r", encoding="utf-8") as f:
#         try:
#             data = json.load(f)
#         except json.JSONDecodeError as e:
#             return {"valid": False, "error": f"JSON invalide: {e}", "url_count": 0}

#     # Vérification des clés
#     expected_keys = {"sites", "tasks"}
#     if not expected_keys.issubset(data.keys()):
#         return {"valid": False, "error": f"Clés manquantes: {expected_keys - set(data.keys())}", "url_count": 0}

#     # Vérification des types
#     if not isinstance(data["sites"], list):
#         return {"valid": False, "error": "La clé 'sites' n'est pas une liste", "url_count": 0}

#     if not isinstance(data["tasks"], list):
#         return {"valid": False, "error": "La clé 'tasks' n'est pas une liste", "url_count": 0}

#     # Compte des URLs
#     url_count = len(data["sites"])

#     return {"valid": True, "error": None, "url_count": url_count}


# def main():
#     total_files = 0
#     valid_files = 0
#     invalid_files = 0
#     total_urls = 0

#     print("📊 Vérification de la structure des fichiers JSON...\n")
#     for filename in os.listdir(RESULTS_DIR):
#         if not filename.endswith(".json"):
#             continue

#         total_files += 1
#         file_path = os.path.join(RESULTS_DIR, filename)
#         result = check_json_structure(file_path)

#         if result["valid"]:
#             valid_files += 1
#             total_urls += result["url_count"]
#             print(f"✅ {filename} → OK ({result['url_count']} URLs)")
#         else:
#             invalid_files += 1
#             print(f"❌ {filename} → {result['error']}")

#     print("\n📌 Statistiques globales :")
#     print(f" - Total fichiers analysés : {total_files}")
#     print(f" - Fichiers valides       : {valid_files}")
#     print(f" - Fichiers invalides     : {invalid_files}")
#     print(f" - Total d'URLs trouvées  : {total_urls}")

# if __name__ == "__main__":
#     main()

import os
import json

RESULTS_DIR = "results_10000"
VISITED_SITES_FILE = "./results_batch1/visited_site.json"

def extract_visited_sites():
    visited = set()
    total_urls = 0
    total_files = 0

    print(f"📊 Scan des fichiers JSON dans {RESULTS_DIR}...\n")

    for filename in os.listdir(RESULTS_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(RESULTS_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ {filename} → Erreur de lecture JSON : {e}")
            continue

        if "sites" in data and isinstance(data["sites"], list):
            urls = data["sites"]
            visited.update(urls)
            total_urls += len(urls)
            total_files += 1
            print(f"✅ {filename} → {len(urls)} URLs ajoutées")
        else:
            print(f"⚠️ {filename} → pas de clé 'sites' valide")

    # Sauvegarde dans le fichier final
    os.makedirs(os.path.dirname(VISITED_SITES_FILE), exist_ok=True)
    with open(VISITED_SITES_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(visited)), f, ensure_ascii=False, indent=2)

    print("\n📌 Statistiques globales :")
    print(f" - Fichiers JSON analysés : {total_files}")
    print(f" - Total d'URLs trouvées  : {total_urls}")
    print(f" - Total unique de sites  : {len(visited)}")
    print(f"✅ Liste sauvegardée dans {VISITED_SITES_FILE}")

    return visited


if __name__ == "__main__":
    extract_visited_sites()
