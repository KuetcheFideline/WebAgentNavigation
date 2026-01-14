# import os
# import sqlite3
# import json
# import keyring
# from cryptography.hazmat.primitives.ciphers import Cipher
# from cryptography.hazmat.primitives.ciphers.algorithms import AES
# from cryptography.hazmat.primitives.ciphers.modes import CBC
# from cryptography.hazmat.primitives.hashes import SHA1
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# def clean(decrypted):
#     last = decrypted[-1]
#     try:
#         return decrypted[:-last].decode("utf-8")
#     except UnicodeDecodeError:
#         # décodage tolérant → remplace les octets invalides par �
#         return decrypted[:-last].decode("utf-8", errors="replace")


# def get_encryption_key(config, password=None):
#     """Génère la clé de chiffrement à partir du mot de passe ou de la configuration."""
#     if isinstance(password, bytes):
#         key_material = password
#     elif isinstance(password, str):
#         key_material = password.encode("utf8")
#     elif isinstance(config["key_material"], str):
#         key_material = config["key_material"].encode("utf8")
#     else:
#         raise ValueError("Mot de passe non valide.")

#     kdf = PBKDF2HMAC(
#         algorithm=SHA1(),
#         iterations=config["iterations"],
#         length=config["length"],
#         salt=config["salt"],
#     )
#     return kdf.derive(key_material)


# def cookie_config():
#     """Configure le chemin des fichiers de cookies et récupère la clé de chiffrement."""
#     config = {
#         "key_material": "peanuts",
#         "iterations": 1,
#     }

#     key_material = None
#     try:
#         import gi
#         gi.require_version("Secret", "1")
#         from gi.repository import Secret
#     except ImportError:
#         pass
#     else:
#         flags = Secret.ServiceFlags.LOAD_COLLECTIONS
#         service = Secret.Service.get_sync(flags)
#         gnome_keyring = service.get_collections()
#         unlocked_keyrings = service.unlock_sync(gnome_keyring).unlocked
#         keyring_name = f"Chromium Safe Storage"

#         for unlocked_keyring in unlocked_keyrings:
#             for item in unlocked_keyring.get_items():
#                 if item.get_label() == keyring_name:
#                     item_app = item.get_attributes().get("application", "Chromium")
#                     if item_app.lower() != "chromium ":
#                         continue
#                     item.load_secret_sync()
#                     key_material = item.get_secret().get_text()
#                     break
#             else:
#                 continue
#             break

#     if key_material is None:
#         try:
#             key_material = keyring.get_password(
#                 f"Chromium Keys",
#                 f"Chromium  Safe Storage",
#             )
#         except RuntimeError:
#             print("Erreur lors de la récupération du mot de passe du keyring.")

#     if key_material is not None:
#         config["key_material"] = key_material
#     return config


# def cookie_decrypt(encrypted_value, key, ini_vector, cookie_database_version):
#     """Décrypte un cookie."""
#     encrypted_value = encrypted_value[3:]  
#     cipher = Cipher(
#         algorithm=AES(key),
#         mode=CBC(ini_vector),
#     )
#     decryptor = cipher.decryptor()
#     decrypted = decryptor.update(encrypted_value) + decryptor.finalize()

#     if cookie_database_version >= 24:
#         decrypted = decrypted[32:]

#     return clean(decrypted)


# config = cookie_config()
# config.update(
#     {"init_vector": b" " * 16, "length": 16, "salt": b"saltysalt"}
# )

# password = None
# enc_key = get_encryption_key(config, password)

# for file in os.listdir("../browser_env/profiles"):
#     if file == "auth" or file == "notauth":
#         for elt in os.listdir(os.path.join("../browser_env/profiles", file)):
#             pat = os.path.join(file, elt, "cookies")

#             os.makedirs(pat, exist_ok=True)

#             for e in os.listdir(os.path.join("../browser_env/profiles", file, elt)):

#                 cookies_DB = os.path.join("../browser_env/profiles", file, elt, e, 'Default/', 'Cookies')
#                 if os.path.exists(cookies_DB):
#                     try:
#                         conn = sqlite3.Connection(cookies_DB, timeout=10)
#                         conn.row_factory = sqlite3.Row
#                         cursor = conn.cursor()
#                         sql_version = "select value from meta where key = 'version';"
#                         cookie_database_version = 0
#                         try:
#                             row = conn.execute(sql_version).fetchone()
#                             if row:
#                                 cookie_database_version = int(row[0])
#                         except sqlite3.OperationalError:
#                             pass

