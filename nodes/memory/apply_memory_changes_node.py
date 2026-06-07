from langchain_core.runnables import RunnableConfig
from graph.state import ManualState
from memory.store_memory import store_memory
from memory.delete_memory import delete_memory
from nodes.memory.memory_utils import is_memory_delete_query

def apply_memory_changes_node(state: ManualState, config: RunnableConfig, *, store):
    """
    Orchestration node that applies updates or removals to the Permanent Memory Profile
    based on the intent classified by the previous node.
    """
    # 1. Grab the extracted text and the intent from your ManualState
    # 'extracted_memories' contains the factual statements or chunks to process
    # 'memory_intent' contains the intent strings (e.g., "store" or "delete")
    extracted_items = state.get("extracted_memories", [])
    intents = state.get("memory_intent", [])

    if not extracted_items:
        print("Apply Memory Changes: No extracted memories found in state to apply.")
        return {"final_response": "No memories were detected to be processed."}

    # 2. Iterate through your extracted memories and pair them with their classified intents
    # In case multiple statements were extracted, we process them sequentially
    is_delete_request = is_memory_delete_query(state.get("user_query", ""))

    for i, chunk in enumerate(extracted_items):
        # Fallback to "store" if your classifier missed an explicit index intent
        current_intent = intents[i] if i < len(intents) else "store"
        
        print(f"Processing memory chunk [{i+1}/{len(extracted_items)}] with intent: '{current_intent}'")

        if current_intent == "delete":
            # Fire your local delete helper
            delete_memory(store=store, deletion_instruction=chunk)
            continue

        if is_delete_request:
            print(f"Skipping store for delete-request query: {chunk}")
            continue

        # Fire your local store/update helper (handles adds and updates via our schema)
        store_memory(store=store, new_memory_chunk=chunk)

    # 3. Return an update to the state indicating the memory action is completed
    return {
        "final_response": f"Successfully processed {len(extracted_items)} permanent memory modification(s)."
    }