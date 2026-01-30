import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import app_graph

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="SAP Banking Sidekick", 
    page_icon="🏦", 
    layout="wide"
)

st.title("🏦 SAP Banking Sidekick")
st.markdown(
    """
    ### Agentic AI for PaPM, ABAP, Fiori & BW
    *Powered by Google Gemini 2.0 Flash • LangGraph • Streamlit*
    """
)

# --- 2. Initialize Session State (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar: Quick Select Complex Scenarios ---
st.sidebar.header("⚡ Complex Banking Scenarios")
st.sidebar.markdown("Click to run a full agent simulation:")

# Define the banking & allocation scenarios
scenarios = {
    "🔄 IT Service Recharges (Recharge Model)": (
        "Design an 'IT Service Recharge' model in PaPM. "
        "1. Source: IT Cost Centers (Sender). "
        "2. Target: Business Units (Receiver). "
        "3. Driver: 'Server CPU Usage' and 'Helpdesk Tickets'. "
        "4. Logic: Calculate the recharge amount (Rate * Quantity) and markup by 5%. "
        "5. Show ABAP code to expose this as a Journal Entry interface."
    ),
    "🌊 Waterfall Cost Allocation (Multi-Step)": (
        "Create a 3-step 'Waterfall' Allocation cycle in PaPM for month-end close. "
        "Step 1: Allocate 'HR & Admin' costs to 'IT' and 'Business' based on Headcount. "
        "Step 2: Allocate 'IT' total costs (direct + received) to 'Business Units' based on System Usage. "
        "Step 3: Final allocation to 'Products' based on Revenue. "
        "Visualize the flow."
    ),
    "🏦 Liquidity Cost Allocation (FTP)": (
        "I need to allocate 'Treasury Funding Costs' down to individual 'Loan Accounts'. "
        "1. Source: Treasury Pool Cost Center. "
        "2. Driver: Daily Average Balance (ADB) of the loan. "
        "3. Constraint: Only allocate to loans with status 'Active'. "
        "4. Provide the BW/4HANA lineage to report on 'Net Interest Margin' after this allocation."
    ),
    "💰 Branch Profitability (End-to-End)": (
        "I need a 'Branch Profitability' dashboard. "
        "1. Use PaPM to allocate Operating Costs to branches based on 'Square Footage'. "
        "2. Expose the results via an ABAP CDS View. "
        "3. Visualize it in Fiori with a heatmap."
    ),
    "📉 Risk Data Lineage (Compliance)": (
        "Audit the 'Risk Weighted Assets' (RWA) field for Basel III. "
        "Trace the lineage in BW/4HANA from the final Composite Provider "
        "back to the source S/4HANA ACDOCA table. Identify transformations."
    ),
     "🚀 Optimize Loan Report (Perf)": (
        "My 'Daily Loan Origination' report is too slow. "
        "It joins 50M records in a BW Composite Provider. "
        "Should I persist the PaPM results to HANA or use a virtual access? "
        "Provide the SQLScript for the optimal approach."
    )
}

# Logic to capture button clicks
sidebar_trigger = None
for label, prompt_text in scenarios.items():
    if st.sidebar.button(label):
        sidebar_trigger = prompt_text

# --- 4. Display Chat History ---
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        # Check if the message has a specific sender name
        expert_name = message.name if hasattr(message, 'name') and message.name else "Assistant"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**{expert_name}:** {message.content}")

# --- 5. Handle Input (Chat OR Sidebar) ---
chat_input = st.chat_input("Ask about PaPM, ABAP, or Banking Models...")

# Determine if the user typed something OR clicked a button
final_prompt = chat_input or sidebar_trigger

if final_prompt:
    # A. Add User Message to History & Display
    st.session_state.messages.append(HumanMessage(content=final_prompt))
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # B. Run the LangGraph Agent
    with st.spinner("The Supervisor is routing your banking request..."):
        inputs = {"messages": st.session_state.messages}
        try:
            # Stream the events from the graph
            for event in app_graph.stream(inputs):
                for key, value in event.items():
                    # We only care about the worker node responses, not the Supervisor's routing step
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

# --- Footer / Sidebar Info ---
st.sidebar.markdown("---")
st.sidebar.info(
    "**System Status:** Online\n"
    "**Model:** Gemini 2.0 Flash\n"
    "**Agents:** PaPM, ABAP, Fiori, BW"
)