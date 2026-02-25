import os
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.crud import file as crud_file
from app.schemas.file import FileResponse, FileUploadResponse
from app.models.models import User, File, FileStatus
from app.services.file_processor import process_file
from app.services.rag import delete_document

router = APIRouter()


def _save_upload(upload: UploadFile, user_id: int) -> dict:
    """Save uploaded file to disk and return file metadata."""
    if upload.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {upload.content_type} not allowed",
        )

    content = upload.file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds max size of {settings.MAX_FILE_SIZE} bytes",
        )

    user_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    ext = os.path.splitext(upload.filename)[1]
    stored_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(user_dir, stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": stored_filename,
        "original_filename": upload.filename,
        "file_path": file_path,
        "file_size": len(content),
        "mime_type": upload.content_type,
        "user_id": user_id,
    }


@router.post(
    "/",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new file",
    responses={
        400: {"description": "File type not allowed or file too large"},
        401: {"description": "Not authenticated"},
    },
)
def upload_file(
    upload: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    file_data = _save_upload(upload, current_user.id)
    from app.schemas.file import FileCreate
    file_in = FileCreate(**file_data)
    return crud_file.create(db, obj_in=file_in)


@router.get(
    "/",
    response_model=List[FileResponse],
    summary="List all files for the current user",
    responses={
        401: {"description": "Not authenticated"},
    },
)
def list_files(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return crud_file.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    summary="Get a file by ID",
    responses={
        404: {"description": "File not found"},
        401: {"description": "Not authenticated"},
    },
)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    file = crud_file.get(db, id=file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file by ID",
    responses={
        404: {"description": "File not found"},
        401: {"description": "Not authenticated"},
    },
)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    file = crud_file.get(db, id=file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Delete from vector store
    delete_document(file_id)

    # Delete from disk
    if os.path.exists(file.file_path):
        os.remove(file.file_path)

    crud_file.remove(db, id=file_id)


@router.post(
    "/{file_id}/process",
    response_model=FileResponse,
    summary="Process an uploaded file for RAG indexing",
    responses={
        404: {"description": "File not found"},
        500: {"description": "Processing failed"},
        401: {"description": "Not authenticated"},
    },
)
def process_uploaded_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    file = crud_file.get(db, id=file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    result = process_file(db, file_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Processing failed")
    return result


@router.post(
    "/{file_id}/attach/{message_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Attach a file to a message",
    responses={
        404: {"description": "File or message not found"},
        401: {"description": "Not authenticated"},
    },
)
def attach_file_to_message(
    file_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    file = crud_file.get(db, id=file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    from app.crud import message as crud_message
    from app.crud import conversation as crud_conversation
    msg = crud_message.get(db, id=message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = crud_conversation.get(db, id=msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    attachment = crud_file.attach_to_message(db, message_id=message_id, file_id=file_id)
    return {"message_id": message_id, "file_id": file_id, "id": attachment.id}
