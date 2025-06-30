
def call_grop_llama(prompt,model):
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

def call_webrl_llama(prompt,model):
    llm = model("llms/providers/models/webrl-llama-3.1-70b.Q2_K.gguf")
    output = llm(prompt)
    print(f"Sortie: {output}")
    return output["choices"][0]["text"].strip()