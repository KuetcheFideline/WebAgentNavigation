#!/usr/bin/env python3
"""
AI CATEGORIZATION FOR INDEXEDDB - CONTEXT-AWARE STRATEGY

Uses hierarchical_reconstruction.json files to provide complete record context
to the AI model, improving categorization accuracy for UNCATEGORIZED items.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from groq import Groq
# OpenAI API
try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    from openai import OpenAI

# Import configurations
sys.path.insert(0, str(Path(__file__).parent))
from regex import TRACKING_PATTERNS_COMPLETE

# User configuration
USER_ID_TO_INDEX = {
    "FR_0417": 0,
    "FR_0446": 1,
    "FR_0458": 2
}

# Load user profiles
USER_PROFILES_FILE = Path(__file__).parent / "user_profiles.json"
if USER_PROFILES_FILE.exists():
    with open(USER_PROFILES_FILE, "r", encoding="utf-8") as f:
        USER_PROFILES = {p["id"]: p for p in json.load(f)}
else:
    print("⚠️  Error: user_profiles.json not found.")
    USER_PROFILES = {}

# =====================================================================
# UTILITIES
# =====================================================================

def get_available_categories() -> List[str]:
    """Returns the list of available categories (without INFRASTRUCTURE)."""
    return [
        cat for cat in TRACKING_PATTERNS_COMPLETE.keys()
        if cat not in ["DIRECT_PII_KEYS", "INFRASTRUCTURE", "INTERNAL_IDB_KEYS"]
    ]

def format_categories_with_details() -> str:
    """Formats categories with their subcategories from regex.py."""
    categories_text = "AVAILABLE CATEGORIES (with subcategories):\n\n"
    
    for category, subcats in TRACKING_PATTERNS_COMPLETE.items():
        if category in ["DIRECT_PII_KEYS", "INFRASTRUCTURE", "INTERNAL_IDB_KEYS"]:
            continue
        
        categories_text += f"## {category}\n"
        
        if isinstance(subcats, dict):
            # Limit to 10 subcategories to avoid overloading the prompt
            subcat_list = list(subcats.keys())[:10]
            for subcat in subcat_list:
                categories_text += f"  - {subcat}\n"
            if len(subcats) > 10:
                categories_text += f"  ... and {len(subcats) - 10} more\n"
        
        categories_text += "\n"
    
    return categories_text

# =====================================================================
# DATA LOADING
# =====================================================================

def load_hierarchical_reconstruction(reconstruction_file: Path) -> Dict:
    """Loads the hierarchical_reconstruction.json file."""
    if not reconstruction_file.exists():
        return {}
    
    with open(reconstruction_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_categorized_files(indexeddb_dir: Path) -> Dict[str, List[Dict]]:
    """Loads all IndexedDB category files."""
    categorized = {}
    
    if not indexeddb_dir.exists():
        return categorized
    
    for json_file in indexeddb_dir.glob("*.json"):
        category = json_file.stem
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                if items:
                    categorized[category] = items
        except Exception as e:
            print(f"  ⚠️  Error loading {json_file}: {e}")
    
    return categorized

# =====================================================================
# EXTRACTION OF RECORDS WITH UNCATEGORIZED
# =====================================================================

def extract_records_with_uncategorized(
    reconstruction: Dict,
    categorized_data: Dict[str, List[Dict]]
) -> List[Dict]:
    """
    Extracts records that contain UNCATEGORIZED fields.
    
    Returns:
        List of records with context: {
            'record_id': str,
            'source_file': str,
            'all_fields': {field_path: {category, value, ...}},
            'uncategorized_fields': [field_paths]
        }
    """
    records_with_uncat = []
    
    # Create a mapping field_path -> category from categorized data
    field_categories = {}
    for category, items in categorized_data.items():
        for item in items:
            field_path = item.get("field_path", "")
            if field_path:
                field_categories[field_path] = {
                    "category": category,
                    "subcategory": item.get("matched_subcategory", "unknown"),
                    "value": item.get("value")
                }
    
    # Browse hierarchical reconstruction
    for source_file, file_data in reconstruction.items():
        records = file_data.get("records", {})
        
        for record_key, record_data in records.items():
            record_id = record_data.get("record_id", "")
            fields = record_data.get("fields", {})
            
            # Identify UNCATEGORIZED fields
            uncategorized_fields = []
            all_fields_info = {}
            
            for field_path, field_info in fields.items():
                category = field_info.get("category", "UNKNOWN")
                
                all_fields_info[field_path] = {
                    "category": category,
                    "subcategory": field_info.get("subcategory", "unknown"),
                    "value": field_info.get("value"),
                    "name": field_info.get("name", field_path.split(".")[-1])
                }
                
                if category == "UNCATEGORIZED":
                    uncategorized_fields.append(field_path)
            
            # If the record contains UNCATEGORIZED, add it
            if uncategorized_fields:
                records_with_uncat.append({
                    "record_id": record_id,
                    "source_file": source_file,
                    "all_fields": all_fields_info,
                    "uncategorized_fields": uncategorized_fields
                })
    
    return records_with_uncat

# =====================================================================
# PROMPT CONSTRUCTION WITH COMPLETE CONTEXT
# =====================================================================

def build_context_aware_prompt(
    record: Dict,
    user_id: str,
    available_categories: List[str]
) -> str:
    """
    Builds a prompt that includes the complete record context.
    """
    user_info = USER_PROFILES.get(user_id, {})
    
    # User context
    user_context = f"""
