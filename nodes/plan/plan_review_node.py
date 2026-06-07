import json
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.planning.plan_reviewer import PLAN_REVIEWER_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2, # Low temperature ensures strict, analytical evaluation
)

def plan_review_node(state: ManualState):
    """
    Evaluates the newly generated plan in the state, provides critical architect 
    feedback, and flags whether the plan is APPROVED or needs REVISION.
    """
    current_plan_data = state.get("plan") or {}
    
    if not current_plan_data:
        print("Plan Review Node: No plan found in state to review.")
        return {
            "final_response": "I tried to review the project plan, but no active plan was found in the state."
        }

    # Format the plan cleanly as JSON for the review window
    formatted_plan = json.dumps(current_plan_data, indent=2)

    # Invoke the reviewer model
    review_response = llm.invoke([
        SystemMessage(content=PLAN_REVIEWER_PROMPT),
        HumanMessage(content=f"Please review this project plan profile:\n\n{formatted_plan}")
    ])

    review_text = review_response.content.strip()
    
    # Check the structural approval keywords
    if review_text.startswith("APPROVED"):
        print("Plan Review Node: Plan successfully APPROVED by architect.")
        # If approved, append the architect's commentary to our final UI response
        user_display = (
            f"{state.get('final_response', '')}\n\n"
            f"### 🛡️ Architect Review\n{review_text.replace('APPROVED', '').strip()}"
        )
        return {
            "final_response": user_display,
            # We can use this custom key dynamically in a conditional router edge later
            "plan_review_status": "approved" 
        }
    else:
        print("Plan Review Node: Plan REVISION_NEEDED. Routing back for adjustments.")
        return {
            "final_response": f"The proposed plan needs adjustment before execution:\n\n{review_text.replace('REVISION_NEEDED', '').strip()}",
            "plan_review_status": "revision_needed"
        }