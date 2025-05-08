from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


class AIAgent1:
    def __init__(self,model='deepseek-r1:8b',temperature=0.0):
        try:
            self.model = OllamaLLM(base_url="http://localhost:11434/",model = model,temperature=temperature)
        except Exception as e:
            print("An error occured: ", e)
    
    def call_lm(self,prompt):
        response = self.model.invoke(prompt)
        return response
    
    def __extract_result(self,results):
        pass

