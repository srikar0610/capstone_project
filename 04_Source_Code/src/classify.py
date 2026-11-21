"""Intent and urgency classification trained only on the development tickets.

Requirement FR-CLS-1. Confidence is the predicted class probability from a
logistic regression, not a fixed number. The validation file is never read here.
"""

from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

PROMPT_VERSION = "classify-v1"


class IntentClassifier:
    def __init__(self, tickets_path: Path) -> None:
        self.tickets_path = tickets_path
        self.intent_model = self._fit(tickets_path, "intent")
        self.urgency_model = self._fit(tickets_path, "urgency")

    @staticmethod
    def _text(subject: str, body: str) -> str:
        return f"{subject or ''}\n{body or ''}".strip()

    def _fit(self, path: Path, label_key: str) -> Pipeline:
        if not path.exists():
            raise FileNotFoundError(
                f"Training tickets were not found at {path}. "
                "Copy development_tickets.json into data/ before starting."
            )
        rows = json.loads(path.read_text(encoding="utf-8"))
        texts: list[str] = []
        labels: list[str] = []
        for row in rows:
            found = row.get("labels") or {}
            label = found.get(label_key)
            if not label:
                continue
            texts.append(self._text(row.get("subject", ""), row.get("body", "")))
            labels.append(str(label))
        if len(set(labels)) < 2:
            raise RuntimeError(f"Need at least two {label_key} classes to train the classifier.")
        model = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                ),
                (
                    "clf",
                    LogisticRegression(max_iter=500, random_state=0, C=4.0),
                ),
            ]
        )
        model.fit(texts, labels)
        return model

    def predict(self, subject: str, body: str) -> dict:
        text = self._text(subject, body)
        if len(text) < 12:
            return {
                "intent": "unclear_request",
                "urgency": "low",
                "confidence": 0.15,
                "urgency_confidence": 0.15,
                "alternatives": [{"intent": "unclear_request", "confidence": 0.15}],
                "prompt_version": PROMPT_VERSION,
                "fallback": True,
            }
        probabilities = self.intent_model.predict_proba([text])[0]
        classes = list(self.intent_model.named_steps["clf"].classes_)
        ranked = sorted(range(len(classes)), key=lambda index: probabilities[index], reverse=True)
        urgency_probabilities = self.urgency_model.predict_proba([text])[0]
        urgency_classes = list(self.urgency_model.named_steps["clf"].classes_)
        urgency_index = int(urgency_probabilities.argmax())
        return {
            "intent": str(classes[ranked[0]]),
            "urgency": str(urgency_classes[urgency_index]),
            "confidence": float(probabilities[ranked[0]]),
            "urgency_confidence": float(urgency_probabilities[urgency_index]),
            "alternatives": [
                {"intent": str(classes[index]), "confidence": float(probabilities[index])}
                for index in ranked[:3]
            ],
            "prompt_version": PROMPT_VERSION,
            "fallback": False,
        }
