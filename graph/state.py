# graph/state.py
from typing import List, TypedDict, Union
from typing_extensions import NotRequired

class ManualState(TypedDict):
    # input
    user_query: str
    query_type: NotRequired[str]

    # ask
    ask_retrieval_decision: NotRequired[bool]

    # plan (Synchronized with Pydantic output model dumps)
    plan: NotRequired[Union[dict, str]]
    plan_review: NotRequired[str]
    plan_ready: NotRequired[bool]  # Standardized to strict boolean type safety
    plan_review_count: NotRequired[int]

    # rag/context
    rag_list: list[str]
    retrieved_context: list[str]

    # memory
    extracted_memories: list[str]
    memory_intent: list[str]

    temporary_memory: list[str]
    chunk_memory: list[str]
    date_memory: dict[str, str]

    # output
    final_response: str


class SubGraphState(TypedDict):
    user_query: str
    retrieved_context: list[str]
    final_response: str
    run_web_search: bool


class AutoState(TypedDict):
    # Input & Operational Buffers
    user_query: NotRequired[str]
    chunk_memory: List[str]
    temporary_memory: List[str]
    retrieved_context: List[str]
    extracted_memories: List[str]
    final_response: str
    date_memory: dict[str, str]
    
    # Iteration & Quality Control Controlling Flags
    auto_ready: bool
    needs_more_search: bool
    needs_better_words: bool
    auto_review_count: int
    review_feedback: NotRequired[str]
