# nodes/memory/user_memory_extraction_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.memory.user_memory_extraction import GENERATE_MEMORY
from langchain_core.prompts import ChatPromptTemplate
from nodes.memory.memory_utils import is_memory_delete_query
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3, # Slightly lower temperature for objective extraction tracking
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", GENERATE_MEMORY),
    ("human", "--- CURRENT SESSION TRANSCRIPT ---\n{history}\n\nLatest User Input: {topic}")
])

def user_memory_extraction_node(state: ManualState):
    """
    Fixed: Aligned function name with graph router configurations.
    Extracts high-value long-term traits from chat history and user inputs.
    """
    user_query = state.get("user_query", "")

    if is_memory_delete_query(user_query):
        return {
            "extracted_memories": [user_query]
        }

    chat_history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(chat_history_list) if chat_history_list else "No active history."

    prompt = chat_template.invoke({
        "history": formatted_history,
        "topic": user_query
    })

    response = llm.invoke(prompt)

    extracted_memories = [
        memory.strip()
        for memory in response.content.splitlines()
        if memory.strip()
    ]

    return {
        "extracted_memories": extracted_memories
    }