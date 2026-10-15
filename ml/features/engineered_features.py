"""
CertiNexus AI — Engineered Document-Level Features

15+ meta-features extracted from certificate text to supplement
TF-IDF representations.
"""

import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class DocumentMetaFeatures(BaseEstimator, TransformerMixin):
    """
    Extract 18 engineered features from certificate text.

    Features include text statistics, keyword densities,
    structural indicators, and domain-specific signals.

    Designed to be used in a FeatureUnion alongside TF-IDF.
    """

    CERTIFICATE_KEYWORDS = {
        "certificate", "certify", "certifies", "certified", "awarded",
        "presented", "recognition", "achievement", "completion",
        "participation", "successfully", "completed", "attended",
        "organized", "conducted", "held", "issued", "hereby",
        "excellence", "merit", "honor",
    }

    TECHNICAL_KEYWORDS = {
        "python", "java", "javascript", "programming", "software",
        "coding", "algorithm", "database", "cloud", "machine learning",
        "ai", "data", "web", "development", "engineering", "technology",
        "computing", "devops", "security", "network", "api", "framework",
        "docker", "kubernetes", "react", "angular", "node", "sql",
        "deep learning", "tensorflow", "pytorch",
    }

    ACHIEVEMENT_KEYWORDS = {
        "winner", "first", "second", "third", "gold", "silver",
        "bronze", "best", "outstanding", "excellent", "distinction",
        "merit", "rank", "topper", "champion", "award", "prize",
        "scholarship", "fellow",
    }

    EVENT_KEYWORDS = {
        "hackathon", "competition", "workshop", "conference",
        "seminar", "symposium", "summit", "fest", "event",
        "tournament", "olympiad", "challenge",
    }

    ACADEMIC_KEYWORDS = {
        "university", "college", "institute", "school", "academy",
        "department", "faculty", "semester", "examination", "degree",
        "diploma", "thesis", "research", "paper", "journal",
    }

    FEATURE_NAMES = [
        "text_length", "word_count", "avg_word_length",
        "unique_word_ratio", "uppercase_ratio",
        "digit_ratio", "punctuation_ratio",
        "sentence_count", "avg_sentence_length",
        "has_date", "has_cert_id", "has_url_email",
        "certificate_keyword_density",
        "technical_keyword_count",
        "achievement_keyword_count",
        "event_keyword_count",
        "academic_keyword_count",
        "has_score_or_grade",
    ]

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        features = []
        for text in X:
            features.append(self._extract_features(text))
        return np.array(features)

    def _extract_features(self, text):
        if not isinstance(text, str) or not text.strip():
            return [0.0] * len(self.FEATURE_NAMES)

        text_lower = text.lower()
        words = text_lower.split()
        word_count = max(len(words), 1)
        chars = list(text)
        char_count = max(len(chars), 1)

        # Basic text stats
        text_length = len(text)
        avg_word_length = (
            sum(len(w) for w in words) / word_count
        )
        unique_words = set(words)
        unique_word_ratio = len(unique_words) / word_count

        # Character-level ratios
        uppercase_count = sum(1 for c in text if c.isupper())
        digit_count = sum(1 for c in text if c.isdigit())
        punct_count = sum(
            1 for c in text if not c.isalnum() and not c.isspace()
        )
        uppercase_ratio = uppercase_count / char_count
        digit_ratio = digit_count / char_count
        punctuation_ratio = punct_count / char_count

        # Sentence-level
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_count = max(len(sentences), 1)
        avg_sentence_length = word_count / sentence_count

        # Pattern indicators
        has_date = 1.0 if (
            re.search(r"\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}", text) or
            re.search(
                r"\b(january|february|march|april|may|june|july|"
                r"august|september|october|november|december)\b",
                text_lower
            )
        ) else 0.0

        has_cert_id = 1.0 if re.search(
            r"\b(cert|crt|doc|ref|id|no)[:\-/]?\s*\w*\d+",
            text_lower,
        ) else 0.0

        has_url_email = 1.0 if (
            re.search(r"https?://|www\.", text_lower) or
            re.search(r"\S+@\S+\.\S+", text_lower)
        ) else 0.0

        has_score_grade = 1.0 if (
            re.search(r"\d+\s*/\s*\d+", text) or
            re.search(r"\d+%", text) or
            re.search(r"grade\s*[:\-]?\s*[a-f][+\-]?", text_lower) or
            re.search(r"[cg]gpa\s*[:\-]?\s*\d+", text_lower)
        ) else 0.0

        # Keyword densities
        cert_density = sum(
            1 for w in words if w in self.CERTIFICATE_KEYWORDS
        ) / word_count
        tech_count = sum(
            1 for w in words if w in self.TECHNICAL_KEYWORDS
        )
        achievement_count = sum(
            1 for w in words if w in self.ACHIEVEMENT_KEYWORDS
        )
        event_count = sum(
            1 for w in words if w in self.EVENT_KEYWORDS
        )
        academic_count = sum(
            1 for w in words if w in self.ACADEMIC_KEYWORDS
        )

        return [
            text_length, word_count, avg_word_length,
            unique_word_ratio, uppercase_ratio,
            digit_ratio, punctuation_ratio,
            sentence_count, avg_sentence_length,
            has_date, has_cert_id, has_url_email,
            cert_density,
            tech_count,
            achievement_count,
            event_count,
            academic_count,
            has_score_grade,
        ]

    def get_feature_names_out(self, input_features=None):
        return self.FEATURE_NAMES
