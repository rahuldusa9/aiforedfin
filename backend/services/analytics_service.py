"""
AI FOR EDUCATION – Analytics Models & Service
Learning analytics, progress tracking, and insights.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from collections import defaultdict
from database import db

logger = logging.getLogger(__name__)


def activity_log_schema() -> dict:
    """Schema for tracking user activities."""
    return {
        "user_id": str,
        "activity_type": str,  # story, quiz, podcast, flashcard, tutor, friend
        "activity_id": str,    # ID of the specific activity
        "topic": str,
        "language": str,
        "duration_ms": 0,
        "score": None,         # For quizzes
        "metadata": {},        # Additional data
        "timestamp": datetime.utcnow(),
    }


def daily_stats_schema() -> dict:
    """Schema for daily aggregated stats."""
    return {
        "user_id": str,
        "date": str,  # YYYY-MM-DD format
        "xp_earned": 0,
        "time_spent_ms": 0,
        "activities": {
            "stories": 0,
            "quizzes": 0,
            "podcasts": 0,
            "flashcards": 0,
            "tutor_sessions": 0,
            "friend_chats": 0,
            "notes": 0,
        },
        "topics_studied": [],
        "languages_used": [],
        "quiz_accuracy": 0,
        "flashcard_accuracy": 0,
    }


class AnalyticsService:
    """Service for learning analytics and insights."""

    def __init__(self):
        self.activities = db.activity_logs if db else None
        self.daily_stats = db.daily_stats if db else None
        self.user_analytics = db.user_analytics if db else None

    def _get_activities(self):
        if self.activities is None:
            from database import db
            self.activities = db.activity_logs
        return self.activities

    def _get_daily_stats(self):
        if self.daily_stats is None:
            from database import db
            self.daily_stats = db.daily_stats
        return self.daily_stats

    def _get_user_analytics(self):
        if self.user_analytics is None:
            from database import db
            self.user_analytics = db.user_analytics
        return self.user_analytics

    # ==================== ACTIVITY LOGGING ====================

    async def log_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_id: str = None,
        topic: str = "",
        language: str = "en",
        duration_ms: int = 0,
        score: float = None,
        metadata: dict = None
    ) -> dict:
        """Log a learning activity."""
        activities = self._get_activities()

        log = activity_log_schema()
        log["user_id"] = user_id
        log["activity_type"] = activity_type
        log["activity_id"] = activity_id or ""
        log["topic"] = topic
        log["language"] = language
        log["duration_ms"] = duration_ms
        log["score"] = score
        log["metadata"] = metadata or {}
        log["timestamp"] = datetime.utcnow()

        activities.insert_one(log)

        # Update daily stats
        await self._update_daily_stats(user_id, activity_type, duration_ms, topic, language, score)

        logger.info(f"[Analytics] Logged {activity_type} for user {user_id}")

        return log

    async def _update_daily_stats(
        self,
        user_id: str,
        activity_type: str,
        duration_ms: int,
        topic: str,
        language: str,
        score: float = None
    ):
        """Update daily aggregated statistics."""
        daily = self._get_daily_stats()
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Get or create daily record
        existing = daily.find_one({"user_id": user_id, "date": today})

        if not existing:
            stats = daily_stats_schema()
            stats["user_id"] = user_id
            stats["date"] = today
            daily.insert_one(stats)

        # Map activity type to field
        activity_field = {
            "story": "stories",
            "quiz": "quizzes",
            "podcast": "podcasts",
            "flashcard": "flashcards",
            "tutor": "tutor_sessions",
            "friend": "friend_chats",
            "note": "notes",
        }.get(activity_type, activity_type + "s")

        update = {
            "$inc": {
                "time_spent_ms": duration_ms,
                f"activities.{activity_field}": 1,
            },
        }

        if topic:
            update["$addToSet"] = {"topics_studied": topic}
        if language:
            if "$addToSet" not in update:
                update["$addToSet"] = {}
            update["$addToSet"]["languages_used"] = language

        daily.update_one({"user_id": user_id, "date": today}, update)

    # ==================== ANALYTICS QUERIES ====================

    async def get_learning_summary(self, user_id: str, days: int = 30) -> dict:
        """Get comprehensive learning summary."""
        activities = self._get_activities()
        daily = self._get_daily_stats()

        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get activity logs
        user_activities = list(activities.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff}
        }))

        # Get daily stats
        start_date = cutoff.strftime("%Y-%m-%d")
        daily_records = list(daily.find({
            "user_id": user_id,
            "date": {"$gte": start_date}
        }).sort("date", 1))

        # Calculate totals
        total_time = sum(a.get("duration_ms", 0) for a in user_activities)
        total_activities = len(user_activities)

        # Activity breakdown
        activity_counts = defaultdict(int)
        for a in user_activities:
            activity_counts[a["activity_type"]] += 1

        # Topic analysis
        topics = defaultdict(int)
        for a in user_activities:
            if a.get("topic"):
                topics[a["topic"]] += 1

        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]

        # Quiz performance
        quiz_activities = [a for a in user_activities if a["activity_type"] == "quiz" and a.get("score") is not None]
        quiz_avg = sum(a["score"] for a in quiz_activities) / len(quiz_activities) if quiz_activities else 0

        # Daily activity chart data
        daily_chart = []
        for record in daily_records:
            daily_chart.append({
                "date": record["date"],
                "time_minutes": record.get("time_spent_ms", 0) / 60000,
                "activities": sum(record.get("activities", {}).values()),
            })

        # Study patterns (hour of day)
        hour_distribution = defaultdict(int)
        for a in user_activities:
            hour = a["timestamp"].hour
            hour_distribution[hour] += 1

        # Best study times
        best_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "period_days": days,
            "total_time_minutes": total_time / 60000,
            "total_activities": total_activities,
            "daily_average_minutes": (total_time / 60000) / max(days, 1),
            "activity_breakdown": dict(activity_counts),
            "top_topics": [{"topic": t[0], "count": t[1]} for t in top_topics],
            "quiz_average_score": round(quiz_avg, 1),
            "daily_chart": daily_chart,
            "best_study_hours": [{"hour": h[0], "count": h[1]} for h in best_hours],
            "languages_used": list(set(a.get("language", "en") for a in user_activities)),
        }

    async def get_strength_weakness_map(self, user_id: str) -> dict:
        """Analyze strengths and weaknesses by topic."""
        activities = self._get_activities()

        # Get quiz and flashcard activities with scores
        scored_activities = list(activities.find({
            "user_id": user_id,
            "activity_type": {"$in": ["quiz", "flashcard"]},
            "score": {"$ne": None},
            "topic": {"$ne": ""}
        }))

        topic_scores = defaultdict(list)
        for a in scored_activities:
            topic_scores[a["topic"]].append(a["score"])

        # Calculate averages and categorize
        strengths = []
        weaknesses = []
        improving = []

        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            count = len(scores)

            # Check trend (last 3 vs first 3)
            if len(scores) >= 6:
                first_avg = sum(scores[:3]) / 3
                last_avg = sum(scores[-3:]) / 3
                trend = last_avg - first_avg
            else:
                trend = 0

            topic_data = {
                "topic": topic,
                "average_score": round(avg, 1),
                "attempts": count,
                "trend": round(trend, 1),
            }

            if avg >= 80:
                strengths.append(topic_data)
            elif avg < 60:
                weaknesses.append(topic_data)
            elif trend > 10:
                improving.append(topic_data)

        # Sort each list
        strengths.sort(key=lambda x: x["average_score"], reverse=True)
        weaknesses.sort(key=lambda x: x["average_score"])
        improving.sort(key=lambda x: x["trend"], reverse=True)

        return {
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "improving": improving[:5],
            "total_topics_studied": len(topic_scores),
        }

    async def get_learning_velocity(self, user_id: str) -> dict:
        """Calculate learning velocity and predictions."""
        daily = self._get_daily_stats()

        # Get last 30 days of data
        cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        records = list(daily.find({
            "user_id": user_id,
            "date": {"$gte": cutoff}
        }).sort("date", 1))

        if len(records) < 7:
            return {
                "velocity": "insufficient_data",
                "message": "Need at least 7 days of activity for velocity analysis"
            }

        # Calculate weekly averages
        weeks = []
        for i in range(0, len(records), 7):
            week_records = records[i:i+7]
            if week_records:
                week_time = sum(r.get("time_spent_ms", 0) for r in week_records)
                week_activities = sum(sum(r.get("activities", {}).values()) for r in week_records)
                weeks.append({
                    "time_minutes": week_time / 60000,
                    "activities": week_activities,
                })

        # Calculate velocity (change between weeks)
        if len(weeks) >= 2:
            time_velocity = weeks[-1]["time_minutes"] - weeks[-2]["time_minutes"]
            activity_velocity = weeks[-1]["activities"] - weeks[-2]["activities"]

            if time_velocity > 30:
                velocity_status = "accelerating"
                velocity_message = "You're spending more time learning each week!"
            elif time_velocity < -30:
                velocity_status = "slowing"
                velocity_message = "Your study time has decreased. Try to stay consistent!"
            else:
                velocity_status = "steady"
                velocity_message = "You're maintaining a consistent study pace."
        else:
            velocity_status = "new"
            velocity_message = "Keep studying to track your learning velocity!"
            time_velocity = 0
            activity_velocity = 0

        # Predict next week
        if len(weeks) >= 2:
            predicted_time = weeks[-1]["time_minutes"] + time_velocity
            predicted_activities = weeks[-1]["activities"] + activity_velocity
        else:
            predicted_time = weeks[-1]["time_minutes"] if weeks else 0
            predicted_activities = weeks[-1]["activities"] if weeks else 0

        return {
            "velocity_status": velocity_status,
            "velocity_message": velocity_message,
            "weekly_time_change_minutes": round(time_velocity, 1),
            "weekly_activity_change": activity_velocity,
            "current_week": weeks[-1] if weeks else None,
            "predicted_next_week": {
                "time_minutes": max(0, round(predicted_time, 1)),
                "activities": max(0, predicted_activities),
            },
            "weekly_history": weeks,
        }

    async def get_time_analytics(self, user_id: str, days: int = 7) -> dict:
        """Get detailed time-based analytics."""
        activities = self._get_activities()

        cutoff = datetime.utcnow() - timedelta(days=days)
        user_activities = list(activities.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff}
        }))

        # Time by day of week
        day_time = defaultdict(int)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for a in user_activities:
            day_idx = a["timestamp"].weekday()
            day_time[day_names[day_idx]] += a.get("duration_ms", 0)

        # Time by hour
        hour_time = defaultdict(int)
        for a in user_activities:
            hour = a["timestamp"].hour
            hour_time[hour] += a.get("duration_ms", 0)

        # Find most productive times
        most_productive_day = max(day_time.items(), key=lambda x: x[1])[0] if day_time else None
        most_productive_hour = max(hour_time.items(), key=lambda x: x[1])[0] if hour_time else None

        # Session analysis
        sessions = []
        current_session = []

        sorted_activities = sorted(user_activities, key=lambda x: x["timestamp"])

        for i, a in enumerate(sorted_activities):
            if i == 0:
                current_session.append(a)
            else:
                time_gap = (a["timestamp"] - sorted_activities[i-1]["timestamp"]).total_seconds() / 60
                if time_gap <= 30:  # 30 min gap = same session
                    current_session.append(a)
                else:
                    if current_session:
                        sessions.append(current_session)
                    current_session = [a]

        if current_session:
            sessions.append(current_session)

        avg_session_length = 0
        if sessions:
            session_lengths = []
            for s in sessions:
                length = sum(a.get("duration_ms", 0) for a in s)
                session_lengths.append(length)
            avg_session_length = sum(session_lengths) / len(session_lengths) / 60000

        return {
            "period_days": days,
            "time_by_day": {d: round(t / 60000, 1) for d, t in day_time.items()},
            "time_by_hour": {h: round(t / 60000, 1) for h, t in hour_time.items()},
            "most_productive_day": most_productive_day,
            "most_productive_hour": most_productive_hour,
            "total_sessions": len(sessions),
            "average_session_minutes": round(avg_session_length, 1),
        }

    async def get_recommendations(self, user_id: str) -> list:
        """Generate personalized learning recommendations."""
        weakness_map = await self.get_strength_weakness_map(user_id)
        velocity = await self.get_learning_velocity(user_id)
        summary = await self.get_learning_summary(user_id, days=14)

        recommendations = []

        # Weakness-based recommendations
        for weakness in weakness_map.get("weaknesses", [])[:3]:
            recommendations.append({
                "type": "weakness",
                "priority": "high",
                "topic": weakness["topic"],
                "message": f"Focus on {weakness['topic']} - your average score is {weakness['average_score']}%",
                "action": "create_flashcards",
                "action_label": "Create Flashcards",
            })

        # Velocity-based recommendations
        if velocity.get("velocity_status") == "slowing":
            recommendations.append({
                "type": "engagement",
                "priority": "medium",
                "message": "Your study time has decreased. Set a daily goal to stay on track!",
                "action": "set_goal",
                "action_label": "Set Daily Goal",
            })

        # Activity-based recommendations
        activity_breakdown = summary.get("activity_breakdown", {})
        if activity_breakdown.get("flashcard", 0) == 0:
            recommendations.append({
                "type": "feature",
                "priority": "medium",
                "message": "Try flashcards! They're proven to boost memory retention.",
                "action": "explore_flashcards",
                "action_label": "Explore Flashcards",
            })

        if summary.get("quiz_average_score", 0) < 70:
            recommendations.append({
                "type": "improvement",
                "priority": "high",
                "message": "Review topics before taking quizzes to improve your scores.",
                "action": "review_weak_topics",
                "action_label": "Review Topics",
            })

        # Time-based recommendations
        if summary.get("daily_average_minutes", 0) < 15:
            recommendations.append({
                "type": "goal",
                "priority": "medium",
                "message": "Try to study at least 20 minutes daily for better results.",
                "action": "set_reminder",
                "action_label": "Set Reminder",
            })

        return recommendations[:5]


# Global instance
_analytics_service = None


def get_analytics_service() -> AnalyticsService:
    """Get or create the analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
