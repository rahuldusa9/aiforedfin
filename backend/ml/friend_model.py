"""
AI FOR EDUCATION - AI Friend Model
Custom ML model for conversational advice without API dependency.
"""

import pickle
import logging
import random
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

ML_DIR = Path(__file__).parent
FRIEND_MODEL_PATH = ML_DIR / "friend_model.pkl"

# Cached model
_friend_model = None

# =============================================================================
# TRAINING DATA - Intent Classification
# =============================================================================

INTENT_TRAINING_DATA = [
    # RELATIONSHIP / CRUSH
    ("i have a crush on someone", "relationship"),
    ("how do i impress a girl", "relationship"),
    ("how to ask someone out", "relationship"),
    ("i like someone but scared to tell", "relationship"),
    ("how to talk to my crush", "relationship"),
    ("she doesn't like me back", "relationship"),
    ("how to get over a breakup", "relationship"),
    ("my girlfriend is angry with me", "relationship"),
    ("how to make friends", "relationship"),
    ("i feel lonely no friends", "relationship"),
    ("how to be popular", "relationship"),
    ("my friend betrayed me", "relationship"),
    ("how to apologize to someone", "relationship"),
    ("i had a fight with my best friend", "relationship"),
    ("how to confess my feelings", "relationship"),

    # ACADEMICS / STUDY
    ("i failed my exam", "academics"),
    ("how to study better", "academics"),
    ("i got bad marks", "academics"),
    ("can't concentrate on studies", "academics"),
    ("how to prepare for exams", "academics"),
    ("i don't understand this subject", "academics"),
    ("how to improve my grades", "academics"),
    ("i'm falling behind in class", "academics"),
    ("how to memorize faster", "academics"),
    ("i have exam tomorrow not prepared", "academics"),
    ("which career should i choose", "academics"),
    ("how to manage study time", "academics"),
    ("i hate studying", "academics"),
    ("my teacher doesn't like me", "academics"),
    ("how to focus while studying", "academics"),

    # FAMILY
    ("my parents don't understand me", "family"),
    ("dad will scold me", "family"),
    ("mom is always angry", "family"),
    ("parents fighting at home", "family"),
    ("how to talk to strict parents", "family"),
    ("my parents compare me to others", "family"),
    ("i want more freedom from parents", "family"),
    ("family doesn't support my dreams", "family"),
    ("how to convince my parents", "family"),
    ("sibling always annoys me", "family"),
    ("parents don't trust me", "family"),
    ("how to make parents proud", "family"),
    ("my parents are divorcing", "family"),
    ("i feel like a disappointment to family", "family"),
    ("parents expect too much from me", "family"),

    # STRESS / ANXIETY
    ("i'm feeling stressed", "stress"),
    ("i'm anxious about everything", "stress"),
    ("can't sleep at night", "stress"),
    ("feeling overwhelmed", "stress"),
    ("too much pressure", "stress"),
    ("i feel like giving up", "stress"),
    ("nothing is going right", "stress"),
    ("i'm scared of failing", "stress"),
    ("feeling hopeless", "stress"),
    ("i cry a lot lately", "stress"),
    ("how to deal with anxiety", "stress"),
    ("i overthink everything", "stress"),
    ("feeling depressed", "stress"),
    ("life is too hard", "stress"),
    ("i need motivation", "stress"),

    # CONFIDENCE / SELF-IMPROVEMENT
    ("i have low self confidence", "confidence"),
    ("how to be more confident", "confidence"),
    ("i'm too shy", "confidence"),
    ("people make fun of me", "confidence"),
    ("i don't like how i look", "confidence"),
    ("how to speak in public", "confidence"),
    ("i'm afraid of what others think", "confidence"),
    ("how to stop being nervous", "confidence"),
    ("i want to improve myself", "confidence"),
    ("how to be more social", "confidence"),
    ("i feel inferior to others", "confidence"),
    ("how to believe in myself", "confidence"),
    ("i compare myself to others", "confidence"),
    ("how to stop being insecure", "confidence"),
    ("i want to be a better person", "confidence"),

    # CASUAL / GENERAL
    ("hello", "casual"),
    ("hi there", "casual"),
    ("how are you", "casual"),
    ("what's up", "casual"),
    ("good morning", "casual"),
    ("i'm bored", "casual"),
    ("tell me something interesting", "casual"),
    ("what should i do today", "casual"),
    ("how's the weather", "casual"),
    ("just wanted to chat", "casual"),
    ("nothing much happening", "casual"),
    ("hey friend", "casual"),
    ("what do you think about", "casual"),
    ("random question", "casual"),
    ("just saying hi", "casual"),
]

