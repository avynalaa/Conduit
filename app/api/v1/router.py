from fastapi import APIRouter
from app.api.v1 import auth, conversations, messages, files, chat, search, config, branches

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(config.router, prefix="/conversations", tags=["config"])
api_router.include_router(branches.router, prefix="/conversations", tags=["branches"])
api_router.include_router(messages.router, prefix="", tags=["messages"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
