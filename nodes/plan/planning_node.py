# nodes/plan/planning_node.py
import json
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.planning.planner import PLANNER_PROMPT
from memory.plan_schema import ProjectPlan
from langchain_core.messages import SystemMessage, HumanMessage
from rag.retrieve_context import retrieve_all_context
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
)
structured_planner = llm.with_structured_output(ProjectPlan)

def planning_node(state: ManualState):
    """
    Generates a structured plan schema, factoring in ongoing chat contexts,
    codebase specifications via RAG, and permanent profile traits.
    """
    user_input = state.get("user_query", "")
    existing_plan_data = state.get("plan") or ""
    
    # 1. Manage strict loop counter tracking
    current_count = state.get("plan_review_count", 0)
    next_count = current_count + 1
    print(f"📋 Planner Executing. Iteration Loop: {next_count}/5")
    
    # 2. Extract external RAG knowledge relevant to the planning topic
    retrieval_data = retrieve_all_context(
        query=user_input, 
        state_memories=state.get("extracted_memories", [])
    )

    # Cleanly format existing plan depending on whether it is stored as an object or string representation
    if existing_plan_data and isinstance(existing_plan_data, dict):
        formatted_existing_plan = json.dumps(existing_plan_data, indent=2)
    elif existing_plan_data:
        formatted_existing_plan = str(existing_plan_data)
    else:
        formatted_existing_plan = "No active plan established yet."

    history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(history_list) if history_list else "No prior history in this session."

    # 3. Build the context injection boundary block
    human_content = (
        f"--- CONVERSATION CONTEXT ---\n{formatted_history}\n\n"
        f"{retrieval_data['formatted_context']}\n\n"
        f"--- CURRENT ACTIVE PLAN ---\n{formatted_existing_plan}\n\n"
        f"--- LATEST USER PLANNING INPUT ---\n{user_input}\n\n"
        "Generate the updated structured ProjectPlan structure."
    )

    updated_plan_object = structured_planner.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=human_content)
    ])

    # Convert object directly to model dump or string matching the system typing constraints
    # If state requires strict string mapping for storage serialization:
    plan_payload = updated_plan_object.model_dump()

    return {
        "plan": plan_payload,
        "plan_review_count": next_count,
        "retrieved_context": retrieval_data["retrieved_context"],
        "final_response": f"I have successfully updated your project plan for **{updated_plan_object.project_name}**."
    }