"""
CertiNexus AI — Feature Pipeline Builder

Combines TF-IDF features with engineered document-level features
into unified feature pipelines for each experiment configuration.
"""

from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MaxAbsScaler

from .tfidf_features import TFIDFFeatureConfigs
from .engineered_features import DocumentMetaFeatures


class FeaturePipelineBuilder:
    """
    Build feature pipelines for the three experiment configurations.

    Configurations:
    1. tfidf_word: TF-IDF word n-grams only
    2. tfidf_word_char: TF-IDF word + character n-grams
    3. tfidf_enriched: TF-IDF word + char + 18 engineered meta-features
    """

    @staticmethod
    def build(config_name: str) -> FeatureUnion:
        """
        Build a feature pipeline by configuration name.

        Parameters
        ----------
        config_name : str
            One of: "tfidf_word", "tfidf_word_char", "tfidf_enriched"

        Returns
        -------
        pipeline : FeatureUnion
        """
        if config_name == "tfidf_word":
            return FeatureUnion([
                ("tfidf", TFIDFFeatureConfigs.word_ngrams()),
            ])

        elif config_name == "tfidf_word_char":
            return TFIDFFeatureConfigs.word_char_ngrams()

        elif config_name == "tfidf_enriched":
            return FeatureUnion([
                ("tfidf_word", TFIDFFeatureConfigs.word_ngrams(4000)),
                ("tfidf_char", TFIDFFeatureConfigs.word_char_ngrams(
                    word_features=3000, char_features=2000
                )),
                ("meta", Pipeline([
                    ("features", DocumentMetaFeatures()),
                    ("scaler", MaxAbsScaler()),
                ])),
            ])

        else:
            raise ValueError(
                f"Unknown config: {config_name}. "
                f"Available: tfidf_word, tfidf_word_char, tfidf_enriched"
            )

    @staticmethod
    def get_all_configs():
        """Return list of all config names."""
        return ["tfidf_word", "tfidf_word_char", "tfidf_enriched"]
