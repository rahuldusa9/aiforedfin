"""
AI FOR EDUCATION – Synthetic Dataset Generator
Generates a realistic synthetic student performance dataset (2000+ rows).
"""

import numpy as np
import pandas as pd
from pathlib import Path

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------
NUM_SAMPLES = 2500
OUTPUT_PATH = Path(__file__).parent / "student_performance_dataset.csv"

TOPICS = [
    "mathematics", "science", "history", "english",
    "programming", "geography", "physics", "chemistry",
    "biology", "literature"
]

DIFFICULTIES = ["easy", "medium", "hard"]


def generate_dataset(n_samples: int = NUM_SAMPLES) -> pd.DataFrame:
    """
    Generate a synthetic student performance dataset.
    
    Features:
        - quiz_accuracy (float 0–1)
        - average_response_time (seconds)
        - difficulty_level (easy/medium/hard)
        - number_of_attempts (int)
        - topic_category (string)
    
    Target:
        - performance_level (low / medium / high)
    """
    np.random.seed(42)

    data = {
        "quiz_accuracy": np.random.beta(5, 3, n_samples),  # Skewed towards higher accuracy
        "average_response_time": np.random.lognormal(2.5, 0.6, n_samples),  # Seconds
        "difficulty_level": np.random.choice(DIFFICULTIES, n_samples, p=[0.3, 0.45, 0.25]),
        "number_of_attempts": np.random.randint(1, 15, n_samples),
        "topic_category": np.random.choice(TOPICS, n_samples),
    }

    df = pd.DataFrame(data)

    # Clip response time to realistic range
    df["average_response_time"] = df["average_response_time"].clip(3, 120)

    # -------------------------------------------------------
    # Generate target: performance_level based on feature logic
    # -------------------------------------------------------
    difficulty_map = {"easy": 0, "medium": 1, "hard": 2}
    diff_numeric = df["difficulty_level"].map(difficulty_map)

    # Composite score drives performance
    score = (
        df["quiz_accuracy"] * 40
        - df["average_response_time"] * 0.15
        - diff_numeric * 3
        + df["number_of_attempts"] * 0.5
        + np.random.normal(0, 2, n_samples)  # Noise
    )

    conditions = [
        score < 15,
        (score >= 15) & (score < 25),
        score >= 25,
    ]
    choices = ["low", "medium", "high"]
    df["performance_level"] = np.select(conditions, choices, default="medium")

    return df


def save_dataset():
    """Generate and save the dataset to CSV."""
    df = generate_dataset()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[ML] Dataset saved to {OUTPUT_PATH}")
    print(f"[ML] Shape: {df.shape}")
    print(f"[ML] Performance distribution:\n{df['performance_level'].value_counts()}")
    return df


if __name__ == "__main__":
    save_dataset()
