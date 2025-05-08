from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


class AIAgent1:
    def __init__(self,model='deepseek-r1:8b',temperature=0.0,chunksize = 8192,chunk_overlap = 200):
        try:
            self.model_name = model
            self.chunksize = chunksize
            self.chunk_overlap = chunk_overlap
            self.model = OllamaLLM(base_url="http://localhost:11434/",model = model,temperature=temperature)
        except Exception as e:
            print("An error occured: ", e)
    
    def truncate_prompt(self,prompt):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            #model_name = self.model_name,
            encoding_name="cl100k_base",
            chunk_size = self.chunksize,
             chunk_overlap=200
        )
        chunks = text_splitter.split_text(prompt)
        return chunks

    
    def call_lm(self,prompt):
        chunks = self.truncate_prompt(prompt=prompt)
        ouputs = [ self.model.invoke(chunk) for chunk in chunks]
        response = "\n \n".join(ouputs)
        return response
    
    def __extract_result(self,results):
        pass

