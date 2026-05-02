# import json
# from pathlib import Path

# def is_idb_internal_key(item):
#     """
#     Identifie si un item est une clé interne/technique d'IndexedDB.
#     Exemple: "serviceWorkerScope", "last_flush_timestamp", "language" 
#     dans un champ se terminant par .key
#     """
#     field_path = item.get('field_path', '').lower()
#     value = str(item.get('value', ''))
    
#     # 1. Identification par le chemin (le plus important dans IndexedDB)
#     # On cible les chemins qui désignent explicitement le nom de la clé
#     internal_suffixes = ('.key', '.value.key', '.name', '.propertyname', '._id')
#     is_key_path = any(field_path.endswith(s) for s in internal_suffixes)
    
#     # 2. Identification par la nature de la valeur
#     # Une clé technique n'a généralement pas d'espaces et est courte
#     is_technical_value = value.isidentifier() or (len(value) < 60 and " " not in value)
    
#     return is_key_path and is_technical_value

# def discover_uncategorized_tasks(base_path: Path):
#     """
#     Parcours l'arborescence pour trouver les dossiers IndexedDB 
#     contenant un fichier UNCATEGORIZED.json
#     """
#     tasks = []
#     if not base_path.exists():
#         return tasks

#     for auth_dir in base_path.iterdir():
#         if not auth_dir.is_dir(): continue
#         for user_dir in auth_dir.iterdir():
#             if not user_dir.is_dir(): continue
#             user_id = user_dir.name

#             for policy_dir in user_dir.iterdir():
#                 if not policy_dir.is_dir(): continue
#                 for storage_dir in policy_dir.iterdir():
#                     if not storage_dir.is_dir(): continue

#                     storage_type = storage_dir.name

#                     # On cible uniquement IndexedDB pour ce filtrage spécifique
#                     if storage_type == "indexeddb":
#                         f = storage_dir / "UNCATEGORIZED.json"
#                         if f.exists():
#                             tasks.append({
#                                 "path": f,
#                                 "user_id": user_id,
#                                 "type": storage_type,
#                                 "dir": storage_dir
#                             })
#     return tasks

# def filter_idb_internal_keys(base_path: Path):
#     """
#     Sépare les clés internes du contenu réel dans les fichiers IndexedDB.
#     """
#     tasks = discover_uncategorized_tasks(base_path)
#     print(f"--- Analyse de {len(tasks)} dossiers IndexedDB ---")

#     for task in tasks:
#         file_path = task['path']
#         storage_dir = task['dir']
        
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 items = json.load(f)
            
#             if not isinstance(items, list):
#                 continue

#             real_data = []
#             internal_keys = []

#             for item in items:
#                 if is_idb_internal_key(item):
#                     internal_keys.append(item)
#                 else:
#                     real_data.append(item)

#             # Si on a détecté des clés internes
#             if internal_keys:
#                 internal_file = storage_dir / "INTERNAL_IDB_KEYS.json"
                
#                 existing_keys = []
#                 if internal_file.exists():
#                     with open(internal_file, 'r', encoding='utf-8') as f:
#                         try:
#                             existing_keys = json.load(f)
#                         except: existing_keys = []
                
#                 # On combine et on sauvegarde
#                 with open(internal_file, 'w', encoding='utf-8') as f:
#                     json.dump(existing_keys + internal_keys, f, indent=4, ensure_ascii=False)

#                 # 2. Nettoyer le fichier UNCATEGORIZED (ne garder que la vraie donnée)
#                 with open(file_path, 'w', encoding='utf-8') as f:
#                     json.dump(real_data, f, indent=4, ensure_ascii=False)
                
#                 print(f"[FILTRÉ] {task['user_id']} : {len(internal_keys)} clés techniques isolées.")

#         except Exception as e:
#             print(f"[ERREUR] Fichier {file_path} : {e}")

# if __name__ == "__main__":
#     base_path = Path(__file__).resolve().parent.parent / "data" / "user"
    
#     filter_idb_internal_keys(base_path)
#     print("--- Fin du pré-filtrage IndexedDB ---")



