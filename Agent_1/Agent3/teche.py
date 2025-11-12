import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# 📁 Chemin du dossier contenant les fichiers JSON
DATA_DIR = "./results_14_oct"  # ← à modifier


def analyze_site_files(data_dir, min_sites=3):
    total_sites = 0
    category_counts = defaultdict(int)

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            category = os.path.splitext(filename)[0]
            file_path = os.path.join(data_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sites = data.get("sites", [])
                    count = len(sites)

                    if count >= min_sites:  # ✅ on garde seulement les catégories valides
                        total_sites += count
                        category_counts[category] = count
            except Exception as e:
                print(f"⚠️ Erreur lors du traitement de {filename}: {e}")

    # Tri décroissant par nombre de sites
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    # Calcul des proportions (recalculées seulement sur les catégories retenues)
    category_proportions = {
        cat: (count / total_sites) * 100 for cat, count in sorted_categories
    }

    return total_sites, sorted_categories, category_proportions


def plot_results(sorted_categories, category_proportions):
    if not sorted_categories:
        print("⚠️ Aucune catégorie avec au moins 3 sites trouvée.")
        return

    categories = [cat for cat, _ in sorted_categories]
    counts = [count for _, count in sorted_categories]

    # --- Histogramme ---
    plt.figure(figsize=(12, 6))
    sns.barplot(x=counts, y=categories, palette="crest")
    plt.title("Nombre de sites par catégorie (≥ 3 sites)", fontsize=14, fontweight="bold")
    plt.xlabel("Nombre de sites")
    plt.ylabel("Catégorie")
    plt.tight_layout()
    plt.show()

    # --- Diagramme circulaire ---
    plt.figure(figsize=(8, 8))
    plt.pie(
        category_proportions.values(),
        labels=category_proportions.keys(),
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("pastel", len(category_proportions))
    )
    plt.title("Proportion des catégories (≥ 3 sites)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    total, counts, proportions = analyze_site_files(DATA_DIR, min_sites=3)

    print(f"\n📊 Nombre total de sites (catégories ≥ 3 sites) : {total}\n")
    print("📂 Nombre de sites par catégorie :")
    for cat, count in counts:
        print(f"  - {cat}: {count} sites")

    print("\n🏆 Catégories les plus représentées :")
    for cat, prop in proportions.items():
        print(f"  - {cat}: {prop:.2f}%")

    # Affichage des graphiques
    plot_results(counts, proportions)
