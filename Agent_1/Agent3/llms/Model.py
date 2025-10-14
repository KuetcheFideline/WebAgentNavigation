from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate
import requests
import re
from pathlib import Path
import json

import requests
import os
import json

class AIAgent1:
    def __init__(self,model='deepseek-coder:latest',temperature=0.0,chunksize = 8192,chunk_overlap = 200):
        try:
            self.chunksize = chunksize
            self.chunk_overlap = chunk_overlap
           # self.model = OllamaLLM(base_url="http://localhost:11434/",model = model,temperature=0)
           
        #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
        #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
            self.model= ChatGroq(temperature=0, groq_api_key="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", model_name="llama-3.3-70b-versatile")




        except Exception as e:
            print("An error occured: ", e)
    

    def Few_shot_Configuration( example,input ):
        pass
         
       
         

    def truncate_prompt(self,prompt):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            #model_name = self.model_name,
            encoding_name="cl100k_base",
            chunk_size = self.chunksize,
             chunk_overlap=200
        )
        chunks = text_splitter.split_text(prompt)
        return chunks

    
    

    # def call_lm3(self, PromptFirst, example):
    #     def escape_curly_braces(text):
    #         if isinstance(text, str):
    #             return text.replace("{", "{{").replace("}", "}}")
    #         return text


    #     processed_examples = [
    #         {
    #             "question": ex["question"],
    #             "answer": escape_curly_braces(ex["answer"])
    #         }
    #         for ex in example
    #     ]


    #     example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")
    #     prompt_template = FewShotPromptTemplate(
    #         examples=processed_examples,
    #         example_prompt=example_prompt,
    #         suffix="Question: {input}",
    #         input_variables=["input"],
    #     )


    #     final_prompt = prompt_template.format(input=PromptFirst)


    #     formatted_prompt = f"<s>[INST] {final_prompt} [/INST]</s>"

    #     payload = {
    #         "prompt": formatted_prompt,
    #         "temperature": 0.2,
    #         "top_p": 0.9,
    #         "max_new_tokens": 300  
    #     }

    #     try:
    #         response = requests.post(
    #             "http://localhost:8001/generate",
    #             json=payload,
    #             headers={"Content-Type": "application/json"}
    #         )
    #         response.raise_for_status()
    #         return response.json().get("generated_text", "[ERROR] No output returned.")
    #     except requests.RequestException as e:
    #         return f"[ERROR] Request failed: {e}"

    def call_lm(self,PromptFirst,example):


        def escape_curly_braces(text):
            if isinstance(text, str):
                return text.replace("{", "{{").replace("}", "}}")
            return text

        processed_examples = [
            {
                "question": ex["question"],
                "answer": escape_curly_braces(ex["answer"])
            }
            for ex in example
        ]
       # print(processed_examples)
        example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")
        Prompt = FewShotPromptTemplate(
             examples =processed_examples,
             example_prompt =example_prompt,
             suffix ="Question: {input}",
             input_variables=["input"],

         )
        #print(Prompt,'la prompt')

        chain = Prompt | self.model
        return chain.invoke({"input": PromptFirst})



    def call_lm3(self, PromptFirst, example):
        def escape_curly_braces(text):
            if isinstance(text, str):
                return text.replace("{", "{{").replace("}", "}}")
            return text


        processed_examples = [
            {
                "question": ex["question"],
                "answer": escape_curly_braces(ex["answer"])
            }
            for ex in example
        ]


        example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")
        prompt_template = FewShotPromptTemplate(
            examples=processed_examples,
            example_prompt=example_prompt,
            suffix="Question: {input}",
            input_variables=["input"],
        )


        final_prompt = prompt_template.format(input=PromptFirst)


        formatted_prompt = f"<s>[INST] {final_prompt} [/INST]</s>"
        payload = {
            "prompt": formatted_prompt,
            "temperature": 0.2,
            "top_p": 0.9,
            "max_new_tokens": 300  
        }

        try:
            response = requests.post(
                "http://localhost:8001/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("generated_text", "[ERROR] No output returned.")
        except requests.RequestException as e:
            return f"[ERROR] Request failed: {e}"




    def Promt_generation(self,file,data):
        filename = f"./prompts/{file}.json"
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                template = json.load(f)
                for key, value in template.items():
                    if isinstance(value, str):
                        value = value.replace("{{", "{").replace("}}", "}")  
                        template[key] = value.format(**data)
               
        
            prompt = (
                
                f"{template['question']}\n\n"
            )
            return prompt
        except FileNotFoundError:
            print("fichier intouvable")
            return None
    
        
        # chunks = self.truncate_prompt(prompt=prompt)
        # ouputs = [ self.model.invoke(chunk) for chunk in chunks]
        # response = "\n \n".join(ouputs)
        # return response
    



    
    
  

