import json
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.planning.plan_reviewer import PLAN_REVIEWER_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,  # Low temperature ensures strict, analytical evaluation
)

def plan_review_node(state: ManualState):
    """
    Evaluates the newly generated plan in the state using the structural prompt,
    parses the decision criteria, and sets plan_ready for the loop-cap router.
    """
    current_plan_data = state.get("plan") or {}
    
    if not current_plan_data:
        print("Plan Review Node: No plan found in state to review.")
        return {
            "final_response": "I tried to review the project plan, but no active plan was found in the state.",
            "plan_ready": False
        }

    # Format the plan cleanly as JSON for the review window
    formatted_plan = json.dumps(current_plan_data, indent=2)

    # Invoke the reviewer model
    review_response = llm.invoke([
        SystemMessage(content=PLAN_REVIEWER_PROMPT),
        HumanMessage(content=f"Please review this project plan profile:\n\n{formatted_plan}")
    ])

    review_text = review_response.content.strip()
    
    # Parse the structural keywords from the updated prompt criteria
    if "plan_ready: True" in review_text:
        print("Plan Review Node: Plan successfully APPROVED by architect.")
        clean_feedback = review_text.replace("plan_ready: True", "").strip()
        
        user_display = (
            f"{state.get('final_response', '')}\n\n"
            f"### 🛡️ Architect Review (Approved)\n{clean_feedback}"
        )
        return {
            "plan_review": clean_feedback,
            "plan_ready": True,
            "final_response": user_display
        }
    else:
        print("Plan Review Node: Plan REVISION_NEEDED. Routing back for adjustments.")
        clean_feedback = review_text.replace("plan_ready: False", "").strip()
        
        user_display = (
            f"The proposed plan needs adjustment before execution:\n\n{clean_feedback}"
        )
        return {
            "plan_review": clean_feedback,
            "plan_ready": False,
            "final_response": user_display
        }