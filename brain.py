import os
import json
import datetime
import re
import sys
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
from groq import Groq
from logger import logger

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

class BraavBrain:
    def __init__(self, url, key):
        logger.info("🧠 Initializing BraavBrain...")
        try:
            self.db = create_client(url, key)
            logger.info("📡 Supabase connected successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
        
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Embeddings model loaded (SentenceTransformer)")
        except Exception as e:
            logger.error(f"❌ Failed to load SentenceTransformer: {e}")
        
        try:
            self.llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
            logger.info("✅ LLM client initialized (Groq)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq client: {e}")

        self.SCHEMA_MAP = """
        SYSTEM DESIGN (THE DRAWERS):
        1. thoughts: Personal journal/diary entries & 'Macha' thoughts.
           Columns: content (text), created_at (timestamp), embedding (vector), metadata (jsonb)
        2. interactions: Historical chat memory between User and ORB.
           Columns: content (text), category (text), created_at (timestamp), embedding (vector)
        3. files_in_void: Digitized PDF/text from external files.
           Columns: content (text), name (text), created_at (timestamp), embedding (vector)
        4. query_logs: Audit trail of ORB's technical execution.
           Columns: user_query (text), agent_plan (jsonb), tool_outputs (text), ai_response (text)
        """
        logger.info("📋 System Manifesto loaded (drawer schema ready)")

    def handle_query(self, user_query):
        self.log_interaction(user_query, "user_input")
        return self.agent_query(user_query)

    def get_embedding(self, text: str):
        return self.embedder.encode(text).tolist()

    def log_interaction(self, content, category):
        try:
            vector = self.get_embedding(content)
            self.db.table("interactions").insert({
                "content": content, "category": category,
                "embedding": vector, "created_at": datetime.datetime.utcnow().isoformat()
            }).execute()
            logger.debug(f"📡 Interaction Logged: {category}")
        except Exception as e:
            logger.error(f"❌ DB Error (Interaction): {e}")

    def is_sql_safe(self, sql: str):
        sql_clean = sql.strip().replace("```sql", "").replace("```", "").rstrip(';')
        sql_upper = sql_clean.upper()
        banned = ["DELETE", "DROP", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        if any(b in sql_upper for b in banned):
            return False, "FORBIDDEN: Destructive SQL."
        
        allowed_tables = ["thoughts", "interactions", "files_in_void", "query_logs"]
        tables_found = re.findall(r'(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql_clean.lower())
        if not all(t in allowed_tables for t in tables_found):
            return False, f"FORBIDDEN: Unauthorized table access."
        
        if "LIMIT" not in sql_upper: sql_clean += " LIMIT 50"
        return True, sql_clean

    def agent_query(self, user_query):
        logger.info(f"\n[USER QUESTION]: {user_query}")
        logger.info("📡 Step 0: Fetching preliminary semantic memories...")
        context = self.retrieve_context(user_query)
        last_error = None

        for attempt in range(1, 4):
            logger.info(f"\n--- 🔄 ATTEMPT {attempt}/3 ---")
            plan_prompt = f"""
            ROLE: Lead Architect of ORB Kernel.
            SYSTEM DESIGN: {self.SCHEMA_MAP}
            PROBLEM: {user_query}
            RECOLLECTION: {context}
            PREVIOUS ERROR: {last_error}
            TASK: Decide if we need specific facts (SQL) or general vibes (SEMANTIC).
            JSON ONLY: {{
                "consideration": "Briefly explain WHY you are choosing SQL or Semantic.",
                "approach": "sql"|"semantic", 
                "sql_intent": "explanation"
            }}
            """
            try:
                plan_res = self.llm.chat.completions.create(
                    messages=[{"role": "system", "content": plan_prompt}],
                    model="llama-3.1-8b-instant", response_format={"type": "json_object"}
                )
                plan = json.loads(plan_res.choices[0].message.content)
                logger.warning(f"🤔 ORB CONSIDERATION: {plan.get('consideration', 'No reasoning provided.')}")
                logger.info(f"📝 NODE 1 (PLAN): {plan['approach'].upper()} | Intent: {plan.get('sql_intent', 'N/A')}")

                data = context
                if plan["approach"] == "sql":
                    logger.info("🛠️ Step 2: Generating and Validating SQL...")
                    gen_prompt = f"SYSTEM: {self.SCHEMA_MAP}\nINTENT: {plan['sql_intent']}\nGENERATE READ-ONLY SQL. NO EXPLANATION."
                    raw_sql = self.llm.chat.completions.create(
                        messages=[{"role": "user", "content": gen_prompt}], 
                        model="llama-3.1-8b-instant"
                    ).choices[0].message.content.strip()
                    
                    safe, final_sql = self.is_sql_safe(raw_sql)
                    if not safe: 
                        logger.warning(f"🚫 SQL BLOCKED: {final_sql}")
                        raise ValueError(final_sql)
                    
                    logger.warning(f"🔍 NODE 2 (SQL EXECUTE): {final_sql}")
                    data = self.db.rpc("execute_sql", {"query_text": final_sql}).execute().data
                    logger.info(f"📊 DATA RETRIEVED: Found {len(data) if data else 0} records.")
                else:
                    logger.info("🧠 Step 2: Proceeding with Semantic Retrieval context only.")

                logger.info("✍️ Step 3: Synthesizing Macha-style response...")
                sum_prompt = f"DATA: {data}\nUSER: {user_query}\nAnswer as a helpful peer. No internal logic mentions."
                answer = self.llm.chat.completions.create(
                    messages=[{"role": "system", "content": sum_prompt}], 
                    model="llama-3.1-8b-instant"
                ).choices[0].message.content
                
                self.log_query(user_query, plan, data, answer)
                self.log_interaction(answer, "ai_response")
                logger.info(f"✅ Mission Success on Attempt {attempt}!")
                return answer

            except Exception as e:
                last_error = str(e)
                logger.error(f"⚠️ NODE FAILURE (Attempt {attempt}): {last_error}", exc_info=True)
                self.log_query(user_query, {"error_attempt": attempt}, str(e), "FAILED")

        return "❌ All attempts failed. Check terminal for schema collisions."

    def retrieve_context(self, query: str):
        logger.debug(f"🧠 Retrieving semantic context for: {query[:50]}...")
        embedding = self.get_embedding(query)
        vector_str = f"'{[float(x) for x in embedding]}'"
        def run(table):
            sql = f"SELECT content FROM {table} ORDER BY embedding <-> {vector_str} LIMIT 3"
            try:
                return self.db.rpc("execute_sql", {"query_text": sql}).execute().data or []
            except Exception as e:
                logger.warning(f"⚠️ Vector search failed on {table}: {e}")
                return []
        return {"thoughts": run("thoughts"), "interactions": run("interactions")}

    def log_query(self, user_query, plan, tool_output, response):
        try:
            self.db.table("query_logs").insert({
                "user_query": user_query, "agent_plan": plan,
                "tool_outputs": str(tool_output), "ai_response": response,
                "created_at": datetime.datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to log query to query_logs: {e}")

    def log_stream(self, text):
        try:
            vector = self.get_embedding(text)
            self.db.table("thoughts").insert({"content": text, "embedding": vector, "metadata": {"is_processed": False}}).execute()
            logger.info(f"💡 Seeded Thought: {text[:40]}...")
            return "💡 Thought Saved"
        except Exception as e:
            logger.error(f"❌ Error seeding thought: {e}")
            return f"Error: {e}"