# nodes/auto/auto_context_node.py
import json
from datetime import datetime, timedelta
from graph.state import AutoState
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.auto.context_distiller import AUTO_CONTEXT_PROMPT

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

def auto_context_node(state: AutoState):
    """
    Auto Pipeline Layer: Compiles the past 7 days of timeline history 
    and long-term memories to establish an operational overview.
    """
    print("🌙 Auto Pipeline: Distilling operational context from the past week...")
    
    # 1. Gather and filter date_memory timeline logs for the last 7 days
    date_memory_dict = state.get("date_memory") or {}
    recent_entries = []
    
    # Calculate a 7-day lookback window based on today's tracking date
    today = datetime.now()
    for i in range(7):
        target_date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if target_date_str in date_memory_dict:
            recent_entries.append(f"[{target_date_str}]: {date_memory_dict[target_date_str]}")
            
    formatted_timeline = "\n".join(recent_entries) if recent_entries else "No timeline entries recorded in the last 7 days."

    # 2. Extract long-term profile data already cached in the state
    permanent_list = state.get("extracted_memories") or []
    formatted_permanents = "\n".join([f"- {m}" for m in permanent_list]) if permanent_list else "No persistent profile rules loaded."

    # 3. Fire the context compiler
    response = llm.invoke([
        SystemMessage(content=AUTO_CONTEXT_PROMPT.format(
            recent_timeline=formatted_timeline,
            permanent_memories=formatted_permanents
        )),
        HumanMessage(content="Analyze the files and compile the current operational context briefing.")
    ])

    # 4. Save the compiled overview directly into your state context list
    updated_context = state.get("retrieved_context") or []
    updated_context.append(f"[Auto System Operational Context]:\n{response.content}")

    return {
        "retrieved_context": updated_context
    }