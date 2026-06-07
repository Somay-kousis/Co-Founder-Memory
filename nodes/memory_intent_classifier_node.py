from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.memory.check_intent import CLASSIFY_INTENT
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", CLASSIFY_INTENT),
    ("human", "{memory}")
])


def memory_intent_classifier_node(state: ManualState):
    memory_intents = []

    for memory in state["extracted_memories"]:
        prompt = chat_template.invoke({
            "memory": memory
        })

        response = llm.invoke(prompt)

        memory_intents.append(
            response.content.strip().lower()
        )

    return {
        "memory_intent": memory_intents
    }