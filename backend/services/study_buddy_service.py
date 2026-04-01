"""
AI FOR EDUCATION – Enhanced Study Buddy Service
Proactive AI companion with study planning, motivation, and personalized coaching.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from database import db
from services.gemini_service import generate_text
from services.analytics_service import get_analytics_service
from services.learning_paths_service import get_learning_paths_service

logger = logging.getLogger(__name__)


# Buddy personalities
BUDDY_PERSONALITIES = {
    "encouraging": {
        "name": "Sunny",
        "avatar": "🌟",
        "style": "Always positive, focuses on progress and celebrates small wins",
        "greetings": [
            "Hey there, superstar! Ready to learn something amazing today?",
            "Welcome back! I'm so excited to see you!",
            "You're doing great! Let's make today count!",
        ]
    },
    "focused": {
        "name": "Scholar",
        "avatar": "🎯",
        "style": "Goal-oriented, keeps you on track, direct but supportive",
        "greetings": [
            "Good to see you! Let's focus and make progress.",
            "Welcome back! I've got your study plan ready.",
            "Let's hit those learning goals today!",
        ]
    },
    "curious": {
        "name": "Spark",
        "avatar": "💡",
        "style": "Asks questions, sparks curiosity, makes learning fun",
        "greetings": [
            "Did you know something interesting happened today? Let me tell you!",
            "I've been thinking about what we could explore today...",
            "What questions do you have? I love finding answers together!",
        ]
    },
    "calm": {
        "name": "Zen",
        "avatar": "🧘",
        "style": "Patient, reassuring, reduces anxiety about learning",
        "greetings": [
            "Take a deep breath. Learning is a journey, not a race.",
            "Welcome! Remember, every small step matters.",
            "It's okay to go at your own pace. I'm here for you.",
        ]
    },
}


def buddy_state_schema() -> dict:
    """Schema for buddy conversation state."""
    return {
        "user_id": str,
        "personality": "encouraging",
        "conversation_history": [],  # Last N messages
        "last_interaction": None,
        "mood_history": [],  # User mood tracking
        "check_in_preferences": {
            "frequency": "daily",
            "preferred_time": "09:00",
            "enabled": True,
        },
        "study_plan": None,
        "goals": [],
        "achievements_mentioned": [],
        "topics_discussed": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


class StudyBuddyService:
    """Enhanced AI Study Buddy with proactive features."""

    def __init__(self):
        self.buddy_states = db.buddy_states if db else None
        self.analytics = get_analytics_service()
        self.learning_paths = get_learning_paths_service()

    def _get_states(self):
        if self.buddy_states is None:
            from database import db
            self.buddy_states = db.buddy_states
        return self.buddy_states

    # ==================== CONVERSATION ====================

    async def chat(
        self,
        user_id: str,
        message: str,
        context: dict = None
    ) -> dict:
        """Have a conversation with the study buddy."""

        state = await self._get_or_create_state(user_id)
        personality = BUDDY_PERSONALITIES[state.get("personality", "encouraging")]

        # Get user context for personalization
        user_context = await self._get_user_context(user_id)

        # Build conversation prompt
        history = state.get("conversation_history", [])[-6:]  # Last 6 messages

        history_text = "\n".join([
            f"{'User' if m['role'] == 'user' else 'Buddy'}: {m['content']}"
            for m in history
        ])

        prompt = f"""You are {personality['name']}, an AI study buddy.
Personality: {personality['style']}
Avatar: {personality['avatar']}

USER CONTEXT:
- Current streak: {user_context.get('streak', 0)} days
- XP: {user_context.get('xp', 0)}
- Recent topics: {', '.join(user_context.get('recent_topics', [])[:3])}
- Weak areas: {', '.join(user_context.get('weak_areas', [])[:2])}
- Last study: {user_context.get('last_study', 'Unknown')}
- Current mood: {context.get('mood', 'neutral') if context else 'neutral'}

CONVERSATION HISTORY:
{history_text}

User: {message}

Respond as {personality['name']}. Be helpful, personalized, and engaging.
If they seem stuck, offer specific suggestions.
If they're doing well, celebrate!
Keep response under 100 words unless explaining something complex.
If they ask for help with studying, offer actionable advice.

