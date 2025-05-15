from llms.Model import AIAgent1
print("Hello from the container")

template_text = """#Category: news
#Confidence: 85
#Url: https://www.bbc.com
#Explanation: Ce site propose des cours en ligne structurés avec des modules d'apprentissage interactifs, des quiz et des certifications. La présence de contenu éducatif organisé et la possibilité de suivre une progression pédagogique sont caractéristiques d'une plateforme d'e-learning."""
model = AIAgent1()

model.call_lm("qui est tu ")
# print(f"Extracted result {model.extract_category(model_output=template_text)}")
# #print(model.call_lm("Hello llamy , what is the name of the oldest president ghana?"))