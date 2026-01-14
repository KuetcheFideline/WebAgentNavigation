
# """
# recuperation du fichier de indexDB  : Comment ca ve se passer 


# """

# import plyvel
# import sqlite3
# import json
# import argparse
# import os 
# import time 
# import subprocess


# def chrome_comparator(key_a, key_b):
#     if key_a == key_b:
#         return 0
#     return -1 if key_a < key_b else 1


# def decodebyte(raw):
#     data = {}
#     parts =raw.split(b"\x00\x01")
#     if len(parts)==2 :
#         data[parts[0].decode("utf-8")]=parts[1].decode("utf-8")
#     elif len(parts)==3:
#         domain = parts[0].decode("utf-8")
#         sub_key = parts[1].decode("utf-8")
#         value = parts[2].decode("utf-8")
#         if domain not in sub_key :
#             data[domain]= {}
        
#         data[domain][sub_key] = value
#     else :
#         data[parts[0].decode('utf-8')]={}
    
#     return data 


# for file in os.listdir("../browser_env/profiles"):
#     if file=="auth" or file =="notauth":
#         for elt in os.listdir(os.path.join("../browser_env/profiles",file)) :
#             pat = os.path.join(file,elt,"indexedDB")

#             os.makedirs(pat, exist_ok=True)

#             for e in os.listdir(os.path.join("../browser_env/profiles",file,elt)):
#                     pat = os.path.join(file,elt,"indexedDB",e)


#                     os.makedirs(pat, exist_ok=True)
#                     parent_path = os.path.join("../browser_env/profiles",file,elt,e,"Default","IndexedDB")
#                     if os.path.exists(parent_path): 
#                         datas= []
#                         for site in os.listdir(parent_path):
#                             data = {}

                            
#                             data[site]=[]
#                             index_DB = os.path.join("../browser_env/profiles",file,elt,e,"Default","IndexedDB",site)
#                             result = subprocess.run(
#                                     ['dfindexeddb', 'db', '-s', index_DB, '--format', 'chrome', '-o', 'jsonl'],
#                                     capture_output=True,
#                                     text=True
#                                 )
#                             if result.returncode == 0:
#                                 lines = result.stdout.strip().splitlines()
#                                 for line in lines : 
#                                     if line :
#                                         obj = json.loads(line)
#                                         valeur = obj.get('value')
#                                         type = obj.get('type')
#                                         if type != 0 and isinstance(valeur, dict):
                    
                                            
#                                          data[site].append(valeur)
#                             else:

#                                 print(f"Erreur: {result.stderr}")
                            
                                    
#                             final =final = os.path.join(pat,f"{site}.json")
#                             datas.append({"data":data})
#                         with open(final, 'w', encoding='utf-8') as jsonl_file:
#                                 # for obj in data :
#                                     jsonl_file.write(json.dumps(data, ensure_ascii=False,indent=4))

                                
"""
Script pour extraire et organiser les données IndexedDB de chaque profil navigateur
"""
import json
import argparse
import os
import subprocess
from pathlib import Path


