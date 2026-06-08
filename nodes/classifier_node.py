# nodes/classifier_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.classifier.classify import CLASSIFY_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

# Strict validation schema to protect the primary router edge paths
class QueryClassification(BaseModel):
    query_type: Literal["ask", "memory", "planning"] = Field(
        description="The primary category classification for the user's intent string."
    )

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0) # Lower temp for perfect routing stability
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
    query = state.get("user_query", "").strip().lower()
    
    # Heuristics: Route informational queries (questions about what is stored/remembered) to 'ask'
    asking_words = ["what", "how", "who", "where", "why", "can", "do", "list", "show", "tell", "display", "retrieve", "are", "is", "have", "which", "describe"]
    memory_words = ["remember", "memory", "memories", "stored", "saved", "project", "decision", "principle", "preference", "vault", "milestone", "dossier", "log", "fact"]
    
    if any(query.startswith(w) for w in asking_words) and any(m in query for m in memory_words):
        print(f"🎯 Heuristic Classifier: Routed query '{state['user_query']}' strictly to 'ask' based on question pattern.")
        return {
            "query_type": "ask"
        }

    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    classification = structured_classifier.invoke(prompt)

    print(f"🎯 Classifier Node: Query categorized strictly as '{classification.query_type}'")

    return {
        "query_type": classification.query_type
    }