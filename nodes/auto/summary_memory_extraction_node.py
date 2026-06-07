# nodes/auto/summary_memory_extraction_node.py
from graph.state import AutoState
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()

class ExtractedProfileMemories(BaseModel):
    new_memories: List[str] = Field(
        default=[],
        description="A list of newly extracted long-term profile adjustments, core technical stacks, or recurring project tracks."
    )

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
structured_extractor = llm.with_structured_output(ExtractedProfileMemories)

EXTRACTION_PROMPT = """You are a profile intelligence observer. Review the finalized daily operational summary document and pull out any persistent, long-term facts about the user's setup, core stack rules, or project goals.

Exclude temporary chat filler or daily step-by-step tasks. Extract only structural parameters that should be remembered forever.

--- TODAY'S DOCUMENT ---
{document}
"""

def summary_memory_extraction_node(state: AutoState):
    """
    Auto Pipeline Layer: Extracts persistent long-term profile data from 
    the final compiled daily report to keep permanent memory up to date.
    """
    print("🧠 Auto Pipeline: Running long-term fact extraction on today's report...")
    doc_text = state.get("final_response") or ""
    
    if not doc_text:
        return {}
        
    extracted = structured_extractor.invoke([
        SystemMessage(content=EXTRACTION_PROMPT.format(document=doc_text)),
        HumanMessage(content="Extract any high-value persistent facts.")
    ])
    
    current_memories = state.get("extracted_memories") or []
    updated_memories = current_memories + extracted.new_memories
    
    print(f"🟢 Fact Extractor: Discovered {len(extracted.new_memories)} persistent profile constraints.")
    return {
        "extracted_memories": updated_memories
    }