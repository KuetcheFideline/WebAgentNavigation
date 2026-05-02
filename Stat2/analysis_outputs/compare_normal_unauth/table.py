import pandas as pd

def presenter_donnees(chemin_fichier):
    # 1. Chargement
    try:
        df = pd.read_csv(chemin_fichier)
    except FileNotFoundError:
        print("Erreur : Le fichier CSV est introuvable.")
        return

    print("=== RAPPORT GLOBAL : AJOUTS (NORMAL VS UNAUTH) ===")

    # 2. Filtrer uniquement les ajouts
    df = df[df['delta'] > 0]

    # 3. Agrégation globale (tous stockages confondus)
    df_grouped = df.groupby('category').agg({
        'count_normal_total': 'sum',
        'count_unauth_total': 'sum'
    }).reset_index()

    # 4. Renommer colonnes
    df_grouped = df_grouped.rename(columns={
        'count_normal_total': 'total_normal',
        'count_unauth_total': 'total_unauth_all'
    })

    # 5. Calcul différence
    df_grouped['difference'] = (
        df_grouped['total_normal'] - df_grouped['total_unauth_all']
    )

    # 6. Tri
    df_grouped = df_grouped.sort_values(by='difference', ascending=False)

    # 7. Affichage console
    print(f"{'Catégorie':<35} | {'Normal':<10} | {'Unauth':<10} | {'Diff'}")
    print("-" * 75)

    for _, row in df_grouped.iterrows():
        cat = row['category']
        cat_display = (cat[:32] + '..') if len(cat) > 32 else cat

        print(f"{cat_display:<35} | {row['total_normal']:<10} | {row['total_unauth_all']:<10} | {row['difference']}")

    # 8. Export HTML
    html_output = "rapport_global_agrege.html"

    style = """
    <style>
        table { border-collapse: collapse; width: 80%; margin: auto; font-family: sans-serif; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }
        th { background-color: #2c3e50; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        h1 { text-align: center; }
        .positive { color: red; font-weight: bold; }
        .negative { color: green; }
    </style>
    """

    html_table = df_grouped.to_html(index=False)

    with open(html_output, "w", encoding="utf-8") as f:
        f.write(f"<html><head>{style}</head><body>")
        f.write("<h1>Comparaison Globale des Données Ajoutées</h1>")
        f.write("<p style='text-align:center;'>Tous stockages confondus</p>")
        f.write(html_table)
        f.write("</body></html>")

    print(f"\n[INFO] Rapport généré : {html_output}")


if __name__ == "__main__":
    presenter_donnees('GLOBAL_compare_normal_unauth.csv')
