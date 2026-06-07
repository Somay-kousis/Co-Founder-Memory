from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.answer import ANSWER_PROMPT
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", ANSWER_PROMPT),
    ("human", "{topic}")
])


def ask_node(state: ManualState):
    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    response = llm.invoke(prompt)

    return {
        "final_response": response.content
    }