import json
import os

# Fichier d'entrée avec les données de haut niveau
input_file = "high_confidence.json"

# Lecture du fichier d'entrée
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Parcours des données et ajout de l'URL à son fichier de catégorie
for entry in data:
    category = entry.get("category", "")
    site_url = entry.get("site", "")

    # Remplacer les slashes par des underscores dans le nom du fichier
    category_filename = category.replace("/", "_") + ".json"
    
    # Si le fichier existe déjà, on l'ouvre et ajoute l'URL
    if os.path.exists(category_filename):
        with open(category_filename, "r+", encoding="utf-8") as category_f:
            category_data = json.load(category_f)
            # Ajouter l'URL à la catégorie
            if site_url not in category_data["sites"]:
                category_data["sites"].append(site_url)
            # Revenir au début du fichier pour écraser son contenu
            category_f.seek(0)
            json.dump(category_data, category_f, ensure_ascii=False, indent=2)
    else:
        # Si le fichier n'existe pas, on le crée
        with open(category_filename, "w", encoding="utf-8") as category_f:
            category_data = {
                "sites": [site_url]
            }
            json.dump(category_data, category_f, ensure_ascii=False, indent=2)

print("✅ Mise à jour des fichiers de catégories réussie !")
