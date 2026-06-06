from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.classifier.classify import CLASSIFY_PROMPT
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", CLASSIFY_PROMPT),
    ("human", "{topic}")
])


def classifier_node(state: ManualState):

    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    response = llm.invoke(prompt)

    return {
    "query_type": response.content.strip().lower()
}