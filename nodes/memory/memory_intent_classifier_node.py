# nodes/memory/memory_intent_classifier_node.py
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.memory.check_intent import CLASSIFY_INTENT
from langchain_core.prompts import ChatPromptTemplate
from nodes.memory.memory_utils import is_memory_delete_query
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

# Strict intent validation schema
class IntentScore(BaseModel):
    intent: str = Field(description="Must be exactly 'store' or 'delete' based on memory modifications context.")

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
structured_classifier = llm.with_structured_output(IntentScore)

chat_template = ChatPromptTemplate.from_messages([
    ("system", CLASSIFY_INTENT),
    ("human", "Memory statement to evaluate: {memory}")
])

def memory_intent_classifier_node(state: ManualState):
    """
    Evaluates extracted updates against a strict Pydantic structure 
    to guarantee correct execution pathways down the line.
    """
    memory_intents = []
    memories_to_check = state.get("extracted_memories") or []

    for memory in memories_to_check:
        if is_memory_delete_query(memory):
            memory_intents.append("delete")
            continue

        prompt = chat_template.invoke({
            "memory": memory
        })

        decision = structured_classifier.invoke(prompt)
        # Cleanly forces lowercase text strings: 'store' or 'delete'
        memory_intents.append(decision.intent.strip().lower())

    return {
        "memory_intent": memory_intents
    }