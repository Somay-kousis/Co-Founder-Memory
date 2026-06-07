# nodes/plan/plan_review_node.py
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
    parses the decision criteria, and sets plan_ready.
    """
    current_plan_data = state.get("plan") or ""
    current_count = state.get("plan_review_count", 0)
    
    if not current_plan_data:
        print("Plan Review Node: No plan found in state to review.")
        return {
            "final_response": "I tried to review the project plan, but no active plan was found in the state.",
            "plan_ready": False,
            "plan_review_count": current_count
        }

    # If plan data is passed as a string representation, ensure it handles formatting gracefully
    if isinstance(current_plan_data, dict):
        formatted_plan = json.dumps(current_plan_data, indent=2)
    else:
        formatted_plan = str(current_plan_data)

    # Invoke the reviewer model
    review_response = llm.invoke([
        SystemMessage(content=PLAN_REVIEWER_PROMPT),
        HumanMessage(content=f"Please review this project plan profile:\n\n{formatted_plan}")
    ])

    review_text = review_response.content.strip()
    
    # Parse the structural keywords and return strict booleans matching the router logic
    if "plan_ready: True" in review_text:
        print(f"🛡️ Plan Review Node: Plan APPROVED by architect on loop iteration {current_count}.")
        clean_feedback = review_text.replace("plan_ready: True", "").strip()
        
        user_display = (
            f"{state.get('final_response', '')}\n\n"
            f"### 🛡️ Architect Review (Approved)\n{clean_feedback}"
        )
        return {
            "plan_review": clean_feedback,
            "plan_ready": True,  # Using a boolean to keep route_plan_review functional
            "final_response": user_display,
            "plan_review_count": current_count
        }
    else:
        print(f"⚠️ Plan Review Node: Plan REVISION_NEEDED on loop iteration {current_count}.")
        clean_feedback = review_text.replace("plan_ready: False", "").strip()
        
        user_display = (
            f"The proposed plan needs adjustment before execution:\n\n{clean_feedback}"
        )
        return {
            "plan_review": clean_feedback,
            "plan_ready": False,  # Strict boolean flag
            "final_response": user_display,
            "plan_review_count": current_count
        }