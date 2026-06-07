# nodes/memory/temporary_memory_node.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from graph.state import ManualState
from dotenv import load_dotenv
load_dotenv()

chunk_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

chunk_summarizer_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are the Session Compression Engine for Co-Founder's Memory.\n\n"
        "Your task is to take a raw conversation transcript slice and compress it into "
        "a list of highly dense, standalone factual summaries or key updates.\n\n"
        "Output Rules:\n"
        "- Return each dense summary chunk on a new line.\n"
        "- Do NOT use bullets, numbers, hyphens, or markdown syntax.\n"
        "- Separate each chunk using standard newlines."
    )),
    ("human", "--- RAW SESSION TRANSCRIPT SLICE ---\n{transcript}")
])

def append_user_message(state: ManualState) -> dict:
    """
    Safely captures user text into a fresh, non-mutated array slice
    and handles automatic sliding window compressions seamlessly.
    """
    # Create local swallow copies to shield graph state stability
    current_temp = list(state.get("temporary_memory") or [])
    current_chunks = list(state.get("chunk_memory") or [])
    user_query = state.get("user_query", "")
    
    if user_query:
        current_temp.append(f"Human: {user_query}")
        
    if len(current_temp) >= 55:
        print(f"Temporary Memory: Buffer reached {len(current_temp)} entries. Automating slice compression...")
        
        oldest_50_slice = current_temp[:50]
        latest_5_preserved = current_temp[50:]
        
        transcript_block = "\n".join(oldest_50_slice)
        prompt = chunk_summarizer_template.invoke({"transcript": transcript_block})
        response = chunk_llm.invoke(prompt)
        
        extracted_summary_lines = [
            line.strip()
            for line in response.content.splitlines()
            if line.strip()
        ]
        
        updated_chunks = current_chunks + extracted_summary_lines
        bookmark_entry = "SYSTEM: Older segments of this chat thread have been compressed and archived to permanent memory."
        new_temp_buffer = [bookmark_entry] + latest_5_preserved
        
        return {
            "temporary_memory": new_temp_buffer,
            "chunk_memory": updated_chunks
        }
        
    return {
        "temporary_memory": current_temp
    }

def append_ai_message(state: ManualState) -> dict:
    """Safely appends AI answers into fresh local variables."""
    current_temp = list(state.get("temporary_memory") or [])
    final_response = state.get("final_response", "")
    
    if final_response:
        current_temp.append(f"AI: {final_response}")
        
    return {
        "temporary_memory": current_temp
    }