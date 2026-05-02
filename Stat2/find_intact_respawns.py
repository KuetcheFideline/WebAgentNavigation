import json
from pathlib import Path
from collections import defaultdict

def find_intact_respawns(filepath):
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        timelines = json.load(f)
    
    intact_respawns = []
    
    for key, timeline in timelines.items():
        events = timeline.get('events', [])
        for i in range(len(events)):
            if events[i]['type'] == 'deleted':
                val_before = events[i]['value']
                category = events[i].get('pii_category', 'UNKNOWN')
                # Search for later addition or modification with the same value
                for j in range(i + 1, len(events)):
                    if events[j]['type'] in ('added', 'modified'):
                        val_after = events[j]['value']
                        if val_before == val_after and val_before != "":
                            intact_respawns.append({
                                'key': key,
                                'value': val_before,
                                'category': category,
                                'deleted_at_phase': events[i]['phase'],
                                'deleted_at_task': events[i]['task_id'],
                                'reappeared_at_phase': events[j]['phase'],
                                'reappeared_at_task': events[j]['task_id']
                            })
                            break # Count only one respawn per deletion for now
    
    return intact_respawns

results_dirs = [
    Path('/home/fideline/Téléchargements/PII_Statistical_Modeling/results/Auth_Perssistence'),
    Path('/home/fideline/Téléchargements/PII_Statistical_Modeling/results/Auth')
]
output_file = Path('/home/fideline/Téléchargements/PII_Statistical_Modeling/results/intact_respawns_by_type_and_category.json')

all_intact_respawns = []
grouped_results = defaultdict(lambda: defaultdict(list))

for base_dir in results_dirs:
    if not base_dir.exists():
        continue
    for user_dir in base_dir.glob('FR_*'):
        user = user_dir.name
        # Define possible storage types and their corresponding relative paths to timelines_complete.json
        storage_configs = [
            ('localstorage', 'ALL/storage_analysis/localstorage/consolidated/timelines_complete.json'),
            ('sessionstorage', 'ALL/storage_analysis/sessionstorage/consolidated/timelines_complete.json'),
            ('indexeddb', 'ALL/storage_analysis/indexeddb/consolidated/timelines_complete.json'),
            ('localstorage', 'ALL/localstorage/lifecycle/consolidated/timelines_complete.json'), # Alt path
            ('sessionstorage', 'ALL/sessionstorage/lifecycle/consolidated/timelines_complete.json'), # Alt path
            ('cookies', 'ALL/cookies/lifecycle/consolidated/timelines_complete.json'),
            ('indexeddb', 'ALL/indexeddb/lifecycle/consolidated/timelines_complete.json'),
        ]
        
        for storage_type, rel_path in storage_configs:
            timeline_path = user_dir / rel_path
            if timeline_path.exists():
                respawns = find_intact_respawns(timeline_path)
                for r in respawns:
                    r['user'] = user
                    r['storage'] = storage_type
                    all_intact_respawns.append(r)
                    
                    # Grouping
                    grouped_results[storage_type][r['category']].append({
                        'user': user,
                        'source': base_dir.name,
                        'key': r['key'],
                        'value': r['value'],
                        'deleted_at': f"{r['deleted_at_phase']} (task {r['deleted_at_task']})",
                        'reappeared_at': f"{r['reappeared_at_phase']} (task {r['reappeared_at_task']})"
                    })

print(f"Total intact respawns: {len(all_intact_respawns)}")

# Save grouped results to file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(grouped_results, f, indent=2, ensure_ascii=False)

print(f"Grouped results saved to: {output_file}")

# Format output for easier reading in terminal
summary = defaultdict(list)
for r in all_intact_respawns:
    summary[r['key']].append(r['value'])

for key, values in summary.items():
    unique_vals = list(set(values))
    print(f"Key: {key} | Values: {unique_vals}")