USER PROFILE (for DIRECT_PII detection):
{json.dumps(user_info, ensure_ascii=False, indent=2)}
"""
    
    # Complete record context
    record_context = f"""
COMPLETE RECORD (ID: {record['record_id']}):
Source: {record['source_file']}

ALL RECORD FIELDS (for context):
"""
    
    for field_path, field_info in record['all_fields'].items():
        value_str = str(field_info['value'])[:100] if field_info['value'] else "null"
        record_context += f"""
  • {field_path}
    Current category: {field_info['category']}
    Value: {value_str}
"""
    
    # Fields to categorize
    fields_to_categorize = f"""
FIELDS TO CATEGORIZE (currently UNCATEGORIZED):
"""
    
    for i, field_path in enumerate(record['uncategorized_fields'], 1):
        field_info = record['all_fields'][field_path]
        value_str = str(field_info['value'])[:500] if field_info['value'] else "null"
        
        fields_to_categorize += f"""
FIELD {i}:
  Path: {field_path}
  Name: {field_info['name']}
  Value: {value_str}
---
"""
    
    prompt = f"""[SYSTEM: ROLE = GDPR_INDEXEDDB_EXPERT]

{user_context}

{record_context}

{fields_to_categorize}

{format_categories_with_details()}

TASK:
Analyze the {len(record['uncategorized_fields'])} UNCATEGORIZED fields above.
Use the COMPLETE RECORD CONTEXT to determine the appropriate category.

STRICT RULES:
- You MUST select exactly ONE category from the provided list.
- You MUST NOT infer intent, user behavior, or legal meaning beyond explicit evidence.
- You MUST NOT use external knowledge or assumptions.
- If there is insufficient evidence, choose UNCATEGORIZED.
- You MUST provide a short, factual explanation based only on:
  - field name
  - value format
  - immediate technical context

