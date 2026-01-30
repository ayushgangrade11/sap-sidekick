import operator
from typing import Annotated, List, TypedDict, Union, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from agents import papm_agent, abap_agent, fiori_agent, bw_agent, llm
from pydantic import BaseModel

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str

# Define the Supervisor's choices
class RouteResponse(BaseModel):
    next: Literal["PaPM_Expert", "ABAP_Developer", "Fiori_UX", "BW_Architect", "FINISH"]

system_prompt = (
    "You are the Supervisor of an SAP Technical Team. "
    "Your goal is to route the user's request to the correct expert. "
    " - For profitability, allocations, or simulations -> 'PaPM_Expert' "
    " - For backend code, BAPIs, or CDS Views -> 'ABAP_Developer' "
    " - For frontend, UI5, or dashboards -> 'Fiori_UX' "
    " - For data warehousing, ADSOs, or lineage -> 'BW_Architect' "
    " - If the user just says hello or the task is done -> 'FINISH'"
)

def supervisor_node(state: AgentState):
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    # Gemini supports structured output via this method seamlessly now
    response = llm.with_structured_output(RouteResponse).invoke(messages)
    return {"next": response.next}

# ... (The rest of graph.py remains exactly the same) ...
# ... (Include the worker nodes and workflow definitions from previous step) ...

def papm_node(state: AgentState):
    response = papm_agent.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content, name="PaPM_Expert")]}

def abap_node(state: AgentState):
    response = abap_agent.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content, name="ABAP_Developer")]}

def fiori_node(state: AgentState):
    response = fiori_agent.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content, name="Fiori_UX")]}

def bw_node(state: AgentState):
    response = bw_agent.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content, name="BW_Architect")]}

workflow = StateGraph(AgentState)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("PaPM_Expert", papm_node)
workflow.add_node("ABAP_Developer", abap_node)
workflow.add_node("Fiori_UX", fiori_node)
workflow.add_node("BW_Architect", bw_node)

workflow.add_edge(START, "Supervisor")
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "PaPM_Expert": "PaPM_Expert",
        "ABAP_Developer": "ABAP_Developer",
        "Fiori_UX": "Fiori_UX",
        "BW_Architect": "BW_Architect",
        "FINISH": END
    }
)
workflow.add_edge("PaPM_Expert", "Supervisor")
workflow.add_edge("ABAP_Developer", "Supervisor")
workflow.add_edge("Fiori_UX", "Supervisor")
workflow.add_edge("BW_Architect", "Supervisor")

app_graph = workflow.compile()