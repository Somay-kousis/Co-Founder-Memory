# graph/main_graph.py
from langgraph.graph import StateGraph, START, END
from graph.state import ManualState
from graph.routes import route_query, route_ask_retrieval, route_plan_review

# Import Core Live Chat & Strategy Nodes
from nodes.classifier_node import classifier_node
from nodes.ask.ask_node import ask_node
from nodes.ask.ask_retrieval_decision_node import ask_retrieval_decision_node
from nodes.plan.planning_node import planning_node
from nodes.plan.plan_review_node import plan_review_node

# Import Durable Memory Profile Managers
from nodes.memory.user_memory_extraction_node import user_memory_extraction_node
from nodes.memory.memory_intent_classifier_node import memory_intent_classifier_node
from nodes.memory.apply_memory_changes_node import apply_memory_changes_node

# Import our compiled Self-Correcting CRAG/SRAG Subgraph
from graph.subgraph import compiled_rag_subgraph

# 1. Initialize the Master State Machine with ManualState
workflow = StateGraph(ManualState)

# ====================================================================
# 📁 NODE REGISTRATION
# ====================================================================

# Intent Gatekeeper
workflow.add_node("classifier_node", classifier_node)

# Conversational & Context Tracks
workflow.add_node("ask_node", ask_node)
workflow.add_node("ask_retrieval_decision_node", ask_retrieval_decision_node)
# Inject the compiled CRAG/SRAG subgraph to act as the full ask_rag_node process block
workflow.add_node("ask_rag_node", compiled_rag_subgraph)

# Iterative Planning Loops
workflow.add_node("planning_node", planning_node)
workflow.add_node("plan_review_node", plan_review_node)

# Permanent Memory Modifications
workflow.add_node("user_memory_extraction_node", user_memory_extraction_node)
workflow.add_node("memory_intent_classifier_node", memory_intent_classifier_node)
workflow.add_node("apply_memory_changes_node", apply_memory_changes_node)

# ====================================================================
# 🚀 CONDITIONAL GRAPH ROUTING
# ====================================================================

# Live execution begins by categorizing user intent
workflow.add_edge(START, "classifier_node")

# Route the conversation path dynamically based on classification outcome
workflow.add_conditional_edges(
    "classifier_node",
    route_query,
    {
        "ask_retrieval_decision_node": "ask_retrieval_decision_node",
        "planning_node": "planning_node",
        "user_memory_extraction_node": "user_memory_extraction_node",
        END: END
    }
)

# --- TRACK A: LIVE CHAT & CONTEXT RETRIEVAL ---
workflow.add_conditional_edges(
    "ask_retrieval_decision_node",
    route_ask_retrieval,
    {
        "ask_rag_node": "ask_rag_node",  # Branches straight into our self-correcting subgraph loop!
        "ask_node": "ask_node"           # Basic chat thread fallback path
    }
)

# Chat outputs terminate execution cleanly
workflow.add_edge("ask_node", END)
workflow.add_edge("ask_rag_node", END)

# --- TRACK B: CRITIQUE-DRIVEN PROJECT PLANNING ---
workflow.add_edge("planning_node", "plan_review_node")

workflow.add_conditional_edges(
    "plan_review_node",
    route_plan_review,
    {
        "planning_node": "planning_node", # Loop Back: Architect requested structural revisions
        END: END                          # Approved or Loop safety cap limit hit
    }
)

# --- TRACK C: DURABLE STORAGE MODIFICATIONS ---
workflow.add_edge("user_memory_extraction_node", "memory_intent_classifier_node")
workflow.add_edge("memory_intent_classifier_node", "apply_memory_changes_node")
workflow.add_edge("apply_memory_changes_node", END)

# ====================================================================
# 🏁 SYSTEM COMPILED RUNNABLE ASSET
# ====================================================================
compiled_main_graph = workflow.compile()