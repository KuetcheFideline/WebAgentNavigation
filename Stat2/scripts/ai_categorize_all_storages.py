# # #!/usr/bin/env python3
# # """
# # Catégorisation IA pour tous les storages UNCATEGORIZED.

# # Itère sur tous les fichiers UNCATEGORIZED.json dans data/user/ et les catégorise
# # via LLM (Groq) en batches de 30 items.
# # """

# # import json
# # import os
# # import sys
# # import time
# # from pathlib import Path
# # from typing import Dict, List, Optional, Tuple
# # from collections import Counter

# # # Pour Groq API
# # try:
# #     from groq import Groq
# # except ImportError:
# #     print("Installation de groq...")
# #     os.system("pip install groq")
# #     from groq import Groq

# # # Importer regex pour catégories
# # sys.path.insert(0, str(Path(__file__).parent))
# # from regex import TRACKING_PATTERNS_COMPLETE

# # # Charger les profils utilisateurs
# # USER_PROFILES_FILE = Path(__file__).parent / 'user_profiles.json'
# # with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
# #     USER_PROFILES = {profile['id']: profile for profile in json.load(f)}


# # def discover_uncategorized_files(base_path: Path) -> List[Tuple[str, str, str, str, str, Path]]:
# #     """
# #     Découvre tous les fichiers UNCATEGORIZED.json dans la structure data/user/.
    
# #     Returns:
# #         List of tuples: (auth_mode, user_id, policy, storage_type, lifecycle, file_path)
# #     """
# #     uncategorized_files = []
    
# #     for auth_mode in ['Auth', 'UnAuth']:
# #         auth_path = base_path / auth_mode
# #         if not auth_path.exists():
# #             continue
            
# #         for user_dir in auth_path.iterdir():
# #             if not user_dir.is_dir():
# #                 continue
# #             user_id = user_dir.name
            
# #             for policy_dir in user_dir.iterdir():
# #                 if not policy_dir.is_dir():
# #                     continue
# #                 policy = policy_dir.name
                
# #                 for storage_dir in policy_dir.iterdir():
# #                     if not storage_dir.is_dir():
# #                         continue
# #                     storage_type = storage_dir.name
                    
# #                     # Pour indexeddb, pas de sous-dossier added/modified
# #                     if storage_type == 'indexeddb':
# #                         uncategorized_file = storage_dir / 'UNCATEGORIZED.json'
# #                         if uncategorized_file.exists():
# #                             uncategorized_files.append((
# #                                 auth_mode, user_id, policy, storage_type, 'all', uncategorized_file
# #                             ))
# #                     else:
# #                         # Pour cookies, localstorage, sessionstorage
# #                         for lifecycle in ['added', 'modified', 'removed']:
# #                             lifecycle_dir = storage_dir / lifecycle
# #                             if not lifecycle_dir.exists():
# #                                 continue
                            
# #                             uncategorized_file = lifecycle_dir / 'UNCATEGORIZED.json'
# #                             if uncategorized_file.exists():
# #                                 uncategorized_files.append((
# #                                     auth_mode, user_id, policy, storage_type, lifecycle, uncategorized_file
# #                                 ))
    
# #     return uncategorized_files



# # # Mapping user_id vers index dans DIRECT_PII
# # USER_ID_TO_INDEX = {
# #     'FR_0417': 0,
# #     'FR_0446': 1,
# #     'FR_0458': 2
# # }


# # def get_pii_categories_list() -> List[str]:
# #     """Retourne la liste des catégories PII disponibles"""
# #     categories = list(TRACKING_PATTERNS_COMPLETE.keys())
    
# #     # Ajouter sous-catégories DIRECT_PII
# #     direct_pii_subcats = [
# #         'DIRECT_PII::email',
# #         'DIRECT_PII::phone',
# #         'DIRECT_PII::name',
# #         'DIRECT_PII::address',
# #         'DIRECT_PII::birthdate',
# #         'DIRECT_PII::gender',
# #         'DIRECT_PII::blood_type',
# #         'DIRECT_PII::password'
# #     ]
    
# #     return categories + direct_pii_subcats


# # def format_regex_patterns_for_prompt(user_id: str) -> str:
# #     """Formate les patterns regex de manière lisible pour le LLM"""
# #     formatted = "PATTERNS DE DÉTECTION COMPLETS (regex.py):\n\n"
    
# #     # Créer une copie des patterns avec le bon DIRECT_PII pour cet utilisateur
# #     patterns_with_user_pii = dict(TRACKING_PATTERNS_COMPLETE)
    
# #     # Sélectionner le bon DIRECT_PII selon l'index de l'utilisateur
# #     user_index = USER_ID_TO_INDEX.get(user_id, 0)  # Défaut: index 0
# #     if isinstance(TRACKING_PATTERNS_COMPLETE['DIRECT_PII'], list):
# #         patterns_with_user_pii['DIRECT_PII'] = TRACKING_PATTERNS_COMPLETE['DIRECT_PII'][user_index]
# #     else:
# #         # Fallback si DIRECT_PII n'est pas encore une liste
# #         patterns_with_user_pii['DIRECT_PII'] = TRACKING_PATTERNS_COMPLETE['DIRECT_PII']
    
# #     for category, patterns in patterns_with_user_pii.items():
# #         formatted += f"## {category}\n"
# #         if isinstance(patterns, dict):
# #             for pattern_name, pattern_value in patterns.items():
# #                 # Limiter la longueur pour éviter un prompt trop long
# #                 if len(str(pattern_value)) > 100:
# #                     pattern_display = str(pattern_value)[:100] + "..."
# #                 else:
# #                     pattern_display = pattern_value
# #                 formatted += f"  - {pattern_name}: {pattern_display}\n"
# #         formatted += "\n"
    
# #     return formatted


# # def build_batch_prompt(
# #     items_batch: List[Dict], 
# #     storage_type: str,
# #     categories: List[str],
# #     regex_patterns: str
# # ) -> str:
# #     """
# #     Construit le prompt pour analyser un batch d'items.
# #     """
# #     # Préparer les items pour le prompt
# #     items_text = ""
# #     for i, item in enumerate(items_batch, 1):
# #         if storage_type == 'cookies':
# #             key = item.get('name', item.get('cookie_key', ''))
# #             value = item.get('value', '')
# #             domain = item.get('domain', '')
# #             items_text += f"""
# # ITEM {i}:
# # Type: Cookie
# # Nom: {key}
# # Domaine: {domain}
# # Valeur: {value[:200] if len(value) > 200 else value}
# # HttpOnly: {item.get('httpOnly', False)}
# # Secure: {item.get('secure', False)}
# # SameSite: {item.get('sameSite', 'None')}
# # ---
# # """
# #         else:  # localStorage, sessionStorage, indexedDB
# #             key = item.get('key', '')
# #             value = item.get('value', '')
# #             items_text += f"""
# # ITEM {i}:
# # Type: {storage_type}
# # Clé: {key}
# # Valeur: {value[:500] if len(value) > 500 else value}
# # ---
# # """
    
# #     prompt = f"""Vous êtes un expert en conformité RGPD spécialisé dans la détection de données personnelles dans le stockage web.

# # TYPE DE STORAGE ANALYSÉ: {storage_type.upper()}

# # {regex_patterns}

# # CATÉGORIES PII DISPONIBLES:
# # {', '.join(categories)}

# # ITEMS À ANALYSER ({len(items_batch)} items):
# # {items_text}

# # TÂCHE:
# # Analysez CHAQUE item et identifiez TOUTES les données personnelles présentes selon le RGPD.

# # INSTRUCTIONS:
# # 1. Utilisez les PATTERNS ci-dessus pour identifier trackeurs et technologies
# # 2. Identifiez les vendors/trackeurs (Google, Meta, Criteo, Taboola, etc.)
# # 3. N'HÉSITEZ PAS à identifier d'autres trackeurs/vendors basés sur vos connaissances
# # 4. Expliquez comment les trackeurs collectent/partagent les données
# # 5. Évaluez les risques RGPD
# # 6. Un item peut avoir plusieurs catégories

