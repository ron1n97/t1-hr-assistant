from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from models import Candidate


class HRState(TypedDict):
    """Состояние HR мультиагентной системы"""
    messages: Annotated[List, add_messages]
    candidates: Optional[List[Candidate]]
    request_type: Optional[str]  # "candidate_search" или "general_question"
    search_query: Optional[str]
    selected_candidates: Optional[List[Candidate]]
    reasoning: Optional[str]
