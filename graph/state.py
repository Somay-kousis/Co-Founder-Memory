from typing import TypedDict, NotRequired


class ManualState(TypedDict):
    # input
    user_query: str
    query_type: NotRequired[str]

    # ask
    ask_retrieval_decision: NotRequired[bool]

    plan: str
    plan_review: str
    plan_ready: str
    plan_review_count: str

    # rag/context
    rag_list: list[str]
    retrieved_context: list[str]

    # memory
    extracted_memories: list[str]
    memory_intent: list[str]

    temporary_memory:list[str]
    chunk_memory: list[str]
    date_memory: dict[str, str]
    permanent_memory: dict[str, str]

    # output
    final_response: str