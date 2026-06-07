import json
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.planning.planner import PLANNER_PROMPT
from memory.plan_schema import ProjectPlan
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
)
structured_planner = llm.with_structured_output(ProjectPlan)

def planning_node(state: ManualState):
    user_input = state.get("user_query", "")
    existing_plan_data = state.get("plan") or {}
    
    # 1. Fetch and increment loop counter
    current_count = state.get("plan_review_count", 0)
    next_count = current_count + 1
    print(f"📋 Planner Executing. Iteration Loop: {next_count}/5")
    
    formatted_existing_plan = json.dumps(existing_plan_data, indent=2) if existing_plan_data else "No active plan established yet."
    history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(history_list) if history_list else "No prior history in this session."

    human_content = (
        f"--- CONVERSATION CONTEXT ---\n{formatted_history}\n\n"
        f"--- CURRENT ACTIVE PLAN ---\n{formatted_existing_plan}\n\n"
        f"--- LATEST USER PLANNING INPUT ---\n{user_input}\n\n"
        "Generate the updated structured ProjectPlan structure."
    )

    updated_plan_object = structured_planner.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=human_content)
    ])

    return {
        "plan": updated_plan_object.model_dump(),
        "plan_review_count": next_count,  # Overwrite counter in global state
        "final_response": f"I have successfully updated your project plan for **{updated_plan_object.project_name}**."
    }