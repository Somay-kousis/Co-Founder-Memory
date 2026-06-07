# nodes/subgraph_nodes/grade_documents_node.py
from graph.state import SubGraphState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

class DocumentGrade(BaseModel):
    binary_score: str = Field(
        description="Is the document relevant to the user query? 'yes' or 'no'"
    )

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
structured_grader = llm.with_structured_output(DocumentGrade)

GRADE_PROMPT = """You are an expert technical QA engineer grading the relevance of a retrieved document chunk to a user query.

User Query: {query}
Retrieved Chunk: {document}

If the document contains technical concepts, keywords, or structure relevant to answering the query, output 'yes'. Otherwise, output 'no'."""

def grade_documents_node(state: SubGraphState):
    """
    CRAG Layer: Evaluates retrieved database documents for explicit topic relevance.
    Safely keeps all partially matching data while triggering backup search indicators.
    """
    query = state["user_query"]
    documents = state.get("retrieved_context") or []
    
    run_web_search = False
    valid_documents = []

    print(f"🧐 CRAG: Examining {len(documents)} retrieved document chunks...")

    for doc in documents:
        prompt = ChatPromptTemplate.from_template(GRADE_PROMPT).format(
            query=query, document=doc
        )
        score = structured_grader.invoke(prompt)
        
        if score.binary_score == "yes":
            valid_documents.append(doc)
        else:
            print("⚠️ CRAG: Found an irrelevant document chunk. Flagging fallback search.")
            run_web_search = True  
            # Keep it as fallback asset instead of completely discarding potentially useful structural context
            valid_documents.append(doc)

    # If the system retrieved absolute zero context, force fallback web search automatically
    if not valid_documents:
        run_web_search = True

    return {
        "retrieved_context": valid_documents,
        "run_web_search": run_web_search
    }