{personality['name']}:"""

        try:
            response = generate_text(prompt, max_tokens=300)

            # Update state
            await self._update_conversation(user_id, message, response.strip())

            # Detect if user needs support
            support_needed = await self._detect_support_need(message)

            result = {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": response.strip(),
                "timestamp": datetime.utcnow().isoformat(),
            }

            if support_needed:
                result["suggestions"] = support_needed

            return result

        except Exception as e:
            logger.error(f"[StudyBuddy] Chat failed: {e}")
            return {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": "Hmm, I had a little trouble there. Can you try again?",
                "error": True,
            }

    async def _get_or_create_state(self, user_id: str) -> dict:
        """Get or create buddy state for a user."""
        states = self._get_states()

        state = states.find_one({"user_id": user_id})
        if not state:
            state = buddy_state_schema()
            state["user_id"] = user_id
            states.insert_one(state)
            state = states.find_one({"user_id": user_id})

        return state

    async def _update_conversation(self, user_id: str, user_msg: str, buddy_msg: str):
        """Update conversation history."""
        states = self._get_states()

        states.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "conversation_history": {
                        "$each": [
                            {"role": "user", "content": user_msg, "time": datetime.utcnow()},
                            {"role": "buddy", "content": buddy_msg, "time": datetime.utcnow()},
                        ],
                        "$slice": -20,  # Keep last 20 messages
                    }
                },
                "$set": {
                    "last_interaction": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            }
        )

    async def _detect_support_need(self, message: str) -> Optional[list]:
        """Detect if user needs specific support."""
        lower_msg = message.lower()

        suggestions = []

        # Struggling indicators
        if any(word in lower_msg for word in ["stuck", "confused", "don't understand", "hard", "difficult"]):
            suggestions.append({
                "type": "explain",
                "label": "Get a simple explanation",
                "action": "explain_topic"
            })

        # Motivation indicators
        if any(word in lower_msg for word in ["bored", "tired", "unmotivated", "give up"]):
            suggestions.append({
                "type": "motivation",
                "label": "Take a quick break activity",
                "action": "break_activity"
            })
            suggestions.append({
                "type": "switch",
                "label": "Try a different topic",
                "action": "suggest_topics"
            })

        # Study help indicators
        if any(word in lower_msg for word in ["study", "learn", "prepare", "exam", "test"]):
            suggestions.append({
                "type": "plan",
                "label": "Create a study plan",
                "action": "create_plan"
            })

        return suggestions if suggestions else None

    async def _get_user_context(self, user_id: str) -> dict:
        """Get user context for personalization."""
        try:
            # Get analytics summary
            summary = await self.analytics.get_learning_summary(user_id, days=7)
            weakness = await self.analytics.get_strength_weakness_map(user_id)

            # Get gamification data
            from services.gamification_service import get_gamification_service
            gamification = get_gamification_service()
            stats = await gamification.get_user_stats(user_id)

            return {
                "streak": stats.get("current_streak", 0),
                "xp": stats.get("xp", 0),
                "level": stats.get("level", {}).get("level", 1),
                "recent_topics": summary.get("top_topics", [])[:3],
                "weak_areas": [w["topic"] for w in weakness.get("weaknesses", [])[:2]],
                "last_study": summary.get("daily_chart", [{}])[-1].get("date", "Unknown"),
                "daily_minutes": summary.get("daily_average_minutes", 0),
            }
        except Exception as e:
            logger.error(f"[StudyBuddy] Context fetch failed: {e}")
            return {}

    # ==================== PROACTIVE CHECK-INS ====================

    async def get_check_in(self, user_id: str) -> dict:
        """Generate a proactive check-in message."""

        state = await self._get_or_create_state(user_id)
        personality = BUDDY_PERSONALITIES[state.get("personality", "encouraging")]
        user_context = await self._get_user_context(user_id)

        # Determine check-in type based on context
        check_in_type = "general"
        insights = []

        last_interaction = state.get("last_interaction")
        if last_interaction:
            days_since = (datetime.utcnow() - last_interaction).days

            if days_since >= 3:
                check_in_type = "return"
                insights.append(f"Haven't seen you in {days_since} days")
            elif days_since == 0 and user_context.get("daily_minutes", 0) > 30:
                check_in_type = "celebration"
                insights.append("Great study session today!")

        # Check streak
        streak = user_context.get("streak", 0)
        if streak >= 7 and streak % 7 == 0:
            check_in_type = "milestone"
            insights.append(f"Incredible {streak}-day streak!")

        # Check weak areas
        weak_areas = user_context.get("weak_areas", [])
        if weak_areas:
            insights.append(f"Could use practice: {weak_areas[0]}")

        prompt = f"""Generate a proactive check-in message as {personality['name']}.
