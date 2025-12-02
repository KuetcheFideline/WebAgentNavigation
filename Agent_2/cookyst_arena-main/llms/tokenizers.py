from typing import Any

import tiktoken
from transformers import LlamaTokenizer,AutoTokenizer # type: ignore


class Tokenizer(object):
    def __init__(self, provider: str, model_name: str) -> None:
        if provider == "openai":
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        elif provider =="gemini":
            self.tokenizer = tiktoken.encoding_for_model(model_name)

        elif provider == "huggingface":
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Fara-7B", trust_remote_code=True)
            self.tokenizer.add_special_tokens = False  # type: ignore[attr-defined]
            self.tokenizer.add_bos_token = False  # type: ignore[attr-defined]
            self.tokenizer.add_eos_token = False  # type: ignore[attr-defined]
            print('je ne passe pas ')
        elif provider == "ours":
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        elif provider == "groq":
            self.tokenizer = ""
        elif provider == "webrl":
            self.tokenizer = ""
        else:
            raise NotImplementedError

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text)

    def decode(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids)

    def __call__(self, text: str) -> list[int]:
        return self.tokenizer.encode(text)
