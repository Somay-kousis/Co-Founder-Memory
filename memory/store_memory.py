# memory/store_memory.py
import json
from langgraph.store.base import BaseStore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from memory.schema import PermanentMemoryProfile
from dotenv import load_dotenv
load_dotenv()

def store_memory(store: BaseStore, new_memory_chunks: list):
    """
    Helper function to merge new memory chunks into the permanent LangGraph Store.
    """
    if isinstance(new_memory_chunks, str):
        new_memory_chunks = [new_memory_chunks]

    if not new_memory_chunks:
        return None

    namespace = ("memory", "profile")
    key = "co_founder_profile"
    
    # 1. Fetch existing profile from LangGraph Store
    existing_item = store.get(namespace, key)
    
    if existing_item and existing_item.value:
        try:
            # Use model_validate to handle validation checks cleanly
            current_profile = PermanentMemoryProfile.model_validate(existing_item.value)
        except Exception:
            current_profile = PermanentMemoryProfile()
        existing_profile_json = json.dumps(current_profile.model_dump(), indent=2)
    else:
        current_profile = PermanentMemoryProfile()
        existing_profile_json = "{}"

    # 2. Set up the Reflection/Merging Prompt
    system_prompt = (
        "You are the Reflection Engine of Co-Founder-Memory. Your job is to take an existing "
        "Permanent Memory Profile and merge new incoming chunks of memory into it.\n\n"
        "Rules for merging:\n"
        "1. Identify if the new info relates to preferences, core principles, projects, strategic decisions, or planning.\n"
        "2. If an item matches an existing entry (e.g., updating a project's status or modifying a tech choice), "
        "update it or append to its historical updates timeline instead of duplicating it.\n"
        "3. If the information is brand new, add it to the correct section.\n"
        "4. Preserve historical timelines and hidden contexts wherever possible."
    )
    
    # Format the chunks as a bulleted list
    new_chunks_text = "\n".join([f"- {m}" for m in new_memory_chunks])
    
    human_prompt = (
        f"--- CURRENT PERMANENT MEMORY PROFILE ---\n{existing_profile_json}\n\n"
        f"--- NEW INCOMING MEMORY CHUNKS ---\n{new_chunks_text}\n\n"
        "Output the completely updated and unified Permanent Memory Profile."
    )

    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
    structured_llm = llm.with_structured_output(PermanentMemoryProfile)
    
    # 3. Run the evaluation and consolidation
    updated_profile = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])

    # 4. Save the merged profile back into the LangGraph store
    store.put(
        namespace,
        key,
        updated_profile.model_dump()
    )
    
    print("Permanent memory successfully consolidated and stored.")
    return updated_profile