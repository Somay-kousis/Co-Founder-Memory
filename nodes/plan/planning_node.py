import json
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.planning.planner import PLANNER_PROMPT
from memory.plan_schema import ProjectPlan
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3, # Low temperature ensures strict structural consistency
)
# Force the LLM to conform exactly to our structured Pydantic layout
structured_planner = llm.with_structured_output(ProjectPlan)

def planning_node(state: ManualState):
    """
    Evaluates the ongoing conversation, extracts project targets, and 
    generates or modifies the structured project plan within the graph state.
    """
    user_input = state.get("user_query", "")
    
    # In your full state, you can map 'plan' as a dictionary slot or string. 
    # Let's check if there's an existing plan in the state, fallback to empty if not.
    existing_plan_data = state.get("plan") or {}
    
    # Format current plan state as readable JSON for the context window
    formatted_existing_plan = json.dumps(existing_plan_data, indent=2) if existing_plan_data else "No active plan established yet."

    # Gather conversational context from our self-cleaning temporary memory log
    history_list = state.get("temporary_memory") or []
    formatted_history = "\n".join(history_list) if history_list else "No prior history in this session."

    # Build the context prompt
    human_content = (
        f"--- CONVERSATION CONTEXT ---\n{formatted_history}\n\n"
        f"--- CURRENT ACTIVE PLAN ---\n{formatted_existing_plan}\n\n"
        f"--- LATEST USER PLANNING INPUT ---\n{user_input}\n\n"
        "Generate the updated structured ProjectPlan structure."
    )

    # Invoke the structured planner
    updated_plan_object = structured_planner.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=human_content)
    ])

    print(f"Planning Node: Plan successfully updated for project '{updated_plan_object.project_name}' with {len(updated_plan_object.tasks)} tracking tasks.")

    # Convert the Pydantic model straight back to a dictionary to pass cleanly through the state
    return {
        "plan": updated_plan_object.model_dump(),
        "final_response": f"I have successfully updated your project plan for **{updated_plan_object.project_name}**. Immediate milestone: *{updated_plan_object.current_milestone}*."
    }