# run_manual.py
import os
from graph.main_graph import compiled_main_graph
from graph.auto_graph import compiled_auto_graph
from storage_utils import load_state, save_state  # <-- NEW IMPORT

def test_live_chat():
    print("\n💬 Testing Live Interactive Graph (Production Track)...")
    print("Type 'bye' to exit the session.")

    # 1. Load the REAL state from memory
    state = load_state()

    while True:
        user_query = input("Enter a live user query:\n> ").strip()
        if user_query.lower() == "bye":
            print("\n👋 Ending live chat session. Goodbye!")
            break

        if not user_query:
            print("No query entered. Please type a question or 'bye' to exit.")
            continue

        state["user_query"] = user_query
        
        # 2. Invoke the graph
        result = compiled_main_graph.invoke(state)

        # 3. Update local state variables
        state.update({
            "temporary_memory": result.get("temporary_memory", state.get("temporary_memory", [])),
            "chunk_memory": result.get("chunk_memory", state.get("chunk_memory", [])),
            "extracted_memories": result.get("extracted_memories", state.get("extracted_memories", [])),
            "retrieved_context": result.get("retrieved_context", state.get("retrieved_context", [])),
            "final_response": result.get("final_response", "")
        })

        # 4. Save the REAL state back to disk immediately
        save_state(state)

        print("\n🤖 AI Final Response Output:\n", state["final_response"])
        print("\n---")

def force_test_midnight_loop():
    print("\n🌙 Force-Triggering Automated Background Graph immediately...")
    
    # 1. Load the REAL daily accumulated state instead of the mock
    real_auto_state = load_state()
    
    # 2. Invoke graph using real data
    result = compiled_auto_graph.invoke(real_auto_state)
    
    # 3. Save the resulting processed memories/dossier back
    if result:
        save_state(result)
        
    print("\n📝 Resulting Dossier Generated:\n", result.get("final_response"))

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ Warning: GROQ_API_KEY environment variable missing.")
        
    print("Select a run profile to execute:")
    print("1 -> Test Live User Chat (Manual Graph + Subgraph)")
    print("2 -> Force Run Today's Automation (Auto Graph Loop)")
    
    choice = input("Enter option (1 or 2): ").strip()
    if choice == "1":
        test_live_chat()
    elif choice == "2":
        force_test_midnight_loop()
    else:
        print("Invalid selection.")