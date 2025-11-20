import argparse
from typing import Any
from transformers import AutoTokenizer, AutoModel
from groq import Groq
from llms.providers.hf_utils import (
    generate_from_huggingface_completion,
)
import base64
import os

from openai import OpenAI
from llms.lm_config import LMConfig

import openai
from llms.providers.openai_utils import (
    generate_from_openai_completion,
    generate_from_openai_chat_completion,
    generate_from_openai_modal,
)


from .providers.cookyst import call_grop_llama,call_webrl_llama


APIInput = str | list[Any] | dict[str, Any]

model = None
tokenizer = None





def encode_image(image_path):
       with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")











def call_banner(prompt):

    print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")


    if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "OPENAI_API_KEY environment variable must be set when using OpenAI API."
            )
    openai.api_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI()
    image_path = os.path.join(os.getcwd(), 'output', 'marked1.png')
    print("valere boude ")
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                    },
                    { "type": "input_text", "text": prompt},
                ],
            }
    ],
)

    return response 

def call_orm(prompt):


    if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "OPENAI_API_KEY environment variable must be set when using OpenAI API."
            )
    openai.api_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI()
    image_path1 = os.path.join(os.getcwd(), 'output', 'marked1.png')
    image_path2 = os.path.join(os.getcwd(), 'output', 'marked2.png')
    image_path3 = os.path.join(os.getcwd(), 'output', 'marked3.png')

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image(image_path1)}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image(image_path2)}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image(image_path3)}",
                    },
                    { "type": "input_text", "text": prompt},
                ],
            }
    ],
)



    return response







def call_llm( 
    lm_config:LMConfig,
    prompt: APIInput,
) -> str:
    global model
    global tokenizer
    
    response: str

    
    if lm_config.provider == "openai":
        if lm_config.mode == "chat":
            assert isinstance(prompt, list)
            response = generate_from_openai_chat_completion(
                messages=prompt,
                model=lm_config.model,
                temperature=lm_config.gen_config["temperature"],
                top_p=lm_config.gen_config["top_p"],
                context_length=lm_config.gen_config["context_length"],
                max_tokens=lm_config.gen_config["max_tokens"],
                stop_token=None,
            )
        elif lm_config.mode == "completion":
            assert isinstance(prompt, str)
            response = generate_from_openai_completion(
                prompt=prompt,
                engine=lm_config.model,
                temperature=lm_config.gen_config["temperature"],
                max_tokens=lm_config.gen_config["max_tokens"],
                top_p=lm_config.gen_config["top_p"],
                stop_token=lm_config.gen_config["stop_token"],
            )
        elif lm_config.mode == "modal":
            response = generate_from_openai_modal(
                prompt=prompt,
                model=lm_config.model,
                temperature=lm_config.gen_config["temperature"],
                max_tokens=lm_config.gen_config["max_tokens"],
                top_p=lm_config.gen_config["top_p"],
                stop_token=lm_config.gen_config["stop_token"],
            )
        else:
            raise ValueError(
                f"OpenAI models do not support mode {lm_config.mode}"
            )
    elif lm_config.provider == "huggingface":
        assert isinstance(prompt, str)
        response = generate_from_huggingface_completion(
            prompt=prompt,
            model_endpoint=lm_config.gen_config["model_endpoint"],
            temperature=lm_config.gen_config["temperature"],
            top_p=lm_config.gen_config["top_p"],
            stop_sequences=lm_config.gen_config["stop_sequences"],
            max_new_tokens=lm_config.gen_config["max_new_tokens"],
        )
    elif lm_config.provider == "ours":
        # print(prompt)
        if lm_config.model == 'manual':
            response = input("Command > ")
        else:
            if not model:
                model = AutoModel.from_pretrained(lm_config.model, trust_remote_code=True, device=f'cuda:{lm_config.cuda}')
                tokenizer = AutoTokenizer.from_pretrained(lm_config.model, trust_remote_code=True)
                model.eval()
            response = call_pretrain_model(prompt, model, tokenizer, lm_config.cuda)
    elif lm_config.provider == "groq":
        response = call_grop_llama(prompt=prompt,model=Groq)
    elif lm_config.provider == "webrl":
        response = call_webrl_llama(lm_config=lm_config,prompt=prompt)

    else:
        raise NotImplementedError(
            f"Provider {lm_config.provider} not implemented"
        )

    return response




