import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import app_graph

# --- Configuration ---
st.set_page_config(page_title="SAP Org Sidekick", page_icon="🏢", layout="wide")
st.title("🏢 SAP Organization Sidekick")

# Add this to your sidebar code in app.py
st.sidebar.markdown("### ⚡ Quick Try Examples")
example_q = st.sidebar.selectbox(
    "Select a complex query:",
    [
        "",
        "Create a Branch Profitability architecture (PaPM + ABAP + Fiori)",
        "Model a Matched Maturity FTP curve in PaPM",
        "Refactor legacy ABAP BSEG select to modern RAP",
        "Trace Basel III RWA lineage in BW/4HANA"
    ]
)

if example_q:
    # Auto-fill the chat input (requires a slight tweak to how input is handled or just copy-paste)
    st.sidebar.info(f"Copy this: {example_q}")


# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        expert_name = message.name if message.name else "Assistant"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**{expert_name}:** {message.content}")

# Chat Input
user_input = st.chat_input("Ask about PaPM models, ABAP code, or Fiori dashboards...")

if user_input:
    # 1. Add User Message to History
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Run the LangGraph Agent
    with st.spinner("The Supervisor is routing your request..."):
        inputs = {"messages": st.session_state.messages}
        for event in app_graph.stream(inputs):
            for key, value in event.items():
                if key != "Supervisor" and "messages" in value:
                    response_msg = value["messages"][0]
                    st.session_state.messages.append(response_msg)
                    
                    expert_name = response_msg.name
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"**{expert_name}:** {response_msg.content}")