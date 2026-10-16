
"""Adapter for Sentio's locally trained DistilBERT classifier."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger("sentio.emotion_model")

ENV_VAR = "SENTIO_MODEL_DIR"
MAX_CHARS = 2000
LOW_CONFIDENCE = 0.5

# Default: <project root>/models/distilbert/
DEFAULT_MODEL_DIR = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "distilbert"
)


@dataclass
class EmotionResult:
    status: str
    label: Optional[str] = None
    confidence: Optional[float] = None
    message: str = ""


class ModelUnavailable(Exception):
    """Raised when the trained model cannot be loaded."""


def resolve_model_dir(path: Optional[str] = None) -> Optional[Path]:
    """Use an explicit path, environment variable, or project default."""
    raw = path or os.environ.get(ENV_VAR)

    if raw:
        return Path(raw).expanduser().resolve()

    return DEFAULT_MODEL_DIR.resolve()


def load_classifier(
    path: Optional[str] = None,
) -> Callable[[str], list[dict[str, Any]]]:
    """Load the local multi-label DistilBERT model."""
    model_dir = resolve_model_dir(path)

    if model_dir is None or not model_dir.is_dir():
        raise ModelUnavailable(
            f"Model folder not found: {model_dir}"
        )

    for filename in ("config.json", "model.safetensors", "tokenizer.json"):
        if not (model_dir / filename).is_file():
            raise ModelUnavailable(
                f"Required model file '{filename}' is missing from "
                f"{model_dir}"
            )

    try:
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
        )
        import torch

    except ImportError as exc:
        raise ModelUnavailable(
            "Required packages are missing. Install torch and transformers."
        ) from exc

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_dir),
            local_files_only=True,
        )

        model = AutoModelForSequenceClassification.from_pretrained(
            str(model_dir),
            local_files_only=True,
        )
        model.eval()

        labels = model.config.id2label or {}
        if not labels or all(
            str(label).upper().startswith("LABEL_")
            for label in labels.values()
        ):
            raise ModelUnavailable(
                "The model's config.json does not contain readable labels."
            )

        if model.config.problem_type != "multi_label_classification":
            raise ModelUnavailable(
                "Expected a multi-label classification model, but the "
                "model configuration specifies a different task."
            )

    except ModelUnavailable:
        raise
    except Exception as exc:
        log.exception("Failed to load model from %s", model_dir)
        raise ModelUnavailable(
            "Model files were found but could not be loaded. "
            "Check the terminal logs for details."
        ) from exc

    def classify(text: str) -> list[dict[str, Any]]:
        text = (text or "").strip()

        if not text:
            return []

        inputs = tokenizer(
            text[:MAX_CHARS],
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )

        with torch.inference_mode():
            logits = model(**inputs).logits
            scores = torch.sigmoid(logits)[0].tolist()

        return [
            {
                "label": str(model.config.id2label.get(i, i)),
                "score": float(score),
            }
            for i, score in enumerate(scores)
        ]

    log.info("Loaded DistilBERT classifier from %s", model_dir)
    return classify


def analyze(
    text: str,
    classifier: Optional[Callable] = None,
    unavailable_reason: str = "",
) -> EmotionResult:
    """Return the highest-scoring category without diagnosing stress."""
    text = (text or "").strip()

    if not text:
        return EmotionResult(
            "no_text",
            message="No written text was provided for analysis.",
        )

    if classifier is None:
        return EmotionResult(
            "unavailable",
            message=unavailable_reason
            or "Text analysis is currently unavailable.",
        )

    try:
        scores = classifier(text[:MAX_CHARS])

        if not scores:
            return EmotionResult(
                "unclear",
                message="The model returned no predictions.",
            )

        best = max(scores, key=lambda item: item["score"])
        label = str(best["label"])
        confidence = float(best["score"])

    except Exception:
        log.exception("Text classification failed")
        return EmotionResult(
            "error",
            message="Text analysis encountered an error.",
        )

    if confidence < LOW_CONFIDENCE:
        return EmotionResult(
            "unclear",
            label=label,
            confidence=confidence,
            message="The result is uncertain and should not be "
                    "treated as a diagnosis.",
        )

    return EmotionResult(
        "ok",
        label=label,
        confidence=confidence,
    )
