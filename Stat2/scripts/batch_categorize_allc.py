#!/usr/bin/env python3
"""
RÉPLIQUE DÉDIÉE all_c — Catégorisation Batch
=============================================
Même logique que batch_categorize.py mais :
  - Lit depuis  data/raw/<auth>/<user>/ALL/storage_state/Auth/all_c/  (récursivement)
  - Écrit dans  data/raw/<auth>/<user>/ALL/categorized_allc_*/ (résultats catégorisés)
  - N'écrase PAS les catégorisations précédentes du pipeline standard.
"""

import json
from pathlib import Path
import sys

# Ajouter le dossier scripts au path pour importer categorize_cookies
sys.path.insert(0, str(Path(__file__).resolve().parent))

from categorize_cookies import (
    categorize_cookie,
    try_decode_value,
    recursive_decode_and_reclassify,
    TRACKING_PATTERNS_COMPLETE
)


# ── Helpers partagés ──────────────────────────────────────────────────────────

def _init_categorized():
    cat = {k: [] for k in TRACKING_PATTERNS_COMPLETE.keys()}
    cat['UNCATEGORIZED'] = []
    return cat


def _assign_category(item, matches):
    """Détermine la catégorie principale et enrichit l'item."""
    if matches:
        primary = next(
            (m['category'] for m in matches if m['category'] != 'SUSPICIOUS_VALUES'),
            matches[0]['category']
        )
    else:
        primary = 'UNCATEGORIZED'
    item['matches'] = matches
    item['primary_category'] = primary
    return primary


def _save_categorized(categorized, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for category, items in categorized.items():
        if items:
            p = output_dir / f"{category}.json"
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)


# ── Cookies ───────────────────────────────────────────────────────────────────

def categorize_cookies_allc(storage_state_dir: Path, output_dir: Path):
    """
    Catégorise les cookies trouvés récursivement dans all_c.
    Retourne (total, categorized_dict).
    """
    categorized = _init_categorized()
    total = 0

    for json_file in storage_state_dir.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
            cookies_data = data.get('cookies', {})

            for action in ('added', 'removed', 'modified'):
                for ck, cookie in cookies_data.get(action, {}).items():
                    if not isinstance(cookie, dict):
                        continue
                    total += 1
                    cookie['action'] = action
                    cookie['source_file'] = str(json_file.name)

                    matches = categorize_cookie(cookie, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    matches = recursive_decode_and_reclassify(cookie, matches, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    primary = _assign_category(cookie, matches)
                    categorized[primary].append(cookie)
        except Exception:
            continue

    _save_categorized(categorized, output_dir)
    return total, categorized


# ── LocalStorage ──────────────────────────────────────────────────────────────

def categorize_localstorage_allc(storage_state_dir: Path, output_dir: Path):
    """
    Catégorise le localStorage trouvé récursivement dans all_c.
    Retourne (total, categorized_dict).
    """
    categorized = _init_categorized()
    total = 0

    for json_file in storage_state_dir.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
            ls_data = data.get('localStorage', {})

            for action in ('added', 'removed', 'modified'):
                for key, value in ls_data.get(action, {}).items():
                    total += 1
                    item = {
                        'name': key,
                        'value': value if isinstance(value, str) else str(value),
                        'action': action,
                        'source_file': str(json_file.name)
                    }
                    matches = categorize_cookie(item, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    matches = recursive_decode_and_reclassify(item, matches, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    primary = _assign_category(item, matches)
                    categorized[primary].append(item)
        except Exception:
            continue

    _save_categorized(categorized, output_dir)
    return total, categorized


# ── SessionStorage ────────────────────────────────────────────────────────────

def categorize_sessionstorage_allc(storage_state_dir: Path, output_dir: Path):
    """
    Catégorise le sessionStorage trouvé récursivement dans all_c.
    Retourne (total, categorized_dict).
    """
    categorized = _init_categorized()
    total = 0

    for json_file in storage_state_dir.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
            ss_data = data.get('sessionStorage', {})

            for action in ('added', 'removed', 'modified'):
                for key, value in ss_data.get(action, {}).items():
                    total += 1
                    item = {
                        'name': key,
                        'value': value if isinstance(value, str) else str(value),
                        'action': action,
                        'source_file': str(json_file.name)
                    }
                    matches = categorize_cookie(item, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    matches = recursive_decode_and_reclassify(item, matches, TRACKING_PATTERNS_COMPLETE, source_type=action)
                    primary = _assign_category(item, matches)
                    categorized[primary].append(item)
        except Exception:
            continue

    _save_categorized(categorized, output_dir)
    return total, categorized


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    project_root = Path(__file__).resolve().parent.parent
    raw_dir      = project_root / "data" / "raw"

    if not raw_dir.exists():
        print(f"❌ Dossier {raw_dir} non trouvé")
        return

    print("=" * 70)
    print("CATÉGORISATION BATCH — all_c UNIQUEMENT")
    print("=" * 70)

    users         = ('FR_0417', 'FR_0446', 'FR_0458')
    auth_statuses = ('Auth', 'Normal', 'Perssistence')
    policy        = 'ALL'

    for auth in auth_statuses:
        for user in users:
            allc_dir = (raw_dir / auth / user / policy
                        / 'storage_state' / 'Auth' / 'all_c')

            if not allc_dir.exists():
                print(f"  [SKIP] {auth}/{user} — all_c introuvable")
                continue

            base_out = raw_dir / auth / user / policy

            print(f"\n  {'='*60}")
            print(f"  {auth} / {user} / ALL_C")
            print(f"  {'='*60}")

            # Cookies
            n_c, cat_c = categorize_cookies_allc(
                allc_dir,
                base_out / 'categorized_allc_cookies'
            )
            n_cat_c = sum(1 for v in cat_c.values() if v)
            print(f"  ✅ Cookies      : {n_c:4d} items → {n_cat_c} catégories")

            # LocalStorage
            n_l, cat_l = categorize_localstorage_allc(
                allc_dir,
                base_out / 'categorized_allc_localstorage'
            )
            n_cat_l = sum(1 for v in cat_l.values() if v)
            print(f"  ✅ LocalStorage : {n_l:4d} items → {n_cat_l} catégories")

            # SessionStorage
            n_s, cat_s = categorize_sessionstorage_allc(
                allc_dir,
                base_out / 'categorized_allc_sessionstorage'
            )
            n_cat_s = sum(1 for v in cat_s.values() if v)
            print(f"  ✅ SessionStorage: {n_s:4d} items → {n_cat_s} catégories")

    print("\n" + "=" * 70)
    print("🎉 CATÉGORISATION all_c TERMINÉE")
    print("=" * 70)
    print("\n📂 Résultats dans : data/raw/<auth>/<user>/ALL/categorized_allc_*/")


if __name__ == '__main__':
    main()
