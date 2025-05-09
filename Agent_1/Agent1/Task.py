from tranco import Tranco
from llms.Model import AIAgent1

Agent1 = AIAgent1()

def SiteCategorisation():
    t = Tranco()
    sites = t.list().top(20)
    for site in sites:
        Prompt = Agent1.Promt_generation("Categorisation",{"domaine":site})
        response = Agent1.call_lm(Prompt)
        print(response)


    return sites


sites = SiteCategorisation()
print(sites)
