"""
AI FOR EDUCATION – Voice Learning Service
Voice commands, oral practice, and pronunciation feedback.
"""

import logging
import json
import re
from typing import Optional, Tuple
from services.gemini_service import generate_text
from services.tts_service import generate_multilingual_speech

logger = logging.getLogger(__name__)


# Voice command patterns
VOICE_COMMANDS = {
    # Story commands
    r"(tell|create|generate|make)\s+(me\s+)?(a\s+)?story\s+(about|on)\s+(.+)": "story",
    r"story\s+(about|on)\s+(.+)": "story",

    # Quiz commands
    r"(quiz|test)\s+(me\s+)?(on|about)\s+(.+)": "quiz",
    r"(start|begin)\s+(a\s+)?quiz\s+(on|about)\s+(.+)": "quiz",

    # Flashcard commands
    r"(review|study)\s+(my\s+)?flashcards?(\s+on\s+(.+))?": "flashcard_review",
    r"(create|make)\s+flashcards?\s+(about|on|for)\s+(.+)": "flashcard_create",

    # Explanation commands
    r"(explain|what\s+is|what\s+are|define)\s+(.+)": "explain",
    r"(how\s+does|how\s+do)\s+(.+)\s+(work|function)": "explain",

    # Note commands
    r"(take|create|make)\s+(a\s+)?notes?\s+(on|about)\s+(.+)": "notes",
    r"summarize\s+(.+)": "summarize",

    # Practice commands
    r"(practice|help\s+me\s+practice)\s+(.+)": "practice",
    r"(pronounce|say|speak)\s+(.+)": "pronounce",

    # Navigation commands
    r"(go\s+to|open|show)\s+(dashboard|home)": "nav_dashboard",
    r"(go\s+to|open|show)\s+(stories?|story\s+mode)": "nav_stories",
    r"(go\s+to|open|show)\s+(quiz|quizzes)": "nav_quiz",
    r"(go\s+to|open|show)\s+(flashcards?)": "nav_flashcards",
    r"(go\s+to|open|show)\s+(tutor|ai\s+tutor)": "nav_tutor",

    # Help commands
    r"(help|what\s+can\s+you\s+do|commands?)": "help",
}