# # RÉPONDEZ UNIQUEMENT EN JSON avec cette structure EXACTE (un objet par item):
# # {{
# #   "items": [
# #     {{
# #       "item_number": 1,
# #       "categories": ["liste des catégories"],
# #       "primary_category": "catégorie principale",
# #       "confidence": 0.0-1.0,
# #       "explanation": "explication concise",
# #       "pii_detected": [
# #         {{
# #           "type": "type de PII",
# #           "value": "valeur exacte ou 'présent'",
# #           "location": "où dans l'item",
# #           "certainty": "low|medium|high",
# #           "tracker": "trackeur si applicable"
# #         }}
# #       ],
# #       "trackers_identified": ["liste trackeurs"],
# #       "technologies_detected": ["fingerprinting, behavioral tracking, etc."],
# #       "gdpr_violations": [
# #         {{
# #           "article": "Article RGPD",
# #           "severity": "low|medium|high|critical",
# #           "description": "description courte"
# #         }}
# #       ],
# #       "vulnerabilities": ["liste vulnérabilités"],
# #       "risk_score": 0-10,
# #       "recommendations": ["liste recommandations"]
# #     }},
# #     ... (répéter pour chaque item)
# #   ]
# # }}

# # IMPORTANT:
# # - Analysez TOUS les {len(items_batch)} items
# # - Pour pii_detected: TOUJOURS inclure type, value, location, certainty
# # - Utilisez les PATTERNS fournis ET vos propres connaissances
# # - Identifiez TOUS les trackeurs, même ceux non listés
# # - Soyez concis mais précis
# # - Répondez UNIQUEMENT en JSON valide
# # """
    
# #     return prompt


# # def analyze_batch_with_ai(
# #     items_batch: List[Dict],
# #     storage_type: str,
# #     categories: List[str],
# #     regex_patterns: str,
# #     client: Groq,
# #     model: str = "llama-3.3-70b-versatile"
# # ) -> Optional[List[Dict]]:
# #     """
# #     Analyse un batch d'items avec l'IA Groq.
# #     """
# #     try:
# #         prompt = build_batch_prompt(items_batch, storage_type, categories, regex_patterns)
        
# #         # Appel API Groq
# #         chat_completion = client.chat.completions.create(
# #             messages=[
# #                 {
# #                     "role": "system",
# #                     "content": "Vous êtes un expert RGPD. Répondez UNIQUEMENT en JSON valide avec un tableau 'items'."
# #                 },
# #                 {
# #                     "role": "user",
# #                     "content": prompt
# #                 }
# #             ],
# #             model=model,
# #             temperature=0.1,
# #             max_tokens=4000,
# #             response_format={"type": "json_object"}
# #         )
        
# #         # Parser réponse
# #         response_text = chat_completion.choices[0].message.content
# #         response_json = json.loads(response_text)
        
# #         # Extraire analyses
# #         if 'items' in response_json:
# #             return response_json['items']
# #         else:
# #             print(f"  Erreur: format JSON invalide (pas de clé 'items')")
# #             return None
        
# #     except json.JSONDecodeError as e:
# #         print(f"  Erreur parsing JSON: {e}")
# #         return None
# #     except Exception as e:
# #         print(f"  Erreur API: {e}")
# #         return None


# # def load_existing_category_file(category_file: Path) -> List[Dict]:
# #     """Charge un fichier de catégorie existant s'il existe"""
# #     if category_file.exists():
# #         with open(category_file, 'r', encoding='utf-8') as f:
# #             return json.load(f)
# #     return []


# # def save_categorized_items(
# #     items_with_analysis: List[Tuple[Dict, Dict]],
# #     output_dir: Path,
# #     storage_type: str
# # ):
# #     """
# #     Sauvegarde les items catégorisés dans les fichiers appropriés.
# #     Respecte le format existant des fichiers de catégories (regex-based).
    
# #     Args:
# #         items_with_analysis: List of (original_item, ai_analysis) tuples
# #         output_dir: Directory where category files are stored
# #         storage_type: Type of storage (cookies, localstorage, sessionstorage, indexeddb)
# #     """
# #     # Grouper par catégorie primaire
# #     categorized_data = {}
    
# #     for original_item, analysis in items_with_analysis:
# #         primary_cat = analysis.get('primary_category', 'FAILED_ANALYSIS')
        
# #         # Créer l'item enrichi en respectant le format existant + flag ai_categorized
# #         enriched_item = {**original_item}
        
# #         # Ajouter le flag ai_categorized pour tous les types
# #         enriched_item['ai_categorized'] = True
        
# #         if storage_type == 'cookies':
# #             # Format cookies: ajouter matched_subcategory, match_type, was_decoded, matched_pattern
# #             enriched_item['matched_subcategory'] = 'ai_categorized'
# #             enriched_item['match_type'] = 'ai_analysis'
# #             enriched_item['was_decoded'] = False
# #             enriched_item['matched_pattern'] = f"AI: {analysis.get('explanation', '')[:100]}"
# #         else:
# #             # Format localStorage/sessionStorage/indexedDB: ajouter _categories, _primary_category, etc.
# #             # Ces champs existent déjà dans UNCATEGORIZED, on les met à jour
# #             enriched_item['_categories'] = analysis.get('categories', [primary_cat])
# #             enriched_item['_primary_category'] = primary_cat
# #             # Garder _is_json, _json_depth, _size_bytes s'ils existent déjà
        
# #         if primary_cat not in categorized_data:
# #             categorized_data[primary_cat] = []
# #         categorized_data[primary_cat].append(enriched_item)
    
# #     # Sauvegarder dans les fichiers de catégories
# #     output_dir.mkdir(parents=True, exist_ok=True)
    
# #     for category, new_items in categorized_data.items():
# #         category_file = output_dir / f'{category}.json'
        
# #         # Charger items existants
# #         existing_items = load_existing_category_file(category_file)
        
# #         # Fusionner (append)
# #         all_items = existing_items + new_items
        
# #         # Sauvegarder
# #         with open(category_file, 'w', encoding='utf-8') as f:
# #             json.dump(all_items, f, indent=2, ensure_ascii=False)
        
# #         print(f"    → {category}: +{len(new_items)} items (total: {len(all_items)})")


# # def process_uncategorized_file(
# #     file_info: Tuple[str, str, str, str, str, Path],
# #     client: Groq,
# #     categories: List[str],
# #     batch_size: int = 30,
# #     limit_per_file: Optional[int] = None,
# #     dry_run: bool = False
# # ) -> Dict:
# #     """
# #     Traite un fichier UNCATEGORIZED.json.
    
# #     Returns:
# #         Statistics dict
# #     """
# #     auth_mode, user_id, policy, storage_type, lifecycle, file_path = file_info
    
# #     # Générer les regex patterns pour cet utilisateur spécifique
# #     regex_patterns = format_regex_patterns_for_prompt(user_id)
    
# #     print(f"\n{'='*80}")
# #     print(f"Traitement: {auth_mode}/{user_id}/{policy}/{storage_type}/{lifecycle}")
# #     print(f"Fichier: {file_path}")
    
# #     # Charger items
# #     with open(file_path, 'r', encoding='utf-8') as f:
# #         all_items = json.load(f)
    
# #     original_count = len(all_items)
    
# #     # Limiter si demandé
# #     if limit_per_file:
# #         items_to_process = all_items[:limit_per_file]
# #         print(f"Mode limité: {len(items_to_process)}/{original_count} items")
# #     else:
# #         items_to_process = all_items
# #         print(f"Total items: {len(items_to_process)}")
    
# #     if dry_run:
# #         print("Mode DRY-RUN: simulation sans appels API")
# #         return {
# #             'file': str(file_path),
# #             'total': len(items_to_process),
# #             'processed': 0,
# #             'failed': 0,
# #             'dry_run': True
# #         }
    
# #     # Statistiques
# #     stats = {
# #         'file': str(file_path),
# #         'total': len(items_to_process),
# #         'processed': 0,
# #         'failed': 0,
# #         'categories_count': Counter()
# #     }
    
# #     # Output directory (même que le fichier UNCATEGORIZED)
# #     output_dir = file_path.parent
    
# #     # Suivre les items traités avec succès pour les retirer de UNCATEGORIZED
# #     successfully_processed_items = []
    
# #     # Traiter par batches
# #     for batch_start in range(0, len(items_to_process), batch_size):
# #         batch_end = min(batch_start + batch_size, len(items_to_process))
# #         items_batch = items_to_process[batch_start:batch_end]
        
# #         print(f"  Batch [{batch_start+1}-{batch_end}/{len(items_to_process)}]...", end=' ')
        
# #         # Analyser avec IA
# #         analyses = analyze_batch_with_ai(
# #             items_batch, storage_type, categories, regex_patterns, client
# #         )
        
# #         if analyses and len(analyses) == len(items_batch):
# #             # Créer les paires (item, analysis)
# #             items_with_analysis = list(zip(items_batch, analyses))
            
