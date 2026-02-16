from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import os
import asyncio
from dotenv import load_dotenv
from logger import logger

load_dotenv()

# Do not import `brain` at module import time (it pulls heavy ML deps).
# We'll import it lazily inside `get_brain()` to avoid blocking startup.
BraavBrain = None

app = FastAPI()

# Allow the React UI (localhost:5173) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class Thought(BaseModel):
    content: str

# Lazy initialize BraavBrain to avoid blocking startup (model downloads may hang)
brain = None
_brain_attempted = False

def get_brain():
    """Attempt to initialize and return the BraavBrain instance once.

    Returns None if initialization fails or required env vars are missing.
    """
    global brain, _brain_attempted
    if brain is not None:
        return brain
    if _brain_attempted:
        return None
    _brain_attempted = True

    SUPA_URL = os.getenv("SUPABASE_URL")
    SUPA_KEY = os.getenv("SUPABASE_KEY")
    if not (SUPA_URL and SUPA_KEY):
        logger.warning("SUPABASE_URL or SUPABASE_KEY not found in .env")
        return None

    # Attempt to import BraavBrain lazily (this may pull ML deps)
    global BraavBrain
    if BraavBrain is None:
        try:
            from brain import BraavBrain as _BB
            BraavBrain = _BB
        except BaseException as e:
            logger.error(f"Lazy import of BraavBrain failed: {e}", exc_info=True)
            return None

    try:
        brain = BraavBrain(SUPA_URL, SUPA_KEY)
        logger.info("BraavBrain initialized.")
        return brain
    except BaseException as e:
        # Catch broad exceptions so the server stays up
        logger.error(f"Failed to initialize BraavBrain (will continue without it): {e}", exc_info=True)
        brain = None
        return None


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Route chat requests to the BraavBrain agent loop when available.

    Falls back to a simple Ollama chat if BraavBrain isn't configured.
    """
    current_brain = get_brain()
    if current_brain:
        # run blocking agent in a thread to avoid blocking the event loop
        try:
            reply = await asyncio.to_thread(current_brain.handle_query, request.message)
            return {"reply": reply}
        except Exception as e:
            logger.error(f"Error in agent: {e}", exc_info=True)
            return {"reply": f"Error in agent: {e}"}

    # Fallback: return a simple Ollama reply
    try:
        logger.info("Falling back to Ollama chat")
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': 'You are the ORB Kernel. You are assisting Macha.'},
            {'role': 'user', 'content': request.message},
        ])
        return {"reply": response['message']['content']}
    except Exception as e:
        logger.error(f"LLM error: {e}", exc_info=True)
        return {"reply": f"LLM error: {e}"}


@app.post("/thoughts")
async def post_thought(thought: Thought):
    """Persist a thought via the BraavBrain if available (calls `log_stream`)."""
    current_brain = get_brain()
    if current_brain:
        try:
            res = await asyncio.to_thread(current_brain.log_stream, thought.content)
            return {"status": res}
        except Exception as e:
            logger.error(f"Error posting thought: {e}", exc_info=True)
            return {"status": f"error: {e}"}
    logger.warning("Could not post thought, no brain configured")
    return {"status": "no-brain-configured"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Bridge API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)