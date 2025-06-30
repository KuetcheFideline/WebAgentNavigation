# LA SEULE MODIFICATION EST ICI : Renommer la variable en 'prompt'
prompt = {
	"intro": """You are an expert web analyst. Your role is to analyze a website's starting page based on its URL and simplified HTML.
Your goal is to understand the site's purpose and identify the most common tasks a user would perform on it.
You MUST provide the answer in a structured JSON format.""",

	"examples": [
		(
			# --- EXEMPLE 1 ---
			"""[INPUT]
URL: "https://www.google.com"
HTML:
"<html>
  <body>
    <form action='/search'>
      <input id='APjFqb' title='Rechercher' aria-label='Rechercher'>
      <button name='btnK' type='submit'>Recherche Google</button>
    </form>
  </body>
</html>"
""",
			# --- OUTPUT ATTENDU POUR L'EXEMPLE 1 ---
			"""[OUTPUT]
{
  "url_analysed": "https://www.google.com",
  "website_category": "search_engine",
  "site_description": "Un moteur de recherche dont le but principal est de permettre aux utilisateurs de trouver des informations sur le web en entrant des requêtes textuelles.",
  "common_tasks": {
    "unauthenticated": [
      "Lancer une recherche en tapant dans la barre de recherche principale.",
      "Cliquer sur les liens de résultats pour naviguer vers d'autres sites."
    ],
    "authenticated": [
      "Consulter l'historique de ses recherches personnelles.",
      "Gérer les paramètres de son compte Google."
    ]
  }
}"""
		),
		(
			# --- EXEMPLE 2 ---
			"""[INPUT]
URL: "https://www.amazon.fr"
HTML:
"<html>
  <body>
    <header>
      <div id='nav-search-bar-form'>
        <input type='text' id='twotabsearchtextbox' name='field-keywords' placeholder='Rechercher sur Amazon.fr'>
        <input id='nav-search-submit-button' type='submit' value='Go'>
      </div>
      <a id='nav-link-accountList' href='/gp/css/homepage.html'>Bonjour, identifiez-vous Compte et listes</a>
      <a id='nav-cart' href='/gp/cart/view.html'>Panier</a>
    </header>
  </body>
</html>"
""",
			# --- OUTPUT ATTENDU POUR L'EXEMPLE 2 ---
			"""[OUTPUT]
{
  "url_analysed": "https://www.amazon.fr",
  "website_category": "e-commerce",
  "site_description": "Un site de commerce en ligne où les utilisateurs peuvent rechercher, comparer et acheter une grande variété de produits.",
  "common_tasks": {
    "unauthenticated": [
      "Rechercher un produit en utilisant la barre de recherche.",
      "Consulter des pages de produits pour voir les détails et les avis.",
      "Comparer les prix entre différents articles."
    ],
    "authenticated": [
      "Ajouter un article au panier.",
      "Passer une commande et effectuer un paiement.",
      "Suivre l'état d'une commande existante.",
      "Rédiger un avis pour un produit acheté."
    ]
  }
}"""
		),
        (
			# --- EXEMPLE 3 ---
			"""[INPUT]
URL: "https://fr.wikipedia.org/wiki/Accueil"
HTML:
"<html>
  <body>
    <header>
      <a href='/wiki/Special:Connexion'>Se connecter</a>
    </header>
    <div id='content'>
      <h1 id='firstHeading'>Wikipédia, l'encyclopédie libre</h1>
      <form action='/w/index.php' id='searchform'>
        <input id='searchInput' name='search' type='search' placeholder='Rechercher dans Wikipédia'>
      </form>
      <p>Bienvenue sur Wikipédia, un projet d’encyclopédie collective en ligne...</p>
    </div>
  </body>
</html>"
""",
			# --- OUTPUT ATTENDU POUR L'EXEMPLE 3 ---
			"""[OUTPUT]
{
  "url_analysed": "https://fr.wikipedia.org/wiki/Accueil",
  "website_category": "information_encyclopedia",
  "site_description": "Une encyclopédie en ligne collaborative où les utilisateurs peuvent trouver et lire des articles sur une multitude de sujets.",
  "common_tasks": {
    "unauthenticated": [
      "Rechercher un article en utilisant la barre de recherche.",
      "Lire un article et naviguer entre les pages via les hyperliens.",
      "Consulter le sommaire d'un article pour naviguer dans ses sections."
    ],
    "authenticated": [
      "Modifier ou corriger une page existante.",
      "Créer un nouvel article encyclopédique.",
      "Participer aux pages de discussion des articles."
    ]
  }
}"""
		)
	],

	"template": """--- END OF EXAMPLES ---

Now, analyze the following website:

[INPUT]
URL: "{url_to_analyze}"
HTML:
"{html_to_analyze}"

[OUTPUT]
""",

	"meta_data": {
        # Décrit la nature de ce prompt spécifique
		"prompt_name": "WebsiteAnalyzerPrompt",
		"output_type": "json_site_analysis",
		"keywords": ["url_to_analyze", "html_to_analyze"],
		"prompt_constructor": "GenericFewShotConstructor",
        # Le modèle ne doit pas générer de phrases ou de séparateurs, juste le JSON brut
		"answer_phrase": "", 
		"action_splitter": ""
	},
}