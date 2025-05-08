from llms.Model import AIAgent1
print("Hello from the container")

model = AIAgent1()
print(model.call_lm("Hello llamy , what is the name of the oldest president of cameroon?"))