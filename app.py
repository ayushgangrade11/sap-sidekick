import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import app_graph

# --- Configuration ---
st.set_page_config(page_title="SAP Org Sidekick", page_icon="🏦", layout="wide")
st.title("🏦 SAP Banking Sidekick")
st.markdown("### Agentic AI for PaPM, ABAP, Fiori & BW")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Quick Select Complex Scenarios ---
st.sidebar.header("⚡ Complex Banking Scenarios")
st.sidebar.markdown("Click to run a full agent simulation:")

# Define the scenarios
scenarios = {
    "💰 Branch Profitability (End-to-End)": (
        "I need a 'Branch Profitability' dashboard. "
        "1. Use PaPM to allocate IT costs to branches based on 'Headcount' driver. "
        "2. Expose the results via an ABAP CDS View. "
        "3. Visualize it in Fiori with a heatmap."
    ),
    "📉 Risk Data Lineage (Compliance)": (
        "Audit the 'Risk Weighted Assets' (RWA) field for Basel III. "
        "Trace the lineage in BW/4HANA from the final Composite Provider "
        "back to the source S/4HANA ACDOCA table. Identify transformations."
    ),
    "📊 FTP Curve Modeling (Quant)": (
        "Model a 'Matched Maturity' Funds Transfer Pricing (FTP) curve in PaPM. "
        "Inputs: 'Loan Duration' and 'Currency'. "
        "Logic: Lookup rates from Z_YIELD_CURVE and calculate the transfer rate."
    ),
    "🚀 Optimize Loan Report (Perf)": (
        "My 'Daily Loan Origination' report is too slow. "
        "It joins 50M records in a BW Composite Provider. "
        "Should I persist the PaPM results to HANA or use a virtual access? "
        "Provide the SQLScript for the optimal approach."
    )
}

# Variable to hold the user's choice
sidebar_trigger = None

# Create a button for each scenario
for label, prompt_text in scenarios.items():
    if st.sidebar.button(label):
        sidebar_trigger = prompt_text

# --- Display Chat History ---
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        expert_name = message.name if message.name else "Assistant"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**{expert_name}:** {message.content}")

# --- Handle Input (Chat OR Sidebar) ---
chat_input = st.chat_input("Ask about PaPM, ABAP, or Banking Models...")

# Logic: Did the user type something OR click a button?
final_prompt = chat_input or sidebar_trigger

if final_prompt:
    # 1. Add User Message to History
    st.session_state.messages.append(HumanMessage(content=final_prompt))
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # 2. Run the LangGraph Agent
    with st.spinner("The Supervisor is routing your banking request..."):
        inputs = {"messages": st.session_state.messages}
        try:
            for event in app_graph.stream(inputs):
                for key, value in event.items():
                    if key != "Supervisor" and "messages" in value:
                        response_msg = value["messages"][0]
                        
                        # Add to history
                        st.session_state.messages.append(response_msg)
                        
                        # Display immediately
                        expert_name = response_msg.name
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(f"**{expert_name}:** {response_msg.content}")
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            st.info("Tip: If using Free Tier, this might be a rate limit. Wait 60s and try again.") 