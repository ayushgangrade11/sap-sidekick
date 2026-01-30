import operator
from typing import Annotated, List, TypedDict, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from agents import papm_agent, abap_agent, fiori_agent, bw_agent, llm

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str

# --- Simplified System Prompt ---
# We tell the model to output ONLY the name, no JSON.
system_prompt = (
    "You are the Supervisor of an SAP Technical Team. "
    "Your goal is to route the request to the correct expert. "
    "Return ONLY the exact name of the expert from this list:\n"
    "PaPM_Expert\n"
    "ABAP_Developer\n"
    "Fiori_UX\n"
    "BW_Architect\n"
    "FINISH\n\n"
    "Rules:\n"
    " - Allocations/Simulation -> PaPM_Expert\n"
    " - Backend Code/CDS -> ABAP_Developer\n"
    " - Frontend/UI/Dashboard -> Fiori_UX\n"
    " - Data Warehousing/Lineage -> BW_Architect\n"
    " - If the user greets you or the task is done -> FINISH"
)

def supervisor_node(state: AgentState):
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    # CRITICAL CHANGE: Standard invoke instead of structured_output
    # This prevents the 500 error on free tier
    response = llm.invoke(messages)
    
    # Clean the output to get just the name
    decision = response.content.strip().replace('"', '').replace("'", "").replace(".", "")
    
    # Fallback safety (if model chats instead of routing)
    valid_nodes = ["PaPM_Expert", "ABAP_Developer", "Fiori_UX", "BW_Architect", "FINISH"]
    if decision not in valid_nodes:
        # If ambiguous, default to PaPM or finish based on context, or just FINISH to be safe
        decision = "FINISH" 
        
    return {"next": decision}

# --- Define Worker Nodes (Same as before) ---
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

# --- Build Graph ---
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



# workflow.add_edge(START, "Supervisor")

# workflow.add_conditional_edges(
#     "Supervisor",
#     lambda x: x["next"],
#     {
#         "PaPM_Expert": "PaPM_Expert",
#         "ABAP_Developer": "ABAP_Developer",
#         "Fiori_UX": "Fiori_UX",
#         "BW_Architect": "BW_Architect",
#         "FINISH": END
#     }
# )

# workflow.add_edge("PaPM_Expert", "Supervisor")
# workflow.add_edge("ABAP_Developer", "Supervisor")
# workflow.add_edge("Fiori_UX", "Supervisor")
# workflow.add_edge("BW_Architect", "Supervisor")


# graph.py

# ... (Previous code remains the same) ...


# --- OPTIMIZATION: Direct to END ---
# Previously, these went back to "Supervisor", costing an extra API call.
# Now, we assume one answer is enough for this prototype.
workflow.add_edge("PaPM_Expert", END)
workflow.add_edge("ABAP_Developer", END)
workflow.add_edge("Fiori_UX", END)
workflow.add_edge("BW_Architect", END)


app_graph = workflow.compile()


