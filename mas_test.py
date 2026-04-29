import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBZhfJoMC866Ah7bW4cGKIcgxT4IvzT00s"

#gemini api AIzaSyBZhfJoMC866Ah7bW4cGKIcgxT4IvzT00s
#pip install -U langchain-google-genai
#pip install -qU langchain-community

# Data loading into dict without preprocessing
data = {}

with open("output.jsonl") as f:
    for i, line in enumerate(f):
        data[i] = json.loads(line)
        
        
# Preprocessing data by metadata filtering?
#processed_data = []

#with open("output.jsonl") as f:
    #for line in f:
        #row = json.loads(line)
        
        #for snap in row["payload"]["snapshots"]:
            #ts = snap["telemetry_snapshot"]
            
            #processed_data.append({
                #"truck_id": ts["truck_id"],
                #"tick": ts["tick"],
                #"speed_kmh": ts["speed_kmh"],
                #"temperature_c": ts["temperature_c"],
                #"co2_ppm": ts["co2_ppm"],
                #"door_open": ts["door_open"],
                #"position": ts["position"]
            #})


#from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
#from langchain_community.tools.json.tool import JsonSpec
#from langchain_openai import OpenAI

#json_spec = JsonSpec(dict_=data)
#json_toolkit = JsonToolkit(spec=json_spec)

#llm = OpenAI(temperature=0)

#json_agent_executor = create_json_agent(
    #llm=llm,
    #toolkit=json_toolkit,
    #verbose=True
#)

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.3,
    max_retries=2,
)


def route_analysis_agent() -> str:
    prompt = f"""
    You are a real-time fleet anomaly detection system.
    
    Analyze the state based on the following instructions:
    - Focus only on abnormal behaviour
    - Do not add anything additional outside the required format
    - If no anomalies are detected, return OK
    
    Return the output only in this format:
    truck_id:
    issues:
    severity: LOW/MEDIUM/HIGH
    reason:
    overall_system_status: OK/WARNING/CRITICAL
    
    Telemetry for analysis:
    {json.dumps(data, indent=2)}
    
    """
    response = model.invoke(prompt)
    return response.content


def cargo_safety_agent() -> str:

    prompt = f"""
    You are a cargo safety monitoring AI.

    Analyze the truck telemetry and detect safety risks.

    Telemetry:
    {json.dumps(data, indent=2)}
    
    """

    response = model.invoke(prompt)
    return response.content


def orchestrator_agent(prompt: str) -> str:

    prompt_lower = prompt.lower()

    if "route" in prompt_lower:
        return route_analysis_agent()

    if "cargo" in prompt_lower:
        return cargo_safety_agent()

    return "Unknown request"


if __name__ == "__main__":
    question = "route"
    answer = orchestrator_agent(question)
    print(answer)
    