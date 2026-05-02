import re
import csv
import json

def analyze_features(csv_path, regex_file):
    # Load regexUpdate.py content
    with open(regex_file, 'r') as f:
        content = f.read()
        try:
            # content is a python dict literal
            patterns_dict = eval(content)
        except Exception as e:
            print(f"Error parsing regex file: {e}")
            # Try to fix potential trailing commas or other issues
            try:
                # remove possible trailing comma before }
                content_fixed = re.sub(r',\s*}', '}', content)
                patterns_dict = eval(content_fixed)
            except Exception as e2:
                print(f"Second attempt failed: {e2}")
                return


    all_regexes = []
    for cat, subcats in patterns_dict.items():
        if isinstance(subcats, dict):
            for subcat, pattern in subcats.items():
                all_regexes.append((cat, subcat, re.compile(pattern, re.IGNORECASE)))

    results = []
    unmatched = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            count, feature = row[0], row[1]
            matched = False
            for cat, subcat, prog in all_regexes:
                if prog.search(feature):
                    matched = True
                    break
            
            if matched:
                results.append((count, feature, cat, subcat))
            else:
                unmatched.append((count, feature))

    print(f"Total matched: {len(results)}")
    print(f"Total unmatched: {len(unmatched)}")
    
    print("\nTop 50 unmatched features:")
    for count, feature in unmatched[:50]:
        print(f"{count},{feature}")

if __name__ == "__main__":
    analyze_features(
        '/home/fideline/Téléchargements/PII_Statistical_Modeling/scripts/regex/name_features_filtered.csv',
        '/home/fideline/Téléchargements/PII_Statistical_Modeling/scripts/regex/regexUpdate.py'
    )
