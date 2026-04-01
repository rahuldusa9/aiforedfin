"""
AI FOR EDUCATION – Gamification Models
XP, Badges, Streaks, Levels, Leaderboards
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class BadgeType(str, Enum):
    """Types of achievement badges."""
    # Learning Milestones
    FIRST_STORY = "first_story"
    FIRST_QUIZ = "first_quiz"
    FIRST_PODCAST = "first_podcast"
    FIRST_FLASHCARD = "first_flashcard"

    # Streak Badges
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_14 = "streak_14"
    STREAK_30 = "streak_30"
    STREAK_100 = "streak_100"

    # XP Milestones
    XP_100 = "xp_100"
    XP_500 = "xp_500"
    XP_1000 = "xp_1000"
    XP_5000 = "xp_5000"
    XP_10000 = "xp_10000"

    # Quiz Performance
    QUIZ_PERFECT = "quiz_perfect"
    QUIZ_MASTER = "quiz_master_10"
    QUIZ_LEGEND = "quiz_legend_50"

    # Explorer Badges
    LANGUAGE_EXPLORER = "language_explorer_5"
    TOPIC_EXPLORER = "topic_explorer_10"
    GENRE_MASTER = "genre_master"

    # Special
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    WEEKEND_WARRIOR = "weekend_warrior"
    SPEED_LEARNER = "speed_learner"
    CONSISTENT_LEARNER = "consistent_learner"


BADGE_INFO = {
    BadgeType.FIRST_STORY: {
        "name": "Storyteller",
        "description": "Generated your first story",
        "icon": "📖",
        "xp_reward": 50
    },
    BadgeType.FIRST_QUIZ: {
        "name": "Quiz Starter",
        "description": "Completed your first quiz",
        "icon": "❓",
        "xp_reward": 50
    },
    BadgeType.FIRST_PODCAST: {
        "name": "Podcast Pioneer",
        "description": "Created your first podcast",
        "icon": "🎙️",
        "xp_reward": 50
    },
    BadgeType.FIRST_FLASHCARD: {
        "name": "Memory Maker",
        "description": "Created your first flashcard deck",
        "icon": "🃏",
        "xp_reward": 50
    },
    BadgeType.STREAK_3: {
        "name": "Getting Started",
        "description": "3-day learning streak",
        "icon": "🔥",
        "xp_reward": 100
    },
    BadgeType.STREAK_7: {
        "name": "Week Warrior",
        "description": "7-day learning streak",
        "icon": "🔥",
        "xp_reward": 250
    },
    BadgeType.STREAK_14: {
        "name": "Fortnight Fighter",
        "description": "14-day learning streak",
        "icon": "🔥",
        "xp_reward": 500
    },
    BadgeType.STREAK_30: {
        "name": "Monthly Master",
        "description": "30-day learning streak",
        "icon": "🏆",
        "xp_reward": 1000
    },
    BadgeType.STREAK_100: {
        "name": "Centurion",
        "description": "100-day learning streak",
        "icon": "👑",
        "xp_reward": 5000
    },
    BadgeType.XP_100: {
        "name": "Beginner",
        "description": "Earned 100 XP",
        "icon": "⭐",
        "xp_reward": 0
    },
    BadgeType.XP_500: {
        "name": "Learner",
        "description": "Earned 500 XP",
        "icon": "⭐",
        "xp_reward": 0
    },
    BadgeType.XP_1000: {
        "name": "Scholar",
        "description": "Earned 1,000 XP",
        "icon": "🌟",
        "xp_reward": 0
    },
    BadgeType.XP_5000: {
        "name": "Expert",
        "description": "Earned 5,000 XP",
        "icon": "💫",
        "xp_reward": 0
    },
    BadgeType.XP_10000: {
        "name": "Master",
        "description": "Earned 10,000 XP",
        "icon": "🏅",
        "xp_reward": 0
    },
    BadgeType.QUIZ_PERFECT: {
        "name": "Perfectionist",
        "description": "Got 100% on a quiz",
        "icon": "💯",
        "xp_reward": 100
    },
    BadgeType.QUIZ_MASTER: {
        "name": "Quiz Master",
        "description": "Completed 10 quizzes",
        "icon": "🧠",
        "xp_reward": 200
    },
    BadgeType.QUIZ_LEGEND: {
        "name": "Quiz Legend",
        "description": "Completed 50 quizzes",
        "icon": "🎓",
        "xp_reward": 500
    },
    BadgeType.LANGUAGE_EXPLORER: {
        "name": "Language Explorer",
        "description": "Learned in 5 different languages",
        "icon": "🌍",
        "xp_reward": 300
    },
    BadgeType.TOPIC_EXPLORER: {
        "name": "Topic Explorer",
        "description": "Explored 10 different topics",
        "icon": "🔍",
        "xp_reward": 250
    },
    BadgeType.GENRE_MASTER: {
        "name": "Genre Master",
        "description": "Tried all story genres",
        "icon": "📚",
        "xp_reward": 200
    },
    BadgeType.EARLY_BIRD: {
        "name": "Early Bird",
        "description": "Started learning before 7 AM",
        "icon": "🌅",
        "xp_reward": 50
    },
    BadgeType.NIGHT_OWL: {
        "name": "Night Owl",
        "description": "Learning after midnight",
        "icon": "🦉",
        "xp_reward": 50
    },
    BadgeType.WEEKEND_WARRIOR: {
        "name": "Weekend Warrior",
        "description": "Learned on 4 weekends in a row",
        "icon": "⚔️",
        "xp_reward": 150
    },
    BadgeType.SPEED_LEARNER: {
        "name": "Speed Learner",
        "description": "Completed 5 activities in one session",
        "icon": "⚡",
        "xp_reward": 100
    },
    BadgeType.CONSISTENT_LEARNER: {
        "name": "Consistent Learner",
        "description": "Studied at the same time for 7 days",
        "icon": "⏰",
        "xp_reward": 150
    },
}


# XP rewards for activities
XP_REWARDS = {
    "story_generated": 25,
    "story_listened": 15,
    "quiz_completed": 30,
    "quiz_perfect": 50,
    "quiz_question_correct": 5,
    "podcast_created": 35,
    "podcast_listened": 20,
    "flashcard_created": 10,
    "flashcard_reviewed": 5,
    "flashcard_mastered": 20,
    "tutor_session": 40,
    "friend_chat": 10,
    "daily_login": 10,
    "streak_bonus": 5,  # Per day of streak
    "note_created": 15,
    "learning_path_progress": 25,
}


# Level thresholds
LEVEL_THRESHOLDS = [
    0,      # Level 1
    100,    # Level 2
    250,    # Level 3
    500,    # Level 4
    1000,   # Level 5
    1750,   # Level 6
    2750,   # Level 7
    4000,   # Level 8
    5500,   # Level 9
    7500,   # Level 10
    10000,  # Level 11
    13000,  # Level 12
    16500,  # Level 13
    20500,  # Level 14
    25000,  # Level 15
    30000,  # Level 16
    36000,  # Level 17
    43000,  # Level 18
    51000,  # Level 19
    60000,  # Level 20
]

LEVEL_NAMES = {
    1: "Newcomer",
    2: "Beginner",
    3: "Apprentice",
    4: "Student",
    5: "Learner",
    6: "Scholar",
    7: "Intellectual",
    8: "Thinker",
    9: "Sage",
    10: "Expert",
    11: "Master",
    12: "Grandmaster",
    13: "Virtuoso",
    14: "Luminary",
    15: "Prodigy",
    16: "Genius",
    17: "Visionary",
    18: "Legend",
    19: "Mythic",
    20: "Transcendent",
}


def calculate_level(xp: int) -> dict:
    """Calculate level from XP."""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
        else:
            break

    # Calculate progress to next level
    current_threshold = LEVEL_THRESHOLDS[level - 1] if level <= len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
    next_threshold = LEVEL_THRESHOLDS[level] if level < len(LEVEL_THRESHOLDS) else current_threshold + 10000

    xp_in_level = xp - current_threshold
    xp_for_level = next_threshold - current_threshold
    progress = (xp_in_level / xp_for_level) * 100 if xp_for_level > 0 else 100

    return {
        "level": level,
        "name": LEVEL_NAMES.get(level, f"Level {level}"),
        "current_xp": xp,
        "xp_in_level": xp_in_level,
        "xp_for_next_level": xp_for_level,
        "xp_to_next": next_threshold - xp,
        "progress_percent": min(progress, 100),
        "next_level_at": next_threshold,
    }


def gamification_schema() -> dict:
    """MongoDB schema for user gamification data."""
    return {
        "user_id": str,
        "xp": 0,
        "level": 1,
        "badges": [],  # List of BadgeType values
        "badge_dates": {},  # {badge_type: datetime}

        # Streak tracking
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": None,
        "streak_freeze_tokens": 2,

        # Activity counts
        "stories_generated": 0,
        "quizzes_completed": 0,
        "podcasts_created": 0,
        "flashcards_created": 0,
        "flashcards_reviewed": 0,
        "tutor_sessions": 0,
        "friend_chats": 0,
        "notes_created": 0,

        # Tracking for badges
        "perfect_quizzes": 0,
        "languages_used": [],
        "topics_explored": [],
        "genres_used": [],
        "weekend_streaks": 0,
        "session_activities": 0,
        "study_times": [],  # Track study times for consistency badge

        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def create_gamification_record(user_id: str) -> dict:
    """Create a new gamification record for a user."""
    record = gamification_schema()
    record["user_id"] = user_id
    record["created_at"] = datetime.utcnow()
    record["updated_at"] = datetime.utcnow()
    return record
