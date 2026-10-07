from fastapi import APIRouter

from app.rag.pipeline import RAGPipeline
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
rag_pipeline = RAGPipeline()


@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    result = rag_pipeline.ask(question=request.question, history=request.history)
    return result