# #             # Sauvegarder
# #             save_categorized_items(items_with_analysis, output_dir, storage_type)
            
# #             # Marquer comme traités avec succès
# #             successfully_processed_items.extend(items_batch)
            
# #             # Stats
# #             stats['processed'] += len(analyses)
# #             for analysis in analyses:
# #                 stats['categories_count'][analysis.get('primary_category', 'UNKNOWN')] += 1
            
# #             print(f"OK ({len(analyses)} items)")
# #         else:
# #             print(f"FAILED (attendu {len(items_batch)}, reçu {len(analyses) if analyses else 0})")
# #             stats['failed'] += len(items_batch)
        
# #         # Rate limiting
# #         if batch_end < len(items_to_process):
# #             time.sleep(2.5)
    
# #     # Mettre à jour UNCATEGORIZED.json en retirant les items traités
# #     if successfully_processed_items:
# #         # Créer un set des items traités pour comparaison rapide
# #         # On utilise une clé unique selon le type de storage
# #         if storage_type == 'cookies':
# #             processed_keys = {item.get('cookie_key', '') for item in successfully_processed_items}
# #             remaining_items = [item for item in all_items if item.get('cookie_key', '') not in processed_keys]
# #         else:
# #             # Pour localStorage/sessionStorage/indexedDB, utiliser la clé
# #             processed_keys = {item.get('key', '') for item in successfully_processed_items}
# #             remaining_items = [item for item in all_items if item.get('key', '') not in processed_keys]
        
# #         # Sauvegarder le fichier UNCATEGORIZED mis à jour
# #         with open(file_path, 'w', encoding='utf-8') as f:
# #             json.dump(remaining_items, f, indent=2, ensure_ascii=False)
        
# #         print(f"  ✓ UNCATEGORIZED mis à jour: {len(remaining_items)} items restants (retiré {len(successfully_processed_items)})")
    
# #     return stats


# # def process_all_uncategorized(
# #     base_path: Path,
# #     api_key: str,
# #     batch_size: int = 30,
# #     limit_per_file: Optional[int] = None,
# #     dry_run: bool = False
# # ):
# #     """
# #     Traite tous les fichiers UNCATEGORIZED.json trouvés.
# #     """
# #     print("="*80)
# #     print("CATÉGORISATION IA - TOUS LES STORAGES")
# #     print("="*80)
    
# #     # Découvrir fichiers
# #     print("\nDécouverte des fichiers UNCATEGORIZED...")
# #     uncategorized_files = discover_uncategorized_files(base_path)
# #     print(f"Trouvé: {len(uncategorized_files)} fichiers UNCATEGORIZED")
    
# #     if not uncategorized_files:
# #         print("Aucun fichier à traiter.")
# #         return
    
# #     # Initialiser client Groq
# #     if not dry_run:
# #         client = Groq(api_key=api_key)
# #     else:
# #         client = None
    
# #     # Préparer contexte
# #     categories = get_pii_categories_list()
    
# #     print(f"Catégories PII: {len(categories)}")
# #     print(f"Batch size: {batch_size}")
# #     if limit_per_file:
# #         print(f"Limite par fichier: {limit_per_file} items")
# #     if dry_run:
# #         print("Mode: DRY-RUN (simulation)")
    
# #     # Statistiques globales
# #     global_stats = {
# #         'files_processed': 0,
# #         'total_items': 0,
# #         'processed_items': 0,
# #         'failed_items': 0,
# #         'categories_distribution': Counter()
# #     }
    
# #     # Traiter chaque fichier
# #     for i, file_info in enumerate(uncategorized_files, 1):
# #         print(f"\n[{i}/{len(uncategorized_files)}]")
        
# #         file_stats = process_uncategorized_file(
# #             file_info, client, categories,
# #             batch_size, limit_per_file, dry_run
# #         )
        
# #         # Agréger stats
# #         global_stats['files_processed'] += 1
# #         global_stats['total_items'] += file_stats['total']
# #         global_stats['processed_items'] += file_stats['processed']
# #         global_stats['failed_items'] += file_stats['failed']
# #         if 'categories_count' in file_stats:
# #             global_stats['categories_distribution'].update(file_stats['categories_count'])
    
# #     # Afficher résumé global
# #     print("\n" + "="*80)
# #     print("RÉSUMÉ GLOBAL")
# #     print("="*80)
# #     print(f"Fichiers traités: {global_stats['files_processed']}")
# #     print(f"Items totaux: {global_stats['total_items']}")
# #     print(f"Items catégorisés: {global_stats['processed_items']}")
# #     print(f"Items échoués: {global_stats['failed_items']}")
    
# #     if global_stats['categories_distribution']:
# #         print(f"\nDistribution des catégories:")
# #         for cat, count in global_stats['categories_distribution'].most_common(10):
# #             pct = count / global_stats['processed_items'] * 100 if global_stats['processed_items'] > 0 else 0
# #             print(f"  {cat}: {count} ({pct:.1f}%)")


# # def main():
# #     """Script principal"""
# #     import argparse
    
# #     parser = argparse.ArgumentParser(
# #         description='Catégorisation IA pour tous les storages UNCATEGORIZED'
# #     )
# #     parser.add_argument('--api-key', help='Groq API key (ou variable GROQ_API_KEY)')
# #     parser.add_argument('--batch-size', type=int, default=30, help='Taille des batches (défaut: 30)')
# #     parser.add_argument('--limit-per-file', type=int, help='Limite d\'items par fichier (pour tests)')
# #     parser.add_argument('--dry-run', action='store_true', help='Simulation sans appels API')
    
# #     args = parser.parse_args()
    
# #     # Récupérer API key
# #     api_key = args.api_key or os.environ.get('GROQ_API_KEY')
    
# #     if not api_key and not args.dry_run:
# #         print("Erreur: API key requise (sauf en mode --dry-run)")
# #         print("Utilisez --api-key ou définissez GROQ_API_KEY")
# #         sys.exit(1)
    
# #     base_path = Path(__file__).parent.parent / 'data' / 'user'
    
# #     if not base_path.exists():
# #         print(f"Erreur: chemin introuvable: {base_path}")
# #         sys.exit(1)
    
# #     process_all_uncategorized(
# #         base_path,
# #         api_key,
# #         batch_size=args.batch_size,
# #         limit_per_file=args.limit_per_file,
# #         dry_run=args.dry_run
# #     )


# # if __name__ == '__main__':
# #     main()

# # Version 2 pour refinement final

# # #!/usr/bin/env python3
# # """
# # INDEXEDDB / COOKIES / STORAGE — IA CATEGORIZATION PIPELINE (FINAL)
# # Logique : Pipeline à deux étapes avec prompt chirurgical et gestion du lifecycle.
# # """

# # import json
# # import os
# # import sys
# # import time
# # from pathlib import Path
# # from typing import Dict, List, Optional, Tuple
# # from collections import Counter
# # from groq import Groq

# # # Importer les configurations existantes
# # sys.path.insert(0, str(Path(__file__).parent))
# # from regex import TRACKING_PATTERNS_COMPLETE
# # from categorize_cookies import try_decode_value, get_patterns_for_user

# # # Configuration des IDs Utilisateurs
# # USER_ID_TO_INDEX = {'FR_0417': 0, 'FR_0446': 1, 'FR_0458': 2}

# # # Charger les profils
# # USER_PROFILES_FILE = Path(__file__).parent / 'user_profiles.json'
# # if USER_PROFILES_FILE.exists():
# #     with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
# #         USER_PROFILES = {p['id']: p for p in json.load(f)}
# # else:
# #     USER_PROFILES = {}

# # # =====================================================================
# # # UTILITAIRES
# # # =====================================================================

# # def get_item_id(item: Dict) -> str:
# #     """Génère un identifiant unique pour le nettoyage."""
# #     return str(item.get('field_path') or item.get('cookie_key') or item.get('key') or item.get('name'))

# # def format_patterns_for_ai(patterns: Dict) -> str:
# #     text = "LISTE DES CATÉGORIES DISPONIBLES :\n"
# #     for cat in patterns.keys():
# #         if cat == 'DIRECT_PII_KEYS': continue
# #         text += f"- {cat}\n"
# #     text += "- INFRASTRUCTURE\n"
# #     return text