def extract_indexeddb_data(index_db_path):
    """
    Extrait les données d'un dossier IndexedDB en utilisant dfindexeddb
    
    Args:
        index_db_path: Chemin vers le dossier IndexedDB d'un site
        
    Returns:
        Liste des objets extraits
    """
    data = []
    
    try:
        result = subprocess.run(
            ['dfindexeddb', 'db', '-s', index_db_path, '--format', 'chrome', '-o', 'jsonl'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            for line in lines:
                if line:
                    try:
                        obj = json.loads(line)
                        valeur = obj.get('value')
                        obj_type = obj.get('type')
                        
                        # Ne garder que les objets valides (type != 0 et valeur dict)
                        if obj_type != 0 and isinstance(valeur, dict):
                            data.append(valeur)
                    except json.JSONDecodeError as e:
                        print(f"  ⚠️  Erreur de parsing JSON: {e}")
        else:
            print(f"  ⚠️  Erreur dfindexeddb: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout lors de l'extraction")
    except FileNotFoundError:
        print(f"  ⚠️  dfindexeddb non trouvé. Installez-le d'abord.")
        return None
    except Exception as e:
        print(f"  ⚠️  Erreur inattendue: {e}")
    
    return data


def process_profile(profile_path, output_base_path, auth_type, profile_id, site_name):
    """
    Traite un profil spécifique et extrait ses données IndexedDB
    
    Args:
        profile_path: Chemin vers le profil source
        output_base_path: Chemin de base pour la sortie
        auth_type: 'auth' ou 'notauth'
        profile_id: Identifiant du profil (ex: FR_0417)
        site_name: Nom du site (ex: all)
    """
    # Chemin vers IndexedDB dans le profil Chrome
    indexeddb_path = Path(profile_path) / "Default" / "IndexedDB"
    
    if not indexeddb_path.exists():
        print(f"  ⚠️  Pas de dossier IndexedDB trouvé dans {profile_path}")
        return
    
    # Créer le dossier de sortie
    output_dir = Path(output_base_path) / auth_type / profile_id / "indexedDB" / site_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  📁 Extraction depuis: {indexeddb_path}")
    print(f"  💾 Sortie vers: {output_dir}")
    
    # Parcourir tous les sites dans IndexedDB
    site_count = 0
    for site_folder in indexeddb_path.iterdir():
        if site_folder.is_dir():
            site_count += 1
            site_name_clean = site_folder.name
            print(f"    🌐 Site: {site_name_clean}")
            
            # Extraire les données
            data = extract_indexeddb_data(str(site_folder))
            
            if data is None:
                continue
            
            # Sauvegarder dans un fichier JSON
            output_file = output_dir / f"{site_name_clean}.json"
            
            site_data = {
                "site": site_name_clean,
                "profile": profile_id,
                "auth_type": auth_type,
                "records_count": len(data),
                "data": data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(site_data, f, ensure_ascii=False, indent=2)
            
            print(f"      ✅ {len(data)} enregistrements extraits -> {output_file.name}")
    
    print(f"  ✅ {site_count} site(s) traité(s) pour le profil {profile_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Extraction des données IndexedDB des profils navigateurs"
    )
    parser.add_argument(
        '--input-dir',
        default='../browser_env/profiles',
        help='Chemin vers le dossier profiles (défaut: ../browser_env/profiles)'
    )
    parser.add_argument(
        '--output-dir',
        default='./extracted_indexeddb',
        help='Chemin vers le dossier de sortie (défaut: ./extracted_indexeddb)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"❌ Erreur: Le dossier {input_path} n'existe pas")
        return
    
    print("=" * 70)
    print("🔍 EXTRACTION DES DONNÉES INDEXEDDB")
    print("=" * 70)
    print(f"📂 Source: {input_path}")
    print(f"📂 Destination: {output_path}")
    print()
    
    # Parcourir les dossiers auth/notauth
    total_profiles = 0
    for auth_folder in input_path.iterdir():
        if auth_folder.name not in ["auth", "notauth"]:
            continue
        
        auth_type = auth_folder.name
        print(f"\n📁 Traitement de '{auth_type}'")
        print("-" * 70)
        
        # Parcourir les sous-dossiers (all, etc.)
        for site_folder in auth_folder.iterdir():
            if not site_folder.is_dir():
                continue
            
            site_name = site_folder.name
            print(f"\n  📂 Catégorie: {site_name}")
            
            # Parcourir les profils individuels (FR_0417, FR_0417_1, etc.)
            for profile_folder in site_folder.iterdir():
                if not profile_folder.is_dir():
                    continue
                
                profile_id = profile_folder.name
                print(f"\n  👤 Profil: {profile_id}")
                
                total_profiles += 1
                process_profile(
                    profile_folder,
                    output_path,
                    auth_type,
                    profile_id,
                    site_name
                )
    
    print("\n" + "=" * 70)
    print(f"✅ Extraction terminée! {total_profiles} profil(s) traité(s)")
    print(f"📂 Résultats disponibles dans: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()