#                         cursor.execute("SELECT * FROM cookies")

#                         output_path = f"{pat}/{e}.jsonl"

#                         with open(output_path, 'w', encoding='utf-8') as jsonl_file:
#                             for row in cursor:
#                                 cookie_data = dict(row)
#                                 if 'encrypted_value' in cookie_data:
#                                     encrypted_value = cookie_data["encrypted_value"]
#                                     if encrypted_value[:3] in (b'v10', b'v11'):
#                                         decrypted_value = cookie_decrypt(
#                                             encrypted_value,
#                                             enc_key,
#                                             config["init_vector"],
#                                             cookie_database_version
#                                         )

#                                     cookie_data['encrypted_value'] = decrypted_value
#                                     # Write each record as a JSON object in one line
#                                     jsonl_file.write(json.dumps(cookie_data, ensure_ascii=False) + "\n")

#                     except sqlite3.OperationalError:
#                         print(f"Impossible de lire {cookies_DB} (Peut-être verrouillé par le navigateur ?)")
#                     except Exception as err:
#                         print(f"Erreur sur {e} : {err}")

#                 else:
#                     print(f"Pas de fichier Cookies trouvé pour {e}")


"""
Script pour extraire et déchiffrer les cookies Chrome/Chromium des profils navigateurs
Supporte le déchiffrement des cookies v10 et v11
"""
import os
import sqlite3
import json
import argparse
import shutil
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def clean_decrypted(decrypted):
    """
    Nettoie les données déchiffrées en retirant le padding PKCS7
    
    Args:
        decrypted: Bytes déchiffrés
        
    Returns:
        String déchiffré et nettoyé
    """
    if not decrypted:
        return ""
    
    # Retirer le padding PKCS7
    last = decrypted[-1]
    try:
        return decrypted[:-last].decode("utf-8")
    except UnicodeDecodeError:
        # Décodage tolérant si erreur
        return decrypted[:-last].decode("utf-8", errors="replace")


def get_encryption_key(config, password=None):
    """
    Génère la clé de chiffrement à partir du mot de passe ou de la configuration
    
    Args:
        config: Dictionnaire de configuration contenant salt, iterations, length
        password: Mot de passe optionnel (None = utiliser key_material du config)
        
    Returns:
        Clé de chiffrement dérivée
    """
    if isinstance(password, bytes):
        key_material = password
    elif isinstance(password, str):
        key_material = password.encode("utf8")
    elif isinstance(config.get("key_material"), str):
        key_material = config["key_material"].encode("utf8")
    else:
        raise ValueError("Mot de passe non valide.")

    kdf = PBKDF2HMAC(
        algorithm=SHA1(),
        iterations=config["iterations"],
        length=config["length"],
        salt=config["salt"],
    )
    return kdf.derive(key_material)


def get_chrome_key_linux():
    """
    Récupère la clé de chiffrement depuis le keyring Linux
    Essaie d'abord avec libsecret, puis avec keyring Python
    
    Returns:
        String de la clé ou None si non trouvé
    """
    key_material = None
    
    # Méthode 1: Essayer avec libsecret (GNOME keyring)
    try:
        import gi
        gi.require_version("Secret", "1")
        from gi.repository import Secret
        
        flags = Secret.ServiceFlags.LOAD_COLLECTIONS
        service = Secret.Service.get_sync(flags)
        gnome_keyring = service.get_collections()
        unlocked_keyrings = service.unlock_sync(gnome_keyring).unlocked
        
        # Essayer différents noms de keyring
        keyring_names = [
            "Chromium Safe Storage",
            "Chrome Safe Storage",
        ]
        
        for keyring_name in keyring_names:
            for unlocked_keyring in unlocked_keyrings:
                for item in unlocked_keyring.get_items():
                    if item.get_label() == keyring_name:
                        item.load_secret_sync()
                        key_material = item.get_secret().get_text()
                        if key_material:
                            print(f"  🔑 Clé trouvée dans {keyring_name}")
                            return key_material
    except ImportError:
        pass
    except Exception as e:
        print(f"  ⚠️  Erreur avec libsecret: {e}")
    
    # Méthode 2: Essayer avec keyring Python
    try:
        import keyring
        
        # Essayer différentes combinaisons
        combinations = [
            ("Chromium Keys", "Chromium Safe Storage"),
            ("Chrome Keys", "Chrome Safe Storage"),
            ("Chromium", "Chromium Safe Storage"),
            ("Chrome", "Chrome Safe Storage"),
        ]
        
        for service, username in combinations:
            try:
                key_material = keyring.get_password(service, username)
                if key_material:
                    print(f"  🔑 Clé trouvée dans keyring: {service}/{username}")
                    return key_material
            except:
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"  ⚠️  Erreur avec keyring: {e}")
    
    return key_material