# # def discover_files(base_path: Path):
# #     tasks = []
# #     for auth in ['Auth', 'UnAuth']:
# #         for user in USER_ID_TO_INDEX.keys():
# #             user_p = base_path / auth / user
# #             if not user_p.exists(): continue
# #             for pol in ['ALL', 'PARTIAL', 'NONE']:
# #                 pol_p = user_p / pol
# #                 if not pol_p.exists(): continue
# #                 for st in ['cookies', 'localstorage', 'sessionstorage', 'indexeddb']:
# #                     st_p = pol_p / st
# #                     if st == 'indexeddb':
# #                         f = st_p / 'UNCATEGORIZED.json'
# #                         if f.exists(): tasks.append({'path': f, 'user_id': user, 'type': st})
# #                     else:
# #                         for lc in ['added', 'modified', 'removed']:
# #                             f = st_p / lc / 'UNCATEGORIZED.json'
# #                             if f.exists(): tasks.append({'path': f, 'user_id': user, 'type': st})
# #     return tasks

# # # =====================================================================
# # # CONSTRUCTION DU PROMPT CHIRURGICAL
# # # =====================================================================

# # def build_prompt(items_batch: List[Dict], storage_type: str, user_id: str, user_patterns: Dict) -> str:
# #     user_info = USER_PROFILES.get(user_id, {})
# #     regex_ref = format_patterns_for_ai(user_patterns)
    
# #     user_context = f"""
# # VALEURS À DÉTECTER (DIRECT_PII) :
# # - FullName: {user_info.get('full_name')}
# # - Email: {user_info.get('email')}
# # - City: {user_info.get('city')}
# # - IP: {user_info.get('ip_address')}
# # - Gender: {user_info.get('gender')}
# # """

# #     items_text = ""
# #     for i, item in enumerate(items_batch, 1):
# #         val_display = item.get('decoded_value_for_ai', item.get('value', ''))
# #         is_mod = 'value_from' in item
        
# #         items_text += f"\nITEM {i}:\n"
# #         items_text += f"NAME/KEY/PATH: {item.get('key', item.get('name', item.get('field_path', '')))}\n"
# #         if is_mod:
# #             items_text += f"OLD_VALUE: {str(item.get('value_from'))[:100]}\n"
# #             items_text += f"NEW_VALUE: {str(val_display)[:500]}\n"
# #         else:
# #             items_text += f"VALUE: {str(val_display)[:500]}\n"
# #         items_text += f"DOMAIN: {item.get('domain', 'N/A')}\n"

# #     return f"""[SYSTEM: ROLE: GDPR_FORENSIC_EXPERT]
# # {user_context}
# # {regex_ref}

# # TÂCHE : Analysez les {len(items_batch)} items de {storage_type.upper()} ci-dessous.
# # Pour chaque item, déterminez sa catégorie unique.

# # RÈGLES CRITIQUES :
# # 1. DIRECT_PII : Priorité absolue si la 'VALUE' contient une donnée du profil utilisateur.
# # 2. IDENTITY_TRACKING : Si l'item contient un identifiant de suivi (UUID, hash, ID tiers).
# # 3. INFRASTRUCTURE : Si la valeur est technique (URL d'API, version logicielle comme 'Chrome/140', CSS, cache technique).
# # 4. USER_PREFERENCES : Si la clé indique un choix (langue, thème).
# # 5. Soyez factuel : basez-vous sur les données fournies, pas sur des définitions générales.

# # RÉPONDEZ UNIQUEMENT EN JSON AVEC CETTE STRUCTURE :
# # {{
# #   "items": [
# #     {{
# #       "item_number": 1,
# #       "category": "NOM_CATEGORIE",
# #       "explanation": "Pourquoi cette donnée spécifique appartient à cette catégorie."
# #     }}
# #   ]
# # }}

# # DONNÉES :
# # {items_text}
# # """

# # # =====================================================================
# # # SAUVEGARDE ET NETTOYAGE
# # # =====================================================================

# # def save_and_cleanup(items_batch, analyses, file_path, storage_type):
# #     output_dir = file_path.parent
    
# #     for original, analysis in zip(items_batch, analyses):
# #         cat = analysis.get('category', 'UNCATEGORIZED')
# #         enriched = original.copy()
        
# #         if storage_type == 'cookies':
# #             enriched.update({
# #                 'matched_subcategory': 'ai_refined',
# #                 'match_type': 'llm_context',
# #                 'matched_pattern': f"AI: {analysis.get('explanation', '')[:100]}",
# #                 'ai_categorized': True
# #             })
# #         else:
# #             enriched.update({
# #                 '_primary_category': cat,
# #                 '_matched_subcategory': 'ai_refined',
# #                 'ai_categorized': True,
# #                 'ai_explanation': analysis.get('explanation', '')
# #             })

# #         target = output_dir / f"{cat}.json"
# #         data = []
# #         if target.exists():
# #             with open(target, 'r', encoding='utf-8') as f:
# #                 try: data = json.load(f)
# #                 except: data = []
# #         data.append(enriched)
# #         with open(target, 'w', encoding='utf-8') as f:
# #             json.dump(data, f, indent=2, ensure_ascii=False)

# #     # Nettoyage UNCATEGORIZED
# #     with open(file_path, 'r', encoding='utf-8') as f:
# #         all_uncat = json.load(f)
# #     batch_ids = [get_item_id(x) for x in items_batch]
# #     remaining = [x for x in all_uncat if get_item_id(x) not in batch_ids]
# #     with open(file_path, 'w', encoding='utf-8') as f:
# #         json.dump(remaining, f, indent=2, ensure_ascii=False)

# # # =====================================================================
# # # LOGIQUE DE DÉCOUVERTE ET MAIN
# # # =====================================================================

# # def main():
# #     api_key = os.environ.get('GROQ_API_KEY')
# #     if not api_key:
# #         print(" GROQ_API_KEY manquante."); return
    
# #     client = Groq(api_key=api_key)
# #     base_path = Path(__file__).resolve().parent.parent / 'data' / 'user'
    
# #     files = discover_files(base_path)

# #     for f_info in files:
# #         file_path = f_info['path']
# #         if not file_path.exists(): continue
# #         with open(file_path, 'r', encoding='utf-8') as f:
# #             items = json.load(f)
        
# #         if not items: continue
# #         print(f"\n🚀 {f_info['user_id']} | {f_info['type']} | {len(items)} items à traiter")

# #         batch_size = 20 # Taille prudente
# #         for i in range(0, len(items), batch_size):
# #             batch = items[i:i+batch_size]
# #             prompt = build_prompt(batch, f_info['type'], f_info['user_id'], get_patterns_for_user(f_info['user_id']))
            
# #             try:
# #                 completion = client.chat.completions.create(
# #                     messages=[{"role": "user", "content": prompt}],
# #                     model="llama-3.3-70b-versatile",
# #                     temperature=0.0, # Strict
# #                     response_format={"type": "json_object"}
# #                 )
                
# #                 resp = json.loads(completion.choices[0].message.content)
# #                 analyses = resp.get('items', [])
                
# #                 if len(analyses) == len(batch):
# #                     save_and_cleanup(batch, analyses, file_path, f_info['type'])
# #                     print(f"   Batch {i//batch_size + 1} OK")
# #                 else:
# #                     print(f"   Taille incohérente ({len(analyses)}/{len(batch)})")
# #             except Exception as e:
# #                 print(f"    Erreur : {e}")
            
# #             time.sleep(2) # Rate limiting Groq

# # if __name__ == '__main__':
# #     main()


# # version 3 avec ajustements mineurs et corrections

# # #!/usr/bin/env python3
# # """
# # PIPELINE DE CATÉGORISATION IA — VERSION FINALE (Dossiers Harmonisés)
# # Gère : Cookies, Storage (avec lifecycle) et IndexedDB (sans lifecycle).
# # Logique : Déduplication spatiale, Reprise sur erreur, Contextualisation PII.
# # """

# # import json
# # import os
# # import sys
# # import time
# # from pathlib import Path
# # from typing import Dict, List, Optional, Tuple
# # from collections import Counter
# # from groq import Groq

# # # Import des configurations existantes
# # sys.path.insert(0, str(Path(__file__).parent))
# # from regex import TRACKING_PATTERNS_COMPLETE
# # from categorize_cookies import try_decode_value, get_patterns_for_user

# # # Mapping Utilisateurs
# # USER_ID_TO_INDEX = {'FR_0417': 0, 'FR_0446': 1, 'FR_0458': 2}

# # # Chargement du profil utilisateur pour détection PII
# # USER_PROFILES_FILE = Path(__file__).parent / 'user_profiles.json'
# # if USER_PROFILES_FILE.exists():
# #     with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
# #         USER_PROFILES = {p['id']: p for p in json.load(f)}
# # else:
# #     print("Erreur : user_profiles.json introuvable.")
# #     USER_PROFILES = {}

