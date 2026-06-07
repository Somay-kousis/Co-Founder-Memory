from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from graph.state import ManualState

# Initialize our specialized compression model for on-the-fly chunking
chunk_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2  # Low temperature keeps the summary factual and concise
)

# This is the exact prompt blueprint from your chunk_memory_node
chunk_summarizer_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are the Session Compression Engine for Co-Founder's Memory.\n\n"
        "Your task is to take a raw conversation transcript slice and compress it into "
        "a list of highly dense, standalone factual summaries or key updates.\n\n"
        "Guidelines:\n"
        "- Extract core decisions, project pivots, tech-stack modifications, bugs encountered, and goals set.\n"
        "- Keep each point strictly standalone. Do not use vague references like 'the user decided this'. "
        "Instead say 'User decided to build Co-Founder's Memory using local Chroma DB'.\n"
        "- Break down the text into clear, atomic bullet points.\n"
        "- Ignore casual greetings, filler chat, or repetitive syntax.\n\n"
        "Output Rules:\n"
        "- Return each dense summary chunk on a new line.\n"
        "- Do NOT use bullets, numbers, hyphens, or markdown syntax.\n"
        "- Do NOT include any introductory or concluding text.\n"
        "- Separate each chunk using standard newlines."
    )),
    ("human", "--- RAW SESSION TRANSCRIPT SLICE ---\n{transcript}")
])

def append_user_message(state: ManualState) -> dict:
    """
    Captures the raw user query, appends it to temporary memory, and
    automatically triggers the chunk_memory extraction engine when the buffer reaches 55.
    """
    current_temp = state.get("temporary_memory") or []
    current_chunks = state.get("chunk_memory") or []
    user_query = state.get("user_query", "")
    
    if user_query:
        current_temp.append(f"Human: {user_query}")
        
    # --- AUTOMATIC TRUNCATION & CHUNK EXTRACTION TRIGGER ---
    if len(current_temp) >= 55:
        print(f"Temporary Memory: Buffer reached {len(current_temp)} entries. Extracting oldest 50 items to chunk_memory...")
        
        # 1. Slice the list: oldest 50 items to compress, latest 5 preserved
        oldest_50_slice = current_temp[:50]
        latest_5_preserved = current_temp[50:]
        
        # 2. Stringify the transcript slice for the LLM chunk extractor
        transcript_block = "\n".join(oldest_50_slice)
        
        # 3. Invoke the chunk extraction call directly
        prompt = chunk_summarizer_template.invoke({"transcript": transcript_block})
        response = chunk_llm.invoke(prompt)
        
        # 4. Parse response lines into a clean array of individual summary strings
        extracted_summary_lines = [
            line.strip()
            for line in response.content.splitlines()
            if line.strip()
        ]
        
        # 5. Append the newly generated summaries to the existing chunk_memory stack
        updated_chunks = current_chunks + extracted_summary_lines
        
        # 6. Build the fresh, cleared temporary memory layout.
        # We introduce a simple system bookmark to maintain continuity for the active session.
        bookmark_entry = "SYSTEM: Older segments of this chat thread have been compressed and archived to permanent memory."
        new_temp_buffer = [bookmark_entry] + latest_5_preserved
        
        print(f"Temporary Memory: Successfully archived 50 items into {len(extracted_summary_lines)} atomic chunks.")
        
        return {
            "temporary_memory": new_temp_buffer,
            "chunk_memory": updated_chunks
        }
        
    return {
        "temporary_memory": current_temp
    }

def append_ai_message(state: ManualState) -> dict:
    """
    Captures the final AI response and appends it to the temporary memory log.
    """
    current_temp = state.get("temporary_memory") or []
    final_response = state.get("final_response", "")
    
    if final_response:
        current_temp.append(f"AI: {final_response}")
        
    return {
        "temporary_memory": current_temp
    }