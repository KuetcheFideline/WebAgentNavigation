from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate

example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")
import re
from pathlib import Path
import json


import os
import json

class AIAgent1:
    def __init__(self,model='deepseek-coder:latest',temperature=0.0,chunksize = 8192,chunk_overlap = 200):
        try:
            self.chunksize = chunksize
            self.chunk_overlap = chunk_overlap
           # self.model = OllamaLLM(base_url="http://localhost:11434/",model = model,temperature=0)
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
         

        chain = Prompt | self.model
        return chain.invoke({"input": PromptFirst})







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
           # print(prompt)
            return prompt
        except FileNotFoundError:
            print("fichier intouvable")
            return None
    
        
        # chunks = self.truncate_prompt(prompt=prompt)
        # ouputs = [ self.model.invoke(chunk) for chunk in chunks]
        # response = "\n \n".join(ouputs)
        # return response
    



    
    def extract_category(self,model_output,result_dir:str="results"):


        # Extract_result et save dans un fichier la categorie et et les urls associés 
        """
            model_output:  
                #Category: [category]\n#Configence: [score]\n#Url: [url]\n#Explanation: [explanation]
        """
        # Expression reguliere pour extraire les champs
        category_pattern = r"#Category: (.*?)\n"
        confidence_pattern = r"Confidence: (\d+)"
        url_pattern = r"#Url: (.*?)\n"
        explanation_pattern = r"#Explanation: (.*?)(?:\n|$)"

        # Extract information from the prompts
        category_match = re.match(category_pattern,model_output)
        confidence_match = re.search(confidence_pattern, model_output)
        url_match = re.search(url_pattern, model_output)
        explanation_match = re.search(explanation_pattern, model_output)

        # check if all the information are there
        if not all([category_match,confidence_match,url_match,explanation_match]):
            print(f"Error: Canot extract info from: {model_output} ")
            return None
        
        result = {
            "category":category_match.group(1).strip(),
            "confidence": int(confidence_match.group(1)),
            "url": url_match.group(1).strip(),
            "explanation": explanation_match.group(1).strip()
        }

        #create the save dir if needed
        Path(result_dir).mkdir(exist_ok=True)

        #defining the path to the json file
        category_file = Path(result_dir)/ f"{result['category']}.json"

        #initialise or load file content 

        if category_file.exists():
            with open(category_file,'r',encoding="utf-8") as f:
                try:
                    print("exist file")
                    category_data = json.load(f)
                    print(category_data["sites"])
                    print(result)
                    if result["url"] not in category_data["sites"]:
                        print("not In")
                        category_data["sites"].append(result["url"])
                    
                    else:
                         print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
                    with open(category_file, "w", encoding="utf-8") as f:
                        json.dump(category_data, f, indent=2, ensure_ascii=False)
                    return result
                    
                except json.JSONDecodeError:
                    print(f"ERROR: corrupted file {category_file}, initialising a new file")
                    category_data = {"sites":[],"tasks":[]}
        else:
            category_data = {"sites":[],"tasks":[]}
        
            if result["url"] not in category_data["sites"]:
                category_data["sites"].append(result["url"])
            else:
                print(f"Info: URL {result['url']} déjà présente dans {category_file}, ignorée.")
            
            with open(category_file, "w", encoding="utf-8") as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
            
            print(f"Succès: URL {result['url']} ajoutée à {category_file}")
            return result




  

