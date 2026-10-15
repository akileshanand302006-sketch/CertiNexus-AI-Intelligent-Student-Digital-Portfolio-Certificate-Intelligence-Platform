"""
CertiNexus AI — CRNN Text Recognizer

Wraps EasyOCR's internal CRNN (Convolutional Recurrent Neural Network)
with BiLSTM + CTC decoding for per-region text recognition.

Provides a clean TextRecognizer interface that operates on cropped
text regions produced by the CRAFT detector.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class RecognitionResult:
    """Recognition result for a single text region."""
    text: str
    confidence: float
    region_id: int
    bbox: Optional[List[List[int]]] = None
    processing_time_ms: float = 0.0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "region_id": self.region_id,
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class FullRecognitionResult:
    """Complete recognition result for an image."""
    regions: List[RecognitionResult]
    full_text: str = ""
    total_time_ms: float = 0.0
    avg_confidence: float = 0.0
    num_regions: int = 0
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.num_regions = len(self.regions)
        if self.regions:
            self.avg_confidence = np.mean(
                [r.confidence for r in self.regions]
            )
        if not self.full_text:
            self.full_text = " ".join(
                r.text for r in self.regions if r.text
            )


class CRNNRecognizer:
    """
    Text recognizer using CRNN+BiLSTM+CTC via EasyOCR.

    Uses EasyOCR's pretrained CRNN model to recognize text
    in individual regions detected by the CRAFT detector.

    Parameters
    ----------
    languages : list of str
        Languages for recognition.
    gpu : bool
        Use GPU for recognition.
    min_confidence : float
        Minimum recognition confidence to include.
    batch_size : int
        Batch size for recognition (not currently used by EasyOCR).
    """

    def __init__(
        self,
        languages: Optional[List[str]] = None,
        gpu: bool = False,
        min_confidence: float = 0.1,
        batch_size: int = 8,
    ):
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.min_confidence = min_confidence
        self.batch_size = batch_size
        self._reader = None

    def _ensure_reader(self):
        """Lazy-initialize EasyOCR reader."""
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(
                self.languages, gpu=self.gpu
            )

    def recognize(
        self,
        image: np.ndarray,
        regions: Optional[List] = None,
    ) -> FullRecognitionResult:
        """
        Recognize text in an image, optionally for specific regions.

        Parameters
        ----------
        image : np.ndarray
            Input image.
        regions : list of TextRegion, optional
            Pre-detected text regions. If None, runs full
            detection+recognition.

        Returns
        -------
        result : FullRecognitionResult
        """
        self._ensure_reader()
        start_time = time.time()

        # Run full EasyOCR pipeline (CRAFT detection + CRNN recognition)
        raw_results = self._reader.readtext(
            image,
            detail=1,
            paragraph=False,
        )

        recognition_results = []
        for idx, (bbox, text, confidence) in enumerate(raw_results):
            if confidence < self.min_confidence:
                continue

            # Convert bbox to our format
            bbox_formatted = [[int(p[0]), int(p[1])] for p in bbox]

            rec_result = RecognitionResult(
                text=text.strip(),
                confidence=float(confidence),
                region_id=idx,
                bbox=bbox_formatted,
            )
            recognition_results.append(rec_result)

        total_time = (time.time() - start_time) * 1000

        full_result = FullRecognitionResult(
            regions=recognition_results,
            total_time_ms=round(total_time, 2),
            metadata={
                "total_raw_results": len(raw_results),
                "filtered_by_confidence": (
                    len(raw_results) - len(recognition_results)
                ),
                "min_confidence": self.min_confidence,
            },
        )

        return full_result

    def recognize_region(
        self,
        image: np.ndarray,
        bbox: List[List[int]],
        region_id: int = 0,
    ) -> RecognitionResult:
        """
        Recognize text in a specific cropped region.

        Parameters
        ----------
        image : np.ndarray
            Full image.
        bbox : list
            Bounding box [[x1,y1], [x2,y2], [x3,y3], [x4,y4]].
        region_id : int
            ID for this region.

        Returns
        -------
        result : RecognitionResult
        """
        self._ensure_reader()
        start_time = time.time()

        # Crop the region
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        x_min = max(0, min(xs))
        x_max = min(image.shape[1], max(xs))
        y_min = max(0, min(ys))
        y_max = min(image.shape[0], max(ys))

        cropped = image[y_min:y_max, x_min:x_max]

        if cropped.size == 0:
            return RecognitionResult(
                text="",
                confidence=0.0,
                region_id=region_id,
                bbox=bbox,
            )

        # Recognize text in cropped region
        raw_results = self._reader.readtext(
            cropped, detail=1, paragraph=False
        )

        # Combine all text in the region
        texts = []
        confidences = []
        for _, text, conf in raw_results:
            texts.append(text.strip())
            confidences.append(conf)

        combined_text = " ".join(texts)
        avg_conf = np.mean(confidences) if confidences else 0.0

        proc_time = (time.time() - start_time) * 1000

        return RecognitionResult(
            text=combined_text,
            confidence=float(avg_conf),
            region_id=region_id,
            bbox=bbox,
            processing_time_ms=round(proc_time, 2),
        )
