# app.py
import os
import time
import threading
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Configure standard logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("co_founder_memory.app")

# Ensure environmental variables are loaded
from dotenv import load_dotenv
load_dotenv()

# Validate critical GROQ_API_KEY on startup
if not os.getenv("GROQ_API_KEY"):
    logger.critical("Configuration Error: GROQ_API_KEY is required but missing.")
    raise RuntimeError("Configuration Error: GROQ_API_KEY is required but missing.")

from graph.main_graph import compiled_main_graph, memory_store
from graph.auto_graph import compiled_auto_graph
from storage_utils import load_state, save_state, get_default_state

app = FastAPI(
    title="Co-Founder Memory Cockpit",
    description="A deployment-ready web service and control center for Co-Founder Memory.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str

def run_scheduler_with_lock_prep():
    """
    Background scheduler daemon loop wrapped to support Postgres advisory locks.
    It checks a 'has_lock' variable to prevent duplicate execution across workers.
    """
    from datetime import datetime
    logger.info("⏳ Smart Background Daemon activated (prepped for advisory lock checking)...")

    while True:
        # Prepped for postgres advisory lock check
        # e.g., has_lock = check_postgres_advisory_lock(9876543210)
        # Defaults to True for simple single-worker/prototype execution.
        has_lock = True
        
        if has_lock:
            try:
                now = datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                
                # Load state
                current_state = load_state()
                
                # Check if today's dossier has already been created
                has_run_today = today_str in current_state.get("date_memory", {})
                
                # Trigger conditions
                is_midnight = (now.hour == 0 and now.minute == 0)
                is_missed_catchup = not has_run_today and now.hour >= 1
                
                if is_midnight or is_missed_catchup:
                    if is_midnight:
                        logger.info(f"⏰ Midnight struck ({now.strftime('%H:%M:%S')}). Executing standard scheduled loop...")
                    else:
                        logger.info(f"🚨 Catch-up detected at {now.strftime('%H:%M:%S')}! Processing today's dossier now...")
                    
                    try:
                        # Invoke auto graph
                        updated_state = compiled_auto_graph.invoke(current_state)
                        if updated_state:
                            if "date_memory" not in updated_state:
                                updated_state["date_memory"] = {}
                            updated_state["date_memory"][today_str] = "Completed"
                            save_state(updated_state)
                        logger.info(f"🟢 Success: Dossier for {today_str} completed and state updated.")
                    except Exception as e:
                        logger.exception("❌ Automation graph error during background execution:")
            except Exception as e:
                logger.exception("❌ Error during background scheduler iteration:")
        else:
            logger.debug("Another worker holds the lock. Skipping scheduler iteration.")

        # Check every 60 seconds
        time.sleep(60)

# Startup background scheduler
@app.on_event("startup")
def start_scheduler():
    if os.getenv("RUN_BACKGROUND_SCHEDULER", "true").lower() == "true":
        logger.info("🚀 Web Cockpit: Launching background scheduler daemon...")
        thread = threading.Thread(target=run_scheduler_with_lock_prep, daemon=True)
        thread.start()

@app.get("/api/state")
def get_state():
    try:
        return load_state()
    except Exception as e:
        logger.exception("Error loading system state:")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
def healthz():
    return {
        "ok": True,
        "storage": "supabase" if os.getenv("SUPABASE_URL") else "local",
        "scheduler": os.getenv("RUN_BACKGROUND_SCHEDULER", "true").lower() == "true",
    }

@app.get("/api/profile")
def get_profile():
    try:
        namespace = ("memory", "profile")
        key = "co_founder_profile"
        profile_item = memory_store.get(namespace, key)
        if profile_item and profile_item.value:
            return profile_item.value
        return {}
    except Exception as e:
        logger.exception("Error retrieving permanent memory profile:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def run_chat(req: ChatRequest):
    try:
        state = load_state()
        state["user_query"] = req.message
        
        # Invoke Main Graph
        result = compiled_main_graph.invoke(state)
        
        # Extract updates
        updated_state = {
            "temporary_memory": result.get("temporary_memory", state.get("temporary_memory", [])),
            "chunk_memory": result.get("chunk_memory", state.get("chunk_memory", []),),
            "extracted_memories": result.get("extracted_memories", state.get("extracted_memories", [])),
            "retrieved_context": result.get("retrieved_context", state.get("retrieved_context", [])),
            "final_response": result.get("final_response", "")
        }
        
        # Sync state
        state.update(updated_state)
        save_state(state)
        
        return {
            "response": state["final_response"],
            "state": state
        }
    except Exception as e:
        logger.exception("Error executing chat endpoint:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auto-run")
def force_auto_run():
    try:
        logger.info("🌙 API Triggered: Running automated daily loop...")
        state = load_state()
        
        # Invoke Auto Graph
        result = compiled_auto_graph.invoke(state)
        
        if result:
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if "date_memory" not in result:
                result["date_memory"] = {}
            result["date_memory"][today_str] = "Completed"
            
            save_state(result)
            return {
                "dossier": result.get("final_response"),
                "state": result
            }
        raise HTTPException(status_code=500, detail="Automated graph returned empty results.")
    except Exception as e:
        logger.exception("Error executing auto-run endpoint:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
def reset_state():
    try:
        default_state = get_default_state()
        save_state(default_state)
        return {"message": "System state reset successful.", "state": default_state}
    except Exception as e:
        logger.exception("Error executing reset endpoint:")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles

# Serve the static files from the 'frontend' directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Launching Co-Founder Memory Cockpit on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
