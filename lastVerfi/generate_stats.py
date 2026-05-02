#!/usr/bin/env python3
"""
Génération des statistiques d'exactitude de la classification PII.
Usage : python3 generate_stats.py
"""

import json
import glob
import os
from collections import defaultdict

directory = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(directory, "*.json")))

files = [f for f in files if os.path.basename(f) != "generate_stats.py"]

cat_stats = defaultdict(lambda: {
    "total": 0, "correct": 0, "incorrect": 0, "partial": 0,
    "ai_total": 0, "ai_correct": 0, "ai_incorrect": 0,
    "noai_total": 0, "noai_correct": 0, "noai_incorrect": 0
})

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f" Erreur JSON : {os.path.basename(file)}")
            continue

    for item in data:
        me = item.get("manual_eval", None)
        if me is None:
            continue

        cat = item.get("_primary_category", os.path.basename(file).replace(".json", ""))
        is_ai = item.get("ai_processed", False)
        s = cat_stats[cat]
        s["total"] += 1

        if me == 1:
            s["correct"] += 1
        elif me == 0:
            s["incorrect"] += 1
        elif me == 3:
            s["partial"] += 1

        if is_ai:
            s["ai_total"] += 1
            if me == 1: s["ai_correct"] += 1
            elif me == 0: s["ai_incorrect"] += 1
        else:
            s["noai_total"] += 1
            if me == 1: s["noai_correct"] += 1
            elif me == 0: s["noai_incorrect"] += 1

# ── Affichage ──────────────────────────────────────────────────────────────────
SEP = "=" * 130
sep = "-" * 130
HDR = f"{'Catégorie':<35} | {'Total':>5} | {'OK(1)':>5} | {'KO(0)':>5} | {'Part(3)':>7} | {'Acc Global':>10} | {'Acc IA':>8} | {'Acc NoIA':>10} | {'Entrées IA':>10} | {'Entrées NoIA':>12}"

print(SEP)
print("STATS PAR _primary_category")
print(SEP)
print(HDR)
print(sep)

total_all = ok_all = ko_all = part_all = 0
ai_ok_all = ai_ko_all = ai_tot_all = 0
noai_ok_all = noai_ko_all = noai_tot_all = 0

for cat, s in sorted(cat_stats.items()):
    base = s['correct'] + s['incorrect']
    acc = f"{s['correct']/base*100:.1f}%" if base > 0 else "N/A"

    ai_base = s['ai_correct'] + s['ai_incorrect']
    acc_ai = f"{s['ai_correct']/ai_base*100:.1f}%" if ai_base > 0 else "N/A"

    noai_base = s['noai_correct'] + s['noai_incorrect']
    acc_noai = f"{s['noai_correct']/noai_base*100:.1f}%" if noai_base > 0 else "N/A"

    print(f"{cat:<35} | {s['total']:>5} | {s['correct']:>5} | {s['incorrect']:>5} | {s['partial']:>7} | {acc:>10} | {acc_ai:>8} | {acc_noai:>10} | {s['ai_total']:>10} | {s['noai_total']:>12}")

    total_all  += s['total'];  ok_all   += s['correct'];   ko_all   += s['incorrect']; part_all += s['partial']
    ai_ok_all  += s['ai_correct'];  ai_ko_all  += s['ai_incorrect'];  ai_tot_all  += s['ai_total']
    noai_ok_all += s['noai_correct']; noai_ko_all += s['noai_incorrect']; noai_tot_all += s['noai_total']

print(sep)

base_all    = ok_all + ko_all
acc_all     = f"{ok_all/base_all*100:.2f}%"     if base_all > 0 else "N/A"
ai_base_all = ai_ok_all + ai_ko_all
acc_ai_all  = f"{ai_ok_all/ai_base_all*100:.2f}%" if ai_base_all > 0 else "N/A"
noai_base_all = noai_ok_all + noai_ko_all
acc_noai_all = f"{noai_ok_all/noai_base_all*100:.2f}%" if noai_base_all > 0 else "N/A"

print(f"{'TOTAL':<35} | {total_all:>5} | {ok_all:>5} | {ko_all:>5} | {part_all:>7} | {acc_all:>10} | {acc_ai_all:>8} | {acc_noai_all:>10} | {ai_tot_all:>10} | {noai_tot_all:>12}")
print(SEP)
print(f"\n   Correctes (1)  : {ok_all}")
print(f"    Incorrectes (0): {ko_all}")
print(f"    Partielles (3) : {part_all}")
print(f"\n    Exactitude globale : {acc_all}  ({ok_all}/{base_all})")
print(f"    Avec IA            : {acc_ai_all}  ({ai_ok_all}/{ai_base_all})")
print(f"   Sans IA (règles)   : {acc_noai_all}  ({noai_ok_all}/{noai_base_all})")
print(SEP)
