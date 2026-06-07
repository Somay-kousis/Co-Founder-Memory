from dotenv import load_dotenv

from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.answer import ANSWER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from nodes.memory.temporary_memory_node import append_ai_message
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

# Added slots for permanent user profiles along with historical system summaries
chat_template = ChatPromptTemplate.from_messages([
    ("system", ANSWER_PROMPT),
    ("human", (
        "--- LONG-TERM PROFILE MEMORIES ---\n"
        "{permanent_memories}\n\n"
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

    # 2. Extract and format permanent memory snapshot items from the state
    extracted_memories_list = state.get("extracted_memories") or []
    if not extracted_memories_list:
        formatted_memories = "No long-term memories relevant to this specific topic found."
    else:
        formatted_memories = "\n".join([f"- {memory}" for memory in extracted_memories_list])

    # 3. Invoke prompt template with history, permanent traits, and the fresh query
    prompt = chat_template.invoke({
        "permanent_memories": formatted_memories,
        "history": formatted_history,
        "topic": state["user_query"]
    })

    response = llm.invoke(prompt)

    # 4. Create a state update snapshot for the AI's response string
    updated_state = {
        "final_response": response.content
    }

    # 5. Pass the updated snapshot to your memory manager
    temp_state_snapshot = {**state, **updated_state}
    memory_update = append_ai_message(temp_state_snapshot)
    
    # 6. RETURN EVERYTHING COOL AND IN SYNC
    return {
        "final_response": updated_state["final_response"],
        "temporary_memory": memory_update.get("temporary_memory", []),
        "chunk_memory": memory_update.get("chunk_memory", state.get("chunk_memory", []))
    }