"""
PRÉ-FILTRAGE INDEXEDDB — AUDIT RGPD READY
V2 : Suppression du bruit de ressources statiques (JS, CSS, Cache)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any


# ============================================================
# REGEX STRUCTURELLES & RESSOURCES (ANTI-BRUIT)
# ============================================================

# postBody.<num> (payload binaire / protobuf)
POSTBODY_INDEX_RE = re.compile(r"\.postbody\.\d+$")

# .<num> final (properties.63, entries[12], etc.)
# GENERIC_NUMERIC_INDEX_RE = re.compile(r"(\[\d+\]|\.\d+)$")

# entries[12], values[3], etc.
ARRAY_INDEX_RE = re.compile(r"\[\d+\]")

# entries numériques avec .version
VERSION_INDEX_RE = re.compile(r"\[\d+\]\.version$")

# Détection des ressources web statiques (js, css, images, etc.)
# Capture les extensions classiques, même avec des paramètres de requête (?v=1.2)
WEB_RESOURCE_RE = re.compile(
    r"\.(js|css|png|jpg|jpeg|gif|svg|woff2?|ttf|otf|ico|map|webmanifest)(\?.*)?$", 
    re.IGNORECASE
)

# ============================================================
# DÉTECTION DES ÉLÉMENTS TECHNIQUES INDEXEDDB
# ============================================================

def is_idb_internal_key(item: Dict[str, Any]) -> bool:
    """
    Détecte si un item correspond à :
    - une clé IndexedDB technique
    - une ressource web statique (JS/CSS/Images)
    - un artefact de cache applicatif
    - un buffer binaire ou index numérique
    """

    field_path = item.get("field_path", "").lower()
    name = item.get("name", "").lower()
    value = item.get("value")
    value_str = str(value).lower()
    
    if name.isdigit() and isinstance(value, (int, float)):
        return True
    # --------------------------------------------------------
    # 1. Ressources Web Statiques & Cache (NOUVEAU)
    # --------------------------------------------------------
    # On élimine les URLs pointant vers des assets techniques
    is_web_resource = bool(WEB_RESOURCE_RE.search(value_str))
    
    # On élimine les noms de cache (ex: "my-app-scripts-v1")
    is_cache_related = (
        "cache" in name 
        or "cachename" in name 
        or "version" in name
    ) and (len(value_str) < 50)

    if is_web_resource or is_cache_related:
        return True

    # --------------------------------------------------------
    # 2. Clés IndexedDB techniques explicites
    # --------------------------------------------------------
    internal_suffixes = (
        ".key",
        ".value.key",
        ".name",
        ".propertyname",
         "._id",
        ".objectstorename",
        ".indexname",
    )

    is_internal_key_path = any(field_path.endswith(s) for s in internal_suffixes)

    # Une valeur technique est généralement courte et sans espace (identifiant)
    is_technical_value = (
        str(value).isidentifier()
        or (len(value_str) < 60 and " " not in value_str)
    )

    if is_internal_key_path and is_technical_value:
        return True

    # --------------------------------------------------------
    # 3. Buffers / payloads structurels (postBody, indices)
    # --------------------------------------------------------
    is_postbody_index = bool(POSTBODY_INDEX_RE.search(field_path))
    # is_numeric_suffix = bool(GENERIC_NUMERIC_INDEX_RE.search(field_path))
    # is_array_index = bool(ARRAY_INDEX_RE.search(field_path))

    # is_numeric_value = isinstance(value, (int, float))
    is_version_index = bool(VERSION_INDEX_RE.search(field_path))

    if (is_postbody_index or is_version_index) :
        return True

    # --------------------------------------------------------
    # 4. Valeurs manifestement non sémantiques (ID profonds)
    # --------------------------------------------------------
    if isinstance(value, (int, float)) and value >= 0 and len(field_path.split(".")) > 4:
        return True

    return False


# ============================================================
# DÉCOUVERTE DES TÂCHES INDEXEDDB
# ============================================================

def discover_uncategorized_tasks(base_path: Path) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []

    if not base_path.exists():
        return tasks

    # Parcours récursif pour trouver UNCATEGORIZED.json dans les dossiers indexeddb
    for uncategorized in base_path.glob("**/indexeddb/UNCATEGORIZED.json"):
        tasks.append({
            "path": uncategorized,
            "dir": uncategorized.parent,
        })

    return tasks


# ============================================================
# FILTRAGE PRINCIPAL
# ============================================================

def filter_idb_internal_keys(base_path: Path) -> None:
    """
    Sépare le bruit technique et les ressources web
    de la donnée réellement exploitable.
    """

    tasks = discover_uncategorized_tasks(base_path)
    print(f"--- Analyse de {len(tasks)} dossiers IndexedDB ---")

    for task in tasks:
        file_path = task["path"]
        storage_dir = task["dir"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)

            if not isinstance(items, list):
                continue

            real_data: List[Dict[str, Any]] = []
            internal_data: List[Dict[str, Any]] = []

            for item in items:
                if is_idb_internal_key(item):
                    item["_internal_reason"] = "TECHNICAL_ASSET_OR_IDB_NOISE"
                    internal_data.append(item)
                else:
                    real_data.append(item)

            if not internal_data:
                continue

            # ------------------------------------------------
            # Sauvegarde des éléments techniques/assets
            # ------------------------------------------------
            internal_file = storage_dir / "INTERNAL_IDB_KEYS.json"

            existing: List[Dict[str, Any]] = []
            if internal_file.exists():
                try:
                    with open(internal_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []

            with open(internal_file, "w", encoding="utf-8") as f:
                json.dump(
                    existing + internal_data,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

            # ------------------------------------------------
            # Mise à jour de UNCATEGORIZED (Data propre)
            # ------------------------------------------------
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    real_data,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

            print(f"[NETTOYÉ] {storage_dir.relative_to(base_path.parent)} : {len(in            print(f"[NETTOYÉ] {storage_dir.relative_to(base_path.parent)} : {len(internal_data)} bruits supprimés.")
ternal_data)} bruits supprimés.")

        except Exception as e:
            print(f"[ERREUR] {file_path} : {e}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Ajuste le chemin vers ton dossier data/user
    base_path = Path(__file__).resolve().parent.parent / "data" / "user"

    filter_idb_internal_keys(base_path)

    print("--- Fin du filtrage des ressources et bruits techniques ---")