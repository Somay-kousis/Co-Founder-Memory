from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.memory.user_memory_extraction import GENERATE_MEMORY
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", GENERATE_MEMORY),
    ("human", "{topic}")
])


def generate_memory_node(state: ManualState):

    prompt = chat_template.invoke({
        "topic": state["user_query"]
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