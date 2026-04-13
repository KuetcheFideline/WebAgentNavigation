import csv
import json

def lire_json(fichier_json):
    with open(fichier_json, 'r', encoding='utf-8') as f:
        urls_json = json.load(f)
    domaines_json = [url.replace('https://', '') for url in urls_json]
    return domaines_json

def lire_csv(fichier_csv):
    with open(fichier_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows_csv = list(reader)
    return rows_csv

def ecrire_csv(fichier_sortie, lignes):
    with open(fichier_sortie, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(lignes)

def filtrer_urls(csv_file, json_file, fichier_sortie):
    domaines_json = lire_json(json_file)
    
    rows_csv = lire_csv(csv_file)
    
    result = []

    for row in rows_csv:
        domaine_csv = row[1]  
        if domaine_csv not in domaines_json:
            result.append(row)  
    ecrire_csv(fichier_sortie, result)

csv_file = 'all_10000.csv'
json_file = '10000_visted.json'
fichier_sortie = 'restes_10000.csv'

filtrer_urls(csv_file, json_file, fichier_sortie)

print("Le fichier CSV final a été créé avec succès !")
