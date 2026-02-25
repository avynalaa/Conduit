from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    TokenData,
    LoginRequest,
    OAuthCallback,
)
from app.schemas.conversation import (
    ConversationBase,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationWithBranches,
)
from app.schemas.message import (
    MessageBase,
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageWithFiles,
)
from app.schemas.branch import (
    BranchBase,
    BranchCreate,
    BranchUpdate,
    BranchResponse,
)
from app.schemas.file import (
    FileBase,
    FileCreate,
    FileUpdate,
    FileResponse,
    FileUploadResponse,
)
from app.schemas.config import (
    ConfigBase,
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
)
from app.schemas.common import PaginatedResponse

# Resolve forward references
ConversationWithMessages.model_rebuild()
ConversationWithBranches.model_rebuild()
MessageWithFiles.model_rebuild()

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "LoginRequest",
    "OAuthCallback",
    # Conversation
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationWithMessages",
    "ConversationWithBranches",
    # Message
    "MessageBase",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",
    "MessageWithFiles",
    # Branch
    "BranchBase",
    "BranchCreate",
    "BranchUpdate",
    "BranchResponse",
    # File
    "FileBase",
    "FileCreate",
    "FileUpdate",
    "FileResponse",
    "FileUploadResponse",
    # Config
    "ConfigBase",
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigResponse",
    # Common
    "PaginatedResponse",
]
