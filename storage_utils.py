# storage_utils.py
import json
import os
from supabase import create_client, Client

STATE_FILE = "live_memory_state.json"

# Initialize Supabase client if credentials exist
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

supabase_client = None
if url and key:
    try:
        supabase_client = create_client(url, key)
        print("storage_utils: Connected to Supabase for state storage.")
    except Exception as e:
        print(f"storage_utils Warning: Could not initialize Supabase client: {e}")

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
    """Loads the real state from Supabase or disk fallback. If none exists, starts fresh."""
    if supabase_client:
        try:
            res = supabase_client.table("state_store").select("state").eq("id", "default").execute()
            if res.data:
                return res.data[0]["state"]
            else:
                # Insert default state
                default_state = get_default_state()
                supabase_client.table("state_store").insert({"id": "default", "state": default_state}).execute()
                return default_state
        except Exception as e:
            print(f"storage_utils: Supabase load_state error, falling back to local file. Error: {e}")

    # Fallback to local file
    if not os.path.exists(STATE_FILE):
        return get_default_state()
    
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Warning: State file corrupted. Starting fresh.")
        return get_default_state()

def save_state(state):
    """Saves the current real state to Supabase or disk fallback."""
    if supabase_client:
        try:
            supabase_client.table("state_store").upsert({"id": "default", "state": state}).execute()
            # Also sync to local file for backup/development
            try:
                with open(STATE_FILE, "w") as f:
                    json.dump(state, f, indent=4)
            except Exception:
                pass
            return
        except Exception as e:
            print(f"storage_utils: Supabase save_state error, falling back to local file. Error: {e}")

    # Fallback to local file
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)