Personality: {personality['style']}
Check-in type: {check_in_type}
User insights: {', '.join(insights)}
User streak: {streak} days
User level: {user_context.get('level', 1)}

Create a brief, engaging check-in (2-3 sentences max).
Include one specific, actionable suggestion.
Match the personality style.

Message:"""

        try:
            message = generate_text(prompt, max_tokens=150)

            return {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": message.strip(),
                "type": check_in_type,
                "insights": insights,
                "suggestions": await self._get_check_in_suggestions(user_id, check_in_type),
            }

        except Exception as e:
            import random
            return {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": random.choice(personality["greetings"]),
                "type": "general",
            }

    async def _get_check_in_suggestions(self, user_id: str, check_in_type: str) -> list:
        """Get suggestions for check-in."""
        suggestions = []

        if check_in_type == "return":
            suggestions = [
                {"label": "Quick 5-min review", "action": "quick_review"},
                {"label": "See what's new", "action": "show_new"},
            ]
        elif check_in_type == "celebration":
            suggestions = [
                {"label": "Keep the momentum!", "action": "continue_study"},
                {"label": "View your progress", "action": "show_progress"},
            ]
        elif check_in_type == "milestone":
            suggestions = [
                {"label": "Share achievement", "action": "share"},
                {"label": "Set new goal", "action": "set_goal"},
            ]
        else:
            suggestions = [
                {"label": "Start studying", "action": "start_study"},
                {"label": "Review flashcards", "action": "review_flashcards"},
            ]

        return suggestions

    # ==================== STUDY PLANNING ====================

    async def create_study_plan(
        self,
        user_id: str,
        goals: List[str],
        available_time_minutes: int = 60,
        days: int = 7
    ) -> dict:
        """Create a personalized study plan."""

        user_context = await self._get_user_context(user_id)
        profile = await self.learning_paths.get_profile(user_id)

        style = profile.get("learning_style", "visual") if profile else "visual"
        weak_areas = user_context.get("weak_areas", [])

        prompt = f"""Create a {days}-day study plan.

User profile:
- Learning style: {style}
- Available time: {available_time_minutes} minutes/day
- Goals: {', '.join(goals)}
- Weak areas to focus on: {', '.join(weak_areas)}
- Current streak: {user_context.get('streak', 0)} days

Return JSON:
{{
    "plan_name": "Plan title",
    "summary": "Brief overview",
    "daily_plans": [
        {{
            "day": 1,
            "focus": "Main focus for the day",
            "activities": [
                {{"type": "flashcards|quiz|story|notes", "topic": "topic", "duration": 15, "priority": "high|medium|low"}}
            ],
            "goal": "What to achieve",
            "motivation": "Encouraging note"
        }}
    ],
    "tips": ["Study tip 1", "Study tip 2"],
    "milestones": [
        {{"day": 3, "milestone": "Description"}},
        {{"day": 7, "milestone": "Description"}}
    ]
}}

