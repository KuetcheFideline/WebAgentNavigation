
prompt = {
    "intro": "",
    "examples": [],
    "template": """

You are a helpful assistant that can assist with web navigation tasks.
You are given an image and a task description. 
Your goal is to complete the task.
you should give only one paragraph for the response 

#Task: {objective}

 
    """,
    "finale": ""
,
    "meta_data": {
        "observation": "image_url",
        "action_type": "describe_image",
        "keywords": ["image_url", "objective"],
        "prompt_constructor": "DescribeImagePromptConstructor",
        "answer_phrase": "",
        "action_splitter": "#"      }

    
    
    
    }