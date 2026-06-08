# storage_utils.py
import json
import os

STATE_FILE = "live_memory_state.json"

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
    """Loads the real state from disk. If none exists, starts fresh."""
    if not os.path.exists(STATE_FILE):
        return get_default_state()
    
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Warning: State file corrupted. Starting fresh.")
        return get_default_state()

def save_state(state):
    """Saves the current real state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)