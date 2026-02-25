# Conduit

A production-ready backend for AI applications. Provides conversation management, multi-branch reasoning, RAG-powered document search, and file processing with a clean REST API.

## Features

- **Conversation Management** — Create, retrieve, and manage multi-turn conversations with full message history
- **Branch Support** — Explore alternative response paths with conversation branching and message regeneration
- **Per-Conversation Config** — Save model, temperature, system prompts, and RAG settings per conversation
- **RAG Integration** — Vector-based document search using Qdrant with automatic text chunking
- **File Processing** — Upload and process PDFs, Word docs, images, and text files
- **Authentication** — JWT-based auth with OAuth2 support (Google, GitHub placeholders)
- **Token Tracking** — Monitor prompt and completion tokens per message
- **Multi-User** — Full user isolation with conversation and file scoping

## Tech Stack

- **Framework** — FastAPI
- **Database** — PostgreSQL with SQLAlchemy ORM
- **Vector DB** — Qdrant with FastEmbed
- **LLM** — LiteLLM (supports OpenAI, Anthropic, etc.)
- **Auth** — JWT with bcrypt
- **File Processing** — PyMuPDF, python-docx, Pillow
- **Migrations** — Alembic

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis (optional, for Celery)

### Installation

```bash
git clone <repo>
cd ai-baas
pip install -e .
```

### Configuration

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/ai_baas
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=gpt-4
```

### Database Setup

```bash
alembic upgrade head
```

### Run

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Project Structure

```
app/
├── api/v1/              # API routes
│   ├── auth.py          # Authentication endpoints
│   ├── conversations.py # Conversation CRUD
│   ├── messages.py      # Message management
│   ├── branches.py      # Branch operations
│   ├── files.py         # File upload/processing
│   ├── chat.py          # Chat completion
│   ├── search.py        # RAG search
│   ├── config.py        # Conversation config
│   └── router.py        # Route aggregation
├── core/
│   ├── config.py        # Settings
│   ├── database.py      # DB connection
│   ├── security.py      # Auth utilities
│   └── exceptions.py    # Custom exceptions
├── crud/                # Database operations
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
│   ├── llm.py           # LLM integration
│   ├── rag.py           # Vector search
│   ├── file_processor.py # File handling
│   └── context.py       # Message context building
└── main.py              # App entry point
```

## API Overview

### Authentication

- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT token
- `GET /api/v1/auth/me` — Current user

### Conversations

- `GET /api/v1/conversations` — List conversations
- `POST /api/v1/conversations` — Create conversation
- `GET /api/v1/conversations/{id}` — Get with messages
- `PATCH /api/v1/conversations/{id}` — Update
- `DELETE /api/v1/conversations/{id}` — Delete

### Chat

- `POST /api/v1/chat` — Send message and get response

Request:
```json
{
  "conversation_id": 1,
  "content": "What is machine learning?",
  "model": "gpt-4",
  "temperature": 0.7,
  "use_rag": true,
  "rag_results": 5
}
```

### Branches

- `GET /api/v1/conversations/{id}/branches` — List branches
- `POST /api/v1/conversations/{id}/branches` — Create branch
- `POST /api/v1/conversations/branches/{id}/switch` — Set active
- `POST /api/v1/conversations/{id}/regenerate?parent_message_id=X` — Regenerate response
- `DELETE /api/v1/conversations/branches/{id}` — Delete branch

### Configuration

- `GET /api/v1/conversations/{id}/config` — Get config
- `PUT /api/v1/conversations/{id}/config` — Set config

### Files

- `POST /api/v1/files` — Upload file
- `GET /api/v1/files` — List files
- `POST /api/v1/files/{id}/process` — Process for RAG
- `DELETE /api/v1/files/{id}` — Delete file

### Search

- `POST /api/v1/search/rag` — Vector search documents

## Development

### Run Tests

```bash
pytest
```

### Database Migrations

Create migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply:
```bash
alembic upgrade head
```

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions welcome. Please ensure code follows the existing patterns and includes appropriate tests.
