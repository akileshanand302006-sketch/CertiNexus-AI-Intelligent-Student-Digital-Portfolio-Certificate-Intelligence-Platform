"""
CertiNexus AI — Prediction Explanation

Structured explanation output that combines feature attribution,
entity extraction, and confidence analysis into a human-readable
explanation of why a certificate was classified a certain way.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PredictionExplanation:
    """
    Complete explanation for a classification prediction.

    Combines:
    - Feature attribution (which words mattered)
    - Top-N alternative predictions
    - Confidence analysis
    - Key entities that influenced the decision
    """
    category: str
    confidence: float
    confidence_level: str  # "high", "medium", "low"

    # Feature attribution
    positive_terms: List[Dict] = field(default_factory=list)
    negative_terms: List[Dict] = field(default_factory=list)

    # Top-N alternatives
    alternatives: List[Dict] = field(default_factory=list)

    # Explanation text
    explanation_text: str = ""

    # Processing info
    model_version: str = ""
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "confidence_level": self.confidence_level,
            "positive_terms": self.positive_terms,
            "negative_terms": self.negative_terms,
            "alternatives": self.alternatives,
            "explanation_text": self.explanation_text,
            "model_version": self.model_version,
            "processing_time_ms": round(self.processing_time_ms, 2),
        }

    def generate_explanation_text(self) -> str:
        """Generate human-readable explanation text."""
        lines = [
            f"This certificate was classified as \"{self.category}\" "
            f"with {self.confidence:.0%} confidence ({self.confidence_level}).",
        ]

        if self.positive_terms:
            top_terms = ", ".join(
                f"\"{t['term']}\"" for t in self.positive_terms[:5]
            )
            lines.append(
                f"Key terms supporting this classification: {top_terms}."
            )

        if self.alternatives:
            alt_text = ", ".join(
                f"{a['class']} ({a['probability']:.0%})"
                for a in self.alternatives[:3]
            )
            lines.append(f"Alternative classifications considered: {alt_text}.")

        if self.confidence_level == "low":
            lines.append(
                "Note: The classification confidence is low. "
                "Manual review is recommended."
            )

        self.explanation_text = " ".join(lines)
        return self.explanation_text
