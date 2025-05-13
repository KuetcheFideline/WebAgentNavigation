from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate

import os
import json
class AIAgent1:
    def __init__(self,model='deepseek-coder:latest',temperature=0):
        try:
            self.model = OllamaLLM(base_url="llm",model = model,temperature=0)
        except Exception as e:
            print("An error occured: ", e)
    
    def call_lm(self,prompt):
       
        response = self.model.invoke(prompt)
        return response
    
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
                
                f"{template['instruction']}\n\n"
                f"Data: {template['data']}\n\n"
            )

            return prompt
        except FileNotFoundError:
            print("fichier intouvable")
            return None
    
        




    def __extract_result(self,results):
        pass

