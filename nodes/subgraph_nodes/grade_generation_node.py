# nodes/subgraph_nodes/grade_generation_node.py
from graph.state import SubGraphState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

class HallucinationGrade(BaseModel):
    binary_score: str = Field(
        description="Is the generated answer grounded in the provided context? 'yes' or 'no'"
    )

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
structured_grader = llm.with_structured_output(HallucinationGrade)

HALLUCINATION_PROMPT = """You are a critical verification agent checking an LLM response for hallucinations.

Retrieved Context Assets:
{context}

Generated Answer:
{generation}

Determine if the generated answer is completely grounded in, supported by, and derived from the retrieved context assets. Output 'yes' if there are zero hallucinations, and 'no' if the answer brings up unverified or external claims not found in the context."""

def grade_generation_node(state: SubGraphState):
    """
    SRAG Layer: Validates the generated answer against source context blocks to block hallucinations.
    Uses the final response payload directly.
    """
    context = "\n".join(state.get("retrieved_context") or [])
    generation = state.get("final_response") or ""

    print("🛡️ SRAG: Cross-examining final generation for facts/hallucinations...")

    if not generation:
        print("⚠️ SRAG: Empty response payload detected.")
        return {"run_web_search": True}

    prompt = ChatPromptTemplate.from_template(HALLUCINATION_PROMPT).format(
        context=context, generation=generation
    )
    score = structured_grader.invoke(prompt)

    if score.binary_score == "yes":
        print("🟢 SRAG Verification Passed: Generation is fully grounded.")
        # If valid, we leave the state intact so the router can push straight to END
        return {"run_web_search": False}
    else:
        print("⚠️ SRAG Verification Failed: Hallucination detected! Flagging search loop fix.")
        # Re-triggering a web search loop provides fresh grounding facts to resolve the hallucination
        return {"run_web_search": True}