import csv
import os

def lire_csv(fichier_csv):
    with open(fichier_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows_csv = list(reader)
    return rows_csv

def decouper_csv(fichier_csv, dossier_sortie, taille_batch=100):
    rows_csv = lire_csv(fichier_csv)
    
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    
    for i in range(0, len(rows_csv), taille_batch):
        fichier_batch = os.path.join(dossier_sortie, f"batch_{i // taille_batch + 1}.csv")
        
        with open(fichier_batch, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows_csv[i:i + taille_batch])
        
        print(f"Fichier {fichier_batch} créé avec succès !")

fichier_csv = 'restes_10000.csv'
dossier_sortie = 'restes_10000'

decouper_csv(fichier_csv, dossier_sortie)

print("Tous les fichiers batch ont été créés avec succès !")
