"""
AI FOR EDUCATION – Quiz Service
Handles quiz generation, scoring, and ML prediction integration.
"""

import logging
from services.gemini_service import generate_quiz
from ml.predictor import predict_performance
from models.quiz import create_quiz_result_doc

logger = logging.getLogger(__name__)


def create_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium") -> dict:
    """
    Generate a quiz via Gemini API.
    
    Returns:
        {
            "topic": str,
            "difficulty": str,
            "questions": list[dict]
        }
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")
    
    if num_questions < 1 or num_questions > 20:
        raise ValueError("Number of questions must be between 1 and 20")
    
    if difficulty not in ["easy", "medium", "hard"]:
        raise ValueError("Difficulty must be easy, medium, or hard")
    
    logger.info(f"[Quiz] Generating {num_questions} {difficulty} questions on: {topic}")
    
    try:
        questions = generate_quiz(topic, num_questions, difficulty)
        
        if not questions or len(questions) == 0:
            raise ValueError("No questions were generated")
        
        # Validate question structure
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                raise ValueError(f"Question {i} is not a valid dictionary")
            if "question" not in q or "options" not in q or "correct" not in q:
                raise ValueError(f"Question {i} is missing required fields")
            if not isinstance(q["options"], dict):
                raise ValueError(f"Question {i} options must be a dictionary")
            if len(q["options"]) != 4:
                raise ValueError(f"Question {i} must have exactly 4 options")
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": len(questions),
            "questions": questions,
        }
    except Exception as e:
        logger.error(f"[Quiz] Generation failed: {e}")
        raise


def evaluate_quiz(
    db,
    user_id: str,
    topic: str,
    difficulty: str,
    questions: list[dict],
    answers: dict,
    time_taken_seconds: float,
) -> dict:
    """
    Evaluate quiz answers, compute score, predict performance.
    
    Args:
        db: MongoDB database instance
        user_id: User ID (string)
        topic: Quiz topic
        difficulty: Difficulty level
        questions: Original questions
        answers: User answers {question_index: "A"|"B"|"C"|"D"}
        time_taken_seconds: Total time taken
    
    Returns:
        Evaluation results with ML predictions
    """
    if not questions or len(questions) == 0:
        raise ValueError("No questions provided for evaluation")
    
    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")
    
    if time_taken_seconds < 0:
        time_taken_seconds = 0
    
    # Score the quiz
    total = len(questions)
    correct = 0
    results_detail = []

    for i, q in enumerate(questions):
        user_answer = answers.get(str(i), "")
        correct_answer = q.get("correct", "")
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct += 1
            
        results_detail.append({
            "question": q.get("question", "Question not found"),
            "user_answer": user_answer if user_answer else "Not answered",
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score = (correct / total * 100) if total > 0 else 0
    avg_response_time = time_taken_seconds / total if total > 0 else 0

    # Count previous attempts for this topic
    try:
        prev_attempts = db.quiz_results.count_documents({
            "user_id": user_id,
            "topic": topic,
        })
    except Exception as e:
        logger.error(f"[Quiz] Failed to count previous attempts: {e}")
        prev_attempts = 0

    # ML Prediction
    try:
        prediction = predict_performance(
            quiz_accuracy=score / 100,
            average_response_time=avg_response_time,
            difficulty_level=difficulty,
            number_of_attempts=prev_attempts + 1,
            topic_category=topic.lower(),
        )
    except Exception as e:
        logger.error(f"[Quiz] ML prediction failed: {e}")
        prediction = {
            "predicted_performance": "medium",
            "confidence": 0.0,
            "recommended_difficulty": difficulty,
            "weakness_probability": 0.0,
            "probabilities": {"low": 0.33, "medium": 0.34, "high": 0.33},
        }

    # Save to database
    try:
        doc = create_quiz_result_doc(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            total_questions=total,
            correct_answers=correct,
            score=score,
            time_taken_seconds=time_taken_seconds,
            average_response_time=avg_response_time,
            number_of_attempts=prev_attempts + 1,
            predicted_performance=prediction["predicted_performance"],
            recommended_difficulty=prediction["recommended_difficulty"],
            weakness_probability=prediction["weakness_probability"],
        )
        result = db.quiz_results.insert_one(doc)
        quiz_result_id = str(result.inserted_id)
    except Exception as e:
        logger.error(f"[Quiz] Failed to save result to database: {e}")
        quiz_result_id = "unknown"

    return {
        "quiz_result_id": quiz_result_id,
        "score": round(score, 2),
        "correct": correct,
        "total": total,
        "average_response_time": round(avg_response_time, 2),
        "details": results_detail,
        "prediction": prediction,
    }
