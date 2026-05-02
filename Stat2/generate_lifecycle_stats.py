import json
from pathlib import Path
from collections import defaultdict

def analyze_lifecycle(filepath):
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            timelines = json.load(f)
        except json.JSONDecodeError:
            return None
    
    stats = defaultdict(lambda: {
        'total_keys': 0,
        'added': 0,
        'modified': 0,
        'deleted': 0,
        'respawns': 0,
        'intact_respawns': 0
    })
    
    for key, timeline in timelines.items():
        events = timeline.get('events', [])
        if not events:
            continue
            
        # Determine category (use first event's category as representative)
        category = next((e.get('pii_category') for e in events if e.get('pii_category')), 'UNKNOWN')
        
        stats[category]['total_keys'] += 1
        
        for i, event in enumerate(events):
            etype = event['type']
            if etype == 'added':
                stats[category]['added'] += 1
            elif etype == 'modified':
                stats[category]['modified'] += 1
            elif etype in ('deleted', 'removed'):
                stats[category]['deleted'] += 1
                
                # Check for respawn
                val_before = event.get('value')
                for j in range(i + 1, len(events)):
                    if events[j]['type'] in ('added', 'modified'):
                        stats[category]['respawns'] += 1
                        val_after = events[j].get('value')
                        if val_before == val_after and val_before != "":
                            stats[category]['intact_respawns'] += 1
                        break # Only count the first respawn after a deletion
                        
    return stats

def main():
    results_dirs = [
        Path('/home/fideline/Téléchargements/PII_Statistical_Modeling/results/Auth_Perssistence'),
        Path('/home/fideline/Téléchargements/PII_Statistical_Modeling/results/Auth')
    ]
    
    global_stats = defaultdict(lambda: defaultdict(lambda: {
        'total_keys': 0,
        'added': 0,
        'modified': 0,
        'deleted': 0,
        'respawns': 0,
        'intact_respawns': 0
    }))
    
    storage_configs = [
        ('localstorage', 'ALL/storage_analysis/localstorage/consolidated/timelines_complete.json'),
        ('sessionstorage', 'ALL/storage_analysis/sessionstorage/consolidated/timelines_complete.json'),
        ('indexeddb', 'ALL/storage_analysis/indexeddb/consolidated/timelines_complete.json'),
        ('localstorage', 'ALL/localstorage/lifecycle/consolidated/timelines_complete.json'),
        ('sessionstorage', 'ALL/sessionstorage/lifecycle/consolidated/timelines_complete.json'),
        ('cookies', 'ALL/cookies/lifecycle/consolidated/timelines_complete.json'),
        ('indexeddb', 'ALL/indexeddb/lifecycle/consolidated/timelines_complete.json'),
    ]
    
    users_processed = 0
    total_files = 0
    
    for base_dir in results_dirs:
        if not base_dir.exists(): continue
        for user_dir in base_dir.glob('FR_*'):
            users_processed += 1
            if users_processed % 10 == 0:
                print(f"Processed {users_processed} users...")
            for storage_type, rel_path in storage_configs:
                timeline_path = user_dir / rel_path
                if timeline_path.exists():
                    total_files += 1
                    file_stats = analyze_lifecycle(timeline_path)
                    if file_stats:
                        for category, data in file_stats.items():
                            for k, v in data.items():
                                global_stats[storage_type][category][k] += v
    
    print(f"Processed {users_processed} users and {total_files} timeline files.")
    
    # Generate Markdown Report
    report = "# Lifecycle Statistics Report\n\n"
    
    for storage, categories in global_stats.items():
        report += f"## Storage Type: {storage}\n\n"
        report += "| Category | Keys | Modif % | Delet % | Respawn % | Intact % |\n"
        report += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for category, s in categories.items():
            keys = s['total_keys']
            if keys == 0: continue
            
            # Percentages relative to number of keys or deletions
            # modification % (keys that were modified at least once? Or total modifs vs keys?)
            # Let's do % of keys that experienced at least one event of that type if we had that, 
            # but here we have total counts. Let's do (total events / keys) * 100 or something else.
            # User asked for "pourcentage de modification de suppression". 
            # Usually it means (num_events / total_keys) * 100 or (num_keys_affected / total_keys).
            # Since we have total counts, let's use those.
            
            m_pct = (s['modified'] / keys * 100) if keys > 0 else 0
            d_pct = (s['deleted'] / keys * 100) if keys > 0 else 0
            r_pct = (s['respawns'] / s['deleted'] * 100) if s['deleted'] > 0 else 0
            i_pct = (s['intact_respawns'] / s['respawns'] * 100) if s['respawns'] > 0 else 0
            
            report += f"| {category} | {keys} | {m_pct:.1f}% | {d_pct:.1f}% | {r_pct:.1f}% | {i_pct:.1f}% |\n"
        report += "\n"
        
    with open('results/lifecycle_stats_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Report generated: results/lifecycle_stats_report.md")

if __name__ == "__main__":
    main()
