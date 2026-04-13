import os
import json

# 📁 Chemin du dossier contenant les fichiers JSON
DATA_DIR = "./results_14_oct"  # ← à modifier
OUTPUT_FILE = "all_sites.json"  # fichier de sortie

def get_all_sites(data_dir):
    all_sites = set()  # Utilisation d'un set pour éviter les doublons

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Si le fichier contient une clé 'sites'
                    if isinstance(data, dict) and "sites" in data:
                        sites = data["sites"]
                    elif isinstance(data, list):  # Si c'est une liste directement
                        sites = data
                    else:
                        continue  # Ignorer les fichiers au format incorrect

                    # Ajouter les sites au set (évite les doublons)
                    all_sites.update(sites)

            except Exception as e:
                print(f"⚠️ Erreur lors du traitement de {filename}: {e}")

    return list(all_sites)


if __name__ == "__main__":
    all_sites = get_all_sites(DATA_DIR)
    print(f"Nombre total de sites collectés : {len(all_sites)}")

    # Sauvegarde dans un fichier JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"all_sites": all_sites}, f, indent=4)

    print(f"✅ Fichier généré : {OUTPUT_FILE}")
