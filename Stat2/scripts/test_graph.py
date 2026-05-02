

import json
import networkx as nx
from pyvis.network import Network

# 1. CHARGEMENT DES DONNÉES
# Remplace 'ton_fichier.json' par le nom réel de ton fichier
with open('/home/franck/Documents/Research/PII_Statistical_Modeling/analysis_gdpr_profiles/reports/cross_site_network_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

network = data['global_domain_network']

# 2. CONFIGURATION DES CATÉGORIES ET COULEURS
CATEGORIES = {
    'SENSITIVE': {
        'domains': ['ameli.fr', 'lcl.fr', 'mgen.fr', 'boursobank.com', 'pharmashopi.com', 'notaires.fr', 'mutavie.fr', 'assurance', 'banque'],
        'color': '#FF4D4D', # Rouge
        'label': 'Données Sensibles'
    },
    'ADTECH': {
        'domains': ['criteo', 'bidswitch', 'pubmatic', 'liveramp', 'adnxs', 'smartadserver', 'doubleclick', 'rubicon', 'adform', '360yield'],
        'color': '#262626', # Noir / Gris foncé
        'label': 'Trackers / AdTech'
    },
    'MEDIA': {
        'domains': ['huffingtonpost.fr', 'nouvelobs.com', 'lefigaro.fr', 'ouest-france.fr', 'latribune.fr', 'planet.fr', 'leparisien.fr'],
        'color': '#FFCC00', # Jaune / Orange
        'label': 'Presse / Hubs'
    },
    'BIG_TECH': {
        'domains': ['youtube.com', 'google', 'facebook', 'linkedin', 'amazon', 'microsoft'],
        'color': '#4D94FF', # Bleu
        'label': 'Gafam / Plateformes'
    }
}

def get_node_style(node):
    """Détermine la couleur et la catégorie d'un domaine."""
    node_lower = node.lower()
    for cat, info in CATEGORIES.items():
        if any(d in node_lower for d in info['domains']):
            return info['color'], cat
    if len(node) > 50:  # Probablement un Consent String en Base64
        return '#E0E0E0', 'CONSENT_STRING'
    return '#99CCFF', 'OTHER'

# 3. CONSTRUCTION DU GRAPHE ET CALCULS
G = nx.DiGraph()
for source, targets in network.items():
    for t in targets:
        G.add_edge(source, t)

# Calcul de l'importance (centralité)
centrality = nx.degree_centrality(G)

# 4. FILTRAGE POUR ÉVITER LE GRAPH TOUFU
# On garde les nœuds si : 
# - Ils sont SENSITIVE (Rouge)
# - OU ils ont beaucoup de connexions (Hubs)
nodes_to_keep = [
    n for n in G.nodes() 
    if centrality[n] > 0.005 or get_node_style(n)[1] == 'SENSITIVE'
]
sub_G = G.subgraph(nodes_to_keep)

# 5. CRÉATION DE LA VISUALISATION INTERACTIVE (PYVIS)
net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)

# Désactiver la physique trop agitée pour plus de stabilité
net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200)

for n in sub_G.nodes():
    color, cat = get_node_style(n)
    
    # Taille basée sur l'importance du domaine
    size = (centrality[n] * 300) + 10
    
    # Nettoyage du label pour les Consent Strings
    display_label = n if cat != 'CONSENT_STRING' else "IAB_CONSENT_DATA"
    
    net.add_node(n, label=display_label, color=color, size=size, title=f"Catégorie: {cat}\nDegré: {G.degree(n)}")

for source, target in sub_G.edges():
    net.add_edge(source, target, color='#E5E7E9')

# 6. GÉNÉRATION DU RAPPORT ET DU FICHIER
print(f"Extraction terminée.")
print(f"Domaines analysés : {len(G.nodes())}")
print(f"Domaines affichés dans l'audit interactif : {len(sub_G.nodes())}")

# Sauvegarde
net.save_graph("audit_interactif.html")
print("\n>>> SUCCESS: Ouvre le fichier 'audit_interactif.html' pour explorer le réseau.")