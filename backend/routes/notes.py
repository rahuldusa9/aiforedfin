"""
AI FOR EDUCATION – Study Notes Routes
AI-powered note generation and management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.notes_service import get_notes_service

router = APIRouter(prefix="/api/notes", tags=["notes"])


class GenerateNotesRequest(BaseModel):
    topic: str
    detail_level: Optional[str] = "comprehensive"
    language: Optional[str] = "en"
    include_examples: Optional[bool] = True
    include_mind_map: Optional[bool] = True


class CreateNoteRequest(BaseModel):
    title: str
    content: str
    topic: Optional[str] = ""
    tags: Optional[List[str]] = None


class UpdateNoteRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[str] = None


class HighlightRequest(BaseModel):
    text: str
    color: Optional[str] = "yellow"
    start_pos: Optional[int] = 0
    end_pos: Optional[int] = 0


class AnnotationRequest(BaseModel):
    text: str
    annotation: str
    position: Optional[int] = 0


class ExplainRequest(BaseModel):
    concept: str
    level: Optional[str] = "simple"
    use_analogy: Optional[bool] = True


class SummarizeRequest(BaseModel):
    text: str
    length: Optional[str] = "medium"


class CreateFolderRequest(BaseModel):
    name: str
    color: Optional[str] = "#4F46E5"
    icon: Optional[str] = "📁"


class MindMapRequest(BaseModel):
    topic: str
    depth: Optional[int] = 2


# ==================== NOTE GENERATION ====================

@router.post("/generate/{user_id}")
async def generate_notes(user_id: str, request: GenerateNotesRequest):
    """Generate study notes using AI."""
    service = get_notes_service()

    try:
        note = await service.generate_notes(
            user_id=user_id,
            topic=request.topic,
            detail_level=request.detail_level,
            language=request.language,
            include_examples=request.include_examples,
            include_mind_map=request.include_mind_map
        )
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """Summarize given text."""
    service = get_notes_service()
    summary = await service.generate_summary(request.text, request.length)
    return {"summary": summary}


@router.post("/mind-map")
async def generate_mind_map(request: MindMapRequest):
    """Generate a mind map for a topic."""
    service = get_notes_service()
    mind_map = await service.generate_mind_map(request.topic, request.depth)
    return {"mind_map": mind_map}


@router.post("/explain")
async def explain_concept(request: ExplainRequest):
    """Explain a concept simply."""
    service = get_notes_service()
    explanation = await service.explain_concept(
        request.concept,
        request.level,
        request.use_analogy
    )
    return explanation


# ==================== NOTE CRUD ====================

@router.post("/{user_id}")
async def create_note(user_id: str, request: CreateNoteRequest):
    """Create a user-written note."""
    service = get_notes_service()
    note = await service.create_note(
        user_id=user_id,
        title=request.title,
        content=request.content,
        topic=request.topic,
        tags=request.tags
    )
    return note


@router.get("/{user_id}")
async def get_user_notes(
    user_id: str,
    folder_id: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50
):
    """Get notes for a user."""
    service = get_notes_service()
    notes = await service.get_user_notes(user_id, folder_id, tag, limit)
    return {"notes": notes}


@router.get("/note/{note_id}/{user_id}")
async def get_note(note_id: str, user_id: str):
    """Get a specific note."""
    service = get_notes_service()
    note = await service.get_note(note_id, user_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/note/{note_id}/{user_id}")
async def update_note(note_id: str, user_id: str, request: UpdateNoteRequest):
    """Update a note."""
    service = get_notes_service()
    updates = request.dict(exclude_none=True)
    success = await service.update_note(note_id, user_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}


@router.delete("/note/{note_id}/{user_id}")
async def delete_note(note_id: str, user_id: str):
    """Delete a note."""
    service = get_notes_service()
    success = await service.delete_note(note_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}


# ==================== HIGHLIGHTS & ANNOTATIONS ====================

@router.post("/highlight/{note_id}/{user_id}")
async def add_highlight(note_id: str, user_id: str, request: HighlightRequest):
    """Add a highlight to a note."""
    service = get_notes_service()
    highlight = await service.add_highlight(
        note_id, user_id,
        request.text, request.color,
        request.start_pos, request.end_pos
    )
    return highlight


@router.post("/annotate/{note_id}/{user_id}")
async def add_annotation(note_id: str, user_id: str, request: AnnotationRequest):
    """Add an annotation to a note."""
    service = get_notes_service()
    annotation = await service.add_annotation(
        note_id, user_id,
        request.text, request.annotation, request.position
    )
    return annotation


# ==================== FOLDERS ====================

@router.post("/folders/{user_id}")
async def create_folder(user_id: str, request: CreateFolderRequest):
    """Create a note folder."""
    service = get_notes_service()
    folder = await service.create_folder(
        user_id, request.name, request.color, request.icon
    )
    return folder


@router.get("/folders/{user_id}")
async def get_folders(user_id: str):
    """Get all folders for a user."""
    service = get_notes_service()
    folders = await service.get_folders(user_id)
    return {"folders": folders}


# ==================== SEARCH ====================

@router.get("/search/{user_id}")
async def search_notes(user_id: str, query: str, limit: int = 20):
    """Search notes."""
    service = get_notes_service()
    results = await service.search_notes(user_id, query, limit)
    return {"results": results}


@router.get("/related/{note_id}/{user_id}")
async def get_related_notes(note_id: str, user_id: str, limit: int = 5):
    """Get notes related to a given note."""
    service = get_notes_service()
    related = await service.get_related_notes(note_id, user_id, limit)
    return {"related": related}
