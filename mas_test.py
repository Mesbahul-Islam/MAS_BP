import getpass
import os
import json

#if "GOOGLE_API_KEY" not in os.environ:
 #   os.environ["GOOGLE_API_KEY"] = "AIzaSyBRq2kF4d0ZDAa-B0d0pWpSiwVhUYQFdks"

if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "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"

#gemini api AIzaSyBZhfJoMC866Ah7bW4cGKIcgxT4IvzT00s
#gemini api AIzaSyBRq2kF4d0ZDAa-B0d0pWpSiwVhUYQFdks
#pip install -U langchain  
#pip install -U langchain-google-genai
#pip install langchain-openrouter
#pip install -qU langchain-community


#from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
#from langchain_community.tools.json.tool import JsonSpec


data = {}

with open ("output.jsonl", 'r') as f:
   for line in f:
        data.update(json.loads(line))

#json_spec = JsonSpec(dict_= data)
#json_toolkit = JsonToolkit(spec= json_spec)


#from langchain_google_genai import ChatGoogleGenerativeAI

#model = ChatGoogleGenerativeAI(
 #   model="gemini-2.5-flash",
  #  temperature=1.0,  # Gemini 3.0+ defaults to 1.0
   # max_tokens=None,
    #timeout=None,
   # max_retries=2,
    # other params...
#)

from langchain_openrouter import ChatOpenRouter

model2 = ChatOpenRouter(
    model="inclusionai/ling-2.6-flash:free",
    temperature=0,
    max_tokens=1024,
    
)

#json_agent_executor = create_json_agent(model2, json_toolkit, handle_parsing_errors=True)

#try:
#        response = json_agent_executor.invoke("Are there any anomalities?")
#    except Exception as e:
#        response = str(e)
#        if response.startswith("Could not parse LLM output: `"):
#                 response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
#                 print(response)

def route_analysis_agent() -> str:
    response = model2.invoke(f"Is there a difference between delivery speeds:\n{data}")   
    print (response.content)
    return response.content

def cargo_safety_agent() -> str:
    
    response = model2.invoke(f"Is there a difference in temperatures:\n{data}") 
    print(response.content)        
    return response.content

def orchestrator_agent(prompt: str) -> str:    
    
    if "route" in question:
        return route_analysis_agent()
    if "cargo" in question:
        return cargo_safety_agent()

    response = model.invoke([HumanMessage(content=question)])
    return response.content


#question = "route"
question = "cargo"
answer = orchestrator_agent(question)

print(answer)