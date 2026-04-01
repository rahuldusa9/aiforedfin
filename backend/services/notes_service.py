"""
AI FOR EDUCATION – Study Notes Service
AI-powered note generation, summaries, and mind maps.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List, Optional
from database import db
from services.gemini_service import generate_text

logger = logging.getLogger(__name__)


def note_schema() -> dict:
    """Schema for a study note."""
    return {
        "note_id": str,
        "user_id": str,
        "title": str,
        "topic": str,
        "content": str,           # Main note content (markdown)
        "summary": str,           # AI-generated summary
        "key_points": [],         # List of key points
        "mind_map": {},           # Mind map structure
        "highlights": [],         # User highlights
        "annotations": [],        # User annotations
        "tags": [],
        "language": "en",
        "source": "ai",           # "ai" or "user"
        "related_notes": [],      # IDs of related notes
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def folder_schema() -> dict:
    """Schema for note folders."""
    return {
        "folder_id": str,
        "user_id": str,
        "name": str,
        "color": "#4F46E5",
        "icon": "📁",
        "note_count": 0,
        "created_at": datetime.utcnow(),
    }


class StudyNotesService:
    """Service for AI-powered study notes."""

    def __init__(self):
        self.notes = db.study_notes if db else None
        self.folders = db.note_folders if db else None

    def _get_notes(self):
        if self.notes is None:
            from database import db
            self.notes = db.study_notes
        return self.notes

    def _get_folders(self):
        if self.folders is None:
            from database import db
            self.folders = db.note_folders
        return self.folders

    # ==================== NOTE GENERATION ====================

    async def generate_notes(
        self,
        user_id: str,
        topic: str,
        detail_level: str = "comprehensive",
        language: str = "en",
        include_examples: bool = True,
        include_mind_map: bool = True
    ) -> dict:
        """Generate study notes using AI."""

        prompt = f"""Create comprehensive study notes about "{topic}" in {language}.

Detail level: {detail_level}

Generate notes in this JSON format:
{{
    "title": "Clear, descriptive title",
    "summary": "2-3 sentence overview",
    "content": "Full markdown content with headers, bullet points, etc.",
    "key_points": ["Point 1", "Point 2", "Point 3", ...],
    "mind_map": {{
        "central": "{topic}",
        "branches": [
            {{"name": "Branch 1", "children": ["Sub 1", "Sub 2"]}},
            {{"name": "Branch 2", "children": ["Sub 1", "Sub 2"]}}
        ]
    }},
    "vocabulary": [
        {{"term": "Term", "definition": "Definition"}}
    ],
    "questions": ["Review question 1?", "Review question 2?"]
}}

Requirements:
- Use clear, educational language
- Include practical examples{"" if not include_examples else " with real-world applications"}
- Structure content with ## headers
- Use bullet points for lists
- Bold **key terms**
- Detail level: {detail_level} (brief=300 words, standard=600 words, comprehensive=1000+ words)
{"- Include mind map for visual learning" if include_mind_map else ""}

Return ONLY valid JSON."""

        try:
            response = generate_text(prompt, max_tokens=4000)

            # Parse JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            data = json.loads(response[start:end])

            # Create note
            note = note_schema()
            note["note_id"] = str(uuid.uuid4())
            note["user_id"] = user_id
            note["title"] = data.get("title", topic)
            note["topic"] = topic
            note["content"] = data.get("content", "")
            note["summary"] = data.get("summary", "")
            note["key_points"] = data.get("key_points", [])
            note["mind_map"] = data.get("mind_map", {})
            note["language"] = language
            note["source"] = "ai"
            note["tags"] = [topic]
            note["vocabulary"] = data.get("vocabulary", [])
            note["review_questions"] = data.get("questions", [])

            # Save to database
            self._get_notes().insert_one(note)

            logger.info(f"[Notes] Generated notes for '{topic}'")

            return note

        except Exception as e:
            logger.error(f"[Notes] Generation failed: {e}")
            raise RuntimeError(f"Failed to generate notes: {e}")

    async def generate_summary(self, text: str, length: str = "medium") -> str:
        """Generate a summary of given text."""
        word_limits = {
            "brief": 50,
            "medium": 150,
            "detailed": 300,
        }
        limit = word_limits.get(length, 150)

        prompt = f"""Summarize the following text in approximately {limit} words.