CATEGORIZATION GUIDELINES:
1. If the VALUE contains user profile data → DIRECT_PII
2. If it's a tracking identifier (UUID, hash, ID) → IDENTITY_TRACKING
3. If it's behavioral data (clicks, views) → BEHAVIORAL_DATA
4. If it's a configuration/preference → USER_PREFERENCES
5. If no clear evidence → keep UNCATEGORIZED
RESPOND IN JSON ONLY:
{{
  "fields": [
    {{
      "field_path": "complete field path",
      "category": "CATEGORY_NAME or UNCATEGORIZED",
      "confidence": 0.0-1.0,
      "explanation": "Technical evidence based on record context"
    }}
  ]
}}
"""
    
    return prompt

# =====================================================================
# AI ANALYSIS
# =====================================================================

def analyze_records_batch_with_ai(
    records_batch: List[Dict],
    user_id: str,
    available_categories: List[str],
    client: OpenAI
) -> Optional[Dict]:
    """
    Analyzes a batch of records with AI using complete context.
    """
    try:
        # Build a combined prompt for all records in the batch
        combined_prompt = f"""[SYSTEM: ROLE = GDPR_INDEXEDDB_EXPERT]

USER PROFILE:
{json.dumps(USER_PROFILES.get(user_id, {}), ensure_ascii=False, indent=2)}

{format_categories_with_details()}

TASK:
Analyze the UNCATEGORIZED fields of {len(records_batch)} records.
For each record, use the COMPLETE CONTEXT to determine the category.

STRICT RULES:
- You MUST select exactly ONE category from the provided list.
- You MUST NOT infer intent, user behavior, or legal meaning beyond explicit evidence.
- You MUST NOT use external knowledge or assumptions.
- If there is insufficient evidence, choose UNCATEGORIZED.
- You MUST provide a short, factual explanation based only on:
  - field name
  - value format
  - immediate technical context

CATEGORIZATION GUIDELINES:
1. If the VALUE contains user profile data → DIRECT_PII
2. If it's a tracking identifier (UUID, hash, ID) → IDENTITY_TRACKING
3. If it's behavioral data (clicks, views) → BEHAVIORAL_DATA
4. If it's a configuration/preference → USER_PREFERENCES
5. If no clear evidence → keep UNCATEGORIZED

