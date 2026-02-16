import streamlit as st
import sqlite3
from google import genai # Modern 2026 Import
import json
import re
from logger import logger

# ==========================================
# 1. THE BRAIN & BUCKET SETUP
# ==========================================
st.set_page_config(page_title="B'Raav Librarian", page_icon="🐕")

# Using the new Client structure
API_KEY = "AIzaSyDH33HLbWBHUy5AEFjCBS3pYMzKsVWPwaw"
client = genai.Client(api_key=API_KEY)
DB_NAME = "braav_ledger.db"

def execute_db(query, params=()):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            logger.info(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error executing query: {query}", exc_info=True)
        st.error(f"Database error: {e}")
        return []


# ==========================================
# 2. CORE LOGIC: THE 2026 ARCHITECT
# ==========================================
def librarian_architect(user_input):
    logger.info(f"Librarian architecting for: {user_input}")
    existing_tables = execute_db("SELECT name FROM sqlite_master WHERE type='table';")
    tables_list = [t[0] for t in existing_tables]
    
    prompt = f"""
    You are B'Raav, the Autonomous Librarian. 
    User input: "{user_input}"
    Existing Tables: {tables_list}
    
    Task: Decide if this fits an existing table or needs a NEW one. 
    Provide SQL for CREATE and INSERT.
    Return ONLY JSON:
    {{
        "explanation": "Brief reason",
        "table_name": "name",
        "new_table_sql": "SQL code or null",
        "insert_sql": "SQL code",
        "params": ["list of values"]
    }}
    """
    
    try:
        # NEW 2026 SDK Call
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # Extract JSON from the new response format
        clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        logger.info(f"Librarian response: {clean_json}")
        return json.loads(clean_json)
    except Exception as e:
        logger.error(f"Error in librarian architect: {e}", exc_info=True)
        st.error(f"Error contacting the librarian: {e}")
        return None

# ==========================================
# 3. STREAMLIT FACE (UI)
# ==========================================
st.title("🐕 B'Raav: The Loyal Librarian")
st.caption("Neuro-Architectural Data Engine | SDK v2.0")

# Session state to keep track of what we are looking at
if 'current_table' not in st.session_state:
    st.session_state.current_table = None

with st.sidebar:
    st.header("Your Buckets")
    tables = execute_db("SELECT name FROM sqlite_master WHERE type='table';")
    for t in tables:
        if t[0] != 'sqlite_sequence':
            if st.button(f"📂 {t[0]}", use_container_width=True):
                st.session_state.current_table = t[0]
                logger.info(f"Switched to table: {t[0]}")

# Main Action Area
thought = st.text_input("Catch a thought:", placeholder="e.g., Applied to Amazon, Senior Data Eng")

if st.button("Bury in Ledger"):
    if thought:
        with st.spinner("Librarian is architecting..."):
            plan = librarian_architect(thought)
            if plan:
                if plan.get("new_table_sql"):
                    logger.info(f"Creating new table: {plan['table_name']}")
                    execute_db(plan["new_table_sql"])
                logger.info(f"Inserting into table: {plan['table_name']}")
                execute_db(plan["insert_sql"], tuple(plan["params"]))
                st.success(f"Archived: {plan['explanation']}")
                st.rerun() # Refresh to show new tables/data
    else:
        st.warning("Input required.")

# Data Display
if st.session_state.current_table:
    st.divider()
    st.subheader(f"Table: {st.session_state.current_table}")
    data = execute_db(f"SELECT * FROM {st.session_state.current_table} ORDER BY rowid DESC LIMIT 10")
    st.table(data)