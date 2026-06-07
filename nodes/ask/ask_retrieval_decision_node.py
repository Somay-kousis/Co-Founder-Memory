from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.retrieval_decision import RETRIVAL_REVIEW_PROMPT
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", RETRIVAL_REVIEW_PROMPT),
    ("human", "{topic}")
])


def cask_retrieval_decision_node(state: ManualState):

    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    response = llm.invoke(prompt)

    return {
    "ask_retrieval_decision" : response
}