# =============================================================================
# RESPONSE TEMPLATES - For each intent
# =============================================================================

RESPONSE_TEMPLATES = {
    "relationship": [
        {
            "opener": "Relationships can be tricky, but here's what works:",
            "actions": [
                "Be yourself - don't pretend to be someone you're not",
                "Start with casual conversations, find common interests",
                "Listen more than you talk - people love good listeners",
                "Be confident but not arrogant - smile and make eye contact",
                "Don't rush things - let the connection grow naturally"
            ],
            "say_this": "Hey, I noticed we both like [common interest]. Want to hang out sometime?",
            "tip": "Confidence is attractive, but being genuine is even more attractive."
        },
        {
            "opener": "Here's the honest truth about this:",
            "actions": [
                "Focus on being friends first before anything else",
                "Show genuine interest in their life and passions",
                "Be kind and respectful, always",
                "Don't play games or try to make them jealous",
                "If they're not interested, respect that and move on"
            ],
            "say_this": "I really enjoy spending time with you. Would you want to grab coffee sometime?",
            "tip": "The right person will appreciate you for who you are."
        },
    ],

    "academics": [
        {
            "opener": "Bad grades aren't the end - here's how to bounce back:",
            "actions": [
                "Figure out what went wrong - was it preparation or understanding?",
                "Make a study schedule and stick to it daily",
                "Ask your teacher for help - they want you to succeed",
                "Study in short focused sessions (25 min study, 5 min break)",
                "Teach what you learn to someone else - it helps retention"
            ],
            "say_this": "I didn't do well this time, but I've made a plan to improve. Can you help me understand [topic]?",
            "tip": "One test doesn't define your intelligence or your future."
        },
        {
            "opener": "Studying smarter beats studying harder:",
            "actions": [
                "Find your best study time - morning or night, when you focus best",
                "Remove distractions - phone in another room while studying",
                "Use active recall - test yourself instead of just reading",
                "Get enough sleep - your brain processes information while sleeping",
                "Take breaks and exercise - it boosts brain function"
            ],
            "say_this": "I'm working on improving my study habits. Any tips that worked for you?",
            "tip": "Consistency beats intensity - 1 hour daily beats 7 hours on Sunday."
        },
    ],

    "family": [
        {
            "opener": "Dealing with parents is tough but possible:",
            "actions": [
                "Pick the right time to talk - not when they're stressed or busy",
                "Start by acknowledging their perspective first",
                "Be honest but respectful - don't get defensive",
                "Show maturity through your actions, not just words",
                "Have a solution ready, not just the problem"
            ],
            "say_this": "I know you're disappointed, and I understand why. Here's what I'm going to do to fix it...",
            "tip": "Parents worry because they care. Understanding that changes everything."
        },
        {
            "opener": "Here's how to handle this at home:",
            "actions": [
                "Don't react in anger - take a breath first",
                "Try to see things from their point of view",
                "Communicate calmly rather than arguing",
                "Build trust slowly through consistent actions",
                "Find small ways to show responsibility"
            ],
            "say_this": "I want us to understand each other better. Can we talk about this calmly?",
            "tip": "Showing maturity in tough moments earns more trust than arguing ever will."
        },
    ],

    "stress": [
        {
            "opener": "I hear you - stress is real, but you can handle it:",
            "actions": [
                "Take a deep breath - seriously, do it right now",
                "Break the big problem into smaller, manageable pieces",
                "Talk to someone you trust about how you're feeling",
                "Get moving - even a short walk helps clear your head",
                "Write down what's bothering you - it helps process emotions"
            ],
            "say_this": "I'm going through a tough time and could use some support.",
            "tip": "This feeling is temporary. You've survived 100% of your bad days so far."
        },
        {
            "opener": "When everything feels overwhelming:",
            "actions": [
                "Focus on just the next small step, not the whole mountain",
                "Limit social media - it often makes anxiety worse",
                "Get enough sleep - tiredness amplifies stress",
                "Remember: most things we worry about never happen",
                "Be kind to yourself - you're doing better than you think"
            ],
            "say_this": "I need a break. Let me focus on one thing at a time.",
            "tip": "You don't have to solve everything today. Just take the next step."
        },
    ],

    "confidence": [
        {
            "opener": "Confidence is a skill you can build:",
            "actions": [
                "Start with small wins - achieve tiny goals daily",
                "Stand tall, make eye contact - body language affects mindset",
                "Stop comparing yourself to others' highlight reels",
                "Practice talking to new people - it gets easier each time",
                "Celebrate your strengths instead of focusing on weaknesses"
            ],
            "say_this": "I'm working on myself and getting better every day.",
            "tip": "Confidence isn't about being perfect, it's about being okay with imperfection."
        },
        {
            "opener": "Here's the truth about confidence:",
            "actions": [
                "Fake it till you make it - act confident even when you don't feel it",
                "Prepare well for things that make you nervous",
                "Remember: most people are too busy worrying about themselves to judge you",
                "Keep a list of your achievements - read it when you doubt yourself",
                "Surround yourself with people who lift you up"
            ],
            "say_this": "I'm not perfect, but I'm working on being the best version of myself.",
            "tip": "The most confident people aren't fearless - they act despite fear."
        },
    ],

    "casual": [
        {
            "opener": "Hey! Good to hear from you.",
            "actions": [],
            "say_this": "",
            "tip": "What's on your mind today?"
        },
        {
            "opener": "What's up! I'm here if you want to chat about anything.",
            "actions": [],
            "say_this": "",
            "tip": "How's your day going?"
        },
        {
            "opener": "Hey there! Nice to hear from you.",
            "actions": [],
            "say_this": "",
            "tip": "Anything specific you want to talk about?"
        },
    ],
}


