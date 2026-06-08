# nodes/auto/auto_review_node.py
from graph.state import AutoState
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from prompts.auto.auto_reviewer import AUTO_REVIEWER_PROMPT
from dotenv import load_dotenv
load_dotenv()

# Unique local schema structure for the quality assurance controller
class AutoReviewDecision(BaseModel):
    needs_more_search: bool = Field(
        description="Set to True if facts, deadlines, URLs, or deep contextual metrics are missing and need a secondary web search loop."
    )
    needs_better_words: bool = Field(
        description="Set to True if the text formatting is messy, chaotic, or lacks a professional, high-density technical vocabulary."
    )
    review_feedback: str = Field(
        description="Detailed, raw commentary outlining exactly what elements are missing or what structural parts need editing."
    )

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
structured_reviewer = llm.with_structured_output(AutoReviewDecision)

def auto_review_node(state: AutoState):
    """
    Auto Pipeline Layer: Critiques the compiled dossier, tracks loop caps,
    and handles dynamic self-correction flags for search or polish loops.
    """
    # 1. Increment loop counter protection variable to avoid infinite cycles
    current_count = state.get("auto_review_count", 0)
    next_count = current_count + 1
    print(f"🔄 Auto Review Node: Critiques Executing. Iteration Loop: {next_count}/5")

    generated_doc = state.get("final_response", "")

    if not generated_doc:
        print("⚠️ Auto Review Node: No generated document found in state to evaluate.")
        return {
            "auto_ready": True,
            "needs_more_search": False,
            "needs_better_words": False,
            "auto_review_count": next_count
        }

    # 2. Invoke structured reviewer to get strict boolean parameters
    critique = structured_reviewer.invoke([
        SystemMessage(content=AUTO_REVIEWER_PROMPT.format(document=generated_doc)),
        HumanMessage(content="Evaluate the document text and produce the structured quality metrics decision.")
    ])

    print(f"📋 Critic Verdict -> Needs Search: {critique.needs_more_search} | Needs Polish: {critique.needs_better_words}")
    print(f"💬 Critic Commentary: {critique.review_feedback}")

    # 3. Apply hard cap loop enforcement boundary
    if next_count >= 5:
        print("🚨 Auto Loop Cap Limit Hit! Forcing immediate pipeline finalization to save tokens.")
        return {
            "auto_ready": True,
            "needs_more_search": False,
            "needs_better_words": False,
            "auto_review_count": next_count
        }

    # Determine if the document is completely solid or needs re-routing
    is_auto_ready = not (critique.needs_more_search or critique.needs_better_words)

    return {
        "needs_more_search": critique.needs_more_search,
        "needs_better_words": critique.needs_better_words,
        "auto_ready": is_auto_ready,
        "auto_review_count": next_count,
        # Preserve the feedback commentary in state so downstream nodes can read it to correct mistakes
        "review_feedback": critique.review_feedback 
    }