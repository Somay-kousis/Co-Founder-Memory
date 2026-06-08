# nodes/ask/ask_retrieval_decision_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.retrieval_decision import RETRIVAL_REVIEW_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

class RetrievalDecision(BaseModel):
    should_retrieve: bool = Field(
        description="True if the query requires technical code context, file specs, or library configurations. False for general chatter."
    )

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0) # Lower temperature for classification stability
structured_classifier = llm.with_structured_output(RetrievalDecision)

chat_template = ChatPromptTemplate.from_messages([
    ("system", RETRIVAL_REVIEW_PROMPT),
    ("human", "{topic}")
])

def ask_retrieval_decision_node(state: ManualState):
    """
    Evaluates if the query needs a Vector DB lookup and outputs a strict boolean.
    """
    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    decision = structured_classifier.invoke(prompt)

    return {
        "ask_retrieval_decision": decision.should_retrieve
    }