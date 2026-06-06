from typing import TypedDict


class ManualState(TypedDict):
    # input
    user_query: str
    query_type: str

    # retrieved context
    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    # ask flow
    ask_review: str
    ask_ready: bool

    # planning flow
    plan_review: str
    plan_ready: bool

    # memory flow
    extracted_memory: str
    is_memory_worthy: bool
    memory_intent: str  # add / update / delete / ignore

    # output
    summary: str
    final_response: str


class AutoState(TypedDict):
    # trigger/context
    context: str
    date: str

    # generated search
    search_query: str
    search_reason: str

    # retrieved context
    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    # research/report
    raw_research: str
    report: str

    # review
    auto_review: str
    auto_ready: bool
    needs_more_search: bool
    needs_better_words: bool
    
    # output
    summary: str
    notify: bool