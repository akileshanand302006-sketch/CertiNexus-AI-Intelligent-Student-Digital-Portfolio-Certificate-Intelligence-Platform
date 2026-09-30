"""
CertiNexus AI — Text Preprocessing Pipeline

Provides a reproducible text cleaning pipeline for certificate OCR text,
compatible with sklearn Pipeline API.
"""

import re
import string

from sklearn.base import BaseEstimator, TransformerMixin


class CertificateTextPreprocessor(BaseEstimator, TransformerMixin):
    """
    Sklearn-compatible text preprocessor for certificate documents.

    Designed to clean OCR-extracted certificate text while preserving
    semantically meaningful information (dates, IDs, organization names).

    Parameters
    ----------
    lowercase : bool
        Convert text to lowercase.
    remove_extra_whitespace : bool
        Normalize multiple spaces/newlines to single space.
    remove_urls : bool
        Remove URLs from text.
    remove_emails : bool
        Remove email addresses from text.
    normalize_numbers : bool
        Replace specific numbers with generic tokens (preserves date patterns).
    remove_special_chars : bool
        Remove non-alphanumeric characters (preserves hyphens, periods, slashes
        commonly found in certificate IDs and dates).
    min_word_length : int
        Remove words shorter than this (0 = keep all).
    """

    def __init__(
        self,
        lowercase=True,
        remove_extra_whitespace=True,
        remove_urls=True,
        remove_emails=True,
        normalize_numbers=False,
        remove_special_chars=True,
        min_word_length=0,
    ):
        self.lowercase = lowercase
        self.remove_extra_whitespace = remove_extra_whitespace
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.normalize_numbers = normalize_numbers
        self.remove_special_chars = remove_special_chars
        self.min_word_length = min_word_length

    def fit(self, X, y=None):
        """No fitting required for rule-based preprocessing."""
        return self

    def transform(self, X, y=None):
        """Transform a list of text strings."""
        return [self._clean_text(text) for text in X]

    def _clean_text(self, text):
        """Apply the full cleaning pipeline to a single text."""
        if not isinstance(text, str):
            return ""

        # Step 1: Lowercase
        if self.lowercase:
            text = text.lower()

        # Step 2: Remove URLs
        if self.remove_urls:
            text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

        # Step 3: Remove emails
        if self.remove_emails:
            text = re.sub(r'\S+@\S+\.\S+', ' ', text)

        # Step 4: Remove special characters (preserve meaningful ones)
        if self.remove_special_chars:
            # Keep alphanumeric, spaces, hyphens, periods, slashes, colons
            # These appear in dates (01/02/2024), certificate IDs (CERT-12345),
            # and structured content
            text = re.sub(r"[^a-zA-Z0-9\s\-\./:]", ' ', text)

        # Step 5: Normalize numbers (optional — may lose meaningful info)
        if self.normalize_numbers:
            # Preserve date-like patterns (dd/mm/yyyy, dd-mm-yyyy)
            # Replace isolated large numbers
            text = re.sub(r'\b\d{5,}\b', ' NUM ', text)

        # Step 6: Normalize whitespace
        if self.remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()

        # Step 7: Remove short words
        if self.min_word_length > 0:
            words = text.split()
            words = [w for w in words if len(w) >= self.min_word_length]
            text = ' '.join(words)

        return text


class TextLengthFeatures(BaseEstimator, TransformerMixin):
    """
    Extract engineered text-level features from certificate text.

    Features:
    - text_length: character count
    - word_count: word count
    - avg_word_length: average word length
    - has_date: whether date patterns are present
    - has_cert_id: whether certificate ID patterns are present
    - keyword_density: density of certificate-related keywords
    - technical_keyword_count: count of technical/programming terms
    - achievement_keyword_count: count of achievement-related terms
    """

    CERTIFICATE_KEYWORDS = {
        'certificate', 'certify', 'certifies', 'certified', 'awarded',
        'presented', 'recognition', 'achievement', 'completion', 'participation',
        'successfully', 'completed', 'attended', 'organized', 'conducted',
        'held', 'issued', 'hereby', 'excellence', 'merit', 'honor'
    }

    TECHNICAL_KEYWORDS = {
        'python', 'java', 'javascript', 'programming', 'software', 'coding',
        'algorithm', 'database', 'cloud', 'machine learning', 'ai', 'data',
        'web', 'development', 'engineering', 'technology', 'computing',
        'devops', 'security', 'network', 'api', 'framework', 'docker',
        'kubernetes', 'react', 'angular', 'node', 'sql', 'deep learning'
    }

    ACHIEVEMENT_KEYWORDS = {
        'winner', 'first', 'second', 'third', 'gold', 'silver', 'bronze',
        'best', 'outstanding', 'excellent', 'distinction', 'merit', 'rank',
        'topper', 'champion', 'award', 'prize', 'scholarship', 'fellow'
    }

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        import numpy as np
        features = []
        for text in X:
            if not isinstance(text, str):
                text = ""
            text_lower = text.lower()
            words = text_lower.split()
            word_count = len(words) if words else 1

            feat = {
                'text_length': len(text),
                'word_count': word_count,
                'avg_word_length': sum(len(w) for w in words) / word_count if words else 0,
                'has_date': 1 if re.search(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}', text) or
                               re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', text_lower) else 0,
                'has_cert_id': 1 if re.search(r'\b(cert|crt|doc|ref|id|no)[:\-/]?\s*\w*\d+', text_lower) else 0,
                'keyword_density': sum(1 for w in words if w in self.CERTIFICATE_KEYWORDS) / word_count,
                'technical_keyword_count': sum(1 for w in words if w in self.TECHNICAL_KEYWORDS),
                'achievement_keyword_count': sum(1 for w in words if w in self.ACHIEVEMENT_KEYWORDS),
            }
            features.append(list(feat.values()))

        return np.array(features)

    def get_feature_names_out(self, input_features=None):
        return [
            'text_length', 'word_count', 'avg_word_length',
            'has_date', 'has_cert_id', 'keyword_density',
            'technical_keyword_count', 'achievement_keyword_count'
        ]


def preprocess_dataset(input_path, output_path):
    """
    Preprocess raw certificate dataset and save cleaned version.
    """
    import pandas as pd

    print("Loading raw dataset...")
    df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} records")

    preprocessor = CertificateTextPreprocessor()
    print("Cleaning text...")
    df['clean_text'] = preprocessor.transform(df['raw_text'].fillna(''))

    # Remove empty rows
    empty_mask = df['clean_text'].str.strip() == ''
    if empty_mask.any():
        print(f"  Removing {empty_mask.sum()} empty records after cleaning")
        df = df[~empty_mask]

    print(f"Saving preprocessed dataset to {output_path}...")
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  Saved {len(df)} records")

    return df


if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_path = os.path.join(base_dir, "dataset", "raw", "certificates.csv")
    processed_path = os.path.join(base_dir, "dataset", "processed", "cleaned_dataset.csv")

    preprocess_dataset(raw_path, processed_path)
    print("\n✓ Preprocessing complete!")
