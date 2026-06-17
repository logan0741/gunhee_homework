from __future__ import annotations

import pickle
from pathlib import Path

_MODEL = None
_MODEL_VERSION = "keyword-v1"

_SPAM_KEYWORDS = [
    "free", "win", "winner", "prize", "click",
    "buy now", "urgent", "cash", "money", "offer", "deal",
    "discount", "limited time", "bonus",
]


def _load_model() -> None:
    global _MODEL, _MODEL_VERSION
    model_path = Path(__file__).resolve().parents[1] / "models" / "spam_pipeline.pkl"
    if model_path.exists():
        with open(model_path, "rb") as f:
            _MODEL = pickle.load(f)
        _MODEL_VERSION = "ml-v2"


_load_model()


def _keyword_hits(text: str) -> int:
    t = text.lower()
    return sum(1 for kw in _SPAM_KEYWORDS if kw in t)


def check_spam(text: str) -> tuple[str, float]:
    if not text or not text.strip():
        return ("ham", 0.0)

    if _MODEL is not None:
        proba = _MODEL.predict_proba([text])[0]
        spam_prob = float(proba[1])
        label = "spam" if spam_prob >= 0.5 else "ham"
        return (label, round(spam_prob, 4))

    hits = _keyword_hits(text)
    score = round(hits / len(_SPAM_KEYWORDS), 4)
    return ("spam" if hits >= 2 else "ham", score)


def check_spam_keyword(text: str) -> tuple[str, float]:
    """Keyword-based v1 classifier — used for baseline comparison in train.py."""
    if not text or not text.strip():
        return ("ham", 0.0)
    hits = _keyword_hits(text)
    score = round(hits / len(_SPAM_KEYWORDS), 4)
    return ("spam" if hits >= 2 else "ham", score)


def get_model_version() -> str:
    return _MODEL_VERSION


def reload_model() -> str:
    """Hot-reload model from disk (for production model updates)."""
    _load_model()
    return _MODEL_VERSION
