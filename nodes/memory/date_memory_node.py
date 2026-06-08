from datetime import datetime
from graph.state import ManualState
from langchain_groq import ChatGroq
from prompts.memory.date_compiler import DATE_COMPILER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,  # Low temperature guarantees factual history tracking
)

chat_template = ChatPromptTemplate.from_messages([
    ("system", DATE_COMPILER_PROMPT),
    ("human", "--- ATOMIC SUMMARY CHUNKS RECENTLY EXTRACTED ---\n{chunks}")
])

def date_memory_node(state: ManualState):
    """
    Takes accumulated items from chunk_memory, synthesizes them into a 
    unified daily narrative, and updates the date_memory history dictionary.
    """
    # 1. Grab current accumulated chunks
    chunks = state.get("chunk_memory", [])
    current_date_dict = state.get("date_memory") or {}

    if not chunks:
        print("Date Memory Node: No chunks available to compile for the day.")
        return {"date_memory": current_date_dict}

    # 2. Format the chunk list as a clean text block for the LLM
    formatted_chunks = "\n".join([f"- {c}" for c in chunks])

    # 3. Invoke the timeline synthesis compiler
    prompt = chat_template.invoke({
        "chunks": formatted_chunks
    })
    
    response = llm.invoke(prompt)

    # 4. Generate the current date string to use as our dictionary key (YYYY-MM-DD format)
    today_key = datetime.now().strftime("%Y-%m-%d")

    # 5. Append or update the specific day's record inside our dictionary layout
    # We copy the dictionary to prevent mutating state directly outside LangGraph transitions
    updated_date_memory = dict(current_date_dict)
    updated_date_memory[today_key] = response.content.strip()

    print(f"Date Memory Node: Successfully compiled daily journal record for key: '{today_key}'.")

    # Return the dictionary update along with clearing out the raw chunk buffer 
    # since they have now been safely archived into a timeline entry.
    return {
        "date_memory": updated_date_memory,
        "chunk_memory": []  # Flush the temporary buffer clean
    }