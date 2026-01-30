from dotenv import load_dotenv
load_dotenv()  # Load GOOGLE_API_KEY from .env

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Initialize Gemini ---
# We use gemini-1.5-pro for high reasoning capability
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Changed from "gemini-1.5-pro"
    temperature=0,
    convert_system_message_to_human=True
)
# --- 1. PaPM Agent (Financial Modeling Expert) ---
papm_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a Senior SAP PaPM (Profitability and Performance Management) Consultant. "
     "Your expertise includes: Allocations, FS-PER, HANA Calculation Views, and Simulation. "
     "When asked about modeling, always suggest the specific 'Function Type' (e.g., Allocation, Join, View). "
     "If the user asks for a simulation, define the 'Drivers' and 'Granularity'."),
    MessagesPlaceholder(variable_name="messages"),
])
papm_agent = papm_prompt | llm

# --- 2. ABAP Agent (Backend Coding Expert) ---
abap_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an Expert SAP ABAP Developer specializing in RAP (Restful ABAP Programming) and BTP. "
     "Always provide syntactically correct ABAP code. "
     "Use modern syntax (inline declarations, VALUE operators). "
     "If asked for data access, prefer CDS Views over direct SELECT statements."),
    MessagesPlaceholder(variable_name="messages"),
])
abap_agent = abap_prompt | llm

# --- 3. Fiori Agent (Frontend UX Expert) ---
fiori_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an SAP Fiori & UI5 Expert. "
     "Focus on SAP Fiori Elements and OData V4 annotations. "
     "When asked for UI code, provide XML Views or manifest.json configurations. "
     "Always ensure accessibility and responsive design principles."),
    MessagesPlaceholder(variable_name="messages"),
])
fiori_agent = fiori_prompt | llm

# --- 4. BW/Data Agent (Data Warehousing Expert) ---
bw_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an SAP BW/4HANA and Datasphere Architect. "
     "Your focus is on ADSOs, Composite Providers, and Data Lineage. "
     "Explain how data flows from source (S/4HANA) to the final reporting layer. "
     "Prioritize LSA++ architecture patterns."),
    MessagesPlaceholder(variable_name="messages"),
])
bw_agent = bw_prompt | llm