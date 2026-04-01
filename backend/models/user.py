"""
AI FOR EDUCATION – User Model
MongoDB document schema for users collection.
"""

from datetime import datetime, timezone


COLLECTION = "users"


def create_user_doc(username: str, email: str, hashed_password: str, full_name: str = "", role: str = "student") -> dict:
    """Build a user document for insertion."""
    now = datetime.now(timezone.utc)
    return {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "role": role,
        "created_at": now,
        "updated_at": now,
    }


def user_to_response(doc: dict) -> dict:
    """Convert a MongoDB user document to API response format."""
    return {
        "id": str(doc["_id"]),
        "username": doc["username"],
        "email": doc["email"],
        "full_name": doc.get("full_name"),
        "role": doc.get("role", "student"),
    }
