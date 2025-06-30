



import google.generativeai as genai

def call_grop_llama(prompt,model):
    #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
    #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
    #gemini AIzaSyAivEeMYTxK5p5QNfqxSjrDTP2q-gyQwV0
    client = model(api_key = "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")
    completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": f"{prompt}"
        }
    ])
    return(completion.choices[0].message.content)


# --- C'est la meilleure pratique pour gérer votre clé API ---
# 1. Ne mettez JAMAIS votre clé API directement dans le code.
# 2. Définissez-la plutôt comme une variable d'environnement.
# Dans votre terminal, avant de lancer le script, exécutez :
# export GOOGLE_API_KEY="AIzaSyAivEeMYTxK5p5QNfqxSjrDTP2q-gyQwV0" 
# (Sur Windows, utilisez "set" au lieu de "export")

def call_google_gemini(prompt: str) -> str:
    
        # La bibliothèque va automatiquement chercher la variable d'environnement GOOGLE_API_KEY
        genai.configure(api_key="AIzaSyDVwl6UqL2oOaEuiF0gxtQcZGWlg7MghZA")

    
        model = genai.GenerativeModel('gemini-2.0-flash')

        response = model.generate_content(prompt)

        return response.text

   
def call_webrl_llama(prompt,model):
    llm = model("llms/providers/models/webrl-llama-3.1-70b.Q2_K.gguf")
    output = llm(prompt)
    print(f"Sortie: {output}")
    return output["choices"][0]["text"].strip()