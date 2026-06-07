# run_manual.py
import os
from graph.main_graph import compiled_main_graph
from graph.auto_graph import compiled_auto_graph

def test_live_chat():
    print("\n💬 Testing Live Interactive Graph (Manual Track)...")
    
    # Simulate a user asking about a past strategic choice
    sample_state = {
        "user_query": "What did I decide about using local DB for Co-Founder's Memory?",
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
    
    result = compiled_main_graph.invoke(sample_state)
    print("\n🤖 AI Final Response Output:\n", result.get("final_response"))

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