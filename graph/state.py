from typing import TypedDict


class ManualState(TypedDict):
    query: str
    query_type: str

    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    is_memory_worthy: bool
    extracted_memory: str

    plan_review: str
    plan_ready: bool

    ask_review: bool

    summary: str
    final_response: str


class AutoState(TypedDict):
    context: str
    query: str
    date: str

    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    raw_research: str

    report: str

    auto_review: str
    auto_ready: bool

    needs_more_search: bool
    search_reason: str

    summary: str
    notify: bool


