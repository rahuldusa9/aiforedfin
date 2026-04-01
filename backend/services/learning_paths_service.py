"""
AI FOR EDUCATION – Learning Paths Service
Personalized learning paths, adaptive difficulty, and onboarding assessment.
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from database import db
from services.gemini_service import generate_text

logger = logging.getLogger(__name__)


# Learning styles
LEARNING_STYLES = {
    "visual": {
        "name": "Visual Learner",
        "description": "You learn best through images, diagrams, and visual content.",
        "recommendations": ["stories", "mind_maps", "flashcards"],
        "icon": "👁️"
    },
    "auditory": {
        "name": "Auditory Learner",
        "description": "You learn best by listening and through verbal explanations.",
        "recommendations": ["podcasts", "stories_audio", "tutor"],
        "icon": "👂"
    },
    "reading": {
        "name": "Reading/Writing Learner",
        "description": "You learn best through reading and taking notes.",
        "recommendations": ["notes", "flashcards", "stories"],
        "icon": "📖"
    },
    "kinesthetic": {
        "name": "Kinesthetic Learner",
        "description": "You learn best through practice and hands-on activities.",
        "recommendations": ["quizzes", "flashcards", "practice"],
        "icon": "🤹"
    },
}

# Difficulty levels
DIFFICULTY_LEVELS = ["beginner", "elementary", "intermediate", "upper_intermediate", "advanced", "expert"]


def learning_profile_schema() -> dict:
    """Schema for user learning profile."""
    return {
        "user_id": str,

        # Learning preferences
        "learning_style": "visual",
        "preferred_difficulty": "intermediate",
        "current_level": "beginner",
        "goals": [],
        "interests": [],
        "daily_goal_minutes": 20,
        "preferred_languages": ["en"],

        # Assessment results
        "assessment_completed": False,
        "assessment_date": None,
        "assessment_scores": {},

        # Adaptive learning data
        "topic_proficiency": {},  # {topic: {level, score, last_activity}}
        "difficulty_adjustments": [],
        "recommended_topics": [],

        # Progress
        "paths_enrolled": [],
        "paths_completed": [],
        "total_lessons_completed": 0,

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def learning_path_schema() -> dict:
    """Schema for a learning path."""
    return {
        "path_id": str,
        "title": str,
        "description": str,
        "subject": str,
        "difficulty": "beginner",
        "estimated_hours": 0,
        "lessons": [],  # List of lesson objects
        "prerequisites": [],
        "skills_gained": [],
        "icon": "📚",
        "color": "#4F46E5",
        "is_featured": False,
        "created_by": "system",
        "created_at": datetime.utcnow(),
    }


def user_path_progress_schema() -> dict:
    """Schema for user's progress on a path."""
    return {
        "user_id": str,
        "path_id": str,
        "enrolled_at": datetime.utcnow(),
        "current_lesson": 0,
        "lessons_completed": [],
        "quiz_scores": {},
        "time_spent_ms": 0,
        "last_activity": datetime.utcnow(),
        "completed": False,
        "completed_at": None,
    }


