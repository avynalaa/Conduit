import os
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import File, FileStatus
from app.crud import file as crud_file
from app.schemas.file import FileUpdate
from app.services.rag import add_document


def process_file(db: Session, file_id: int) -> Optional[File]:
    """Process a file and extract text content."""
    file = crud_file.get(db, id=file_id)
    if not file:
        return None

    # Mark as processing
    crud_file.update(db, db_obj=file, obj_in=FileUpdate(status=FileStatus.PROCESSING))

    try:
        text = _extract_text(file.file_path, file.mime_type)

        # Index in vector store for RAG
        chunks_added = 0
        if text and not file.mime_type.startswith("image/"):
            chunks_added = add_document(text=text, file_id=file.id, user_id=file.user_id)

        crud_file.update(db, db_obj=file, obj_in=FileUpdate(
            status=FileStatus.COMPLETED,
            extracted_text=text,
            extra_metadata={"chunks_indexed": chunks_added},
        ))
    except Exception as e:
        crud_file.update(db, db_obj=file, obj_in=FileUpdate(
            status=FileStatus.FAILED,
            extra_metadata={"error": str(e)},
        ))

    return crud_file.get(db, id=file_id)


def _extract_text(file_path: str, mime_type: str) -> str:
    """Route to the correct parser based on mime type."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if mime_type == "application/pdf":
        return _extract_pdf(file_path)
    elif mime_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
        return _extract_docx(file_path)
    elif mime_type == "text/plain":
        return _extract_text_file(file_path)
    elif mime_type == "text/csv":
        return _extract_text_file(file_path)
    elif mime_type in ("application/json", "application/xml"):
        return _extract_text_file(file_path)
    elif mime_type.startswith("image/"):
        return _extract_image_metadata(file_path)
    else:
        raise ValueError(f"Unsupported mime type: {mime_type}")


def _extract_pdf(file_path: str) -> str:
    import fitz  # PyMuPDF
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def _extract_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_image_metadata(file_path: str) -> str:
    from PIL import Image
    img = Image.open(file_path)
    info = {
        "format": img.format,
        "size": f"{img.width}x{img.height}",
        "mode": img.mode,
    }
    exif = img.getexif()
    if exif:
        info["exif_tags"] = len(exif)
    return str(info)


def process_pending_files(db: Session, limit: int = 10) -> list:
    """Process all pending files."""
    pending = crud_file.get_pending(db, limit=limit)
    results = []
    for file in pending:
        result = process_file(db, file.id)
        results.append(result)
    return results
