"""
CertiNexus AI — Certificate Duplicate Detection

Detects duplicate certificates using multiple strategies:
1. File hash (SHA-256) — exact file duplicates
2. Perceptual hash (pHash) — visually similar images
3. Text similarity (Jaccard + cosine) — semantically similar text
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class DuplicateResult:
    """Result of duplicate detection for a single document."""
    is_duplicate: bool
    duplicate_type: Optional[str] = None  # "exact", "visual", "text"
    similarity_score: float = 0.0
    matched_document_id: Optional[str] = None
    details: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "is_duplicate": self.is_duplicate,
            "duplicate_type": self.duplicate_type,
            "similarity_score": round(self.similarity_score, 4),
            "matched_document_id": self.matched_document_id,
            "details": self.details,
        }


class DuplicateDetector:
    """
    Multi-strategy duplicate detection for certificates.

    Strategies:
    1. File hash: SHA-256 for exact binary duplicates
    2. Text similarity: Jaccard index on word sets + cosine on TF vectors

    Parameters
    ----------
    text_similarity_threshold : float
        Threshold for text-based duplicate detection (Jaccard).
    """

    def __init__(self, text_similarity_threshold: float = 0.85):
        self.text_similarity_threshold = text_similarity_threshold
        # In-memory index (in production, use database)
        self._file_hashes: Dict[str, str] = {}  # hash -> doc_id
        self._text_fingerprints: Dict[str, Tuple[str, set]] = {}  # doc_id -> (text, word_set)

    def compute_file_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def compute_text_hash(self, text: str) -> str:
        """Compute hash of normalized text."""
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()

    def compute_perceptual_hash(self, image_or_path) -> str:
        """
        Compute perceptual difference hash (dHash) for certificate image duplicate detection.
        Works across minor image compressions, watermarks, or resizing.
        """
        try:
            import cv2
            if isinstance(image_or_path, str):
                import os
                if not os.path.exists(image_or_path):
                    return ""
                img = cv2.imread(image_or_path, cv2.IMREAD_GRAYSCALE)
            else:
                img = image_or_path
                if len(img.shape) == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if img is None:
                return ""

            # Resize to 9x8 to compute horizontal gradients
            resized = cv2.resize(img, (9, 8), interpolation=cv2.INTER_AREA)
            # Compare adjacent pixels
            diff = resized[:, 1:] > resized[:, :-1]
            # Convert boolean array to hex string (64-bit hash)
            decimal_val = 0
            hex_str = []
            for index, val in enumerate(diff.flatten()):
                if val:
                    decimal_val += 2 ** (index % 4)
                if (index % 4) == 3:
                    hex_str.append(hex(decimal_val)[2:])
                    decimal_val = 0
            return "".join(hex_str)
        except Exception as e:
            return ""

    def hamming_similarity(self, hash1: str, hash2: str) -> float:
        """Compute normalized similarity [0, 1] between two perceptual hex hashes."""
        if not hash1 or not hash2 or len(hash1) != len(hash2):
            return 0.0
        try:
            bin1 = bin(int(hash1, 16))[2:].zfill(64)
            bin2 = bin(int(hash2, 16))[2:].zfill(64)
            diff = sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
            return 1.0 - (diff / 64.0)
        except Exception:
            return 0.0

    def check_duplicate(
        self,
        document_id: str,
        text: str,
        file_path: Optional[str] = None,
        image_or_path: Optional[any] = None,
    ) -> DuplicateResult:
        """
        Check if a document is a duplicate via file hash, visual perceptual hash, or text similarity.

        Parameters
        ----------
        document_id : str
            Unique ID for this document.
        text : str
            Document text.
        file_path : str, optional
            Path to the document file for hash comparison.
        image_or_path : str or np.ndarray, optional
            Image path or array for perceptual hashing.

        Returns
        -------
        result : DuplicateResult
        """
        # Strategy 1: Exact File Hash
        if file_path:
            file_hash = self.compute_file_hash(file_path)
            if file_hash in self._file_hashes:
                return DuplicateResult(
                    is_duplicate=True,
                    duplicate_type="exact",
                    similarity_score=1.0,
                    matched_document_id=self._file_hashes[file_hash],
                    details={"hash": file_hash},
                )
            self._file_hashes[file_hash] = document_id

        # Strategy 2: Perceptual Hash (Visual)
        target_img = image_or_path or file_path
        if target_img:
            phash = self.compute_perceptual_hash(target_img)
            if phash:
                if not hasattr(self, "_perceptual_hashes"):
                    self._perceptual_hashes: Dict[str, Tuple[str, str]] = {}
                for existing_doc_id, (existing_hash, _) in self._perceptual_hashes.items():
                    sim = self.hamming_similarity(phash, existing_hash)
                    if sim >= 0.92:
                        return DuplicateResult(
                            is_duplicate=True,
                            duplicate_type="visual",
                            similarity_score=sim,
                            matched_document_id=existing_doc_id,
                            details={"phash": phash, "hamming_similarity": round(sim, 4)},
                        )
                self._perceptual_hashes[document_id] = (phash, document_id)

        # Strategy 3: Text similarity
        word_set = set(text.lower().split())
        if not word_set:
            return DuplicateResult(is_duplicate=False)

        best_match = None
        best_score = 0.0

        for existing_id, (existing_text, existing_words) in (
            self._text_fingerprints.items()
        ):
            if not existing_words:
                continue

            # Jaccard similarity
            intersection = len(word_set & existing_words)
            union = len(word_set | existing_words)
            jaccard = intersection / union if union > 0 else 0

            if jaccard > best_score:
                best_score = jaccard
                best_match = existing_id

        # Register this document
        self._text_fingerprints[document_id] = (text, word_set)

        if best_score >= self.text_similarity_threshold:
            return DuplicateResult(
                is_duplicate=True,
                duplicate_type="text",
                similarity_score=best_score,
                matched_document_id=best_match,
                details={
                    "jaccard_similarity": round(best_score, 4),
                },
            )

        return DuplicateResult(is_duplicate=False, similarity_score=best_score)

    def clear_index(self):
        """Clear the in-memory duplicate index."""
        self._file_hashes.clear()
        self._text_fingerprints.clear()
        if hasattr(self, "_perceptual_hashes"):
            self._perceptual_hashes.clear()

