#!/usr/bin/env python3
"""
Lifecycle Analysis - Phase Combinée Auth/ALL + Perssistence/ALL
================================================================
Combine les événements cookies des deux phases en une seule timeline
chronologique continue par cookie.

- Auth/ALL      → Phase 1 (navigation authentifiée)
- Perssistence/ALL → Phase 2 (continuation / persistance)

L'ordre des événements est déterminé par le champ `timestamp` réel,
ce qui garantit une cohérence chronologique indépendante de la numérotation
des task_ids (qui repart à zéro dans chaque phase).

Sortie : results/Auth_Perssistence/{user}/cookies/lifecycle/
  - lifecycle_data.json              (métriques globales)
  - consolidated/timelines_complete.json  (timelines complètes)

Les données sources dans data/user/ ne sont PAS modifiées.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter

# Import des modules d'analyse partagés
sys.path.insert(0, str(Path(__file__).parent))
import privacy_metrics as pm


# =====================================================================
# 1. CLÉ COOKIE
# =====================================================================

def create_cookie_key(cookie: Dict) -> str:
    """Crée une clé unique pour un cookie : name|domain|path"""
    return f"{cookie.get('name', '')}|{cookie.get('domain', '')}|{cookie.get('path', '/')}"


# =====================================================================
# 2. CHARGEMENT ET FUSION DES DEUX PHASES
# =====================================================================

def load_phase_cookies(directory: Path, phase_label: str) -> List[Dict]:
    """
    Charge tous les cookies depuis un répertoire de catégories.
    Ajoute le champ `_phase` à chaque cookie pour traçabilité.
    """
    all_cookies = []

    if not directory.exists():
        return all_cookies

    for json_file in directory.glob("*.json"):
        # Ignorer les fichiers de métadonnées
        if json_file.stem.startswith("_"):
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                if not isinstance(items, list):
                    continue
                for item in items:
                    item["_phase"] = phase_label
                    item["_category"] = json_file.stem  # ex: IDENTITY_TRACKING
                    all_cookies.append(item)
        except Exception as e:
            print(f"    Erreur lecture {json_file}: {e}")

    return all_cookies


def group_by_key(cookies: List[Dict]) -> Dict[str, List[Dict]]:
    """Groupe les cookies par leur clé unique (name|domain|path)."""
    grouped: Dict[str, List[Dict]] = {}
    for cookie in cookies:
        key = create_cookie_key(cookie)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(cookie)
    return grouped


def parse_timestamp(cookie: Dict) -> float:
    """Convertit le champ timestamp en float POSIX. Retourne 0 si absent/invalide."""
    ts = cookie.get("timestamp", "")
    if not ts:
        return 0.0
    try:
        return datetime.fromisoformat(str(ts)).timestamp()
    except Exception:
        return 0.0


# =====================================================================
# 3. CONSTRUCTION DE LA TIMELINE COMBINÉE
# =====================================================================

def build_combined_timeline(cookie_key: str, all_events: List[Dict]) -> Dict:
    """
    Construit la timeline fusionnée pour un cookie.

    all_events : liste de cookies issus de added + modified + removed
                 des deux phases, déjà enrichis avec _phase et _event_type.
    """
    # Trier par timestamp réel
    all_events.sort(key=parse_timestamp)

    events = []
    for cookie in all_events:
        ts = parse_timestamp(cookie)
        expires = cookie.get("expires", -1)
        now = datetime.now().timestamp()
        duration = (expires - now) / (24 * 3600) if expires and expires > 0 else 0.0

        value = cookie.get("value", "")
        entropy = pm.calculate_entropy(str(value)) if value else 0.0

        category = cookie.get("_category", "unknown")
        subcategory = cookie.get("matched_subcategory", "")
        pii_category = f"{category}::{subcategory}" if subcategory else category

        changed_fields_raw = cookie.get("changed_fields", "none")
        if isinstance(changed_fields_raw, str):
            changed_fields = [f.strip() for f in changed_fields_raw.split(",")
                              if f.strip() and f.strip() != "none"]
        else:
            changed_fields = changed_fields_raw if isinstance(changed_fields_raw, list) else []

        events.append({
            "timestamp": cookie.get("timestamp", ""),
            "task_id": cookie.get("task_id", ""),
            "phase": cookie.get("_phase", "unknown"),
            "type": cookie.get("_event_type", "unknown"),
            "duration_days": round(duration, 2),
            "entropy": round(entropy, 4),
            "pii_category": pii_category,
            "changed_fields": changed_fields,
            "initial_url": cookie.get("initial_url", ""),
            "final_url": cookie.get("final_url", ""),
            "value": value,
        })

    duration_evolution = [e["duration_days"] for e in events]
    entropy_evolution = [e["entropy"] for e in events]
    pii_categories = [e["pii_category"] for e in events]

    num_auth = sum(1 for e in events if e["phase"] == "auth")
    num_perssistence = sum(1 for e in events if e["phase"] == "perssistence")
    num_modifications = sum(1 for e in events if e["type"] == "modified")
    num_removals = sum(1 for e in events if e["type"] == "removed")

    # Détection de la continuité inter-phases : cookie présent dans les deux
    phases_present = set(e["phase"] for e in events)
    crosses_phases = len(phases_present) > 1

    return {
        "key": cookie_key,
        "events": events,
        "duration_evolution": duration_evolution,
        "entropy_evolution": entropy_evolution,
        "pii_categories": pii_categories,
        "num_auth_events": num_auth,
        "num_perssistence_events": num_perssistence,
        "num_modifications": num_modifications,
        "num_removals": num_removals,
        "crosses_phases": crosses_phases,
    }


# =====================================================================
# 4. ANALYSE GLOBALE
# =====================================================================

def analyze_combined_lifecycle(
    auth_added_dir: Path,
    auth_modified_dir: Path,
    auth_removed_dir: Path,
    pers_added_dir: Path,
    pers_modified_dir: Path,
    pers_removed_dir: Path,
) -> Dict:
    """Analyse complète du cycle de vie combiné Auth + Perssistence."""

    print("\n Chargement des cookies Auth/ALL...")
    auth_added     = load_phase_cookies(auth_added_dir,     "auth")
    auth_modified  = load_phase_cookies(auth_modified_dir,  "auth")
    auth_removed   = load_phase_cookies(auth_removed_dir,   "auth")

    print(" Chargement des cookies Perssistence/ALL...")
    pers_added     = load_phase_cookies(pers_added_dir,     "perssistence")
    pers_modified  = load_phase_cookies(pers_modified_dir,  "perssistence")
    pers_removed   = load_phase_cookies(pers_removed_dir,   "perssistence")

    # Annoter le type d'événement
    for c in auth_added + pers_added:
        c["_event_type"] = "added"
    for c in auth_modified + pers_modified:
        c["_event_type"] = "modified"
    for c in auth_removed + pers_removed:
        c["_event_type"] = "removed"

    all_cookies = (auth_added + auth_modified + auth_removed +
                   pers_added + pers_modified + pers_removed)

    print(f"   Auth:         {len(auth_added)} added | {len(auth_modified)} modified | {len(auth_removed)} removed")
    print(f"   Perssistence: {len(pers_added)} added | {len(pers_modified)} modified | {len(pers_removed)} removed")
    print(f"   Total brut:   {len(all_cookies)} événements")

    # Grouper par clé cookie
    grouped = group_by_key(all_cookies)
    print(f"\n   {len(grouped)} clés cookies uniques")

    # Construire les timelines
    print("\n⏱  Construction des timelines combinées...")
    timelines = {}
    for key, events in grouped.items():
        timelines[key] = build_combined_timeline(key, events)

    # Métriques globales
    total = len(timelines)
    crosses = sum(1 for t in timelines.values() if t["crosses_phases"])
    modified = sum(1 for t in timelines.values() if t["num_modifications"] > 0)
    removed_count = sum(1 for t in timelines.values() if t["num_removals"] > 0)

    # Évolution durée
    dur_inc = dur_dec = 0
    for t in timelines.values():
        if len(t["duration_evolution"]) > 1:
            if t["duration_evolution"][-1] > t["duration_evolution"][0]:
                dur_inc += 1
            elif t["duration_evolution"][-1] < t["duration_evolution"][0]:
                dur_dec += 1

    # Évolution entropie
    ent_inc = ent_dec = 0
    for t in timelines.values():
        if len(t["entropy_evolution"]) > 1:
            if t["entropy_evolution"][-1] > t["entropy_evolution"][0]:
                ent_inc += 1
            elif t["entropy_evolution"][-1] < t["entropy_evolution"][0]:
                ent_dec += 1

    # transitions PII
    pii_transitions = Counter()
    transitions_details = []
    for t in timelines.values():
        cats = t["pii_categories"]
        if len(cats) > 1 and cats[0] != cats[-1]:
            pii_transitions[(cats[0], cats[-1])] += 1
            transitions_details.append({
                "key": t["key"],
                "transition": f"{cats[0]} → {cats[-1]}",
                "value_initial": t["events"][0]["value"],
                "value_final": t["events"][-1]["value"],
                "num_events": len(cats),
                "phases": list(set(e["phase"] for e in t["events"]))
            })

    # Volatilité
    volatility = Counter()
    for t in timelines.values():
        n = t["num_modifications"]
        if n == 0:
            volatility["stable"] += 1
        elif n <= 2:
            volatility["moderate"] += 1
        else:
            volatility["high"] += 1

    top_modified = sorted(timelines.values(), key=lambda x: x["num_modifications"], reverse=True)[:50]

    return {
        "timelines": timelines,
        "metrics": {
            "total_cookies": total,
            "cookies_crossing_phases": crosses,
            "cookies_modified": modified,
            "cookies_removed": removed_count,
            "duration_increases": dur_inc,
            "duration_decreases": dur_dec,
            "entropy_increases": ent_inc,
            "entropy_decreases": ent_dec,
            "pii_transitions": {f"{k[0]} → {k[1]}": v for k, v in pii_transitions.items()},
            "volatility_distribution": dict(volatility),
        },
        "top_modified": top_modified,
        "transitions_details": transitions_details,
    }


# =====================================================================
# 5. MAIN
# =====================================================================

def main():
    base_dir    = Path(__file__).resolve().parent.parent / "data"
    output_base = Path(__file__).resolve().parent.parent / "results"

    users   = ("FR_0417", "FR_0446", "FR_0458")

    print("=" * 70)
    print(" LIFECYCLE ANALYSIS - Combiné Auth/ALL + Perssistence/ALL")
    print("=" * 70)

    for user in users:
        print(f"\n{'='*70}")
        print(f" USER : {user}")
        print(f"{'='*70}")

        auth_base = base_dir / "user" / "Auth" / user / "ALL" / "cookies"
        pers_base = base_dir / "user" / "Perssistence" / user / "ALL" / "cookies"

        # Vérification minimale
        if not auth_base.exists() and not pers_base.exists():
            print(f"   Aucun dossier cookies trouvé pour {user}, ignoré.")
            continue

        auth_added_dir    = auth_base / "added"
        auth_modified_dir = auth_base / "modified"
        auth_removed_dir  = auth_base / "removed"
        pers_added_dir    = pers_base / "added"
        pers_modified_dir = pers_base / "modified"
        pers_removed_dir  = pers_base / "removed"

        results = analyze_combined_lifecycle(
            auth_added_dir, auth_modified_dir, auth_removed_dir,
            pers_added_dir, pers_modified_dir, pers_removed_dir,
        )

        # Dossier de sortie (séparé des résultats originaux)
        output_dir = output_base / "Auth_Perssistence" / user / "ALL" / "cookies" / "lifecycle"
        output_dir.mkdir(parents=True, exist_ok=True)

        # --- Sauvegarde métriques ---
        metrics_path = output_dir / "lifecycle_data.json"
        serializable = {
            "phases": ["Auth/ALL", "Perssistence/ALL"],
            "metrics": results["metrics"],
            "num_timelines": len(results["timelines"]),
            "top_modified_keys": [t["key"] for t in results["top_modified"][:20]],
        }
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        print(f"\n   Métriques → {metrics_path}")

        # --- Sauvegarde timelines complètes ---
        timelines_dir = output_dir / "consolidated"
        timelines_dir.mkdir(parents=True, exist_ok=True)
        timelines_path = timelines_dir / "timelines_complete.json"
        
        # --- Sauvegarde détails transitions ---
        transitions_path = output_dir / "pii_transitions_details.json"
        with open(transitions_path, "w", encoding="utf-8") as f:
            json.dump(results["transitions_details"], f, indent=2, ensure_ascii=False)
        print(f"  Détails Transitions → {transitions_path}")

        timelines_out = {}
        for key, tl in results["timelines"].items():
            timelines_out[key] = {
                "key": tl["key"],
                "crosses_phases": tl["crosses_phases"],
                "num_auth_events": tl["num_auth_events"],
                "num_perssistence_events": tl["num_perssistence_events"],
                "num_modifications": tl["num_modifications"],
                "num_removals": tl["num_removals"],
                "events": tl["events"],
                "duration_evolution": tl["duration_evolution"],
                "entropy_evolution": tl["entropy_evolution"],
                "pii_categories": tl["pii_categories"],
            }

        with open(timelines_path, "w", encoding="utf-8") as f:
            json.dump(timelines_out, f, indent=2, ensure_ascii=False)

        size_mb = timelines_path.stat().st_size / 1024 / 1024
        print(f"   Timelines → {timelines_path} ({size_mb:.1f} MB)")

        # --- Résumé console ---
        m = results["metrics"]
        print(f"\n  RÉSUMÉ {user}:")
        print(f"    Cookies totaux        : {m['total_cookies']:,}")
        print(f"    Cookies cross-phases  : {m['cookies_crossing_phases']:,}  ← persistants entre Auth et Perssistence")
        print(f"    Cookies modifiés      : {m['cookies_modified']:,}")
        print(f"    Cookies supprimés     : {m['cookies_removed']:,}")
        print(f"    Durée ↑               : {m['duration_increases']:,}  |  Durée ↓ : {m['duration_decreases']:,}")
        print(f"    Entropie ↑            : {m['entropy_increases']:,}  |  Entropie ↓ : {m['entropy_decreases']:,}")
        print(f"    Volatilité            : {m['volatility_distribution']}")

    print(f"\n{'='*70}")
    print(" TERMINÉ — résultats dans results/Auth_Perssistence/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
