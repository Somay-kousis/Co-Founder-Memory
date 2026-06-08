# storage_utils.py
import json
import os
import logging
from supabase import create_client, Client

# Set up logging
logger = logging.getLogger("co_founder_memory.storage")

STATE_FILE = "live_memory_state.json"

# Validate critical GROQ_API_KEY on startup
if not os.getenv("GROQ_API_KEY"):
    logger.critical("GROQ_API_KEY is missing from environment variables.")
    raise RuntimeError("Configuration Error: GROQ_API_KEY is required but missing.")

# Check if Supabase is intended to be configured
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
SUPABASE_CONFIGURED = bool(url)

supabase_client = None
if SUPABASE_CONFIGURED:
    if not key:
        logger.critical("SUPABASE_URL is set but no Supabase key (SUPABASE_SERVICE_KEY/SUPABASE_KEY) was found.")
        raise RuntimeError("Configuration Error: Supabase key is missing while SUPABASE_URL is configured.")
    try:
        supabase_client = create_client(url, key)
        logger.info("storage_utils: Connected to Supabase for state storage.")
    except Exception as e:
        logger.exception("storage_utils: Failed to initialize Supabase client.")
        raise RuntimeError(f"Initialization Error: Could not connect to Supabase: {e}")

def get_default_state():
    """Returns a fresh, empty state for a brand new system."""
    return {
        "chunk_memory": [],
        "temporary_memory": [],
        "retrieved_context": [],
        "extracted_memories": [],
        "rag_list": [],
        "memory_intent": [],
        "final_response": "",
        "date_memory": {},
        "auto_ready": False,
        "needs_more_search": False,
        "needs_better_words": False,
        "auto_review_count": 0
    }

def load_state():
    """Loads the state. If Supabase is configured, it enforces Supabase. Otherwise, falls back to local JSON."""
    if SUPABASE_CONFIGURED:
        try:
            res = supabase_client.table("state_store").select("state").eq("id", "default").execute()
            if res.data:
                return res.data[0]["state"]
            else:
                default_state = get_default_state()
                supabase_client.table("state_store").insert({"id": "default", "state": default_state}).execute()
                return default_state
        except Exception as e:
            logger.exception("storage_utils: Failed to load state from Supabase table 'state_store'.")
            raise RuntimeError(f"Database read failure: {e}")

    # Local fallback path: only active if Supabase is not configured
    logger.debug("storage_utils: Supabase not configured. Loading state from local JSON.")
    if not os.path.exists(STATE_FILE):
        return get_default_state()
    
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"storage_utils: State file corrupted. Starting fresh. Error: {e}")
        return get_default_state()

def save_state(state):
    """Saves the state. If Supabase is configured, it enforces Supabase. Otherwise, falls back to local JSON."""
    if SUPABASE_CONFIGURED:
        try:
            supabase_client.table("state_store").upsert({"id": "default", "state": state}).execute()
            return
        except Exception as e:
            logger.exception("storage_utils: Failed to save state to Supabase table 'state_store'.")
            raise RuntimeError(f"Database write failure: {e}")

    # Local fallback path: only active if Supabase is not configured
    logger.debug("storage_utils: Supabase not configured. Saving state to local JSON.")
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.exception("storage_utils: Failed to write state to local file.")
        raise