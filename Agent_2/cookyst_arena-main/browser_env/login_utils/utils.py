import re
from playwright.async_api import Page, Locator, expect

def locate_robustly_without_labels(page:Page, llm_data: dict) -> Locator | None:
    """
            Choisit la meilleure stratégie de localisation à partir des attributs natifs de la page.
    """
    if not llm_data or llm_data.get('action') != 'click':
        print("ℹ️ No 'click' action suggested.")
        return None

    tag = llm_data.get('tag')
    text = llm_data.get('text')
    attributes = llm_data.get('attributes', {})

    print("--- Attempting to locate element  ---")
    print(f"Data: {llm_data}")

    # --- Stratégie 1 : L'attribut 'id' (s'il existe) ---
  
    if tag and attributes.get('id'):
        selector = f"#{attributes['id']}"
        print(f"✅ Strategy 1: Using unique ID. Selector: {selector}")
        # On vérifie quand même que la balise correspond pour plus de sécurité
        locator = page.locator(selector)
        if locator.first.evaluate(f"node => node.tagName.toLowerCase() === '{tag}'"):
             return locator.first

    # --- Stratégie 2 : Combinaison d'attributs sémantiques ---
    # On cherche des attributs qui décrivent la fonction de l'élément.
    if tag and attributes:
        # On priorise les attributs les plus discriminants
        priority_attrs = ['aria-label', 'title', 'href', 'role', 'name']
        attr_selector_parts = []
        for attr in priority_attrs:
            if attr in attributes:
                value = attributes[attr].replace("'", "\\'").replace('"', '\\"')
                attr_selector_parts.append(f"[{attr}='{value}']")
        
        if attr_selector_parts:
            selector = f"{tag}{''.join(attr_selector_parts)}"
            print(f"✅ Strategy 2: Using semantic attributes. Selector: {selector}")
            return page.locator(selector).first

    # --- Stratégie 3 : Le Rôle et le Texte Exact (très puissant) ---
    if tag and text and len(text.strip()) > 1:
        # On mappe les balises communes à des rôles Playwright
        role_map = {'a': 'link', 'button': 'button', 'input': 'textbox', 'nav': 'navigation', 'div': 'generic'}
        role = role_map.get(tag, None)

        if role:
            print(f"✅ Strategy 3: Using role '{role}' and exact text '{text}'")
            # Utilise une expression régulière pour être insensible à la casse et exact
            try:
                # La meilleure méthode : combine rôle et nom
                return page.get_by_role(role, name=re.compile(f"^{re.escape(text)}$", re.IGNORECASE)).first
            except Exception:
                pass

    # --- Stratégie 4 : Le Texte Seul (fallback général) ---
    if text and len(text.strip()) > 1:
        print(f"✅ Strategy 4: Using get_by_text (exact). Text: '{text}'")
        return page.get_by_text(text, exact=True).first
            
    print(" All location strategies failed. Could not find a reliable way to locate the element.")
    return None