class VoiceLearningService:
    """Service for voice-based learning interactions."""

    def __init__(self):
        self.commands = VOICE_COMMANDS

    def parse_voice_command(self, text: str) -> Tuple[Optional[str], Optional[dict]]:
        """
        Parse a voice command and extract intent + parameters.

        Returns: (command_type, parameters)
        """
        text = text.lower().strip()

        for pattern, command_type in self.commands.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()

                params = {}

                # Extract topic based on command type
                if command_type == "story":
                    # Find the topic in groups
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "quiz":
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "flashcard_create":
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "flashcard_review":
                    if groups and groups[-1]:
                        params["topic"] = groups[-1]

                elif command_type == "explain":
                    # Get the concept to explain
                    params["concept"] = groups[-1] if groups else ""

                elif command_type == "notes":
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "summarize":
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "practice":
                    params["topic"] = groups[-1] if groups else ""

                elif command_type == "pronounce":
                    params["text"] = groups[-1] if groups else ""

                logger.info(f"[Voice] Parsed command: {command_type} with params: {params}")

                return command_type, params

        # No pattern matched - try AI interpretation
        return self._ai_interpret_command(text)

    def _ai_interpret_command(self, text: str) -> Tuple[Optional[str], Optional[dict]]:
        """Use AI to interpret ambiguous commands."""

        prompt = f"""Interpret this voice command for a learning app: "{text}"

Available actions:
- story: Generate a story about a topic
- quiz: Start a quiz on a topic
- flashcard_create: Create flashcards for a topic
- flashcard_review: Review existing flashcards
- explain: Explain a concept
- notes: Create study notes
- summarize: Summarize a topic
- practice: Practice exercises on a topic
- help: Show help/commands
- unknown: Cannot understand

Return JSON:
{{"action": "action_name", "topic": "extracted topic or empty string", "confidence": 0.0-1.0}}

Return ONLY JSON."""

        try:
            response = generate_text(prompt, max_tokens=200)

            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])

                action = data.get("action", "unknown")
                if action == "unknown" or data.get("confidence", 0) < 0.5:
                    return None, None

                return action, {"topic": data.get("topic", "")}

        except Exception as e:
            logger.error(f"[Voice] AI interpretation failed: {e}")

        return None, None

    async def process_voice_input(
        self,
        text: str,
        user_id: str,
        language: str = "en"
    ) -> dict:
        """
        Process voice input and return appropriate response.
        """
        command_type, params = self.parse_voice_command(text)

        if not command_type:
            return {
                "success": False,
                "message": "I didn't understand that. Try saying 'help' for available commands.",
                "suggestions": [
                    "Tell me a story about space",
                    "Quiz me on history",
                    "Explain photosynthesis",
                    "Create flashcards about math",
                ]
            }

        response = {
            "success": True,
            "command": command_type,
            "params": params,
        }

        # Handle navigation commands
        if command_type.startswith("nav_"):
            route_map = {
                "nav_dashboard": "/dashboard",
                "nav_stories": "/story",
                "nav_quiz": "/quiz",
                "nav_flashcards": "/flashcards",
                "nav_tutor": "/tutor",
            }
            response["action"] = "navigate"
            response["route"] = route_map.get(command_type, "/dashboard")
            response["message"] = f"Opening {command_type.replace('nav_', '')}..."

        elif command_type == "help":
            response["action"] = "show_help"
            response["message"] = "Here's what I can do:"
            response["commands"] = [
                {"phrase": "Tell me a story about [topic]", "action": "Generate a story"},
                {"phrase": "Quiz me on [topic]", "action": "Start a quiz"},
                {"phrase": "Create flashcards about [topic]", "action": "Generate flashcards"},
                {"phrase": "Review my flashcards", "action": "Start flashcard review"},
                {"phrase": "Explain [concept]", "action": "Get an explanation"},
                {"phrase": "Take notes on [topic]", "action": "Generate study notes"},
                {"phrase": "Practice [topic]", "action": "Get practice exercises"},
            ]

        elif command_type == "explain":
            # Quick explanation via AI
            concept = params.get("concept", "")
            if concept:
                explanation = await self._quick_explain(concept, language)
                response["message"] = explanation
                response["action"] = "speak"

        elif command_type == "pronounce":
            # Generate pronunciation audio
            text_to_speak = params.get("text", "")
            if text_to_speak:
                audio_path = generate_multilingual_speech(
                    text_to_speak,
                    language=language,
                    style="teacher"
                )
                response["action"] = "play_audio"
                response["audio_url"] = f"/api/audio/{audio_path.split('/')[-1]}"
                response["message"] = f"Here's how to pronounce: {text_to_speak}"

        else:
            # Return action for frontend to handle
            response["action"] = "execute"
            response["message"] = f"Executing: {command_type}"

        return response

    async def _quick_explain(self, concept: str, language: str = "en") -> str:
        """Generate a quick voice-friendly explanation."""

        prompt = f"""Explain "{concept}" in 2-3 simple sentences.
Make it conversational and easy to understand when spoken aloud.
Language: {language}
Keep it under 50 words."""

        try:
            explanation = generate_text(prompt, max_tokens=150)
            return explanation.strip()
        except Exception as e:
            return f"I couldn't explain {concept} right now. Please try again."

    async def generate_oral_practice(
        self,
        topic: str,
        practice_type: str = "vocabulary",
        language: str = "en",
        difficulty: str = "medium"
    ) -> dict:
        """Generate oral practice exercises."""

        prompt = f"""Create oral practice exercises for "{topic}" in {language}.

Practice type: {practice_type}
Difficulty: {difficulty}

Return JSON:
{{
    "title": "Practice title",
    "instructions": "Clear spoken instructions",
    "exercises": [
        {{
            "prompt": "What the learner should say/respond to",
            "expected": "Expected correct response",
            "hint": "Hint if needed",
            "audio_prompt": "Text for TTS prompt"
        }}
    ],
    "vocabulary": ["word1", "word2"],
    "phrases": ["useful phrase 1", "useful phrase 2"]
}}

Create 5 exercises appropriate for oral practice.
Return ONLY JSON."""

        try:
            response = generate_text(prompt, max_tokens=2000)

            start = response.find('{')
            end = response.rfind('}') + 1
            practice = json.loads(response[start:end])

            return {
                "success": True,
                "practice": practice,
                "language": language,
                "topic": topic,
            }

        except Exception as e:
            logger.error(f"[Voice] Oral practice generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def check_pronunciation(
        self,
        expected_text: str,
        spoken_text: str,
        language: str = "en"
    ) -> dict:
        """
        Compare expected vs spoken text for pronunciation feedback.
        Note: This is a text comparison - actual speech recognition would be on frontend.
        """

        # Simple text comparison
        expected_words = expected_text.lower().split()
        spoken_words = spoken_text.lower().split()

        correct_words = 0
        feedback = []

        for i, expected_word in enumerate(expected_words):
            if i < len(spoken_words):
                spoken_word = spoken_words[i]
                if expected_word == spoken_word:
                    correct_words += 1
                    feedback.append({"word": expected_word, "status": "correct"})
                else:
                    feedback.append({
                        "word": expected_word,
                        "status": "incorrect",
                        "spoken": spoken_word
                    })
            else:
                feedback.append({"word": expected_word, "status": "missing"})

        accuracy = (correct_words / len(expected_words) * 100) if expected_words else 0

        return {
            "accuracy": round(accuracy, 1),
            "correct_words": correct_words,
            "total_words": len(expected_words),
            "feedback": feedback,
            "passed": accuracy >= 70,
        }

    def get_voice_tips(self, language: str = "en") -> list:
        """Get tips for voice learning."""
        tips = [
            {
                "title": "Speak Clearly",
                "description": "Pronounce words clearly and at a moderate pace for better recognition."
            },
            {
                "title": "Use Keywords",
                "description": "Start with keywords like 'story about', 'quiz me on', or 'explain'."
            },
            {
                "title": "Be Specific",
                "description": "Include the topic you want to learn about in your command."
            },
            {
                "title": "Practice Regularly",
                "description": "Regular voice practice improves both pronunciation and confidence."
            },
        ]
        return tips


# Global instance
_voice_service = None


def get_voice_service() -> VoiceLearningService:
    """Get or create the voice learning service instance."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceLearningService()
    return _voice_service
