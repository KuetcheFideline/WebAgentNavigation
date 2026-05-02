"""
compare_normal_vs_unauth.py
============================
Comparaison quantitative et catégorielle entre :
  - data/user/Normal/FR_xxxx/ALL/   (utilisateur en navigation « normale »)
  - data/user/UnAuth/FR_xxxx/ALL/   (utilisateur non authentifié, consentement ALL)

Pour chaque round (FR_0417, FR_0446, FR_0458), le script :
  1. Compte le nombre total d'entrées par storage (cookies, localstorage,
     sessionstorage, indexeddb) et par évènement (added, modified, removed).
  2. Décompose ce total par catégorie PII (nom du fichier JSON).
  3. Compare Normal vs UnAuth et calcule le delta absolu et relatif.
  4. Affiche des tableaux de synthèse et exporte les résultats en CSV.

Usage :
    python analysis/compare_normal_vs_unauth.py
"""

import json
import os
import csv
from collections import defaultdict
from pathlib import Path

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
USER_DIR = BASE_DIR / "data" / "user"

ROUNDS   = ["FR_0417", "FR_0446", "FR_0458"]
STORAGES = ["cookies", "localstorage", "sessionstorage", "indexeddb"]
EVENTS   = ["added", "modified", "removed"]

OUTPUT_DIR = BASE_DIR / "analysis_outputs" / "compare_normal_unauth"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def count_entries(path: Path) -> int:
    """Compte le nombre d'entrées dans un fichier JSON (liste ou dict)."""
    if not path.exists():
        return 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 1
        return 0
    except Exception:
        return 0


def collect_counts(mode_dir: Path) -> dict:
    """
    Parcourt mode_dir/{storage}/...
    Certains storages (cookies, localstorage, sessionstorage) ont des sous-dossiers added/modified/removed.
    D'autres (comme indexeddb parfois) ont les JSON directement à la racine du storage.
    """
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for storage in STORAGES:
        storage_dir = mode_dir / storage
        if not storage_dir.exists():
            continue

        # Cas 1 : Sous-dossiers added/modified/removed
        found_events = False
        for event in EVENTS:
            event_dir = storage_dir / event
            if event_dir.is_dir():
                found_events = True
                for cat_file in sorted(event_dir.glob("*.json")):
                    category = cat_file.stem
                    n = count_entries(cat_file)
                    counts[storage][event][category] += n
                    counts[storage][event]["__total__"] += n
        
        # Cas 2 : Fichiers JSON directs (on les considère comme 'added' ou 'total')
        # Si on ne trouve pas de sous-dossiers d'évènements, on regarde la racine
        if not found_events:
            for cat_file in sorted(storage_dir.glob("*.json")):
                if cat_file.suffix == '.json':
                    category = cat_file.stem
                    n = count_entries(cat_file)
                    # On attribue par défaut à 'added' pour la comparaison de volume
                    counts[storage]["added"][category] += n
                    counts[storage]["added"]["__total__"] += n

    return counts


