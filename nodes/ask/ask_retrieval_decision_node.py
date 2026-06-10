# nodes/ask/ask_retrieval_decision_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.ask.retrieval_decision import RETRIVAL_REVIEW_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging
import re
load_dotenv()

logger = logging.getLogger("co_founder_memory.retrieval_decision")

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

RETRIEVAL_HINTS = (
    "rag",
    "memory",
    "remember",
    "recall",
    "project",
    "projects",
    "roadmap",
    "decision",
    "decisions",
    "profile",
    "context",
    "what did i",
    "what am i",
    "my ",
    "our ",
)

GENERAL_KNOWLEDGE_HINTS = (
    "what is ",
    "explain ",
    "define ",
    "how does ",
)


def fallback_retrieval_decision(query: str) -> bool:
    normalized = re.sub(r"\s+", " ", query.lower()).strip()
    if any(hint in normalized for hint in RETRIEVAL_HINTS):
        return True
    if any(normalized.startswith(hint) for hint in GENERAL_KNOWLEDGE_HINTS):
        return False
    # Safer failure mode: retrieve context instead of pretending we know nothing.
    return True

def ask_retrieval_decision_node(state: ManualState):
    """
    Evaluates if the query needs a Vector DB lookup and outputs a strict boolean.
    """
    prompt = chat_template.invoke({
        "topic": state["user_query"]
    })

    try:
        decision = structured_classifier.invoke(prompt)
        should_retrieve = decision.should_retrieve
    except Exception as exc:
        logger.warning("Structured retrieval decision failed; using fallback classifier. Error: %s", exc)
        should_retrieve = fallback_retrieval_decision(state["user_query"])

    return {
        "ask_retrieval_decision": should_retrieve
    }
