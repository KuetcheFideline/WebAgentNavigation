import json
import re

# Ton fichier d'entrée
input_file = "errors.json"  # change le nom si besoin

# Fichiers de sortie
high_conf_file = "high_confidence.json"
low_conf_file = "low_confidence.json"

# Expression régulière pour extraire Category et Confidence
pattern = re.compile(r"Category:\s*(.+)\nConfidence:\s*(\d+)", re.MULTILINE)

# Listes pour stocker les données
high_conf = []
low_conf = []

# Lecture du fichier
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Parcours des entrées
for entry_list in data:  # Parcours chaque liste dans le fichier JSON
    for entry in entry_list:  # Parcours chaque dictionnaire dans chaque liste
        llm_content = entry.get("llm_content", "")
        match = pattern.search(llm_content)
        if match:
            category = match.group(1).strip()
            confidence = int(match.group(2))

            entry["category"] = category
            entry["confidence"] = confidence

            if confidence > 75:
                high_conf.append(entry)
            else:
                low_conf.append(entry)
        else:
            # Si le format du texte ne correspond pas, on met dans le low_conf par défaut
            low_conf.append(entry)

# Écriture des deux fichiers
with open(high_conf_file, "w", encoding="utf-8") as f:
    json.dump(high_conf, f, ensure_ascii=False, indent=2)

with open(low_conf_file, "w", encoding="utf-8") as f:
    json.dump(low_conf, f, ensure_ascii=False, indent=2)

print(f"✅ Fichier séparé avec succès !")
print(f" - {len(high_conf)} entrées avec confiance > 75 → {high_conf_file}")
print(f" - {len(low_conf)} entrées avec confiance ≤ 75 → {low_conf_file}")