def cookie_config():
    """
    Configure le déchiffrement des cookies et récupère la clé de chiffrement
    
    Returns:
        Dictionnaire de configuration
    """
    config = {
        "key_material": "peanuts",  # Valeur par défaut
        "iterations": 1,
        "init_vector": b" " * 16,
        "length": 16,
        "salt": b"saltysalt"
    }
    
    # Essayer de récupérer la vraie clé depuis le système
    key_material = get_chrome_key_linux()
    
    if key_material is not None:
        config["key_material"] = key_material
        print("  ✅ Clé de chiffrement récupérée du système")
    else:
        print("  ⚠️  Utilisation de la clé par défaut (les cookies peuvent ne pas se déchiffrer)")
    
    return config


def cookie_decrypt(encrypted_value, key, init_vector, cookie_database_version):
    """
    Déchiffre un cookie chiffré
    
    Args:
        encrypted_value: Valeur chiffrée (avec préfixe v10 ou v11)
        key: Clé de déchiffrement
        init_vector: Vecteur d'initialisation
        cookie_database_version: Version de la base de données
        
    Returns:
        Valeur déchiffrée ou message d'erreur
    """
    if not encrypted_value or len(encrypted_value) < 3:
        return ""
    
    # Retirer le préfixe (v10 ou v11)
    encrypted_value = encrypted_value[3:]
    
    try:
        cipher = Cipher(
            algorithm=AES(key),
            mode=CBC(init_vector),
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_value) + decryptor.finalize()
        
        # Pour les versions récentes, retirer les 32 premiers bytes
        if cookie_database_version >= 24:
            decrypted = decrypted[32:]
        
        return clean_decrypted(decrypted)
    except Exception as e:
        return f"[ERREUR_DECHIFFREMENT: {str(e)}]"