# # # =====================================================================
# # # UTILITAIRES DE STRUCTURE
# # # =====================================================================

# # def get_item_id(item: Dict) -> str:
# #     """Génère un ID unique pour le nettoyage."""
# #     return str(item.get('field_path') or item.get('cookie_key') or item.get('key') or item.get('name'))

# # def discover_uncategorized_tasks(base_path: Path):
# #     """
# #     Scanne l'arborescence : base_path / AuthMode / UserID / Policy / Storage / [Lifecycle]
# #     """
# #     tasks = []
# #     if not base_path.exists(): return []
    
# #     for auth_dir in base_path.iterdir():
# #         if not auth_dir.is_dir(): continue
# #         for user_dir in auth_dir.iterdir():
# #             if not user_dir.is_dir(): continue
# #             user_id = user_dir.name
# #             for policy_dir in user_dir.iterdir():
# #                 if not policy_dir.is_dir(): continue
# #                 for storage_dir in policy_dir.iterdir():
# #                     if not storage_dir.is_dir(): continue
# #                     storage_type = storage_dir.name
                    
# #                     if storage_type == 'indexeddb':
# #                         # IndexedDB : Fichier directement dans le dossier indexeddb/
# #                         f = storage_dir / 'UNCATEGORIZED.json'
# #                         if f.exists():
# #                             tasks.append({'path': f, 'user_id': user_id, 'type': storage_type})
# #                     else:
# #                         # Cookies/Storage : Fichiers dans added/modified/removed
# #                         for lc_dir in storage_dir.iterdir():
# #                             if not lc_dir.is_dir(): continue
# #                             f = lc_dir / 'UNCATEGORIZED.json'
# #                             if f.exists():
# #                                 tasks.append({'path': f, 'user_id': user_id, 'type': storage_type})
# #     return tasks

# # # =====================================================================
# # # CONSTRUCTION DU PROMPT
# # # =====================================================================

# # def build_expert_prompt(items_batch: List[Dict], storage_type: str, user_id: str) -> str:
# #     user_info = USER_PROFILES.get(user_id, {})
# #     all_cats = [c for c in TRACKING_PATTERNS_COMPLETE.keys() if c != 'DIRECT_PII_KEYS'] + ["INFRASTRUCTURE"]
    
# #     user_context = f"""
# # IDENTITÉ DE L'UTILISATEUR (Si trouvé dans la valeur -> DIRECT_PII) :
# # - profile   : {json.dumps(user_info)} 
# # """

# #     items_text = ""
# #     for i, item in enumerate(items_batch, 1):
# #         val = item.get('decoded_value_for_ai', item.get('value', ''))
# #         is_mod = 'value_from' in item
        
# #         items_text += f"\nITEM {i}:\n"
# #         items_text += f"ID/KEY/PATH: {item.get('key', item.get('name', item.get('field_path', '')))}\n"
# #         if is_mod:
# #             items_text += f"STATE: MODIFIED (Old: {str(item.get('value_from'))[:100]}...)\n"
# #             items_text += f"NEW_VALUE: {str(val)[:500]}\n"
# #         else:
# #             items_text += f"VALUE: {str(val)[:600]}\n"
# #         items_text += f"DOMAIN: {item.get('domain', 'N/A')}\n---"

# #     return f"""[SYSTEM: ROLE: GDPR_FORENSIC_EXPERT]
# # {user_context}

# # TÂCHE : Analysez PRÉCISÉMENT les {len(items_batch)} items suivants.

# # CONSIGNES DE RIGUEUR :
# # 1. Ne suivez PAS l'ordre de la liste des catégories. Une catégorie peut être utilisée 10 fois ou jamais.
# # 2. Pour chaque explication, vous DEVEZ citer le nom de la clé (ex: "La clé '_ga' est un identifiant Google...").
# # 3. Si vous ne voyez pas de preuve de tracking ou de PII, utilisez "INFRASTRUCTURE" ou "UNCATEGORIZED".
# # 4. INTERDICTION de réciter la définition de la catégorie. Donnez la raison technique liée à l'ITEM.

# # CATÉGORIES AUTORISÉES : {', '.join(all_cats)}

# # ITEMS À TRAITER :
# # {items_text}

# # RÉPONDEZ UNIQUEMENT EN JSON :
# # {{ "items": [ {{ "item_number": 1, "category": "NOM_CATEGORIE", "explanation": "PREUVE : La clé [NOM] contient [INFO]..." }} ] }}
# # """
# # # =====================================================================
# # # SAUVEGARDE ET GESTION DU FLUX
# # # =====================================================================

# # def save_categorized_items(items_batch, analyses, file_path, storage_type):
# #     """Range les items dans les JSON de catégorie et nettoie UNCATEGORIZED."""
# #     output_dir = file_path.parent
# #     items_to_keep_in_uncat = []
    
# #     for original, analysis in zip(items_batch, analyses):
# #         cat = analysis.get('category', 'UNCATEGORIZED')
# #         enriched = original.copy()
# #         enriched['ai_processed'] = True
# #         enriched['ai_categorized'] = True
# #         enriched['ai_explanation'] = analysis.get('explanation', '')

# #         if cat != 'UNCATEGORIZED':
# #             # Harmonisation des attributs
# #             if storage_type == 'cookies':
# #                 enriched.update({'matched_subcategory': 'ai_refined', 'match_type': 'llm_context'})
# #             else:
# #                 enriched.update({'_primary_category': cat, '_matched_subcategory': 'ai_refined'})
            
# #             # Sauvegarde Physique
# #             target_file = output_dir / f"{cat}.json"
# #             data = []
# #             if target_file.exists():
# #                 with open(target_file, 'r', encoding='utf-8') as f:
# #                     try: data = json.load(f)
# #                     except: data = []
# #             data.append(enriched)
# #             with open(target_file, 'w', encoding='utf-8') as f:
# #                 json.dump(data, f, indent=2, ensure_ascii=False)
# #         else:
# #             items_to_keep_in_uncat.append(enriched)

# #     # Nettoyage et Reprise sur erreur
# #     with open(file_path, 'r', encoding='utf-8') as f:
# #         full_list = json.load(f)
    
# #     batch_ids = [get_item_id(x) for x in items_batch]
# #     new_uncat = [x for x in full_list if get_item_id(x) not in batch_ids]
# #     new_uncat.extend(items_to_keep_in_uncat)
    
# #     with open(file_path, 'w', encoding='utf-8') as f:
# #         json.dump(new_uncat, f, indent=2, ensure_ascii=False)

# # # =====================================================================
# # # MAIN LOOP
# # # =====================================================================

# # def main():
# #     api_key = os.environ.get('GROQ_API_KEY')
# #     if not api_key:
# #         print(" GROQ_API_KEY manquante."); return
    
# #     client = Groq(api_key=api_key)
# #     base_path = Path(__file__).resolve().parent.parent / 'data' / 'user'
# #     tasks = discover_uncategorized_tasks(base_path)

# #     print(f" {len(tasks)} fichiers UNCATEGORIZED détectés.")

# #     for task in tasks:
# #         file_path = task['path']
# #         with open(file_path, 'r', encoding='utf-8') as f:
# #             all_items = json.load(f)
        
# #         # On ne traite que ce qui n'est pas marqué ai_processed
# #         items_to_do = [x for x in all_items if not x.get('ai_processed')]
        
# #         if not items_to_do: continue
            
# #         print(f"\n{task['user_id']} | {task['type']} | {len(items_to_do)} restants")
        
# #         batch_size = 20
# #         for i in range(0, len(items_to_do), batch_size):
# #             batch = items_to_do[i:i+batch_size]
# #             prompt = build_expert_prompt(batch, task['type'], task['user_id'])
            
# #             try:
# #                 chat_completion = client.chat.completions.create(
# #                     messages=[{"role": "user", "content": prompt}],
# #                     model="llama-3.3-70b-versatile",
# #                     temperature=0.0,
# #                     response_format={"type": "json_object"}
# #                 )
                
# #                 resp = json.loads(chat_completion.choices[0].message.content)
# #                 print(resp)
# #                 time.sleep(600)
# #                 analyses = resp.get('items', [])
                