RECORDS TO ANALYZE:
"""
        
        for idx, record in enumerate(records_batch, 1):
            combined_prompt += f"\n--- RECORD {idx} (ID: {record['record_id']}) ---\n"
            combined_prompt += f"Source: {record['source_file']}\n\n"
            
            # Record context
            combined_prompt += "Complete record context:\n"
            for field_path, field_info in list(record['all_fields'].items())[:5]:  # Limit to 5 fields for context
                value_str = str(field_info['value'])[:50] if field_info['value'] else "null"
                combined_prompt += f"  • {field_path}: {field_info['category']} = {value_str}\n"
            
            # Fields to categorize
            combined_prompt += "\nUNCATEGORIZED fields to categorize:\n"
            for field_path in record['uncategorized_fields']:
                field_info = record['all_fields'][field_path]
                value_str = str(field_info['value'])[:200] if field_info['value'] else "null"
                combined_prompt += f"  - {field_path}: {value_str}\n"
        
        combined_prompt += """\n\nRESPOND IN JSON ONLY:
{
  "records": [
    {
      "record_id": "record ID",
      "fields": [
        {
          "field_path": "complete path",
          "category": "CATEGORY_NAME or UNCATEGORIZED",
          "confidence": 0.0-1.0,
          "explanation": "Technical evidence"
        }
      ]
    }
  ]
}
"""
        
        completion = client.chat.completions.create(
            model="gpt-4.1",
            # model="llama-3.3-70b-versatile",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a GDPR expert. Respond ONLY in valid JSON."
                },
                {
                    "role": "user",
                    "content": combined_prompt
                }
            ]
        )
        
        response = json.loads(completion.choices[0].message.content)
        return response
        
    except Exception as e:
        print(f"    ⚠️  API Error: {e}")
        return None

# =====================================================================
# SAVE AI CATEGORIZATIONS (INTERMEDIATE)
# =====================================================================

def save_ai_categorizations_intermediate(
    all_categorizations: List[Dict],
    output_dir: Path
):
    """
    Saves AI categorizations to an intermediate file.
    A separate script will handle redistribution.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ai_results_file = output_dir / "ai_categorizations.json"
    
    with open(ai_results_file, "w", encoding="utf-8") as f:
        json.dump(all_categorizations, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 Saved: {len(all_categorizations)} AI categorizations")
    print(f"     → {ai_results_file}")
    
    # Statistics
    stats = {
        "total_records": len(all_categorizations),
        "total_fields": sum(len(r.get("fields", [])) for r in all_categorizations),
        "categories_distribution": Counter()
    }
    
    for record_cat in all_categorizations:
        for field in record_cat.get("fields", []):
            category = field.get("category", "UNCATEGORIZED")
            stats["categories_distribution"][category] += 1
    
    # Save stats
    stats_file = output_dir / "ai_categorization_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    return stats

# =====================================================================
# SAVE RESULTS (OLD VERSION - TO BE REMOVED)
# =====================================================================

def save_ai_categorized_results_OLD(
    records_analyzed: List[Tuple[Dict, List[Dict]]],
    output_dir: Path,
    categorized_data: Dict[str, List[Dict]]
):
    """
    Saves AI categorization results.
    Updates existing category files.
    """
    # Create output directory
    categorized_dir = output_dir / "categorized"
    categorized_dir.mkdir(parents=True, exist_ok=True)
    
    # Group new items by category
    new_items_by_category = defaultdict(list)
    still_uncategorized = []
    
    stats = {
        "total_fields_analyzed": 0,
        "fields_recategorized": 0,
        "fields_still_uncategorized": 0,
        "categories_distribution": Counter()
    }
    
    for record, analyses in records_analyzed:
        for analysis in analyses:
            field_path = analysis.get("field_path", "")
            new_category = analysis.get("category", "UNCATEGORIZED")
            confidence = analysis.get("confidence", 0.0)
            explanation = analysis.get("explanation", "")
            
            stats["total_fields_analyzed"] += 1
            
            # Find original item in UNCATEGORIZED
            original_item = None
            if "UNCATEGORIZED" in categorized_data:
                for item in categorized_data["UNCATEGORIZED"]:
                    if item.get("field_path") == field_path:
                        original_item = item.copy()
                        break
            
            if not original_item:
                continue
            
            # Enrich the item
            enriched_item = original_item.copy()
            enriched_item["ai_categorized"] = True
            enriched_item["ai_confidence"] = confidence
            enriched_item["ai_explanation"] = explanation
            enriched_item["record_id"] = record["record_id"]
            
            if new_category != "UNCATEGORIZED":
                enriched_item["_primary_category"] = new_category
                enriched_item["_matched_subcategory"] = "ai_context_aware"
                new_items_by_category[new_category].append(enriched_item)
                stats["fields_recategorized"] += 1
                stats["categories_distribution"][new_category] += 1
            else:
                still_uncategorized.append(enriched_item)
                stats["fields_still_uncategorized"] += 1
    
    # Save category files
    for category, new_items in new_items_by_category.items():
        category_file = categorized_dir / f"{category}.json"
        
        # Load existing items
        existing_items = []
        if category_file.exists():
            try:
                with open(category_file, "r", encoding="utf-8") as f:
                    existing_items = json.load(f)
            except:
                existing_items = []
        
        # Merge
        all_items = existing_items + new_items
        
        # Save
        with open(category_file, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=2, ensure_ascii=False)
        
        print(f"    → {category}: +{len(new_items)} items")
    
    # Save reduced UNCATEGORIZED
    if still_uncategorized:
        uncat_file = categorized_dir / "UNCATEGORIZED.json"
        with open(uncat_file, "w", encoding="utf-8") as f:
            json.dump(still_uncategorized, f, indent=2, ensure_ascii=False)
        print(f"    → UNCATEGORIZED: {len(still_uncategorized)} remaining items")
    
    # Save AI report
    report_file = output_dir / "ai_categorization_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    return stats

# =====================================================================
# MAIN PROCESSING
# =====================================================================

def process_indexeddb_ai_categorization(
    aggregates_dir: Path,
    user_dir: Path,
    output_base_dir: Path,
    user_id: str,
    client: OpenAI
):
    """
    Processes AI categorization for an IndexedDB configuration.
    """
    # Load hierarchical reconstruction
    reconstruction_file = aggregates_dir / "hierarchical_reconstruction.json"
    reconstruction = load_hierarchical_reconstruction(reconstruction_file)
    
    if not reconstruction:
        print(f"  ⚠️  No reconstruction found")
        return
    
    # Load categorized data
    categorized_data = load_categorized_files(user_dir)
    
    if "UNCATEGORIZED" not in categorized_data:
        print(f"  ✓ No UNCATEGORIZED to process")
        return
    
    # Extract records with UNCATEGORIZED
    records_with_uncat = extract_records_with_uncategorized(
        reconstruction,
        categorized_data
    )
    
    if not records_with_uncat:
        print(f"  ✓ No records with UNCATEGORIZED")
        return
    
    print(f"  📊 {len(records_with_uncat)} records with UNCATEGORIZED")
    
    # Available categories
    available_categories = get_available_categories()
    
    # Analyze in batches of 10 records
    batch_size = 10
    all_categorizations = []
    
    for batch_start in range(0, len(records_with_uncat), batch_size):
        batch_end = min(batch_start + batch_size, len(records_with_uncat))
        records_batch = records_with_uncat[batch_start:batch_end]
        
        print(f"    Batch [{batch_start+1}-{batch_end}/{len(records_with_uncat)}]...", end=" ")
        
        # Analyze the batch
        batch_response = analyze_records_batch_with_ai(
            records_batch,
            user_id,
            available_categories,
            client
        )
        print(batch_response)
        if batch_response and "records" in batch_response:
            batch_results = batch_response["records"]
            all_categorizations.extend(batch_results)
            total_fields = sum(len(r.get("fields", [])) for r in batch_results)
            print(f"✓ ({len(batch_results)} records, {total_fields} fields)")
        else:
            print("✗")
        
        # Rate limiting
        if batch_end < len(records_with_uncat):
            time.sleep(2.0)
    
    # Save AI categorizations
    print(f"  💾 Saving AI categorizations...")
    stats = save_ai_categorizations_intermediate(
        all_categorizations,
        output_base_dir
    )
    
    print(f"  ✓ {stats['total_records']} records processed")
    print(f"  ✓ {stats['total_fields']} fields categorized")
    print(f"  ℹ  Use redistribute_ai_categorizations.py to redistribute")

# =====================================================================
# MAIN
# =====================================================================

def main():
    """Main entry point."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(" OPENAI_API_KEY missing")
        return

    client = OpenAI(api_key=api_key)

    base_dir = Path(__file__).resolve().parent.parent / "data"
    aggregates_base = base_dir / "aggregates" / "indexeddb"
    user_base = base_dir / "user"
    output_base = base_dir / "aggregates_ai_complete" / "indexeddb"
    
    print("=" * 80)
    print("AI CATEGORIZATION - INDEXEDDB (CONTEXT-AWARE)")
    print("=" * 80)
    
    users = ["FR_0417", "FR_0446", "FR_0458"]
    
    for auth in ["Auth", "UnAuth"]:
        for user in users:
            for policy in ["ALL", "PARTIAL", "NONE"]:
                aggregates_dir = aggregates_base / auth / user / policy
                user_dir = user_base / auth / user / policy / "indexeddb"
                output_dir = output_base / auth / user / policy
                
                if not aggregates_dir.exists() or not user_dir.exists():
                    continue
                
                print(f"\n📁 {auth}/{user}/{policy}")
                
                process_indexeddb_ai_categorization(
                    aggregates_dir,
                    user_dir,
                    output_dir,
                    user,
                    client
                )
    
    print("\n" + "=" * 80)
    print("✅ AI CATEGORIZATION COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()