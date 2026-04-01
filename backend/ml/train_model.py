"""
AI FOR EDUCATION – Student Performance Model Training
Trains RandomForest and LogisticRegression, saves the best model.
"""

import pickle
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from ml.generate_dataset import generate_dataset

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Paths
# -------------------------------------------------------
ML_DIR = Path(__file__).parent
MODEL_PATH = ML_DIR / "model.pkl"
SCALER_PATH = ML_DIR / "scaler.pkl"
ENCODERS_PATH = ML_DIR / "label_encoders.pkl"


def train_performance_model():
    """
    Full training pipeline:
    1. Generate/load dataset
    2. Encode categorical features
    3. Scale numerical features
    4. Train RandomForest + LogisticRegression
    5. Compare accuracy and save the best
    """
    logger.info("[ML] Starting performance model training...")

    # -------------------------------------------------------
    # 1. Generate dataset
    # -------------------------------------------------------
    df = generate_dataset()
    logger.info(f"[ML] Dataset shape: {df.shape}")

    # -------------------------------------------------------
    # 2. Encode categorical features
    # -------------------------------------------------------
    label_encoders = {}

    le_difficulty = LabelEncoder()
    df["difficulty_encoded"] = le_difficulty.fit_transform(df["difficulty_level"])
    label_encoders["difficulty_level"] = le_difficulty

    le_topic = LabelEncoder()
    df["topic_encoded"] = le_topic.fit_transform(df["topic_category"])
    label_encoders["topic_category"] = le_topic

    le_target = LabelEncoder()
    df["target"] = le_target.fit_transform(df["performance_level"])
    label_encoders["performance_level"] = le_target

    # -------------------------------------------------------
    # 3. Prepare features and target
    # -------------------------------------------------------
    feature_cols = [
        "quiz_accuracy",
        "average_response_time",
        "difficulty_encoded",
        "number_of_attempts",
        "topic_encoded",
    ]
    X = df[feature_cols].values
    y = df["target"].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # -------------------------------------------------------
    # 4. Train models
    # -------------------------------------------------------
    # Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)

    logger.info(f"[ML] Random Forest Accuracy: {rf_accuracy:.4f}")
    logger.info(f"[ML] RF Report:\n{classification_report(y_test, rf_pred, target_names=le_target.classes_)}")

    # Logistic Regression
    lr_model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        multi_class="multinomial",
        solver="lbfgs",
    )
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_pred)

    logger.info(f"[ML] Logistic Regression Accuracy: {lr_accuracy:.4f}")
    logger.info(f"[ML] LR Report:\n{classification_report(y_test, lr_pred, target_names=le_target.classes_)}")

    # -------------------------------------------------------
    # 5. Save best model
    # -------------------------------------------------------
    if rf_accuracy >= lr_accuracy:
        best_model = rf_model
        best_name = "RandomForest"
        best_accuracy = rf_accuracy
    else:
        best_model = lr_model
        best_name = "LogisticRegression"
        best_accuracy = lr_accuracy

    logger.info(f"[ML] Best model: {best_name} (accuracy={best_accuracy:.4f})")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    with open(ENCODERS_PATH, "wb") as f:
        pickle.dump(label_encoders, f)

    logger.info(f"[ML] Model saved to {MODEL_PATH}")
    logger.info(f"[ML] Scaler saved to {SCALER_PATH}")
    logger.info(f"[ML] Encoders saved to {ENCODERS_PATH}")

    return {
        "best_model": best_name,
        "rf_accuracy": rf_accuracy,
        "lr_accuracy": lr_accuracy,
        "best_accuracy": best_accuracy,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = train_performance_model()
    print(f"\nTraining Results: {results}")
