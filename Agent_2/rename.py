import json
from pathlib import Path
import os

def process_json_to_new_folder(dossier_source_str, dossier_dest_str):
    """
    Lit les fichiers .json d'un dossier source, met à jour leur 'task_id',
    et les enregistre avec un nom numérique séquentiel dans un nouveau dossier de destination.

    Args:
        dossier_source_str (str): Le chemin vers le dossier contenant les fichiers originaux.
        dossier_dest_str (str): Le chemin vers le dossier où les nouveaux fichiers seront créés.
    """
    dossier_source = Path(dossier_source_str)
    dossier_dest = Path(dossier_dest_str)

    if not dossier_source.is_dir():
        print(f"Erreur : Le dossier source '{dossier_source}' n'existe pas ou n'est pas un dossier.")
        return

    fichiers_json = sorted(dossier_source.glob('*.json'))

    if not fichiers_json:
        print(f"Aucun fichier .json n'a été trouvé dans '{dossier_source}'.")
        return

    try:
        dossier_dest.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Erreur : Impossible de créer le dossier de destination '{dossier_dest}'. Raison : {e}")
        return

    if any(dossier_dest.iterdir()):
        print(f" Avertissement : Le dossier de destination '{dossier_dest}' n'est pas vide.")
        
    print("--- APERÇU DE L'OPÉRATION ---")
    print(f"Dossier source : {dossier_source}")
    print(f"Dossier destination : {dossier_dest}")
    print("Les fichiers suivants seront créés :")
    for i, fichier_source in enumerate(fichiers_json):
        nouveau_nom = f"{i}.json"
        nouveau_id = str(i)
        print(f"  - {dossier_dest / nouveau_nom} (à partir de '{fichier_source.name}', task_id='{nouveau_id}')")

    print("-" * 20)
    try:
        confirmation = input("Voulez-vous continuer ? (o/n) : ")
        if confirmation.lower() != 'o':
            print("Opération annulée par l'utilisateur.")
            return
    except KeyboardInterrupt:
        print("\nOpération annulée.")
        return

    print("\nLancement du traitement...")
    fichiers_crees = 0
    erreurs = 0
    for compteur, fichier_source in enumerate(fichiers_json):
        nouveau_id = str(compteur)
        nouveau_nom_fichier = f"{nouveau_id}.json"
        chemin_destination_fichier = dossier_dest / nouveau_nom_fichier

        try:
            with open(fichier_source, 'r', encoding='utf-8') as f_in:
                data = json.load(f_in)
            
            data['task_id'] = nouveau_id

            with open(chemin_destination_fichier, 'w', encoding='utf-8') as f_out:
                json.dump(data, f_out, indent=2, ensure_ascii=False)
            
            fichiers_crees += 1

        except json.JSONDecodeError:
            print(f"  ! Erreur : Le fichier source '{fichier_source.name}' n'est pas un JSON valide et a été ignoré.")
            erreurs += 1
        except Exception as e:
            print(f"  ! Une erreur inattendue est survenue avec '{fichier_source.name}': {e}")
            erreurs += 1

    print(f"\nOpération terminée. {fichiers_crees} fichier(s) ont été créé(s) dans '{dossier_dest}'. {erreurs} erreur(s) rencontrée(s).")
    print(f"Le dossier source '{dossier_source}' est resté intact.")

if __name__ == "__main__":
    dossier_source_input = input("Entrez le chemin du dossier source : ")
    dossier_dest_input = input("Entrez le nom ou le chemin du dossier de destination à créer : ")
    
    process_json_to_new_folder(dossier_source_input, dossier_dest_input)