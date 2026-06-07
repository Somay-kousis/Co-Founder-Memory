import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from memory.schema import PermanentMemoryProfile

def delete_memory(store, deletion_instruction: str):
    """
    Helper function to remove or modify specific details from the permanent memory profile.
    
    Args:
        store: The active LangGraph BaseStore instance passed from your node.
        deletion_instruction: The raw text detailing what the user wants forgotten.
    """
    namespace = ("memory", "profile")
    key = "co_founder_profile"
    
    # 1. Fetch the existing profile from the LangGraph Store
    existing_item = store.get(namespace, key)
    
    # If there is no profile to delete from, we can exit early
    if not existing_item or not existing_item.value:
        print("No permanent memory profile found to delete from.")
        return None
        
    current_profile = PermanentMemoryProfile(**existing_item.value)
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

    # 3. Initialize your structured LLM
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.1)
    structured_llm = llm.with_structured_output(PermanentMemoryProfile)
    
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