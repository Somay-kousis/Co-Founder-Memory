# nodes/classifier_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.classifier.classify import CLASSIFY_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

# Strict validation schema to protect the primary router edge paths
class QueryClassification(BaseModel):
    query_type: Literal["ask", "memory", "planning"] = Field(
        description="The primary category classification for the user's intent string."
    )

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0) # Lower temp for perfect routing stability
structured_classifier = llm.with_structured_output(QueryClassification)

chat_template = ChatPromptTemplate.from_messages([
    ("system", CLASSIFY_PROMPT),
    ("human", "{topic}")
])

def classifier_node(state: ManualState):
    """
    Evaluates raw user input and guarantees an exact type matching 
    the master graph router's edge rules.
    """
    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    classification = structured_classifier.invoke(prompt)

    print(f"🎯 Classifier Node: Query categorized strictly as '{classification.query_type}'")

    return {
        "query_type": classification.query_type
    }