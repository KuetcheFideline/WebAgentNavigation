prompt = {
    "intro": "",
    "examples": [],
    "template": """<html> {html} </html>        
<image> {image_url} </image>            
You are a helpful assistant that can assist with web navigation tasks.
You are given a simplified html webpage, an image from the webpage
and a task description. 
Your goal is to complete the task.
#Task : {objective } 
# """,
    "meta_data": {
        "observation": "html_image",
        "action_type": "id_html_nasc_tree",
        "keywords": [
            "html",
            "image_url",
            "objective"],
        "prompt_constructor": "ImageHTMLPromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"
    },
    
    }