"""
AI FOR EDUCATION – Gemini AI Service
Handles all text generation via Google Gemini API.
"""

import logging
import json
import re
from typing import Optional

import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Initialize Gemini
# -------------------------------------------------------
_model = None


def _get_model():
    """Lazy-initialize the Gemini model."""
    global _model
    if _model is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("[Gemini] Model initialized.")
    return _model


def generate_text(prompt: str, max_tokens: int = 4096) -> str:
    """
    Generate text using Gemini API.
    
    Args:
        prompt: The input prompt
        max_tokens: Maximum output tokens
    
    Returns:
        Generated text string
    """
    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"[Gemini] Generation error: {e}")
        raise


def generate_podcast_script(topic: str) -> list[dict]:
    """
    Generate a structured 2-speaker podcast script.
    
    Returns:
        List of dialogue entries: [{"speaker": "Host"|"Expert", "text": "..."}]
    """
    prompt = f"""Create an educational podcast script about: "{topic}"

The podcast should have exactly 2 speakers:
- "Host" — asks questions and guides the conversation
- "Expert" — provides detailed educational explanations

Generate exactly 10-14 dialogue exchanges (alternating speakers).
Each line should be engaging, educational, and conversational.
Keep each speaker turn to 2-4 sentences maximum.

Return ONLY valid JSON array format like:
[
  {{"speaker": "Host", "text": "Welcome to our show..."}},
  {{"speaker": "Expert", "text": "Thanks for having me..."}}
]

No markdown, no code blocks, no extra text. Only the JSON array."""

    raw = generate_text(prompt, max_tokens=3000)

    # Parse JSON from response
    try:
        # Try direct parse
        script = json.loads(raw)
    except json.JSONDecodeError:
        # Extract JSON from response
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            script = json.loads(match.group())
        else:
            logger.error(f"[Gemini] Could not parse podcast script: {raw[:200]}")
            script = [
                {"speaker": "Host", "text": f"Welcome! Today we're discussing {topic}."},
                {"speaker": "Expert", "text": f"Thanks! {topic} is a fascinating subject. Let me explain the key concepts."},
                {"speaker": "Host", "text": "That sounds great. What should students know first?"},
                {"speaker": "Expert", "text": f"The fundamentals of {topic} include understanding the core principles and how they apply in real life."},
            ]

    return script


def generate_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium") -> list[dict]:
    """
    Generate quiz questions via Gemini.
    
    Returns:
        List of questions with options and correct answer.
    """
    prompt = f"""Generate exactly {num_questions} multiple-choice quiz questions about "{topic}" at {difficulty} difficulty level.

Each question must have exactly 4 options (A, B, C, D) and one correct answer.

Return ONLY valid JSON array format:
[
  {{
    "question": "What is...?",
    "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
    "correct": "A",
    "explanation": "Brief explanation of why this is correct"
  }}
]

No markdown, no code blocks, no extra text. Only the JSON array."""

    raw = generate_text(prompt, max_tokens=3000)

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            questions = json.loads(match.group())
        else:
            logger.error(f"[Gemini] Could not parse quiz: {raw[:200]}")
            questions = [{
                "question": f"What is a key concept in {topic}?",
                "options": {"A": "Concept A", "B": "Concept B", "C": "Concept C", "D": "Concept D"},
                "correct": "A",
                "explanation": "This is a fundamental concept."
            }]

    return questions[:num_questions]


def generate_story(topic: str) -> str:
    """
    Convert a topic into a narrative educational explanation.
    """
    prompt = f"""Create an engaging educational story that teaches about "{topic}".

The story should:
- Be written as a narrative (not a textbook)
- Include characters and a plot
- Weave educational concepts naturally into the narrative
- Be 400-600 words long
- Be suitable for students
- End with a brief summary of what was learned

Write the story directly, no titles or headers needed."""

    return generate_text(prompt, max_tokens=2000)


def generate_learning_path(topic: str) -> dict:
    """
    Generate a structured learning path with concepts, examples, and mini tests.
    """
    prompt = f"""Create a structured learning path for the topic: "{topic}"

Divide into exactly 4-5 steps. For each step provide:
- step_number (int)
- title (string)
- concept_explanation (detailed explanation, 3-5 sentences)
- examples (list of 2-3 practical examples)
- mini_test (one question with answer to test understanding)

Return ONLY valid JSON format:
{{
  "topic": "{topic}",
  "total_steps": 4,
  "estimated_time_minutes": 30,
  "steps": [
    {{
      "step_number": 1,
      "title": "Introduction to...",
      "concept_explanation": "...",
      "examples": ["Example 1", "Example 2"],
      "mini_test": {{
        "question": "...",
        "answer": "..."
      }}
    }}
  ]
}}

No markdown, no code blocks. Only JSON."""

    raw = generate_text(prompt, max_tokens=3000)

    try:
        path = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            path = json.loads(match.group())
        else:
            logger.error(f"[Gemini] Could not parse learning path: {raw[:200]}")
            path = {
                "topic": topic,
                "total_steps": 1,
                "estimated_time_minutes": 15,
                "steps": [{
                    "step_number": 1,
                    "title": f"Introduction to {topic}",
                    "concept_explanation": f"Let's start learning about {topic}.",
                    "examples": ["Example 1", "Example 2"],
                    "mini_test": {"question": f"What is {topic}?", "answer": "A fundamental concept."}
                }]
            }

    return path


def generate_chat_response(message: str, sentiment: str, is_negative: bool) -> str:
    """
    Generate an AI Friend chat response, adjusting tone based on sentiment.
    """
    tone_instruction = ""
    if is_negative:
        tone_instruction = """The student seems to be feeling {sentiment}. 
Please respond with extra empathy, encouragement, and support. 
Acknowledge their feelings first, then gently offer help or encouragement.
Be warm and caring.""".format(sentiment=sentiment)
    else:
        tone_instruction = "Respond in a friendly, encouraging, and helpful tone."

    prompt = f"""You are an AI study buddy and emotional support friend for a student.

{tone_instruction}

Student's message: "{message}"

Respond naturally in 2-4 sentences. Be conversational, supportive, and helpful.
If they're asking about a topic, explain briefly. If they're sharing feelings, be empathetic."""

    return generate_text(prompt, max_tokens=500)
