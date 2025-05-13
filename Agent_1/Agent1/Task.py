from tranco import Tranco
from llms.Model import AIAgent1

Agent1 = AIAgent1()

def SiteCategorisation():

    t = Tranco(cache=True,cache_dir=".tranco")
    latest_list = t.list()
    sites = ["http://" + x for x in latest_list.top(10)]
    
    for site in sites:
        Prompt = Agent1.Promt_generation("Categorisation",{"domaine":site})
        response = Agent1.call_lm(Prompt)
        print(response)


    return sites


sites = SiteCategorisation()
print(sites)