Create a realistic, balanced plan.
Return ONLY JSON."""

        try:
            response = generate_text(prompt, max_tokens=3000)

            start = response.find('{')
            end = response.rfind('}') + 1
            plan = json.loads(response[start:end])

            # Save plan to state
            states = self._get_states()
            states.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "study_plan": plan,
                        "goals": goals,
                        "updated_at": datetime.utcnow(),
                    }
                }
            )

            logger.info(f"[StudyBuddy] Created study plan for user {user_id}")

            return plan

        except Exception as e:
            logger.error(f"[StudyBuddy] Plan creation failed: {e}")
            raise RuntimeError(f"Failed to create study plan: {e}")

    async def get_study_plan(self, user_id: str) -> Optional[dict]:
        """Get user's current study plan."""
        state = await self._get_or_create_state(user_id)
        return state.get("study_plan")

    async def get_todays_tasks(self, user_id: str) -> dict:
        """Get today's tasks from the study plan."""
        plan = await self.get_study_plan(user_id)

        if not plan:
            return {
                "has_plan": False,
                "message": "No study plan set. Would you like me to create one?",
            }

        # Calculate which day of the plan we're on
        # For now, just return day 1 or cycle through
        daily_plans = plan.get("daily_plans", [])
        if not daily_plans:
            return {"has_plan": False}

        # Get current day (simple implementation - could track actual start date)
        day_index = datetime.utcnow().weekday() % len(daily_plans)
        today = daily_plans[day_index]

        return {
            "has_plan": True,
            "day": today.get("day", day_index + 1),
            "focus": today.get("focus", ""),
            "activities": today.get("activities", []),
            "goal": today.get("goal", ""),
            "motivation": today.get("motivation", ""),
        }

    # ==================== MOTIVATION & COACHING ====================

    async def get_motivation(self, user_id: str, context: str = "") -> dict:
        """Get a motivational message."""

        state = await self._get_or_create_state(user_id)
        personality = BUDDY_PERSONALITIES[state.get("personality", "encouraging")]
        user_context = await self._get_user_context(user_id)

        prompt = f"""Generate a motivational message as {personality['name']}.
User context: {context if context else 'General motivation needed'}
User streak: {user_context.get('streak', 0)} days
User XP: {user_context.get('xp', 0)}

Create a short, powerful motivational message (2-3 sentences).
Be specific to their progress if possible.
End with an encouraging call to action.

Message:"""

        try:
            message = generate_text(prompt, max_tokens=150)

            return {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": message.strip(),
                "type": "motivation",
            }

        except Exception as e:
            return {
                "buddy": personality["name"],
                "avatar": personality["avatar"],
                "message": "You're capable of amazing things. Keep going! 💪",
                "type": "motivation",
            }

    async def explain_simply(self, topic: str, level: str = "eli5") -> dict:
        """Explain a topic simply (Explain Like I'm 5)."""

        level_prompts = {
            "eli5": "Explain like I'm 5 years old. Use simple words and fun comparisons.",
            "simple": "Explain simply for a beginner. Avoid jargon.",
            "detailed": "Explain in detail but still accessible.",
        }

        prompt = f"""{level_prompts.get(level, level_prompts['simple'])}

Topic: {topic}

Give a clear, memorable explanation in 3-4 sentences.
Use a relatable analogy if helpful.

Explanation:"""

        try:
            explanation = generate_text(prompt, max_tokens=200)

            return {
                "topic": topic,
                "level": level,
                "explanation": explanation.strip(),
            }

        except Exception as e:
            return {
                "topic": topic,
                "error": str(e),
            }

    # ==================== PERSONALITY ====================

    async def set_personality(self, user_id: str, personality: str) -> dict:
        """Set buddy personality."""
        if personality not in BUDDY_PERSONALITIES:
            raise ValueError(f"Invalid personality: {personality}")

        states = self._get_states()
        states.update_one(
            {"user_id": user_id},
            {"$set": {"personality": personality, "updated_at": datetime.utcnow()}}
        )

        info = BUDDY_PERSONALITIES[personality]
        return {
            "personality": personality,
            "name": info["name"],
            "avatar": info["avatar"],
            "message": f"Hi! I'm {info['name']}. {info['greetings'][0]}",
        }

    async def get_personalities(self) -> list:
        """Get available personalities."""
        return [
            {
                "id": key,
                "name": info["name"],
                "avatar": info["avatar"],
                "description": info["style"],
            }
            for key, info in BUDDY_PERSONALITIES.items()
        ]


# Global instance
_buddy_service = None


def get_study_buddy_service() -> StudyBuddyService:
    """Get or create the study buddy service instance."""
    global _buddy_service
    if _buddy_service is None:
        _buddy_service = StudyBuddyService()
    return _buddy_service
