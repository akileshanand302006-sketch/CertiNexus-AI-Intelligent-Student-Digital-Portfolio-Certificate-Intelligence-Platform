"""
CertiNexus AI — TF-IDF Feature Configurations

Three distinct TF-IDF vectorizer configurations for the
classifier comparison experiments.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion


class TFIDFFeatureConfigs:
    """
    Factory for TF-IDF feature configurations.

    Provides three configurations:
    1. Word N-grams (1,2) — baseline
    2. Word + Character N-grams — captures subword patterns
    3. Enriched — Word + Char + meta-features
    """

    @staticmethod
    def word_ngrams(max_features: int = 5000) -> TfidfVectorizer:
        """TF-IDF with word unigrams and bigrams."""
        return TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=max_features,
            sublinear_tf=True,
            min_df=2,
            max_df=0.95,
        )

    @staticmethod
    def word_char_ngrams(
        word_features: int = 4000,
        char_features: int = 3000,
    ) -> FeatureUnion:
        """Combined word and character N-gram TF-IDF."""
        return FeatureUnion([
            ("word", TfidfVectorizer(
                analyzer="word",
                ngram_range=(1, 2),
                max_features=word_features,
                sublinear_tf=True,
                min_df=2,
                max_df=0.95,
            )),
            ("char", TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 4),
                max_features=char_features,
                sublinear_tf=True,
                min_df=2,
            )),
        ])

    @staticmethod
    def get_config(name: str):
        """Get a feature config by name."""
        configs = {
            "tfidf_word": TFIDFFeatureConfigs.word_ngrams,
            "tfidf_word_char": TFIDFFeatureConfigs.word_char_ngrams,
        }
        if name not in configs:
            raise ValueError(
                f"Unknown config: {name}. "
                f"Available: {list(configs.keys())}"
            )
        return configs[name]()
