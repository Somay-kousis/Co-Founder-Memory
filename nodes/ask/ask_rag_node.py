# nodes/ask/ask_rag_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.answer import ANSWER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from rag.retrieve_context import retrieve_all_context
from nodes.memory.temporary_memory_node import append_ai_message
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", ANSWER_PROMPT),
    ("human", (
        "--- CURRENT CONVERSATION HISTORY ---\n"
        "{history}\n\n"
        "{context_block}\n\n"
        "Latest User Input: {topic}"
    ))
])

def ask_rag_node(state: ManualState):
    """
    Executes deep retrieval across Chroma and permanent memory profiles, 
    injecting relevant background constraints before answering.
    """
    user_query = state.get("user_query", "")
    
    # 1. Pull the self-cleaning historical chat buffer
    chat_history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(chat_history_list) if chat_history_list else "No prior history in this session."

    # 2. Fetch both Chroma chunks and permanent profile tracking items
    retrieval_data = retrieve_all_context(
        query=user_query, 
        state_memories=state.get("extracted_memories", [])
    )

    print("🔍 Ask RAG Node: Successfully injected combined Vector DB and Profile context.")

    # 3. Fire the context-weighted prompt execution
    prompt = chat_template.invoke({
        "history": formatted_history,
        "context_block": retrieval_data["formatted_context"],
        "topic": user_query
    })

    response = llm.invoke(prompt)

    # 4. Create a state update snapshot for the AI's response string
    updated_state = {
        "final_response": response.content
    }

    # 5. Pass the updated snapshot to your memory manager to sync chat windows
    temp_state_snapshot = {**state, **updated_state}
    memory_update = append_ai_message(temp_state_snapshot)

    return {
        "final_response": updated_state["final_response"],
        "retrieved_context": retrieval_data["retrieved_context"],
        "temporary_memory": memory_update.get("temporary_memory", []),
        "chunk_memory": memory_update.get("chunk_memory", state.get("chunk_memory", []))
    }