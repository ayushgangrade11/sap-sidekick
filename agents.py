from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Initialize Gemini (Free Tier Optimized) ---
# We use 'gemini-1.5-flash' because it is lighter and more stable on free tier.
# We add max_retries=5 to automatically handle 500/503 server errors.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_retries=5,
    request_timeout=60,
    convert_system_message_to_human=True
)

# --- 1. PaPM Agent ---
papm_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a Senior SAP PaPM Consultant. "
     "Expertise: Allocations, FS-PER, HANA Calculation Views. "
     "Suggest specific 'Function Types' and 'Drivers' for simulations."),
    MessagesPlaceholder(variable_name="messages"),
])
papm_agent = papm_prompt | llm

# --- 2. ABAP Agent ---
abap_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an Expert SAP ABAP Developer (RAP & BTP). "
     "Output syntactically correct ABAP code with inline declarations. "
     "Prefer CDS Views over direct SELECTs."),
    MessagesPlaceholder(variable_name="messages"),
])
abap_agent = abap_prompt | llm

# --- 3. Fiori Agent ---
fiori_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an SAP Fiori & UI5 Expert. "
     "Focus on Fiori Elements, OData V4, and manifest.json. "
     "Provide XML Views when asked for UI."),
    MessagesPlaceholder(variable_name="messages"),
])
fiori_agent = fiori_prompt | llm

# --- 4. BW Agent ---
bw_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an SAP BW/4HANA Architect. "
     "Focus on ADSOs, Composite Providers, and LSA++ architecture. "
     "Explain data lineage clearly."),
    MessagesPlaceholder(variable_name="messages"),
])
bw_agent = bw_prompt | llm