Focus on the main ideas and key takeaways.

TEXT:
{text}

SUMMARY:"""

        summary = generate_text(prompt, max_tokens=limit * 2)
        return summary.strip()

    async def generate_mind_map(self, topic: str, depth: int = 2) -> dict:
        """Generate a mind map structure for a topic."""

        prompt = f"""Create a mind map structure for "{topic}" with {depth} levels of depth.

Return JSON in this exact format:
{{
    "central": "{topic}",
    "branches": [
        {{
            "name": "Main concept 1",
            "color": "#FF6B6B",
            "children": [
                {{"name": "Sub-concept 1.1", "children": []}},
                {{"name": "Sub-concept 1.2", "children": []}}
            ]
        }},
        {{
            "name": "Main concept 2",
            "color": "#4ECDC4",
            "children": [
                {{"name": "Sub-concept 2.1", "children": []}},
                {{"name": "Sub-concept 2.2", "children": []}}
            ]
        }}
    ]
}}

Create 4-6 main branches with 2-4 children each.
Use educational, accurate information.
Return ONLY valid JSON."""

        try:
            response = generate_text(prompt, max_tokens=2000)

            start = response.find('{')
            end = response.rfind('}') + 1
            mind_map = json.loads(response[start:end])

            return mind_map

        except Exception as e:
            logger.error(f"[Notes] Mind map generation failed: {e}")
            return {
                "central": topic,
                "branches": []
            }

    async def explain_concept(
        self,
        concept: str,
        level: str = "simple",
        analogy: bool = True
    ) -> dict:
        """Explain a concept at different levels."""

        prompt = f"""Explain "{concept}" at a {level} level.

{"Include a relatable analogy." if analogy else ""}

Return JSON:
{{
    "explanation": "Clear explanation",
    "analogy": "Relatable analogy (if requested)",
    "example": "Practical example",
    "common_mistakes": ["Mistake 1", "Mistake 2"],
    "related_concepts": ["Concept 1", "Concept 2"]
}}

Level guide:
- simple: For beginners, use everyday language
- intermediate: Include technical terms with explanations
- advanced: Detailed, technical explanation

