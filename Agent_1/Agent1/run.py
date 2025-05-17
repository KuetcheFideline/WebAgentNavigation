from llms.Model import AIAgent1
from utils.utils import read_from_json,get_category_list_from_folder,extract_json_from_output,add_task_to_category_json
import json
model = AIAgent1()


def task_generation():  
    examples = read_from_json("./prompts/FewShotTask.json")
    #print(examples)
    categories = get_category_list_from_folder("./results")
    """"
    categories = [
    "e-learning",
    "ecommerce",
    "health",
    "news",
        "food_and_recipes",
    "social_media",
    "finance",
    "education",
    "entertainment",
    "travel",
    "job_search",
    "real_estate",
    "government",
    "non_profit",
    "legal_services",
    "productivity_tools",
    "cloud_storage",
    "forum_community",
    "sports",
    "food_and_recipes",
    "personal_blogging",
    "portfolio",
    "tech_review",
    "music_streaming",
    "video_streaming",
    "gaming",
    "automotive",
    "fashion_and_beauty",
    "parenting",
    "event_management",
    "spirituality_and_religion"
]
    """

    print(categories)
    for category in categories:
        data = {
            "website_category" :category
        }
        Prompt_first = model.Promt_generation("Tasks",data=data)
        response = model.call_lm(PromptFirst=Prompt_first,example=examples)
        format_res = extract_json_from_output(response.content)
        #json.dumps(format_res,indent=2)
        print(format_res["website_category"])
        add_task_to_category_json(f"./results/{format_res["website_category"]}.json",format_res)

     
if __name__ == "__main__":
    task_generation()

# print(f"Extracted result {model.extract_category(model_output=template_text)}")
# #print(model.call_lm("Hello llamy , what is the name of the oldest president ghana?"))