class LearningPathsService:
    """Service for personalized learning paths."""

    def __init__(self):
        self.profiles = db.learning_profiles if db else None
        self.paths = db.learning_paths if db else None
        self.progress = db.path_progress if db else None

    def _get_profiles(self):
        if self.profiles is None:
            from database import db
            self.profiles = db.learning_profiles
        return self.profiles

    def _get_paths(self):
        if self.paths is None:
            from database import db
            self.paths = db.learning_paths
        return self.paths

    def _get_progress(self):
        if self.progress is None:
            from database import db
            self.progress = db.path_progress
        return self.progress

    # ==================== ONBOARDING ASSESSMENT ====================

    async def generate_assessment(self, topics: List[str] = None) -> dict:
        """Generate an onboarding assessment."""

        if not topics:
            topics = ["general knowledge", "learning preferences", "goals"]

        prompt = f"""Create a learning assessment questionnaire.

Topics to assess: {', '.join(topics)}

Return JSON with this structure:
{{
    "questions": [
        {{
            "id": "q1",
            "type": "multiple_choice",
            "category": "learning_style",
            "question": "Question text",
            "options": [
                {{"value": "a", "text": "Option A", "style_points": {{"visual": 1}}}},
                {{"value": "b", "text": "Option B", "style_points": {{"auditory": 1}}}}
            ]
        }},
        {{
            "id": "q2",
            "type": "scale",
            "category": "difficulty",
            "question": "Rate your comfort with...",
            "min": 1,
            "max": 5,
            "labels": ["Beginner", "Expert"]
        }},
        {{
            "id": "q3",
            "type": "multi_select",
            "category": "interests",
            "question": "Select topics you're interested in:",
            "options": ["Science", "History", "Math", "Language", "Arts"]
        }}
    ]
}}

Create 8-10 questions covering:
- 3 learning style questions
- 2 difficulty/level questions
- 2 interest/goal questions
- 2 preference questions

Return ONLY JSON."""

        try:
            response = generate_text(prompt, max_tokens=3000)

            start = response.find('{')
            end = response.rfind('}') + 1
            assessment = json.loads(response[start:end])

            return {
                "assessment_id": str(uuid.uuid4()),
                "questions": assessment.get("questions", []),
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"[LearningPath] Assessment generation failed: {e}")
            return self._get_default_assessment()

    def _get_default_assessment(self) -> dict:
        """Return a default assessment if AI generation fails."""
        return {
            "assessment_id": str(uuid.uuid4()),
            "questions": [
                {
                    "id": "ls1",
                    "type": "multiple_choice",
                    "category": "learning_style",
                    "question": "How do you prefer to learn new concepts?",
                    "options": [
                        {"value": "a", "text": "Watching videos or looking at diagrams", "style_points": {"visual": 2}},
                        {"value": "b", "text": "Listening to explanations or podcasts", "style_points": {"auditory": 2}},
                        {"value": "c", "text": "Reading articles and taking notes", "style_points": {"reading": 2}},
                        {"value": "d", "text": "Practicing with quizzes and exercises", "style_points": {"kinesthetic": 2}},
                    ]
                },
                {
                    "id": "ls2",
                    "type": "multiple_choice",
                    "category": "learning_style",
                    "question": "When studying, what helps you remember best?",
                    "options": [
                        {"value": "a", "text": "Color-coded notes and mind maps", "style_points": {"visual": 2}},
                        {"value": "b", "text": "Discussing with others or self-explanation", "style_points": {"auditory": 2}},
                        {"value": "c", "text": "Writing summaries in my own words", "style_points": {"reading": 2}},
                        {"value": "d", "text": "Teaching others or applying concepts", "style_points": {"kinesthetic": 2}},
                    ]
                },
                {
                    "id": "diff1",
                    "type": "scale",
                    "category": "difficulty",
                    "question": "How would you rate your overall academic level?",
                    "min": 1,
                    "max": 5,
                    "labels": ["Beginner", "Elementary", "Intermediate", "Advanced", "Expert"]
                },
                {
                    "id": "goal1",
                    "type": "multi_select",
                    "category": "interests",
                    "question": "What subjects interest you most?",
                    "options": ["Science", "Technology", "History", "Mathematics", "Language & Literature", "Arts", "Social Studies", "Health & Wellness"]
                },
                {
                    "id": "pref1",
                    "type": "multiple_choice",
                    "category": "preferences",
                    "question": "How much time can you dedicate to learning daily?",
                    "options": [
                        {"value": "10", "text": "10-15 minutes"},
                        {"value": "20", "text": "20-30 minutes"},
                        {"value": "45", "text": "45-60 minutes"},
                        {"value": "60", "text": "More than an hour"},
                    ]
                },
            ],
        }

    async def process_assessment(self, user_id: str, answers: List[dict]) -> dict:
        """Process assessment answers and create learning profile."""
        profiles = self._get_profiles()

        # Calculate learning style
        style_scores = {"visual": 0, "auditory": 0, "reading": 0, "kinesthetic": 0}

        interests = []
        difficulty_score = 3
        daily_goal = 20

        for answer in answers:
            category = answer.get("category", "")
            value = answer.get("value")

            if category == "learning_style" and isinstance(value, dict):
                style_points = value.get("style_points", {})
                for style, points in style_points.items():
                    style_scores[style] = style_scores.get(style, 0) + points

            elif category == "interests" and isinstance(value, list):
                interests.extend(value)

            elif category == "difficulty" and isinstance(value, (int, float)):
                difficulty_score = value

            elif category == "preferences" and answer.get("id") == "pref1":
                daily_goal = int(value) if value else 20

        # Determine primary learning style
        primary_style = max(style_scores.items(), key=lambda x: x[1])[0]

        # Map difficulty score to level
        difficulty_map = {
            1: "beginner",
            2: "elementary",
            3: "intermediate",
            4: "upper_intermediate",
            5: "advanced",
        }
        difficulty = difficulty_map.get(int(difficulty_score), "intermediate")

        # Create or update profile
        existing = profiles.find_one({"user_id": user_id})

        profile_data = {
            "user_id": user_id,
            "learning_style": primary_style,
            "learning_style_scores": style_scores,
            "preferred_difficulty": difficulty,
            "current_level": difficulty,
            "interests": interests,
            "daily_goal_minutes": daily_goal,
            "assessment_completed": True,
            "assessment_date": datetime.utcnow(),
            "assessment_scores": {
                "style_scores": style_scores,
                "difficulty_score": difficulty_score,
            },
            "updated_at": datetime.utcnow(),
        }

        if existing:
            profiles.update_one({"user_id": user_id}, {"$set": profile_data})
        else:
            profile_data["created_at"] = datetime.utcnow()
            profiles.insert_one(profile_data)

        # Generate recommendations based on profile
        recommendations = await self._generate_recommendations(profile_data)

        logger.info(f"[LearningPath] Created profile for user {user_id}: {primary_style}, {difficulty}")

        return {
            "profile": {
                "learning_style": LEARNING_STYLES[primary_style],
                "difficulty": difficulty,
                "interests": interests,
                "daily_goal": daily_goal,
            },
            "recommendations": recommendations,
        }

    async def _generate_recommendations(self, profile: dict) -> list:
        """Generate personalized recommendations based on profile."""
        style = profile.get("learning_style", "visual")
        style_info = LEARNING_STYLES.get(style, LEARNING_STYLES["visual"])
        interests = profile.get("interests", [])

        recommendations = []

        # Feature recommendations based on learning style
        for feature in style_info["recommendations"][:3]:
            rec = {
                "type": "feature",
                "feature": feature,
                "reason": f"Great for {style_info['name']}s like you!",
            }
            recommendations.append(rec)

        # Topic recommendations based on interests
        for interest in interests[:3]:
            rec = {
                "type": "topic",
                "topic": interest,
                "reason": f"Based on your interest in {interest}",
            }
            recommendations.append(rec)

        return recommendations

    # ==================== LEARNING PROFILE ====================

    async def get_profile(self, user_id: str) -> Optional[dict]:
        """Get user's learning profile."""
        profiles = self._get_profiles()
        profile = profiles.find_one({"user_id": user_id})

        if profile:
            profile["_id"] = str(profile["_id"])
            if profile.get("learning_style"):
                profile["style_info"] = LEARNING_STYLES.get(profile["learning_style"])

        return profile

    async def update_profile(self, user_id: str, updates: dict) -> bool:
        """Update learning profile."""
        profiles = self._get_profiles()

        allowed = ["daily_goal_minutes", "preferred_languages", "goals", "interests"]
        safe_updates = {k: v for k, v in updates.items() if k in allowed}
        safe_updates["updated_at"] = datetime.utcnow()

        result = profiles.update_one(
            {"user_id": user_id},
            {"$set": safe_updates}
        )

        return result.modified_count > 0

    # ==================== ADAPTIVE DIFFICULTY ====================

    async def update_topic_proficiency(
        self,
        user_id: str,
        topic: str,
        score: float,
        activity_type: str
    ) -> dict:
        """Update user's proficiency in a topic based on activity results."""
        profiles = self._get_profiles()

        profile = profiles.find_one({"user_id": user_id})
        if not profile:
            return {}

        proficiency = profile.get("topic_proficiency", {})
        topic_data = proficiency.get(topic, {
            "level": "beginner",
            "score": 50,
            "attempts": 0,
            "last_activity": None,
        })

        # Update score with weighted average
        old_score = topic_data.get("score", 50)
        attempts = topic_data.get("attempts", 0)

        # Weight recent performance more heavily
        if attempts == 0:
            new_score = score
        else:
            weight = min(0.3 + (attempts * 0.1), 0.7)  # Max 70% weight for old scores
            new_score = (old_score * weight) + (score * (1 - weight))

        # Determine level based on score
        if new_score >= 90:
            level = "expert"
        elif new_score >= 80:
            level = "advanced"
        elif new_score >= 70:
            level = "upper_intermediate"
        elif new_score >= 60:
            level = "intermediate"
        elif new_score >= 40:
            level = "elementary"
        else:
            level = "beginner"

        topic_data.update({
            "level": level,
            "score": round(new_score, 1),
            "attempts": attempts + 1,
            "last_activity": datetime.utcnow(),
        })

        proficiency[topic] = topic_data

        profiles.update_one(
            {"user_id": user_id},
            {"$set": {"topic_proficiency": proficiency, "updated_at": datetime.utcnow()}}
        )

        # Check if difficulty adjustment needed
        adjustment = self._check_difficulty_adjustment(profile, topic, new_score)

        return {
            "topic": topic,
            "new_level": level,
            "new_score": round(new_score, 1),
            "adjustment": adjustment,
        }

    def _check_difficulty_adjustment(self, profile: dict, topic: str, score: float) -> Optional[dict]:
        """Check if difficulty should be adjusted."""

        current_difficulty = profile.get("preferred_difficulty", "intermediate")
        current_idx = DIFFICULTY_LEVELS.index(current_difficulty) if current_difficulty in DIFFICULTY_LEVELS else 2

        adjustment = None

        # If scoring very high consistently, suggest increase
        if score >= 90:
            if current_idx < len(DIFFICULTY_LEVELS) - 1:
                adjustment = {
                    "type": "increase",
                    "suggested": DIFFICULTY_LEVELS[current_idx + 1],
                    "reason": f"You're doing great! Consider increasing difficulty.",
                }

        # If scoring very low consistently, suggest decrease
        elif score < 50:
            if current_idx > 0:
                adjustment = {
                    "type": "decrease",
                    "suggested": DIFFICULTY_LEVELS[current_idx - 1],
                    "reason": f"Try an easier level to build confidence.",
                }

        return adjustment

    async def get_recommended_difficulty(self, user_id: str, topic: str = None) -> str:
        """Get recommended difficulty for a user/topic."""
        profiles = self._get_profiles()
        profile = profiles.find_one({"user_id": user_id})

        if not profile:
            return "intermediate"

        if topic:
            proficiency = profile.get("topic_proficiency", {})
            topic_data = proficiency.get(topic)
            if topic_data:
                return topic_data.get("level", profile.get("preferred_difficulty", "intermediate"))

        return profile.get("preferred_difficulty", "intermediate")

    # ==================== LEARNING PATHS ====================

    async def create_path(
        self,
        title: str,
        description: str,
        subject: str,
        lessons: List[dict],
        difficulty: str = "beginner",
        icon: str = "📚"
    ) -> dict:
        """Create a new learning path."""
        paths = self._get_paths()

        path = learning_path_schema()
        path["path_id"] = str(uuid.uuid4())
        path["title"] = title
        path["description"] = description
        path["subject"] = subject
        path["difficulty"] = difficulty
        path["lessons"] = lessons
        path["icon"] = icon
        path["estimated_hours"] = len(lessons) * 0.5  # Rough estimate

        paths.insert_one(path)

        return path

    async def generate_path(
        self,
        user_id: str,
        topic: str,
        goal: str = "",
        lesson_count: int = 10
    ) -> dict:
        """Generate a personalized learning path using AI."""

        profile = await self.get_profile(user_id)
        difficulty = profile.get("preferred_difficulty", "intermediate") if profile else "intermediate"
        style = profile.get("learning_style", "visual") if profile else "visual"

        prompt = f"""Create a learning path for "{topic}".

User profile:
- Learning style: {style}
- Difficulty: {difficulty}
- Goal: {goal if goal else "Learn " + topic}

Return JSON:
{{
    "title": "Path title",
    "description": "2-3 sentence description",
    "lessons": [
        {{
            "lesson_number": 1,
            "title": "Lesson title",
            "description": "What you'll learn",
            "activities": [
                {{
                    "type": "story|quiz|flashcards|video|practice",
                    "topic": "Specific topic",
                    "duration_minutes": 10
                }}
            ],
            "objectives": ["Objective 1", "Objective 2"]
        }}
    ],
    "skills_gained": ["Skill 1", "Skill 2"],
    "prerequisites": []
}}

Create {lesson_count} lessons with progressive difficulty.
Tailor activities to {style} learning style.
Return ONLY JSON."""

        try:
            response = generate_text(prompt, max_tokens=4000)

            start = response.find('{')
            end = response.rfind('}') + 1
            path_data = json.loads(response[start:end])

            path = await self.create_path(
                title=path_data.get("title", f"Learn {topic}"),
                description=path_data.get("description", ""),
                subject=topic,
                lessons=path_data.get("lessons", []),
                difficulty=difficulty,
            )

            # Auto-enroll user
            await self.enroll_in_path(user_id, path["path_id"])

            return path

        except Exception as e:
            logger.error(f"[LearningPath] Path generation failed: {e}")
            raise RuntimeError(f"Failed to generate learning path: {e}")

    async def get_available_paths(self, difficulty: str = None, subject: str = None) -> List[dict]:
        """Get available learning paths."""
        paths = self._get_paths()

        query = {}
        if difficulty:
            query["difficulty"] = difficulty
        if subject:
            query["subject"] = {"$regex": subject, "$options": "i"}

        available = list(paths.find(query).sort("created_at", -1))

        for path in available:
            path["_id"] = str(path["_id"])
            path["lesson_count"] = len(path.get("lessons", []))

        return available

    async def enroll_in_path(self, user_id: str, path_id: str) -> dict:
        """Enroll a user in a learning path."""
        progress = self._get_progress()
        profiles = self._get_profiles()

        # Check if already enrolled
        existing = progress.find_one({"user_id": user_id, "path_id": path_id})
        if existing:
            existing["_id"] = str(existing["_id"])
            return existing

        enrollment = user_path_progress_schema()
        enrollment["user_id"] = user_id
        enrollment["path_id"] = path_id

        progress.insert_one(enrollment)

        # Update profile
        profiles.update_one(
            {"user_id": user_id},
            {"$addToSet": {"paths_enrolled": path_id}}
        )

        return enrollment

    async def get_user_paths(self, user_id: str) -> List[dict]:
        """Get paths a user is enrolled in."""
        progress_col = self._get_progress()
        paths = self._get_paths()

        user_progress = list(progress_col.find({"user_id": user_id}))

        result = []
        for prog in user_progress:
            path = paths.find_one({"path_id": prog["path_id"]})
            if path:
                path["_id"] = str(path["_id"])
                path["progress"] = {
                    "current_lesson": prog.get("current_lesson", 0),
                    "lessons_completed": len(prog.get("lessons_completed", [])),
                    "total_lessons": len(path.get("lessons", [])),
                    "percent_complete": round(
                        len(prog.get("lessons_completed", [])) / max(len(path.get("lessons", [])), 1) * 100
                    ),
                    "last_activity": prog.get("last_activity"),
                    "completed": prog.get("completed", False),
                }
                result.append(path)

        return result

    async def complete_lesson(
        self,
        user_id: str,
        path_id: str,
        lesson_number: int,
        score: float = None
    ) -> dict:
        """Mark a lesson as complete."""
        progress_col = self._get_progress()
        paths = self._get_paths()

        path = paths.find_one({"path_id": path_id})
        if not path:
            raise ValueError("Path not found")

        total_lessons = len(path.get("lessons", []))

        progress_col.update_one(
            {"user_id": user_id, "path_id": path_id},
            {
                "$addToSet": {"lessons_completed": lesson_number},
                "$set": {
                    "current_lesson": lesson_number + 1,
                    "last_activity": datetime.utcnow(),
                },
            }
        )

        if score is not None:
            progress_col.update_one(
                {"user_id": user_id, "path_id": path_id},
                {"$set": {f"quiz_scores.lesson_{lesson_number}": score}}
            )

        # Check if path completed
        user_progress = progress_col.find_one({"user_id": user_id, "path_id": path_id})
        completed_count = len(user_progress.get("lessons_completed", []))

        if completed_count >= total_lessons:
            progress_col.update_one(
                {"user_id": user_id, "path_id": path_id},
                {"$set": {"completed": True, "completed_at": datetime.utcnow()}}
            )

        return {
            "lesson_completed": lesson_number,
            "lessons_completed": completed_count,
            "total_lessons": total_lessons,
            "path_completed": completed_count >= total_lessons,
        }


# Global instance
_learning_paths_service = None


def get_learning_paths_service() -> LearningPathsService:
    """Get or create the learning paths service instance."""
    global _learning_paths_service
    if _learning_paths_service is None:
        _learning_paths_service = LearningPathsService()
    return _learning_paths_service