# #                 if len(analyses) == len(batch):
# #                     save_categorized_items(batch, analyses, file_path, task['type'])
# #                     print(f"   Lot {i//batch_size + 1} OK")
# #                 else: print("  Réponse IA malformée")
# #             except Exception as e:
# #                 print(f"   Erreur API : {e}")
            
# #             time.sleep(1.5)

# # if __name__ == '__main__':
# #     main()


# # Version 4 avec corrections de bugs et améliorations mineures

# #!/usr/bin/env python3
# """
# PIPELINE DE CATÉGORISATION IA — VERSION GPT (ALIGNÉE À GROQ)

# Gère : Cookies, Storage (avec lifecycle) et IndexedDB (sans lifecycle).
# Logique : Déduplication spatiale, Reprise sur erreur, Contextualisation PII.
# """

# import json
# import os
# import sys
# import time
# from pathlib import Path
# from typing import Dict, List
# from collections import Counter

# from openai import OpenAI
# from groq import Groq
# # =====================================================================
# # IMPORTS PROJET
# # =============================================================OUI========

# sys.path.insert(0, str(Path(__file__).parent))

# from regex import TRACKING_PATTERNS_COMPLETE
# from categorize_cookies import try_decode_value, get_patterns_for_user

# # =====================================================================
# # MAPPING UTILISATEURS
# # =====================================================================

# USER_ID_TO_INDEX = {
#     "FR_0417": 0,
#     "FR_0446": 1,
#     "FR_0458": 2
# }

# # =====================================================================
# # PROFILS UTILISATEURS (PII CONTEXT)
# # =====================================================================

# USER_PROFILES_FILE = Path(__file__).parent / "user_profiles.json"

# if USER_PROFILES_FILE.exists():
#     with open(USER_PROFILES_FILE, "r", encoding="utf-8") as f:
#         USER_PROFILES = {p["id"]: p for p in json.load(f)}
# else:
#     print(" Erreur : user_profiles.json introuvable.")
#     USER_PROFILES = {}

# # =====================================================================
# # UTILITAIRES
# # =====================================================================

# def get_item_id(item: Dict) -> str:
#     return str(
#         item.get("field_path")
#         or item.get("cookie_key")
#         or item.get("key")
#         or item.get("name")
#     )

# # =====================================================================
# # DÉCOUVERTE DES TÂCHES
# # =====================================================================

# def discover_uncategorized_tasks(base_path: Path):
#     tasks = []
#     if not base_path.exists():
#         return tasks

#     for auth_dir in base_path.iterdir():
#         if not auth_dir.is_dir():
#             continue
#         for user_dir in auth_dir.iterdir():
#             if not user_dir.is_dir():
#                 continue
#             user_id = user_dir.name

#             for policy_dir in user_dir.iterdir():
#                 if not policy_dir.is_dir():
#                     continue
#                 for storage_dir in policy_dir.iterdir():
#                     if not storage_dir.is_dir():
#                         continue

#                     storage_type = storage_dir.name

#                     # IndexedDB has its own dedicated AI categorization strategy
#                     # See: ai_categorize_indexeddb.py
#                     if storage_type == "indexeddb":
#                         continue  # Skip IndexedDB
                    
#                     # For cookies, localstorage, sessionstorage
#                     for lc_dir in storage_dir.iterdir():
#                             if not lc_dir.is_dir():
#                                 continue
#                             f = lc_dir / "UNCATEGORIZED.json"
#                             if f.exists():
#                                 tasks.append({
#                                     "path": f,
#                                     "user_id": user_id,
#                                     "type": storage_type
#                                 })
#     return tasks

# # =====================================================================
# # CONSTRUCTION DU PROMPT 
# # =====================================================================

# def build_expert_prompt(items_batch: List[Dict], storage_type: str, user_id: str) -> str:
#     user_info = USER_PROFILES.get(user_id, {})

#     #  catégories strictement autorisées
#     all_cats = [
#         c for c in TRACKING_PATTERNS_COMPLETE.keys()
#         if c != "DIRECT_PII_KEYS"
#     ] + ["INFRASTRUCTURE"]

#     user_context = f"""
# IDENTITÉ DE L'UTILISATEUR
# (Si une information exacte est retrouvée dans une valeur → DIRECT_PII)

# Profil utilisateur (JSON brut) :
# {json.dumps(user_info, ensure_ascii=False)}
# """

#     items_text = ""

#     for i, item in enumerate(items_batch, 1):
#         value = item.get("decoded_value", item.get("value", ""))
#         is_modified = "value_from" in item

#         items_text += f"""
# ITEM {i}
# ID / KEY / PATH : {item.get("key", item.get("name", item.get("field_path", "")))}
# DOMAIN : {item.get("domain", "N/A")}
# """

#         if is_modified:
#             items_text += f"""STATE : MODIFIED
# OLD_VALUE : {str(item.get("value_from"))[:150]}...
# NEW_VALUE : {str(value)[:600]}
# """
#         else:
#             items_text += f"""VALUE :
# {str(value)[:600]}
# """
#         items_text += "\n---\n"

#     return f"""[SYSTEM: ROLE = GDPR_FORENSIC_EXPERT]
# {user_context}

# TÂCHE :
# Analysez PRÉCISÉMENT les {len(items_batch)} items suivants.

# CONSIGNES DE RIGUEUR (OBLIGATOIRES) :
# 1. Ne suivez PAS l'ordre de la liste des catégories.
# 2. Une catégorie peut être utilisée plusieurs fois ou jamais.
# 3. Chaque explication DOIT citer explicitement le nom de la clé.
# 4. Si aucune preuve technique claire n’existe :
#    → utilisez "UNCATEGORIZED".
# 5. INTERDICTION ABSOLUE :
#    - de réciter une définition générique
#    - de spéculer
#    - d’inventer une finalité

# CATÉGORIES AUTORISÉES (LISTE FERMÉE) :
# {', '.join(all_cats)}

# ITEMS À ANALYSER :
# {items_text}

# FORMAT DE RÉPONSE — JSON STRICT UNIQUEMENT :
# {{
#   "items": [
#     {{
#       "item_number": 1,
#       "category": "NOM_CATEGORIE",
#       "explanation": "PREUVE : La clé '[NOM]' contient '[ÉLÉMENT TECHNIQUE]' indiquant [...]"
#     }}
#   ]
# }}
# """

# # =====================================================================
# # SAUVEGARDE
# # =====================================================================

# def save_categorized_items(items_batch, analyses, file_path, storage_type):
#     output_dir = file_path.parent
#     keep_uncat = []

#     # Créer un mapping des analyses par item_id
#     analysis_map = {get_item_id(a): a for a in analyses}

#     for original in items_batch:
#         item_id = get_item_id(original)
#         analysis = analysis_map.get(item_id, {})
#         cat = analysis.get("category", "UNCATEGORIZED")

#         enriched = original.copy()
#         enriched["ai_processed"] = True
#         enriched["ai_categorized"] = True
#         enriched["ai_explanation"] = analysis.get("explanation", "")

#         if cat != "UNCATEGORIZED":
#             if storage_type == "cookies":
#                 enriched.update({
#                     "matched_subcategory": "ai_refined",
#                     "match_type": "llm_context"
#                 })
#             else:
#                 enriched.update({
#                     "_primary_category": cat,
#                     "_matched_subcategory": "ai_refined"
#                 })

#             target_file = output_dir / f"{cat}.json"
#             data = []

#             if target_file.exists():
#                 try:
#                     with open(target_file, "r", encoding="utf-8") as f:
#                         data = json.load(f)
#                 except:
#                     data = []

#             data.append(enriched)

#             with open(target_file, "w", encoding="utf-8") as f:
#                 json.dump(data, f, indent=2, ensure_ascii=False)
#         else:
#             keep_uncat.append(enriched)

#     # Nettoyage UNCATEGORIZED
#     with open(file_path, "r", encoding="utf-8") as f:
#         full_list = json.load(f)

#     batch_ids = {get_item_id(x) for x in items_batch}
#     new_uncat = [x for x in full_list if get_item_id(x) not in batch_ids]
#     new_uncat.extend(keep_uncat)

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(new_uncat, f, indent=2, ensure_ascii=False)

# # =====================================================================
# # MAIN LOOP
# # =====================================================================

# def main():
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         print(" OPENAI_API_KEY manquante")
#         return

#     client = OpenAI(api_key=api_key)

#     base_path = Path(__file__).resolve().parent.parent / "data" / "user"
#     tasks = discover_uncategorized_tasks(base_path)

#     print(f" {len(tasks)} fichiers UNCATEGORIZED détectés")

#     for task in tasks:
#         file_path = task["path"]

