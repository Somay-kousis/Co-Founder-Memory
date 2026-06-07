# nodes/auto/generate_doc_node.py
from graph.state import AutoState
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.auto.doc_generator import DOC_GENERATOR_PROMPT
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

def generate_doc_node(state: AutoState):
    """
    Auto Pipeline Layer: Takes all collected research, intelligence hits, 
    and weekly background items to build a beautifully structured technical summary document.
    """
    print("📝 Auto Pipeline: Compiling raw research streams into structured Markdown documentation...")

    # 1. Gather all raw context items and web data from the state array
    retrieved_list = state.get("retrieved_context") or []
    if not retrieved_list:
        combined_context = "No background assets or search results were collected today."
    else:
        combined_context = "\n\n=== ASSET ===\n".join(retrieved_list)

    # 2. Invoke the document engine
    response = llm.invoke([
        SystemMessage(content=DOC_GENERATOR_PROMPT.format(retrieved_context=combined_context)),
        HumanMessage(content="Compile these assets into the finalized structural markdown document layout.")
    ])

    print("🟢 Doc Generator: Dossier successfully compiled and saved to state pipeline.")

    # 3. Store the markdown document inside final_response so auto_review_node can audit it next
    return {
        "final_response": response.content
    }