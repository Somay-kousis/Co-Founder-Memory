from typing import TypedDict


class ManualState(TypedDict):
    query: str
    query_type: str

    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    summary: str

    is_memory_worthy: bool
    candidate_memory: str

    review: str
    final_response: str


class AutoState(TypedDict):
    context: str
    query: str
    date: str

    search_github: str
    search_web1: str
    search_web2: str
    search_memory: str

    rag_list: list
    permanent_memory_list: list
    temporary_memory_list: list

    review: str
    summary: str

    report: str
    notify: bool