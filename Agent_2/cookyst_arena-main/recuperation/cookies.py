import os 
import sqlite3
import json
import keyring
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC




def clean(decrypted):
    last = decrypted[-1]
    try:
        return decrypted[:-last].decode("utf-8")
    except UnicodeDecodeError:
        # décodage tolérant → remplace les octets invalides par �
        return decrypted[:-last].decode("utf-8", errors="replace")



def get_encryption_key(config, password=None):
    """Génère la clé de chiffrement à partir du mot de passe ou de la configuration."""
    if isinstance(password, bytes):
        key_material = password
    elif isinstance(password, str):
        key_material = password.encode("utf8")
    elif isinstance(config["key_material"], str):
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



    
def cookie_config():
    """Configure le chemin des fichiers de cookies et récupère la clé de chiffrement."""
      

    config = {
        "key_material": "peanuts",
        "iterations": 1,
    }

    key_material = None
    try:
        import gi 
        gi.require_version("Secret", "1")
        from gi.repository import Secret
    except ImportError:
        pass
    else:
        flags = Secret.ServiceFlags.LOAD_COLLECTIONS
        service = Secret.Service.get_sync(flags)
        gnome_keyring = service.get_collections()
        unlocked_keyrings = service.unlock_sync(gnome_keyring).unlocked
        keyring_name = f"Chromium Safe Storage"

        for unlocked_keyring in unlocked_keyrings:
            for item in unlocked_keyring.get_items():
                if item.get_label() == keyring_name:
                    item_app = item.get_attributes().get("application", "Chromium")
                    if item_app.lower() != "Chromium ":
                        continue
                    item.load_secret_sync()
                    key_material = item.get_secret().get_text()
                    break
            else:
                continue
            break

    if key_material is None:
        try:
            key_material = keyring.get_password(
                f"Chromium Keys",
                f"Chromium  Safe Storage",
            )
        except RuntimeError:
            print("Erreur lors de la récupération du mot de passe du keyring.")

    if key_material is not None:
        config["key_material"] = key_material
    return config





def cookie_decrypt(encrypted_value, key, ini_vector,cookie_database_version):
    """Décrypte un cookie."""

   
    encrypted_value = encrypted_value[3:]  
    cipher = Cipher(
        algorithm=AES(key),
        mode=CBC(ini_vector),
    )
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted_value) + decryptor.finalize()

    if cookie_database_version >= 24:
          decrypted = decrypted[32:]


    return clean(decrypted)

config = cookie_config()
config.update(
        {"init_vector": b" " * 16, "length": 16, "salt": b"saltysalt"}
    )

password = None

enc_key = get_encryption_key(config, password)

for file in os.listdir("../browser_env/profiles"):
    if file=="auth" or file =="notauth":
        for elt in os.listdir(os.path.join("../browser_env/profiles",file)) :
            pat = os.path.join(file,elt,"cookies")

            os.makedirs(pat, exist_ok=True)

            for e in os.listdir(os.path.join("../browser_env/profiles",file,elt)):

                    cookies_DB = os.path.join("../browser_env/profiles",file,elt,e,'Default/','Cookies')
                    if os.path.exists(cookies_DB):
                        try :
                            conn = sqlite3.Connection(cookies_DB,timeout=10)
                            conn.row_factory = sqlite3.Row 
                            cursor = conn.cursor()
                            sql_version = "select value from meta where key = 'version';"
                            cookie_database_version = 0
                            try:
                                row = conn.execute(sql_version).fetchone()
                                if row:
                                    cookie_database_version = int(row[0])
                            except sqlite3.OperationalError:
                                pass


                            cursor.execute("SELECT * FROM cookies")

                            output_path = f"{pat}/{e}.json"

                            with open(output_path, 'w', encoding='utf-8') as jsonl_file:
                                data= []
                                for row in cursor:
                                    cookie_data = dict(row)
                                    if 'encrypted_value' in cookie_data:
                                        encrypted_value= cookie_data["encrypted_value"]
                                        if encrypted_value[:3] in (b'v10', b'v11'):
                                                decrypted_value = cookie_decrypt(
                                                    encrypted_value,
                                                    enc_key,
                                                    config["init_vector"],
                                                    cookie_database_version
                                                )
                                        
                                        cookie_data['encrypted_value'] = decrypted_value
                                        data.append(cookie_data)                           
                                jsonl_file.write(json.dumps(data, ensure_ascii=False,indent=4))

                        except sqlite3.OperationalError:
                             print(f" Impossible de lire {cookies_DB} (Peut-être verrouillé par le navigateur ?)")
                        except Exception as err:
                            print(f" Erreur sur {e} : {err}")

                    else:
                        print(f"Pas de fichier Cookies trouvé pour {e}")

                        
                        