#         with open(file_path, "r", encoding="utf-8") as f:
#             all_items = json.load(f)

#         items_to_do = [x for x in all_items if not x.get("ai_processed")]

#         if not items_to_do:
#             continue

#         print(f"\n {task['user_id']} | {task['type']} | {len(items_to_do)} restants")

#         batch_size = 20
#         for i in range(0, len(items_to_do), batch_size):
#             batch = items_to_do[i:i + batch_size]
#             prompt = build_expert_prompt(batch, task["type"], task["user_id"])

#             success = False
#             for attempt in range(1, 4):  
#                 try:
#                     completion = client.chat.completions.create(
#                         model="gpt-4.1-mini",
#                         temperature=0.0,
#                         response_format={"type": "json_object"},
#                         messages=[{"role": "user", "content": prompt}]
#                     )

#                     resp = json.loads(completion.choices[0].message.content)
#                     analyses = resp.get("items", [])

#                     if len(analyses) == len(batch):
#                         print(analyses)
#                         continue
#                         save_categorized_items(batch, analyses, file_path, task["type"])
#                         print(f"    Lot {i // batch_size + 1} OK (attempt {attempt})")
#                         success = True
#                         break
#                     else:
#                         print(f"Réponse IA malformée (attempt {attempt})")

#                 except Exception as e:
#                     print(f"Erreur API GPT (attempt {attempt}) : {e}")

#                 time.sleep(1.5)

#             if not success:
#                 log_file = file_path.parent / "failed_batches.log"
#                 with open(log_file, "a", encoding="utf-8") as lf:
#                     lf.write(f"{time.asctime()} | {task['user_id']} | {task['type']} | Lot {i // batch_size + 1} échoué\n")
#                 print(f"    Lot {i // batch_size + 1} échoué après 3 tentatives. Restera UNCATEGORIZED.")


# if __name__ == "__main__":
#     main()



#!/usr/bin/env python3
"""
AI CATEGORIZATION FOR COOKIES/STORAGE - PARALLELIZED VERSION

Parallel processing of UNCATEGORIZED items for cookies, localStorage, and sessionStorage.
One process per configuration to avoid conflicts and maximize CPU usage.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
from multiprocessing import Pool, cpu_count
import traceback

# OpenAI API
try:
    from openai import OpenAI
    from openai import RateLimitError, APIError
except ImportError:
    print("Installing openai...")
    os.system("pip install openai")
    from openai import OpenAI
    from openai import RateLimitError, APIError

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

def get_item_id(item: Dict) -> str:
    """Generates a unique identifier for an item."""
    return str(
        item.get("field_path")
        or item.get("cookie_key")
        or item.get("key")
        or item.get("name")
    )

# =====================================================================
# TASK DISCOVERY
# =====================================================================

def discover_uncategorized_tasks(base_path: Path) -> List[Dict]:
    """
    Discovers all UNCATEGORIZED.json files in the data/user structure.
    Skips IndexedDB (has its own specialized pipeline).
    """
    tasks = []
    
    if not base_path.exists():
        return tasks
    
    for auth_dir in base_path.iterdir():
        if not auth_dir.is_dir():
            continue
        auth_mode = auth_dir.name
        
        for user_dir in auth_dir.iterdir():
            if not user_dir.is_dir():
                continue
            user_id = user_dir.name
            
            for policy_dir in user_dir.iterdir():
                if not policy_dir.is_dir():
                    continue
                policy = policy_dir.name
                
                for storage_dir in policy_dir.iterdir():
                    if not storage_dir.is_dir():
                        continue
                    storage_type = storage_dir.name
                    
                    # Skip IndexedDB (has its own specialized pipeline)
                    if storage_type == "indexeddb":
                        continue
                    
                    # For cookies, localstorage, sessionstorage
                    for lifecycle_dir in storage_dir.iterdir():
                        if not lifecycle_dir.is_dir():
                            continue
                        lifecycle = lifecycle_dir.name
                        
                        uncategorized_file = lifecycle_dir / "UNCATEGORIZED.json"
                        if uncategorized_file.exists():
                            tasks.append({
                                "auth": auth_mode,
                                "user": user_id,
                                "policy": policy,
                                "storage": storage_type,
                                "lifecycle": lifecycle,
                                "path": uncategorized_file
                            })
    
    return tasks

# =====================================================================
# PROMPT CONSTRUCTION
# =====================================================================

def build_batch_prompt(
    items_batch: List[Dict],
    storage_type: str,
    user_id: str,
    available_categories: List[str]
) -> str:
    """
    Builds a prompt for analyzing a batch of items.
    Aligned with IndexedDB prompt style but adapted for cookies/storage.
    """
    user_info = USER_PROFILES.get(user_id, {})
    
    # User context
    user_context = f"""
USER PROFILE (for DIRECT_PII detection):
{json.dumps(user_info, ensure_ascii=False, indent=2)}
"""
    
    # Items to categorize
    items_text = f"""
ITEMS TO CATEGORIZE ({len(items_batch)} items from {storage_type.upper()}):
"""
    
    for i, item in enumerate(items_batch, 1):
        key = item.get("key", item.get("name", item.get("cookie_key", "")))
        value = item.get("value", "")
        domain = item.get("domain", "N/A")
        
        # Check if it's a modified item
        is_modified = "value_from" in item
        
        items_text += f"""
ITEM {i}:
  Type: {storage_type}
  Key/Name: {key}
  Domain: {domain}
"""
        
        if is_modified:
            items_text += f"""  State: MODIFIED
  Old Value: {str(item.get("value_from"))[:150]}
  New Value: {str(value)[:500]}
"""
        else:
            items_text += f"""  Value: {str(value)[:500]}
"""
        
        # Additional cookie attributes
        if storage_type == "cookies":
            items_text += f"""  HttpOnly: {item.get("httpOnly", False)}
  Secure: {item.get("secure", False)}
  SameSite: {item.get("sameSite", "None")}
"""
        
        items_text += "---\n"
    
    prompt = f"""[SYSTEM: ROLE = GDPR_STORAGE_EXPERT]

{user_context}

{format_categories_with_details()}

{items_text}

TASK:
Analyze the {len(items_batch)} items above from {storage_type.upper()}.
For each item, determine the appropriate category.

STRICT RULES:
- You MUST select exactly ONE category from the provided list.
- You MUST NOT infer intent, user behavior, or legal meaning beyond explicit evidence.
- You MUST NOT use external knowledge or assumptions.
- If there is insufficient evidence, choose UNCATEGORIZED.
- You MUST provide a short, factual explanation based only on:
  - key/cookie name
  - value format
  - domain context
  - immediate technical context

CATEGORIZATION GUIDELINES:
1. If the VALUE contains user profile data → DIRECT_PII
2. If it's a tracking identifier (UUID, hash, ID) → IDENTITY_TRACKING
3. If it's behavioral data (clicks, views, session tracking) → BEHAVIORAL_DATA
4. If it's a configuration/preference → USER_PREFERENCES
5. If it's a technical counter (version, sequence) → INFRASTRUCTURE
6. If no clear evidence → keep UNCATEGORIZED

