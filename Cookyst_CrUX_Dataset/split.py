import os
import pandas as pd
from urllib.parse import urlparse

csv_files = ['top_1000.csv', 'top_5000.csv', 'top_10000.csv']
output_folders = ['folder_1000', 'folder_5000', 'folder_10000']

batch_size = 100

def extract_domain(url):
    """
    Extrait le domaine d'une URL, ex:
    https://www.microsoft.com → microsoft.com
    """
    if pd.isna(url):
        return ''
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # enlever le "www." si présent
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.strip()

def split_and_format_csv(input_file, output_folder, batch_size):
    df = pd.read_csv(input_file)

    # on garde seulement le rang et le domaine
    df['domain'] = df['origin'].apply(extract_domain)
    formatted_df = df[['top_rank', 'domain']]

    os.makedirs(output_folder, exist_ok=True)

    # création des fichiers batch
    for i in range(0, len(formatted_df), batch_size):
        batch = formatted_df.iloc[i:i + batch_size]

        batch_filename = os.path.join(output_folder, f"batch_{(i // batch_size + 1):04d}.csv")

        batch.to_csv(batch_filename, index=False, header=False)
import os
import pandas as pd
from urllib.parse import urlparse

csv_files = ['top_1000.csv', 'top_5000.csv', 'top_10000.csv']
output_folders = ['folder_1000', 'folder_5000', 'folder_10000']

batch_size = 100

def extract_domain(url):
    """
    Extrait le domaine d'une URL, ex:
    https://www.microsoft.com → microsoft.com
    """
    if pd.isna(url):
        return ''
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.strip()

def split_and_format_csv(input_file, output_folder, batch_size):
    df = pd.read_csv(input_file)

    # Extraire les domaines
    df['domain'] = df['origin'].apply(extract_domain)
    formatted_df = df[['domain']]

    os.makedirs(output_folder, exist_ok=True)

    # Création des fichiers batch
    for i in range(0, len(formatted_df), batch_size):
        batch = formatted_df.iloc[i:i + batch_size].reset_index(drop=True)

        # Ajouter une colonne incrémentale qui commence à 1 pour chaque fichier
        batch.insert(0, 'index', range(1, len(batch) + 1))

        batch_filename = os.path.join(output_folder, f"batch_{(i // batch_size + 1):04d}.csv")

        # Enregistrer sans les en-têtes
        batch.to_csv(batch_filename, index=False, header=False)

for input_file, output_folder in zip(csv_files, output_folders):
    split_and_format_csv(input_file, output_folder, batch_size)

print("✅ Les fichiers ont été divisés et sauvegardés avec numérotation incrémentale.")

for input_file, output_folder in zip(csv_files, output_folders):
    split_and_format_csv(input_file, output_folder, batch_size)

print("✅ Les fichiers ont été divisés et sauvegardés avec domaine simplifié.")
