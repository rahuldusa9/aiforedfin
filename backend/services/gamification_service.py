"""
AI FOR EDUCATION – Gamification Service
Handles XP, badges, streaks, levels, and leaderboards.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from database import db
from models.gamification import (
    BadgeType, BADGE_INFO, XP_REWARDS, calculate_level,
    create_gamification_record, LEVEL_NAMES
)

logger = logging.getLogger(__name__)


class GamificationService:
    """Service for managing user gamification."""

    def __init__(self):
        self.collection = db.gamification if db else None

    def _get_collection(self):
        """Get the gamification collection."""
        if self.collection is None:
            from database import db
            self.collection = db.gamification
        return self.collection

    async def get_user_stats(self, user_id: str) -> dict:
        """Get or create gamification stats for a user."""
        collection = self._get_collection()
        stats = collection.find_one({"user_id": user_id})

        if not stats:
            stats = create_gamification_record(user_id)
            collection.insert_one(stats)
            stats = collection.find_one({"user_id": user_id})

        # Calculate level info
        level_info = calculate_level(stats.get("xp", 0))

        # Format badges
        badges = []
        badge_dates = stats.get("badge_dates", {})
        for badge_type in stats.get("badges", []):
            badge_info = BADGE_INFO.get(BadgeType(badge_type), {})
            badges.append({
                "type": badge_type,
                "name": badge_info.get("name", badge_type),
                "description": badge_info.get("description", ""),
                "icon": badge_info.get("icon", "🏆"),
                "earned_at": badge_dates.get(badge_type),
            })

        return {
            "user_id": user_id,
            "xp": stats.get("xp", 0),
            "level": level_info,
            "badges": badges,
            "badge_count": len(badges),
            "current_streak": stats.get("current_streak", 0),
            "longest_streak": stats.get("longest_streak", 0),
            "streak_freeze_tokens": stats.get("streak_freeze_tokens", 2),
            "stats": {
                "stories_generated": stats.get("stories_generated", 0),
                "quizzes_completed": stats.get("quizzes_completed", 0),
                "podcasts_created": stats.get("podcasts_created", 0),
                "flashcards_created": stats.get("flashcards_created", 0),
                "flashcards_reviewed": stats.get("flashcards_reviewed", 0),
                "tutor_sessions": stats.get("tutor_sessions", 0),
                "notes_created": stats.get("notes_created", 0),
            },
            "last_activity": stats.get("last_activity_date"),
        }

    async def award_xp(self, user_id: str, activity: str, bonus_multiplier: float = 1.0) -> dict:
        """Award XP for an activity."""
        collection = self._get_collection()

        base_xp = XP_REWARDS.get(activity, 0)
        xp_earned = int(base_xp * bonus_multiplier)

        if xp_earned <= 0:
            return {"xp_earned": 0}

        # Get current stats
        stats = collection.find_one({"user_id": user_id})
        if not stats:
            stats = create_gamification_record(user_id)
            collection.insert_one(stats)

        old_xp = stats.get("xp", 0)
        new_xp = old_xp + xp_earned

        old_level = calculate_level(old_xp)["level"]
        new_level_info = calculate_level(new_xp)

        # Update XP
        collection.update_one(
            {"user_id": user_id},
            {
                "$set": {"xp": new_xp, "updated_at": datetime.utcnow()},
                "$inc": {f"{activity.replace('_', '_')}s" if not activity.endswith('s') else activity: 1}
            }
        )

        result = {
            "xp_earned": xp_earned,
            "total_xp": new_xp,
            "level": new_level_info,
            "leveled_up": new_level_info["level"] > old_level,
        }

        # Check for XP badges
        new_badges = await self._check_xp_badges(user_id, new_xp)
        if new_badges:
            result["new_badges"] = new_badges

        logger.info(f"[Gamification] User {user_id} earned {xp_earned} XP for {activity}")

        return result

    async def update_streak(self, user_id: str) -> dict:
        """Update user's learning streak."""
        collection = self._get_collection()
        today = datetime.utcnow().date()

        stats = collection.find_one({"user_id": user_id})
        if not stats:
            stats = create_gamification_record(user_id)
            collection.insert_one(stats)

        last_activity = stats.get("last_activity_date")
        current_streak = stats.get("current_streak", 0)
        longest_streak = stats.get("longest_streak", 0)

        if last_activity:
            last_date = last_activity.date() if isinstance(last_activity, datetime) else last_activity
            days_diff = (today - last_date).days

            if days_diff == 0:
                # Already logged in today
                return {
                    "streak": current_streak,
                    "streak_maintained": True,
                    "streak_increased": False,
                }
            elif days_diff == 1:
                # Consecutive day - increase streak
                current_streak += 1
            elif days_diff == 2 and stats.get("streak_freeze_tokens", 0) > 0:
                # Missed one day but has freeze token
                collection.update_one(
                    {"user_id": user_id},
                    {"$inc": {"streak_freeze_tokens": -1}}
                )
                current_streak += 1
            else:
                # Streak broken
                current_streak = 1
        else:
            current_streak = 1

        # Update longest streak
        if current_streak > longest_streak:
            longest_streak = current_streak

        # Calculate streak bonus XP
        streak_bonus = current_streak * XP_REWARDS["streak_bonus"]

        collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "last_activity_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                "$inc": {"xp": streak_bonus}
            }
        )

        # Check for streak badges
        new_badges = await self._check_streak_badges(user_id, current_streak)

        result = {
            "streak": current_streak,
            "longest_streak": longest_streak,
            "streak_bonus_xp": streak_bonus,
            "streak_increased": True,
        }

        if new_badges:
            result["new_badges"] = new_badges

        logger.info(f"[Gamification] User {user_id} streak: {current_streak} days")

        return result

    async def award_badge(self, user_id: str, badge_type: BadgeType) -> Optional[dict]:
        """Award a badge to a user."""
        collection = self._get_collection()

        stats = collection.find_one({"user_id": user_id})
        if not stats:
            return None

        # Check if already has badge
        if badge_type.value in stats.get("badges", []):
            return None

        badge_info = BADGE_INFO.get(badge_type, {})
        xp_reward = badge_info.get("xp_reward", 0)

        collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"badges": badge_type.value},
                "$set": {
                    f"badge_dates.{badge_type.value}": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                "$inc": {"xp": xp_reward}
            }
        )

        logger.info(f"[Gamification] User {user_id} earned badge: {badge_type.value}")

        return {
            "type": badge_type.value,
            "name": badge_info.get("name", badge_type.value),
            "description": badge_info.get("description", ""),
            "icon": badge_info.get("icon", "🏆"),
            "xp_reward": xp_reward,
        }

    async def _check_xp_badges(self, user_id: str, xp: int) -> list:
        """Check and award XP milestone badges."""
        new_badges = []

        xp_badges = [
            (100, BadgeType.XP_100),
            (500, BadgeType.XP_500),
            (1000, BadgeType.XP_1000),
            (5000, BadgeType.XP_5000),
            (10000, BadgeType.XP_10000),
        ]

        for threshold, badge_type in xp_badges:
            if xp >= threshold:
                badge = await self.award_badge(user_id, badge_type)
                if badge:
                    new_badges.append(badge)

        return new_badges

    async def _check_streak_badges(self, user_id: str, streak: int) -> list:
        """Check and award streak badges."""
        new_badges = []

        streak_badges = [
            (3, BadgeType.STREAK_3),
            (7, BadgeType.STREAK_7),
            (14, BadgeType.STREAK_14),
            (30, BadgeType.STREAK_30),
            (100, BadgeType.STREAK_100),
        ]

        for threshold, badge_type in streak_badges:
            if streak >= threshold:
                badge = await self.award_badge(user_id, badge_type)
                if badge:
                    new_badges.append(badge)

        return new_badges

    async def track_activity(self, user_id: str, activity_type: str, metadata: dict = None) -> dict:
        """Track an activity and award appropriate XP/badges."""
        collection = self._get_collection()

        # Update streak first
        streak_result = await self.update_streak(user_id)

        # Award XP for the activity
        xp_result = await self.award_xp(user_id, activity_type)

        # Track specific activities for badges
        stats = collection.find_one({"user_id": user_id})
        new_badges = []

        if activity_type == "story_generated":
            if stats.get("stories_generated", 0) == 0:
                badge = await self.award_badge(user_id, BadgeType.FIRST_STORY)
                if badge:
                    new_badges.append(badge)

            # Track language
            if metadata and metadata.get("language"):
                collection.update_one(
                    {"user_id": user_id},
                    {"$addToSet": {"languages_used": metadata["language"]}}
                )
                # Check language explorer badge
                updated = collection.find_one({"user_id": user_id})
                if len(updated.get("languages_used", [])) >= 5:
                    badge = await self.award_badge(user_id, BadgeType.LANGUAGE_EXPLORER)
                    if badge:
                        new_badges.append(badge)

            # Track topic
            if metadata and metadata.get("topic"):
                collection.update_one(
                    {"user_id": user_id},
                    {"$addToSet": {"topics_explored": metadata["topic"]}}
                )
                updated = collection.find_one({"user_id": user_id})
                if len(updated.get("topics_explored", [])) >= 10:
                    badge = await self.award_badge(user_id, BadgeType.TOPIC_EXPLORER)
                    if badge:
                        new_badges.append(badge)

        elif activity_type == "quiz_completed":
            if stats.get("quizzes_completed", 0) == 0:
                badge = await self.award_badge(user_id, BadgeType.FIRST_QUIZ)
                if badge:
                    new_badges.append(badge)

            # Check if perfect score
            if metadata and metadata.get("score") == 100:
                badge = await self.award_badge(user_id, BadgeType.QUIZ_PERFECT)
                if badge:
                    new_badges.append(badge)
                collection.update_one(
                    {"user_id": user_id},
                    {"$inc": {"perfect_quizzes": 1}}
                )

            # Check quiz master badges
            quizzes = stats.get("quizzes_completed", 0) + 1
            if quizzes >= 10:
                badge = await self.award_badge(user_id, BadgeType.QUIZ_MASTER)
                if badge:
                    new_badges.append(badge)
            if quizzes >= 50:
                badge = await self.award_badge(user_id, BadgeType.QUIZ_LEGEND)
                if badge:
                    new_badges.append(badge)

        elif activity_type == "podcast_created":
            if stats.get("podcasts_created", 0) == 0:
                badge = await self.award_badge(user_id, BadgeType.FIRST_PODCAST)
                if badge:
                    new_badges.append(badge)

        elif activity_type == "flashcard_created":
            if stats.get("flashcards_created", 0) == 0:
                badge = await self.award_badge(user_id, BadgeType.FIRST_FLASHCARD)
                if badge:
                    new_badges.append(badge)

        # Check time-based badges
        hour = datetime.utcnow().hour
        if hour < 7:
            badge = await self.award_badge(user_id, BadgeType.EARLY_BIRD)
            if badge:
                new_badges.append(badge)
        elif hour >= 0 and hour < 5:
            badge = await self.award_badge(user_id, BadgeType.NIGHT_OWL)
            if badge:
                new_badges.append(badge)

        return {
            "activity": activity_type,
            "xp": xp_result,
            "streak": streak_result,
            "new_badges": new_badges + xp_result.get("new_badges", []) + streak_result.get("new_badges", []),
        }

    async def get_leaderboard(self, limit: int = 10, timeframe: str = "all") -> list:
        """Get the XP leaderboard."""
        collection = self._get_collection()

        # Build query based on timeframe
        query = {}
        if timeframe == "weekly":
            week_ago = datetime.utcnow() - timedelta(days=7)
            query["updated_at"] = {"$gte": week_ago}
        elif timeframe == "monthly":
            month_ago = datetime.utcnow() - timedelta(days=30)
            query["updated_at"] = {"$gte": month_ago}

        # Get top users by XP
        cursor = collection.find(query).sort("xp", -1).limit(limit)

        leaderboard = []
        rank = 1
        for stats in cursor:
            level_info = calculate_level(stats.get("xp", 0))
            leaderboard.append({
                "rank": rank,
                "user_id": stats["user_id"],
                "xp": stats.get("xp", 0),
                "level": level_info["level"],
                "level_name": level_info["name"],
                "streak": stats.get("current_streak", 0),
                "badge_count": len(stats.get("badges", [])),
            })
            rank += 1

        return leaderboard

    async def get_available_badges(self) -> list:
        """Get all available badges with info."""
        badges = []
        for badge_type, info in BADGE_INFO.items():
            badges.append({
                "type": badge_type.value,
                "name": info["name"],
                "description": info["description"],
                "icon": info["icon"],
                "xp_reward": info["xp_reward"],
            })
        return badges

    async def use_streak_freeze(self, user_id: str) -> dict:
        """Use a streak freeze token."""
        collection = self._get_collection()
        stats = collection.find_one({"user_id": user_id})

        if not stats or stats.get("streak_freeze_tokens", 0) <= 0:
            return {"success": False, "message": "No streak freeze tokens available"}

        collection.update_one(
            {"user_id": user_id},
            {"$inc": {"streak_freeze_tokens": -1}}
        )

        return {
            "success": True,
            "tokens_remaining": stats["streak_freeze_tokens"] - 1,
        }


# Global instance
_gamification_service = None


def get_gamification_service() -> GamificationService:
    """Get or create the gamification service instance."""
    global _gamification_service
    if _gamification_service is None:
        _gamification_service = GamificationService()
    return _gamification_service