def _load_friend_model():
    """Load or train the friend model."""
    global _friend_model

    if _friend_model is not None:
        return

    if FRIEND_MODEL_PATH.exists():
        try:
            with open(FRIEND_MODEL_PATH, "rb") as f:
                _friend_model = pickle.load(f)
            logger.info("[Friend ML] Model loaded from file")
            return
        except Exception as e:
            logger.warning(f"[Friend ML] Failed to load model: {e}, retraining...")

    # Train new model
    _train_friend_model()


def _train_friend_model():
    """Train the intent classification model."""
    global _friend_model

    logger.info("[Friend ML] Training intent classifier...")

    texts = [item[0] for item in INTENT_TRAINING_DATA]
    labels = [item[1] for item in INTENT_TRAINING_DATA]

    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )),
        ('clf', MultinomialNB(alpha=0.1))
    ])

    # Train
    pipeline.fit(texts, labels)

    # Test accuracy
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    pipeline_test = Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 2))),
        ('clf', MultinomialNB(alpha=0.1))
    ])
    pipeline_test.fit(X_train, y_train)
    accuracy = pipeline_test.score(X_test, y_test)
    logger.info(f"[Friend ML] Model accuracy: {accuracy:.2%}")

    _friend_model = {
        'pipeline': pipeline,
        'intents': list(set(labels)),
        'accuracy': accuracy
    }

    # Save model
    with open(FRIEND_MODEL_PATH, "wb") as f:
        pickle.dump(_friend_model, f)

    logger.info("[Friend ML] Model trained and saved")


def classify_intent(message: str) -> Tuple[str, float]:
    """
    Classify the intent of a message.

    Returns:
        (intent, confidence)
    """
    _load_friend_model()

    pipeline = _friend_model['pipeline']

    # Predict
    intent = pipeline.predict([message.lower()])[0]

    # Get confidence
    proba = pipeline.predict_proba([message.lower()])[0]
    confidence = float(max(proba))

    return intent, confidence


def generate_response_from_model(message: str, sentiment: str = "neutral") -> dict:
    """
    Generate a response using the ML model (no API needed).

    Args:
        message: User's message
        sentiment: Detected sentiment

    Returns:
        {
            "response": str,
            "intent": str,
            "confidence": float,
            "source": "model"
        }
    """
    _load_friend_model()

    # Classify intent
    intent, confidence = classify_intent(message)

    # Get response template
    templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["casual"])
    template = random.choice(templates)

    # Build response
    if intent == "casual":
        # Simple casual response
        response = f"{template['opener']}\n\n{template['tip']}"
    else:
        # Structured advice response
        response_parts = [template['opener'], ""]

        if template['actions']:
            response_parts.append("Do this:")
            for action in template['actions']:
                response_parts.append(f"• {action}")
            response_parts.append("")

        if template['say_this']:
            response_parts.append("Say this:")
            response_parts.append(f'"{template["say_this"]}"')
            response_parts.append("")

        if template['tip']:
            response_parts.append(f"Tip: {template['tip']}")

        response = "\n".join(response_parts)

    return {
        "response": response,
        "intent": intent,
        "confidence": confidence,
        "source": "model"
    }


def get_all_intents() -> List[str]:
    """Get all available intent categories."""
    _load_friend_model()
    return _friend_model['intents']


def add_training_example(message: str, intent: str):
    """
    Add a new training example and retrain (for future learning).

    Note: This would need to persist to a database in production.
    """
    global INTENT_TRAINING_DATA
    INTENT_TRAINING_DATA.append((message, intent))
    _train_friend_model()
    logger.info(f"[Friend ML] Added new example and retrained: {message[:30]}... -> {intent}")
