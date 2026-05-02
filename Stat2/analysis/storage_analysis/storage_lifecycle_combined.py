#!/usr/bin/env python3
"""
Storage Lifecycle Analysis - Phase Combinée Auth/ALL + Perssistence/ALL
======================================================================
Combine les événements de stockage (localStorage, IndexedDB, etc.) des deux phases 
en une seule timeline chronologique continue par item.

- Auth/ALL         → Phase 1 (navigation authentifiée)
- Perssistence/ALL → Phase 2 (continuation / persistance post-session)

L'ordre des événements est déterminé par le champ `timestamp` réel.

Sortie : results/Auth_Perssistence/{user}/storage_analysis/
  - {storage_type}/lifecycle_data.json
  - {storage_type}/consolidated/timelines_complete.json
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict

# Import des modules d'analyse partagés
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import analysis.privacy_metrics as pm

# =====================================================================
# 1. CLÉS ET HELPERS
# =====================================================================

def create_storage_key(item: Dict) -> str:
    """
    Crée une clé unique pour un item de stockage.
    localStorage/sessionStorage utilisent 'key'
    IndexedDB utilise 'name|source_file'
    """
    if 'key' in item:
        return item['key']
    
    name = item.get('name', '')
    source_file = item.get('source_file', '')
    return f"{name}|{source_file}"

def parse_timestamp(item: Dict) -> float:
    """Convertit le champ timestamp en float POSIX."""
    ts = item.get("timestamp", "")
    if not ts:
        return 0.0
    try:
        if isinstance(ts, (int, float)):
            return float(ts)
        return datetime.fromisoformat(str(ts)).timestamp()
    except Exception:
        return 0.0

# =====================================================================
# 2. CHARGEMENT DES DONNÉES
# =====================================================================

def load_phase_items(directory: Path, phase_label: str, storage_type: str) -> List[Dict]:
    """Charge tous les items depuis un répertoire de catégories."""
    all_items = []
    if not directory.exists():
        return all_items

    for json_file in directory.glob("*.json"):
        if json_file.stem.startswith("_"):
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                if not isinstance(items, list):
                    continue
                for item in items:
                    item["_phase"] = phase_label
                    item["_category"] = json_file.stem
                    item["_storage_type"] = storage_type
                    all_items.append(item)
        except Exception as e:
            print(f"  ⚠️  Erreur lecture {json_file}: {e}")
    return all_items

# =====================================================================
# 3. CONSTRUCTION DE LA TIMELINE
# =====================================================================

def build_combined_timeline(key: str, all_events: List[Dict]) -> Dict:
    """Construit la timeline fusionnée pour un item."""
    # Trier par timestamp réel
    all_events.sort(key=parse_timestamp)

    events = []
    for item in all_events:
        value = str(item.get("value", ""))
        entropy = pm.calculate_entropy(value)
        size = len(value.encode('utf-8'))
        
        category = item.get("_category", "unknown")
        matches = item.get('matches', [])
        if matches and len(matches) > 0:
            subcategory = matches[0].get('subcategory', '')
            pii_category = f"{category}::{subcategory}" if subcategory else category
        else:
            pii_category = category

        events.append({
            "timestamp": item.get("timestamp", ""),
            "task_id": item.get("task_id", ""),
            "phase": item.get("_phase", "unknown"),
            "type": item.get("_event_type", "unknown"),
            "entropy": round(entropy, 4),
            "size_bytes": size,
            "pii_category": pii_category,
            "url": item.get("final_url", item.get("initial_url", "")),
            "value": value,
        })

    entropy_evolution = [e["entropy"] for e in events]
    size_evolution = [e["size_bytes"] for e in events]
    pii_categories = [e["pii_category"] for e in events]

    num_auth = sum(1 for e in events if e["phase"] == "auth")
    num_pers = sum(1 for e in events if e["phase"] == "perssistence")
    num_modifications = sum(1 for e in events if e["type"] == "modified")
    num_removals = sum(1 for e in events if e["type"] == "removed") or sum(1 for e in events if e["type"] == "deleted")

    # Continuité inter-phases
    phases_present = set(e["phase"] for e in events)
    crosses_phases = len(phases_present) > 1

    return {
        "key": key,
        "events": events,
        "entropy_evolution": entropy_evolution,
        "size_evolution": size_evolution,
        "pii_categories": pii_categories,
        "num_auth_events": num_auth,
        "num_persistence_events": num_pers,
        "num_modifications": num_modifications,
        "num_removals": num_removals,
        "crosses_phases": crosses_phases,
    }

# =====================================================================
# 4. ANALYSE PRINCIPALE
# =====================================================================

def analyze_combined_storage(user: str, storage_type: str, base_dir: Path, output_base: Path):
    """Analyse combinée pour un type de stockage spécifique."""
    
    auth_base = base_dir / "user" / "Auth" / user / "ALL" / storage_type
    pers_base = base_dir / "user" / "Perssistence" / user / "ALL" / storage_type

    if not auth_base.exists() and not pers_base.exists():
        print(f"   ⚠️  Données manquantes pour {user} / {storage_type}")
        return

    print(f"\n--- Analyse {storage_type.upper()} pour {user} ---")
    
    # Chargement Phase 1 (Auth)
    print("   Lancement chargement Phase 1 (Auth)...")
    auth_added = load_phase_items(auth_base / "added", "auth", storage_type)
    for c in auth_added: c["_event_type"] = "added"
    
    auth_modified = load_phase_items(auth_base / "modified", "auth", storage_type)
    for c in auth_modified: c["_event_type"] = "modified"
    
    auth_removed = load_phase_items(auth_base / "removed", "auth", storage_type)
    if not auth_removed:
        auth_removed = load_phase_items(auth_base / "deleted", "auth", storage_type)
    for c in auth_removed: c["_event_type"] = "deleted"
    
    print(f"   Phase 1 chargée: {len(auth_added)} added, {len(auth_modified)} modified, {len(auth_removed)} deleted")

    # Chargement Phase 2 (Persistence)
    print("   Lancement chargement Phase 2 (Persistence)...")
    pers_added = load_phase_items(pers_base / "added", "perssistence", storage_type)
    for c in pers_added: c["_event_type"] = "added"
    
    pers_modified = load_phase_items(pers_base / "modified", "perssistence", storage_type)
    for c in pers_modified: c["_event_type"] = "modified"
    
    pers_removed = load_phase_items(pers_base / "removed", "perssistence", storage_type)
    if not pers_removed:
        pers_removed = load_phase_items(pers_base / "deleted", "perssistence", storage_type)
    for c in pers_removed: c["_event_type"] = "deleted"
    
    print(f"   Phase 2 chargée: {len(pers_added)} added, {len(pers_modified)} modified, {len(pers_removed)} deleted")

    # Groupement par clé
    print("   Groupement des items par clé...")
    grouped = defaultdict(list)
    for item in (auth_added + auth_modified + auth_removed + pers_added + pers_modified + pers_removed):
        key = create_storage_key(item)
        grouped[key].append(item)
    
    # Nettoyage mémoire
    del auth_added, auth_modified, auth_removed, pers_added, pers_modified, pers_removed
    
    print(f"   {len(grouped)} items uniques détectés. Construction des timelines...")

    # Timelines
    timelines = {}
    count = 0
    total_keys = len(grouped)
    for key, events in grouped.items():
        timelines[key] = build_combined_timeline(key, events)
        count += 1
        if count % 1000 == 0:
            print(f"      {count}/{total_keys} timelines construites...")

    # Métriques
    print("   Calcul des métriques globales...")
    total = len(timelines)
    crosses = sum(1 for t in timelines.values() if t["crosses_phases"])
    modified = sum(1 for t in timelines.values() if t["num_modifications"] > 0)
    
    volatility = Counter()
    transitions_details = []
    
    for key, t in timelines.items():
        n = t["num_modifications"]
        if n == 0: volatility["stable"] += 1
        elif n <= 2: volatility["moderate"] += 1
        else: volatility["high"] += 1
        
        # Détection des transitions PII
        cats = t["pii_categories"]
        if len(cats) > 1 and cats[0] != cats[-1]:
            transitions_details.append({
                "key": key,
                "transition": f"{cats[0]} → {cats[-1]}",
                "value_initial": t["events"][0]["value"],
                "value_final": t["events"][-1]["value"],
                "num_events": len(cats),
                "phases": list(set(e["phase"] for e in t["events"]))
            })

    # Export
    print(f"   Export des résultats ({len(transitions_details)} transitions détectées)...")
    output_dir = output_base / "Auth_Perssistence" / user / "ALL" / "storage_analysis" / storage_type
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export détails transitions
    with open(output_dir / "pii_transitions_details.json", 'w') as f:
        json.dump(transitions_details, f, indent=2)
    
    metrics_path = output_dir / "lifecycle_data.json"
    serializable = {
        "storage_type": storage_type,
        "metrics": {
            "total_items": total,
            "items_crossing_phases": crosses,
            "items_modified": modified,
            "volatility_distribution": dict(volatility)
        },
        "num_timelines": len(timelines)
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    timelines_path = output_dir / "consolidated" / "timelines_complete.json"
    timelines_path.parent.mkdir(parents=True, exist_ok=True)
    with open(timelines_path, "w", encoding="utf-8") as f:
        # On limite le dump pour éviter des fichiers géants si besoin, mais ici on garde tout pour la fidélité
        json.dump(timelines, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Résultats exportés dans {output_dir}")
    print(f"   Items traversant les phases : {crosses}")

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent / "data"
    output_base = Path(__file__).resolve().parent.parent.parent / "results"
    
    users = ("FR_0417", "FR_0446", "FR_0458")
    storage_types = ("localstorage", "indexeddb", "sessionstorage")
    
    for user in users:
        print(f"\n{'='*70}\nUTILISATEUR : {user}\n{'='*70}")
        for st in storage_types:
            analyze_combined_storage(user, st, base_dir, output_base)

if __name__ == "__main__":
    main()
