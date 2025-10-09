from llms.Model import AIAgent1
from utils.utils import read_from_json,get_category_list_from_folder,extract_json_from_output,add_task_to_category_json
import json
model = AIAgent1()


def task_generation():  
    examples = read_from_json("./prompts/FewShotTask.json")
    #print(examples)
    categories = get_category_list_from_folder("./results")
    #print("######################deve#######################################""")

    #print(categories)
    #print("######################deve#######################################""")

    for category in categories:
        data = {
            "website_category" :category
        }
        #print(data)
        #print("######################deve#######################################""")

        Prompt_first = model.Promt_generation("Tasks",data=data)
        #print(Prompt_first)
        #print("######################deve#######################################""")

        response = model.call_lm(PromptFirst=Prompt_first,example=examples)
        #print(response,"##########################################################################")
        format_res = extract_json_from_output(response.content)
        #json.dumps(format_res,indent=2)
        # print(format_res['website_category'])
        add_task_to_category_json(f"./results/{format_res['website_category']}.json",format_res)

     
if __name__ == "__main__":
    task_generation()

# print(f"Extracted result {model.extract_category(model_output=template_text)}")
# #print(model.call_lm("Hello llamy , what is the name of the oldest president ghana?"))