Return ONLY valid JSON."""

        try:
            response = generate_text(prompt, max_tokens=1500)

            start = response.find('{')
            end = response.rfind('}') + 1
            explanation = json.loads(response[start:end])

            return explanation

        except Exception as e:
            logger.error(f"[Notes] Explanation failed: {e}")
            return {
                "explanation": f"Failed to generate explanation: {e}",
                "analogy": "",
                "example": "",
                "common_mistakes": [],
                "related_concepts": [],
            }

    # ==================== NOTE CRUD ====================

    async def create_note(
        self,
        user_id: str,
        title: str,
        content: str,
        topic: str = "",
        tags: list = None
    ) -> dict:
        """Create a user-written note."""
        notes = self._get_notes()

        note = note_schema()
        note["note_id"] = str(uuid.uuid4())
        note["user_id"] = user_id
        note["title"] = title
        note["content"] = content
        note["topic"] = topic
        note["tags"] = tags or []
        note["source"] = "user"

        notes.insert_one(note)

        return note

    async def get_user_notes(
        self,
        user_id: str,
        folder_id: str = None,
        tag: str = None,
        limit: int = 50
    ) -> List[dict]:
        """Get notes for a user."""
        notes = self._get_notes()

        query = {"user_id": user_id}
        if folder_id:
            query["folder_id"] = folder_id
        if tag:
            query["tags"] = tag

        user_notes = list(notes.find(query).sort("updated_at", -1).limit(limit))

        for note in user_notes:
            note["_id"] = str(note["_id"])

        return user_notes

    async def get_note(self, note_id: str, user_id: str) -> Optional[dict]:
        """Get a specific note."""
        notes = self._get_notes()
        note = notes.find_one({"note_id": note_id, "user_id": user_id})

        if note:
            note["_id"] = str(note["_id"])

        return note

    async def update_note(
        self,
        note_id: str,
        user_id: str,
        updates: dict
    ) -> bool:
        """Update a note."""
        notes = self._get_notes()

        allowed_fields = ["title", "content", "tags", "highlights", "annotations", "folder_id"]
        safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        safe_updates["updated_at"] = datetime.utcnow()

        result = notes.update_one(
            {"note_id": note_id, "user_id": user_id},
            {"$set": safe_updates}
        )

        return result.modified_count > 0

    async def delete_note(self, note_id: str, user_id: str) -> bool:
        """Delete a note."""
        notes = self._get_notes()
        result = notes.delete_one({"note_id": note_id, "user_id": user_id})
        return result.deleted_count > 0

    async def add_highlight(
        self,
        note_id: str,
        user_id: str,
        text: str,
        color: str = "yellow",
        start_pos: int = 0,
        end_pos: int = 0
    ) -> dict:
        """Add a highlight to a note."""
        notes = self._get_notes()

        highlight = {
            "id": str(uuid.uuid4()),
            "text": text,
            "color": color,
            "start": start_pos,
            "end": end_pos,
            "created_at": datetime.utcnow().isoformat(),
        }

        notes.update_one(
            {"note_id": note_id, "user_id": user_id},
            {
                "$push": {"highlights": highlight},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return highlight

    async def add_annotation(
        self,
        note_id: str,
        user_id: str,
        text: str,
        annotation: str,
        position: int = 0
    ) -> dict:
        """Add an annotation to a note."""
        notes = self._get_notes()

        note_annotation = {
            "id": str(uuid.uuid4()),
            "text": text,
            "annotation": annotation,
            "position": position,
            "created_at": datetime.utcnow().isoformat(),
        }

        notes.update_one(
            {"note_id": note_id, "user_id": user_id},
            {
                "$push": {"annotations": note_annotation},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return note_annotation

    # ==================== FOLDERS ====================

    async def create_folder(
        self,
        user_id: str,
        name: str,
        color: str = "#4F46E5",
        icon: str = "📁"
    ) -> dict:
        """Create a note folder."""
        folders = self._get_folders()

        folder = folder_schema()
        folder["folder_id"] = str(uuid.uuid4())
        folder["user_id"] = user_id
        folder["name"] = name
        folder["color"] = color
        folder["icon"] = icon

        folders.insert_one(folder)

        return folder

    async def get_folders(self, user_id: str) -> List[dict]:
        """Get all folders for a user."""
        folders = self._get_folders()
        notes = self._get_notes()

        user_folders = list(folders.find({"user_id": user_id}))

        for folder in user_folders:
            folder["_id"] = str(folder["_id"])
            # Count notes in folder
            count = notes.count_documents({"folder_id": folder["folder_id"]})
            folder["note_count"] = count

        return user_folders

    # ==================== SEARCH ====================

    async def search_notes(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[dict]:
        """Search notes by title, content, or tags."""
        notes = self._get_notes()

        search_results = list(notes.find({
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}},
                {"topic": {"$regex": query, "$options": "i"}},
            ]
        }).limit(limit))

        for note in search_results:
            note["_id"] = str(note["_id"])

        return search_results

    async def get_related_notes(self, note_id: str, user_id: str, limit: int = 5) -> List[dict]:
        """Find notes related to a given note."""
        notes = self._get_notes()

        # Get the source note
        source = notes.find_one({"note_id": note_id, "user_id": user_id})
        if not source:
            return []

        # Find notes with similar tags or topic
        tags = source.get("tags", [])
        topic = source.get("topic", "")

        related = list(notes.find({
            "user_id": user_id,
            "note_id": {"$ne": note_id},
            "$or": [
                {"tags": {"$in": tags}},
                {"topic": topic},
            ]
        }).limit(limit))

        for note in related:
            note["_id"] = str(note["_id"])

        return related


# Global instance
_notes_service = None


def get_notes_service() -> StudyNotesService:
    """Get or create the study notes service instance."""
    global _notes_service
    if _notes_service is None:
        _notes_service = StudyNotesService()
    return _notes_service