RESPOND IN JSON ONLY:
{{
  "items": [
    {{
      "item_number": 1,
      "key": "exact key/name from item",
      "category": "CATEGORY_NAME or UNCATEGORIZED",
      "confidence": 0.0-1.0,
      "explanation": "Technical evidence based on key/value/domain"
    }}
  ]
}}
"""
    
    return prompt

# =====================================================================
# AI ANALYSIS WITH RETRY
# =====================================================================

def analyze_batch_with_ai(
    items_batch: List[Dict],
    storage_type: str,
    user_id: str,
    available_categories: List[str],
    client: OpenAI,
    max_retries: int = 5
) -> Optional[Dict]:
    """
    Analyzes a batch of items with AI using retry logic.
    """
    prompt = build_batch_prompt(items_batch, storage_type, user_id, available_categories)
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a GDPR expert. Respond ONLY in valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response = json.loads(completion.choices[0].message.content)
            return response
            
        except RateLimitError as e:
            wait_time = 2 ** attempt
            print(f"      Rate limit hit (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
            
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                print(f"     Max retries reached, batch failed")
                return None
                
        except APIError as e:
            wait_time = 2 ** attempt
            print(f"      API Error: {e} (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
            
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                print(f"     Max retries reached, batch failed")
                return None
                
        except Exception as e:
            print(f"     Unrecoverable error: {e}")
            return None
    
    return None

# =====================================================================
# SAVE CATEGORIZED ITEMS
# =====================================================================

def save_categorized_items(
    items_batch: List[Dict],
    analyses: List[Dict],
    file_path: Path,
    storage_type: str
):
    """
    Saves categorized items to appropriate category files.
    """
    output_dir = file_path.parent
    keep_uncat = []
    
    # Create mapping of analyses by item key
    analysis_map = {}
    for analysis in analyses:
        item_num = analysis.get("item_number", 0)
        if 1 <= item_num <= len(items_batch):
            analysis_map[item_num] = analysis
    
    for i, original in enumerate(items_batch, 1):
        analysis = analysis_map.get(i, {})
        cat = analysis.get("category", "UNCATEGORIZED")
        
        enriched = original.copy()
        enriched["ai_processed"] = True
        enriched["ai_categorized"] = True
        enriched["ai_confidence"] = analysis.get("confidence", 0.0)
        enriched["ai_explanation"] = analysis.get("explanation", "")
        
        if cat != "UNCATEGORIZED":
            # Format specific attributes
            if storage_type == "cookies":
                enriched.update({
                    "matched_subcategory": "ai_refined",
                    "match_type": "llm_context"
                })
            else:
                enriched.update({
                    "_primary_category": cat,
                    "_matched_subcategory": "ai_refined"
                })
            
            # Save to category file
            target_file = output_dir / f"{cat}.json"
            data = []
            
            if target_file.exists():
                try:
                    with open(target_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    data = []
            
            data.append(enriched)
            
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            keep_uncat.append(enriched)
    
    # Clean UNCATEGORIZED file
    with open(file_path, "r", encoding="utf-8") as f:
        full_list = json.load(f)
    
    batch_ids = {get_item_id(x) for x in items_batch}
    new_uncat = [x for x in full_list if get_item_id(x) not in batch_ids]
    new_uncat.extend(keep_uncat)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_uncat, f, indent=2, ensure_ascii=False)

# =====================================================================
# WORKER FUNCTION FOR PARALLEL PROCESSING
# =====================================================================

def process_single_configuration(config: Dict) -> Dict:
    """
    Worker function to process a single configuration.
    This runs in a separate process.
    """
    auth = config['auth']
    user = config['user']
    policy = config['policy']
    storage = config['storage']
    lifecycle = config['lifecycle']
    file_path = Path(config['path'])
    api_key = config['api_key']
    
    config_name = f"{auth}/{user}/{policy}/{storage}/{lifecycle}"
    
    try:
        print(f"\n[{config_name}] 🚀 Starting...")
        
        # Initialize OpenAI client in this process
        client = OpenAI(api_key=api_key)
        
        # Load items
        with open(file_path, "r", encoding="utf-8") as f:
            all_items = json.load(f)
        
        # Filter items not yet processed
        items_to_do = [x for x in all_items if not x.get("ai_processed")]
        
        if not items_to_do:
            return {
                'config': config_name,
                'status': 'skipped',
                'reason': 'All items already processed'
            }
        
        print(f"[{config_name}] 📊 {len(items_to_do)} items to process")
        
        # Available categories
        available_categories = get_available_categories()

        # Analyze in batches of 10 items
        batch_size = 10
        all_categorizations = []
        failed_batches = 0
        
        for batch_start in range(0, len(items_to_do), batch_size):
            batch_end = min(batch_start + batch_size, len(items_to_do))
            items_batch = items_to_do[batch_start:batch_end]
            
            print(f"[{config_name}] Batch [{batch_start+1}-{batch_end}/{len(items_to_do)}]...", end=" ")
            
            # Analyze the batch with retry logic
            batch_response = analyze_batch_with_ai(
                items_batch,
                storage,
                user,
                available_categories,
                client,
                max_retries=5
            )
            
            if batch_response and "items" in batch_response:
                analyses = batch_response["items"]
                
                if len(analyses) == len(items_batch):
                    save_categorized_items(items_batch, analyses, file_path, storage)
                    all_categorizations.extend(analyses)
                    print(f"✓ ({len(analyses)} items)")
                else:
                    failed_batches += 1
                    print(f"✗ FAILED (expected {len(items_batch)}, got {len(analyses)})")
            else:
                failed_batches += 1
                print("✗ FAILED")
            
            # Rate limiting between batches
            if batch_end < len(items_to_do):
                wait_time = 2.0 if failed_batches > 0 else 1.0
                time.sleep(wait_time)
        
        # Statistics
        stats = {
            "total_processed": len(all_categorizations),
            "categories_distribution": Counter()
        }
        
        for analysis in all_categorizations:
            category = analysis.get("category", "UNCATEGORIZED")
            stats["categories_distribution"][category] += 1
        
        if failed_batches > 0:
            print(f"[{config_name}] ⚠️  Completed with {failed_batches} failed batches")
        
        print(f"[{config_name}] ✅ Completed - {stats['total_processed']} items categorized")
        
        return {
            'config': config_name,
            'status': 'success' if failed_batches == 0 else 'partial',
            'stats': stats,
            'failed_batches': failed_batches
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[{config_name}] ❌ Error: {e}")
        print(error_trace)
        return {
            'config': config_name,
            'status': 'error',
            'error': str(e),
            'traceback': error_trace
        }

# =====================================================================
# MAIN PARALLEL PROCESSING
# =====================================================================

def main():
    """Main entry point with parallel processing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(" OPENAI_API_KEY missing")
        return

    base_path = Path(__file__).resolve().parent.parent / "data" / "user"
    
    print("=" * 80)
    print("AI CATEGORIZATION - COOKIES/STORAGE (PARALLELIZED)")
    print("=" * 80)
    
    # Discover all tasks
    print("\n🔍 Discovering UNCATEGORIZED files...")
    raw_tasks = discover_uncategorized_tasks(base_path)
    
    if not raw_tasks:
        print("⚠️  No UNCATEGORIZED files to process")
        return
    
    print(f"📋 Found {len(raw_tasks)} UNCATEGORIZED files")
    
    # Prepare configurations for parallel processing
    configurations = []
    for task in raw_tasks:
        configurations.append({
            'auth': task['auth'],
            'user': task['user'],
            'policy': task['policy'],
            'storage': task['storage'],
            'lifecycle': task['lifecycle'],
            'path': str(task['path']),
            'api_key': api_key
        })
    
    # Determine number of workers (limit to avoid overwhelming API)
    num_workers = min(11, cpu_count(), len(configurations))
    print(f"🔧 Using {num_workers} parallel workers (CPU cores: {cpu_count()})")
    print(f"⚠️  Limited to 11 workers to avoid OpenAI rate limits")

    # Process configurations in parallel
    print(f"\n{'='*80}")
    print("STARTING PARALLEL PROCESSING")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    with Pool(processes=num_workers) as pool:
        results = pool.map(process_single_configuration, configurations)
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print(f"\n{'='*80}")
    print("PROCESSING SUMMARY")
    print(f"{'='*80}\n")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    partial_count = sum(1 for r in results if r['status'] == 'partial')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    total_items = 0
    total_failed_batches = 0
    global_categories = Counter()
    
    for result in results:
        if result['status'] in ['success', 'partial']:
            stats = result.get('stats', {})
            failed = result.get('failed_batches', 0)
            total_items += stats.get('total_processed', 0)
            total_failed_batches += failed
            global_categories.update(stats.get('categories_distribution', {}))
            
            status_icon = "✅" if result['status'] == 'success' else "⚠️"
            failed_info = f" ({failed} failed batches)" if failed > 0 else ""
            print(f"{status_icon} {result['config']}: {stats.get('total_processed', 0)} items{failed_info}")
        elif result['status'] == 'skipped':
            print(f"  {result['config']}: {result['reason']}")
        elif result['status'] == 'error':
            print(f"❌ {result['config']}: {result['error']}")
    
    print(f"\n{'='*80}")
    print(f" Full Success: {success_count}")
    print(f"  Partial Success: {partial_count}")
    print(f"  Skipped: {skipped_count}")
    print(f" Errors: {error_count}")
    print(f" Total items categorized: {total_items}")
    if total_failed_batches > 0:
        print(f"  Total failed batches: {total_failed_batches}")
    
    if global_categories:
        print(f"\n Category distribution (top 10):")
        for cat, count in global_categories.most_common(10):
            pct = count / total_items * 100 if total_items > 0 else 0
            print(f"  {cat}: {count} ({pct:.1f}%)")
    
    print(f"\n⏱️  Total time: {elapsed_time:.2f}s")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()