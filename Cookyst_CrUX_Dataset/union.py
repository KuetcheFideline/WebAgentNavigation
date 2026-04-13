import os
import csv

dossier = 'folder_10000'  

all_urls = []
for fichier in os.listdir(dossier):
    if fichier.endswith('.csv'):
        with open(os.path.join(dossier, fichier), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                all_urls.append(row)  

with open('all_10000.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for url in all_urls:
        writer.writerow(url)

print("Le fichier CSV final a été créé avec succès !")