def extract_cookies_from_profile(profile_path, output_path, config, enc_key):
    """
    Extrait et déchiffre les cookies d'un profil
    
    Args:
        profile_path: Chemin vers le profil Chrome
        output_path: Chemin de sortie pour le fichier JSONL
        config: Configuration de déchiffrement
        enc_key: Clé de chiffrement
        
    Returns:
        Nombre de cookies extraits
    """
    cookies_db = Path(profile_path) / "Default" / "Cookies"
    
    if not cookies_db.exists():
        print(f"  ⚠️  Fichier Cookies non trouvé: {cookies_db}")
        return 0
    
    # Copier la base de données pour éviter les verrouillages
    temp_db = Path(output_path).parent / f"temp_{Path(profile_path).name}_cookies.db"
    
    try:
        shutil.copy2(cookies_db, temp_db)
    except Exception as e:
        print(f"  ⚠️  Impossible de copier la base de données: {e}")
        print(f"  ⚠️  Le navigateur est peut-être ouvert. Fermez-le et réessayez.")
        return 0
    
    cookie_count = 0
    encrypted_count = 0
    decrypted_count = 0
    error_count = 0
    
    try:
        conn = sqlite3.Connection(str(temp_db), timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer la version de la base de données
        cookie_database_version = 0
        try:
            sql_version = "SELECT value FROM meta WHERE key = 'version';"
            row = conn.execute(sql_version).fetchone()
            if row:
                cookie_database_version = int(row[0])
                print(f"  📊 Version de la base: {cookie_database_version}")
        except sqlite3.OperationalError:
            pass
        
        # Extraire tous les cookies
        cursor.execute("SELECT * FROM cookies")
        
        # Créer le dossier de sortie
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as jsonl_file:
            for row in cursor:
                cookie_data = dict(row)
                cookie_count += 1
                
                # Déchiffrer la valeur si elle est chiffrée
                if 'encrypted_value' in cookie_data:
                    encrypted_value = cookie_data["encrypted_value"]
                    
                    if encrypted_value and encrypted_value[:3] in (b'v10', b'v11'):
                        encrypted_count += 1
                        decrypted_value = cookie_decrypt(
                            encrypted_value,
                            enc_key,
                            config["init_vector"],
                            cookie_database_version
                        )
                        
                        if not decrypted_value.startswith("[ERREUR_"):
                            decrypted_count += 1
                        else:
                            error_count += 1
                        
                        cookie_data['encrypted_value'] = decrypted_value
                    else:
                        # Pas chiffré ou format inconnu
                        cookie_data['encrypted_value'] = encrypted_value.decode('utf-8', errors='replace') if isinstance(encrypted_value, bytes) else encrypted_value
                
                # Convertir les bytes en string pour JSON
                for key, value in cookie_data.items():
                    if isinstance(value, bytes):
                        cookie_data[key] = value.decode('utf-8', errors='replace')
                
                # Écrire en JSONL (une ligne par cookie)
                jsonl_file.write(json.dumps(cookie_data, ensure_ascii=False) + "\n")
        
        conn.close()
        
        # Nettoyer le fichier temporaire
        temp_db.unlink()
        
        print(f"  ✅ {cookie_count} cookies extraits")
        if encrypted_count > 0:
            print(f"    📊 {encrypted_count} chiffrés, {decrypted_count} déchiffrés, {error_count} erreurs")
        
        return cookie_count
        
    except sqlite3.OperationalError as e:
        print(f"  ❌ Erreur SQL: {e}")
        print(f"  ⚠️  La base de données est peut-être verrouillée par le navigateur")
        return 0
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return 0
    finally:
        # Nettoyer le fichier temporaire en cas d'erreur
        if temp_db.exists():
            try:
                temp_db.unlink()
            except:
                pass


def process_profile(profile_path, output_base_path, auth_type, profile_id, site_name, config, enc_key):
    """
    Traite un profil spécifique et extrait ses cookies
    
    Args:
        profile_path: Chemin vers le profil source
        output_base_path: Chemin de base pour la sortie
        auth_type: 'auth' ou 'notauth'
        profile_id: Identifiant du profil (ex: FR_0417)
        site_name: Nom du site (ex: all)
        config: Configuration de déchiffrement
        enc_key: Clé de chiffrement
    """
    # Créer le dossier de sortie
    output_dir = Path(output_base_path) / auth_type / profile_id / "cookies"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{site_name}.jsonl"
    
    print(f"  📁 Profil: {profile_path}")
    print(f"  💾 Sortie: {output_file}")
    
    # Extraire les cookies
    cookie_count = extract_cookies_from_profile(profile_path, output_file, config, enc_key)
    
    if cookie_count > 0:
        # Créer un fichier de métadonnées JSON
        metadata_file = output_dir / f"{site_name}_metadata.json"
        metadata = {
            "profile": profile_id,
            "auth_type": auth_type,
            "site_name": site_name,
            "cookie_count": cookie_count,
            "output_file": str(output_file.name)
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Extraction et déchiffrement des cookies Chrome/Chromium"
    )
    parser.add_argument(
        '--input-dir',
        default='../browser_env/profiles',
        help='Chemin vers le dossier profiles (défaut: ../browser_env/profiles)'
    )
    parser.add_argument(
        '--output-dir',
        default='./extracted_cookies',
        help='Chemin vers le dossier de sortie (défaut: ./extracted_cookies)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"❌ Erreur: Le dossier {input_path} n'existe pas")
        return 1
    
    print("=" * 70)
    print("🍪 EXTRACTION DES COOKIES CHROME/CHROMIUM")
    print("=" * 70)
    print(f"📂 Source: {input_path}")
    print(f"📂 Destination: {output_path}")
    print()
    
    # Configuration du déchiffrement
    print("🔧 Configuration du déchiffrement...")
    config = cookie_config()
    
    try:
        enc_key = get_encryption_key(config, password=None)
        print("  ✅ Clé de chiffrement générée")
    except Exception as e:
        print(f"  ❌ Erreur lors de la génération de la clé: {e}")
        return 1
    
    print()
    
    # Parcourir les dossiers auth/notauth
    total_profiles = 0
    total_cookies = 0
    
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
                    site_name,
                    config,
                    enc_key
                )
    
    print("\n" + "=" * 70)
    print(f"✅ Extraction terminée!")
    print(f"   {total_profiles} profil(s) traité(s)")
    print(f"📂 Résultats disponibles dans: {output_path}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())