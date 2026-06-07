from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.answer import ANSWER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from nodes.memory.temporary_memory_node import append_ai_message

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

# Added an explicit tip to the LLM so it knows how to handle the background system bookmarks
chat_template = ChatPromptTemplate.from_messages([
    ("system", ANSWER_PROMPT),
    ("human", (
        "--- CURRENT CONVERSATION HISTORY ---\n"
        "Note: History may begin with a 'SYSTEM:' summary representing older compressed segments.\n\n"
        "{history}\n\n"
        "Latest User Input: {topic}"
    ))
])


def ask_node(state: ManualState):
    # 1. Format the ongoing transcript for the LLM context layer
    chat_history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(chat_history_list) if chat_history_list else "No prior history in this session."

    # 2. Invoke prompt template with history and the fresh query
    prompt = chat_template.invoke({
        "history": formatted_history,
        "topic": state["user_query"]
    })

    response = llm.invoke(prompt)

    # 3. Create a state update snapshot for the AI's response string
    updated_state = {
        "final_response": response.content
    }

    # 4. Pass the updated snapshot to your memory manager
    temp_state_snapshot = {**state, **updated_state}
    memory_update = append_ai_message(temp_state_snapshot)
    
    # 5. RETURN EVERYTHING COOL AND IN SYNC
    # We include 'chunk_memory' here so that if the window triggered an archive step,
    # those precious compressed facts are safely preserved back into the graph state.
    return {
        "final_response": updated_state["final_response"],
        "temporary_memory": memory_update.get("temporary_memory", []),
        "chunk_memory": memory_update.get("chunk_memory", state.get("chunk_memory", []))
    }