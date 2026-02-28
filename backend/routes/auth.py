"""
AI FOR EDUCATION – Authentication Routes
User registration, login, and profile management.
"""

import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId

from database import get_db
from models.user import create_user_doc, user_to_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# -------------------------------------------------------
# Request / Response Schemas
# -------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    role: str


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def _hash_password(password: str) -> str:
    """Simple SHA-256 hash (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db=Depends(get_db)):
    """Register a new user."""
    # Check existing
    existing = db.users.find_one({"$or": [{"username": req.username}, {"email": req.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    doc = create_user_doc(
        username=req.username,
        email=req.email,
        hashed_password=_hash_password(req.password),
        full_name=req.full_name,
    )
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    logger.info(f"[Auth] New user registered: {req.username}")
    return user_to_response(doc)


@router.post("/login", response_model=UserResponse)
def login(req: LoginRequest, db=Depends(get_db)):
    """Login with username and password."""
    user = db.users.find_one({"username": req.username})
    if not user or user["hashed_password"] != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    logger.info(f"[Auth] User logged in: {user['username']}")
    return user_to_response(user)


@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db=Depends(get_db)):
    """Get user by ID."""
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user_to_response(user)
