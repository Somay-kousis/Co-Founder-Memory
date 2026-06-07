# run_manual.py
import os
from graph.main_graph import compiled_main_graph
from graph.auto_graph import compiled_auto_graph

def test_live_chat():
    print("\n💬 Testing Live Interactive Graph (Manual Track)...")
    print("Type 'bye' to exit the session.")

    state = {
        "temporary_memory": [
            "Human: Hey, let's make sure our database choice doesn't need cloud tokens.",
            "AI: Sounds good. We should store everything in local Chroma vectors to keep it free."
        ],
        "extracted_memories": ["User values offline-first privacy controls."],
        "chunk_memory": [],
        "date_memory": {},
        "rag_list": [],
        "retrieved_context": [],
        "memory_intent": [],
        "final_response": ""
    }

    while True:
        user_query = input("Enter a live user query:\n> ").strip()
        if user_query.lower() == "bye":
            print("\n👋 Ending live chat session. Goodbye!")
            break

        if not user_query:
            print("No query entered. Please type a question or 'bye' to exit.")
            continue

        state["user_query"] = user_query
        result = compiled_main_graph.invoke(state)

        # Keep state transitions so the session maintains history context.
        state.update({
            "temporary_memory": result.get("temporary_memory", state.get("temporary_memory", [])),
            "chunk_memory": result.get("chunk_memory", state.get("chunk_memory", [])),
            "extracted_memories": result.get("extracted_memories", state.get("extracted_memories", [])),
            "retrieved_context": result.get("retrieved_context", state.get("retrieved_context", [])),
            "final_response": result.get("final_response", "")
        })

        print("\n🤖 AI Final Response Output:\n", state["final_response"])
        print("\n---")

def force_test_midnight_loop():
    print("\n🌙 Force-Triggering Automated Background Graph immediately...")
    
    mock_auto_state = {
        "chunk_memory": [
            "User resolved C++ segment fault errors by cleaning build logs",
            "User plans to join Smart India Hackathon next season"
        ],
        "temporary_memory": [],
        "retrieved_context": [],
        "extracted_memories": [],
        "final_response": "",
        "date_memory": {},
        "auto_ready": False,
        "needs_more_search": False,
        "needs_better_words": False,
        "auto_review_count": 0
    }
    
    result = compiled_auto_graph.invoke(mock_auto_state)
    print("\n📝 Resulting Dossier Generated:\n", result.get("final_response"))

if __name__ == "__main__":
    # Ensure your keys are in environment before starting
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