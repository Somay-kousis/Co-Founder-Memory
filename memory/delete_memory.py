# memory/delete_memory.py
import json
from langgraph.store.base import BaseStore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from memory.schema import PermanentMemoryProfile
from dotenv import load_dotenv
load_dotenv()

def delete_memory(store: BaseStore, deletion_instruction: str):
    """
    Helper function to remove or modify specific details from the permanent memory profile.
    """
    namespace = ("memory", "profile")
    key = "co_founder_profile"
    
    # 1. Fetch the existing profile from the LangGraph Store
    existing_item = store.get(namespace, key)
    
    if not existing_item or not existing_item.value:
        print("No permanent memory profile found to delete from.")
        return None
        
    try:
        current_profile = PermanentMemoryProfile.model_validate(existing_item.value)
    except Exception:
        print("Failed to validate active profile layout during deletion process execution.")
        return None

    existing_profile_json = json.dumps(current_profile.model_dump(), indent=2)

    # 2. Set up the Scrubber Prompt
    system_prompt = (
        "You are the Pruning Engine of Co-Founder-Memory. Your job is to review an existing "
        "Permanent Memory Profile and remove or update information based on a user's deletion request.\n\n"
        "Rules for deletion:\n"
        "1. Identify which section (preferences, principles, projects, decisions, planning) contains the information to be forgotten.\n"
        "2. Completely remove the item, or modify the text/status so that the requested fact is no longer considered true or relevant.\n"
        "3. Do not touch or modify any other unrelated memories or historical timelines.\n"
        "4. Maintain a clean, valid structure that adheres perfectly to the schema."
    )
    
    human_prompt = (
        f"--- CURRENT PERMANENT MEMORY PROFILE ---\n{existing_profile_json}\n\n"
        f"--- DELETION REQUEST ---\nForget this: {deletion_instruction}\n\n"
        "Output the completely updated and pruned Permanent Memory Profile."
    )

    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.1)
    structured_llm = llm.with_structured_output(PermanentMemoryProfile)
    delete_all_signals = [
        "delete all the memories",
        "forget all the memories",
        "delete all memory",
        "forget all memory",
        "clear all memories",
        "remove all memories",
        "forget everything",
        "delete everything"
    ]

    if any(signal in deletion_instruction.lower() for signal in delete_all_signals):
        empty_profile = PermanentMemoryProfile().model_dump()
        store.put(namespace, key, empty_profile)
        print("All permanent memories have been cleared.")
        return empty_profile

    
    # 4. Run the evaluation and pruning
    pruned_profile = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])

    # 5. Save the pruned profile back into the store
    store.put(
        namespace,
        key,
        pruned_profile.model_dump()
    )
    
    print("Requested details successfully pruned from permanent memory.")
    return pruned_profile