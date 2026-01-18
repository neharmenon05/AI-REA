from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.news_service import NewsService

router = APIRouter()

class NewsRequest(BaseModel):
    query: str

class NewsResponse(BaseModel):
    news: list

@router.post("/", response_model=NewsResponse)
def get_news(req: NewsRequest):
    service = NewsService()
    items = service.search_news(req.query)
    return NewsResponse(news=items)
