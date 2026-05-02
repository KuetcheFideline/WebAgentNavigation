import re
import csv
import json

def analyze_patterns(csv_path, regex_file):
    # Load regexUpdate.py content
    with open(regex_file, 'r') as f:
        content = f.read()
        print(f"Read {len(content)} bytes from {regex_file}")
        try:
            content_fixed = re.sub(r',\s*}', '}', content)
            patterns_dict = eval(content_fixed)
        except Exception as e:
            print(f"Error parsing regex file: {e}")
            return
    
    print(f"Found {len(patterns_dict)} main categories")


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
            # Format in cookie_name_patterns.csv seems to be: count, percentage, cumulative, pattern
            count, pattern_str = row[0], row[3]
            matched = False
            # Check if the existing regexes match this pattern string
            # This is slightly tricky because row[3] IS a pattern. 
            # We want to see if our existing patterns are broad enough to cover examples that would match row[3]
            # or if row[3] is already literally covered.
            for cat, subcat, prog in all_regexes:
                # We check if our regex would match the pattern string itself, 
                # which is a good proxy for "is it covered?".
                if prog.search(pattern_str):
                    matched = True
                    break
            
            if matched:
                results.append((count, pattern_str, cat, subcat))
            else:
                unmatched.append((count, pattern_str))

    print(f"Total matched patterns: {len(results)}")
    print(f"Total unmatched patterns: {len(unmatched)}")
    
    print("\nTop 50 unmatched patterns:")
    for count, patt in unmatched[:50]:
        print(f"{count},{patt}")

if __name__ == "__main__":
    analyze_patterns(
        '/home/fideline/Téléchargements/PII_Statistical_Modeling/scripts/regex/cookie_name_patterns.csv',
        '/home/fideline/Téléchargements/PII_Statistical_Modeling/scripts/regex/regexUpdate.py'
    )