def pct_diff(a: int, b: int) -> str:
    """Différence relative de b par rapport à a (en %)."""
    if a == 0:
        return "N/A" if b == 0 else "+∞"
    return f"{(b - a) / a * 100:+.1f}%"


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    # Résultats globaux (tous rounds confondus)
    global_normal  = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    global_unauth  = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    all_categories = set()

    for round_id in ROUNDS:
        normal_dir = USER_DIR / "Normal" / round_id / "ALL"
        unauth_dir = USER_DIR / "UnAuth"  / round_id / "ALL"

        if not normal_dir.exists():
            print(f"[WARN] Répertoire Normal introuvable : {normal_dir}")
        if not unauth_dir.exists():
            print(f"[WARN] Répertoire UnAuth introuvable : {unauth_dir}")

        n_counts = collect_counts(normal_dir) if normal_dir.exists() else {}
        u_counts = collect_counts(unauth_dir) if unauth_dir.exists() else {}

        # ── Collecte des catégories présentes ────────────────────
        for storage in STORAGES:
            for event in EVENTS:
                for cat in n_counts.get(storage, {}).get(event, {}):
                    if cat != "__total__":
                        all_categories.add(cat)
                for cat in u_counts.get(storage, {}).get(event, {}):
                    if cat != "__total__":
                        all_categories.add(cat)

        # ── Accumulation globale ──────────────────────────────────
        for storage in STORAGES:
            for event in EVENTS:
                for cat, n in n_counts.get(storage, {}).get(event, {}).items():
                    global_normal[storage][event][cat] += n
                for cat, n in u_counts.get(storage, {}).get(event, {}).items():
                    global_unauth[storage][event][cat] += n

        # ──────────────────────────────────────────────────────────
        # TABLEAU 1 : Totaux par storage × event (résumé quantitatif)
        # ──────────────────────────────────────────────────────────
        print(f"\n{'='*80}")
        print(f"  ROUND : {round_id}")
        print(f"{'='*80}")
        print(f"\n{'─'*70}")
        print(f"  TABLEAU 1 — Quantité totale d'entrées par storage et évènement")
        print(f"{'─'*70}")
        header = f"{'Storage':<18} {'Event':<12} {'Normal':>10} {'UnAuth':>10} {'Delta':>10} {'Var%':>8}"
        print(header)
        print("─" * 70)

        for storage in STORAGES:
            for event in EVENTS:
                n_total = n_counts.get(storage, {}).get(event, {}).get("__total__", 0)
                u_total = u_counts.get(storage, {}).get(event, {}).get("__total__", 0)
                delta   = u_total - n_total
                var     = pct_diff(n_total, u_total)
                delta_str = f"{delta:+d}" if (n_total > 0 or u_total > 0) else "—"
                if n_total > 0 or u_total > 0:
                    print(f"{storage:<18} {event:<12} {n_total:>10,} {u_total:>10,} {delta_str:>10} {var:>8}")

        # ──────────────────────────────────────────────────────────
        # TABLEAU 2 : Répartition par catégorie (tous storages, added)
        # ──────────────────────────────────────────────────────────
        print(f"\n{'─'*80}")
        print(f"  TABLEAU 2 — Répartition par catégorie PII (événement : added, tous storages)")
        print(f"{'─'*80}")
        header2 = f"{'Catégorie':<35} {'Normal':>10} {'UnAuth':>10} {'Delta':>10} {'Var%':>8}"
        print(header2)
        print("─" * 80)

        # Agrège toutes les catégories pour l'event "added" tous storages
        cat_normal_added: dict[str, int] = defaultdict(int)
        cat_unauth_added: dict[str, int] = defaultdict(int)

        for storage in STORAGES:
            for cat, n in n_counts.get(storage, {}).get("added", {}).items():
                if cat != "__total__":
                    cat_normal_added[cat] += n
            for cat, n in u_counts.get(storage, {}).get("added", {}).items():
                if cat != "__total__":
                    cat_unauth_added[cat] += n

        all_cats_round = sorted(set(list(cat_normal_added.keys()) + list(cat_unauth_added.keys())))
        for cat in all_cats_round:
            n_c = cat_normal_added.get(cat, 0)
            u_c = cat_unauth_added.get(cat, 0)
            delta = u_c - n_c
            var   = pct_diff(n_c, u_c)
            delta_str = f"{delta:+d}"
            print(f"{cat:<35} {n_c:>10,} {u_c:>10,} {delta_str:>10} {var:>8}")

        total_n = sum(cat_normal_added.values())
        total_u = sum(cat_unauth_added.values())
        print("─" * 80)
        print(f"{'TOTAL':<35} {total_n:>10,} {total_u:>10,} {total_u - total_n:>+10,} {pct_diff(total_n, total_u):>8}")

        # ──────────────────────────────────────────────────────────
        # TABLEAU 3 : Répartition par catégorie × storage (added)
        # ──────────────────────────────────────────────────────────
        print(f"\n{'─'*90}")
        print(f"  TABLEAU 3 — Répartition par catégorie PII × storage (événement : added)")
        print(f"{'─'*90}")

        for storage in STORAGES:
            # Vérifie si ce storage a des données
            n_st = n_counts.get(storage, {}).get("added", {})
            u_st = u_counts.get(storage, {}).get("added", {})
            cats_st = sorted(set(
                [k for k in n_st if k != "__total__"] +
                [k for k in u_st if k != "__total__"]
            ))
            if not cats_st:
                continue

            print(f"\n  [{storage.upper()}]")
            print(f"  {'Catégorie':<35} {'Normal':>10} {'UnAuth':>10} {'Delta':>10} {'Var%':>8}")
            print("  " + "─" * 68)
            for cat in cats_st:
                n_c  = n_st.get(cat, 0)
                u_c  = u_st.get(cat, 0)
                delta = u_c - n_c
                var   = pct_diff(n_c, u_c)
                print(f"  {cat:<35} {n_c:>10,} {u_c:>10,} {delta:>+10,} {var:>8}")
            total_n_st = n_st.get("__total__", 0)
            total_u_st = u_st.get("__total__", 0)
            print("  " + "─" * 68)
            print(f"  {'TOTAL':<35} {total_n_st:>10,} {total_u_st:>10,} "
                  f"{total_u_st - total_n_st:>+10,} {pct_diff(total_n_st, total_u_st):>8}")

        # ── Export CSV par round ──────────────────────────────────
        csv_path = OUTPUT_DIR / f"{round_id}_compare_normal_unauth.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["round", "storage", "event", "category",
                             "count_normal", "count_unauth", "delta", "pct_variation"])
            for storage in STORAGES:
                for event in EVENTS:
                    n_ev = n_counts.get(storage, {}).get(event, {})
                    u_ev = u_counts.get(storage, {}).get(event, {})
                    cats_ev = sorted(set(
                        [k for k in n_ev if k != "__total__"] +
                        [k for k in u_ev if k != "__total__"]
                    ))
                    for cat in cats_ev:
                        n_c = n_ev.get(cat, 0)
                        u_c = u_ev.get(cat, 0)
                        writer.writerow([round_id, storage, event, cat,
                                         n_c, u_c, u_c - n_c, pct_diff(n_c, u_c)])
        print(f"\n  → CSV exporté : {csv_path}")

    # ──────────────────────────────────────────────────────────────
    # TABLEAU GLOBAL (tous rounds)
    # ──────────────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"  SYNTHÈSE GLOBALE — Tous rounds confondus")
    print(f"{'='*80}")

    # Agrège les catégories pour "added" tous storages tous rounds
    total_cat_normal: dict[str, int] = defaultdict(int)
    total_cat_unauth: dict[str, int] = defaultdict(int)
    for storage in STORAGES:
        for cat, n in global_normal[storage]["added"].items():
            if cat != "__total__":
                total_cat_normal[cat] += n
        for cat, n in global_unauth[storage]["added"].items():
            if cat != "__total__":
                total_cat_unauth[cat] += n

    print(f"\n  {'Catégorie':<35} {'Normal':>10} {'UnAuth':>10} {'Delta':>10} {'Var%':>8}")
    print("  " + "─" * 70)
    for cat in sorted(all_categories):
        n_c = total_cat_normal.get(cat, 0)
        u_c = total_cat_unauth.get(cat, 0)
        delta = u_c - n_c
        var   = pct_diff(n_c, u_c)
        print(f"  {cat:<35} {n_c:>10,} {u_c:>10,} {delta:>+10,} {var:>8}")

    total_n_g = sum(total_cat_normal.values())
    total_u_g = sum(total_cat_unauth.values())
    print("  " + "─" * 70)
    print(f"  {'TOTAL':<35} {total_n_g:>10,} {total_u_g:>10,} "
          f"{total_u_g - total_n_g:>+10,} {pct_diff(total_n_g, total_u_g):>8}")

    # Export CSV global
    global_csv = OUTPUT_DIR / "GLOBAL_compare_normal_unauth.csv"
    with open(global_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["storage", "event", "category",
                         "count_normal_total", "count_unauth_total",
                         "delta", "pct_variation"])
        for storage in STORAGES:
            for event in EVENTS:
                n_ev = global_normal[storage][event]
                u_ev = global_unauth[storage][event]
                cats_ev = sorted(set(
                    [k for k in n_ev if k != "__total__"] +
                    [k for k in u_ev if k != "__total__"]
                ))
                for cat in cats_ev:
                    n_c = n_ev.get(cat, 0)
                    u_c = u_ev.get(cat, 0)
                    writer.writerow([storage, event, cat,
                                     n_c, u_c, u_c - n_c, pct_diff(n_c, u_c)])

    print(f"\n  → CSV global exporté : {global_csv}")
    print(f"\n[OK] Analyse terminée. Résultats dans : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
