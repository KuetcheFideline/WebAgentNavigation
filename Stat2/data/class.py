import os
import json

# Configuration des chemins et des types de stockage
base_dir = "./user"
storage_types = ["cookies", "localstorage", "indexeddb", "sessionstorage"]

# Dictionnaire pour stocker la matrice [catégorie][stockage]
matrix = {}

# 1. Parcours de l'arborescence
for root, dirs, files in os.walk(base_dir):
    # On ignore les données de calcul IA
    if "_vector_data" in root:
        continue
        
    # On identifie le type de stockage en fonction du nom du dossier dans le chemin
    current_storage = "other"
    for st in storage_types:
        if st in root.split(os.sep):
            current_storage = st
            break
            
    # 2. Lecture des fichiers JSON
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Comptage des éléments dans la liste
                    count = len(data) if isinstance(data, list) else (1 if isinstance(data, dict) else 0)
                    
                    category = file.replace(".json", "")
                    if category not in matrix:
                        matrix[category] = {st: 0 for st in storage_types + ["other"]}
                    
                    matrix[category][current_storage] += count
            except Exception:
                pass

# 3. Calculs des totaux et affichage
grand_total_all = sum(sum(s.values()) for s in matrix.values())
sorted_categories = sorted(matrix.items(), key=lambda x: sum(x[1].values()), reverse=True)

# En-tête du tableau
print(f"| {'Category':<35} | {'Cookies':<10} | {'LocalStorage':<12} | {'IndexedDB':<10} | {'SessionStorage':<14} | {'TOTAL':<10} | {'%':<8} |")
print("|" + "-"*37 + "|" + "-"*12 + "|" + "-"*14 + "|" + "-"*12 + "|" + "-"*16 + "|" + "-"*12 + "|" + "-"*10 + "|")

for cat, storages in sorted_categories:
    row_total = sum(storages.values())
    percentage = (row_total / grand_total_all * 100) if grand_total_all > 0 else 0
    
    print(f"| {cat:<35} | {storages['cookies']:<10} | {storages['localstorage']:<12} | {storages['indexeddb']:<10} | {storages['sessionstorage']:<14} | {row_total:<10} | {percentage:>6.2f}% |")

print("-" * 110)
print(f"TOTAL GÉNÉRAL : {grand_total_all} éléments")
