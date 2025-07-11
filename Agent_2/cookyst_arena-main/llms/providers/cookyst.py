
from ..apikey_manager import with_api_key,   APIKeyManager
from typing import Callable

keys = [
    "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",
    "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"
]

api_manager =APIKeyManager(
    api_keys=keys,
    requests_per_window=30,  
    window_in_minutes=1   
)

manages_api_call = with_api_key(api_manager)


@manages_api_call
def call_grop_llama(prompt,model, *, api_key: str):
    client = model(api_key=api_key)
    
    # client = model(api_key = "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")
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