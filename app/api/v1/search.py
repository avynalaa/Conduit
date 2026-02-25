from typing import Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.services.rag import query as rag_query
from app.models.models import User

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5


class SearchResult(BaseModel):
    content: str
    metadata: dict
    distance: float = None


@router.post(
    "/rag",
    response_model=List[SearchResult],
    summary="Search documents using RAG vector similarity",
    responses={
        401: {"description": "Not authenticated"},
    },
)
def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    results = rag_query(
        query_text=request.query,
        user_id=current_user.id,
        n_results=request.n_results,
    )
    return results
