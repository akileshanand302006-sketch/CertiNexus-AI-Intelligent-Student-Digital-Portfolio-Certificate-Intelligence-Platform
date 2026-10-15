"""
CertiNexus AI — Complete OCR Pipeline

Integrates the full CRAFT -> CRNN -> Post-processing pipeline
into a single, easy-to-use interface.

Pipeline stages:
1. Image preprocessing (grayscale, denoise, deskew, CLAHE)
2. CRAFT text detection (bounding boxes)
3. CRNN text recognition (per-region text + confidence)
4. Post-processing (artifact removal, domain corrections)
5. Text merging in reading order
"""

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from .preprocessing import ImagePreprocessor, PreprocessingResult
from .craft_detector import CRAFTDetector, DetectionResult
from .crnn_recognizer import CRNNRecognizer, FullRecognitionResult
from .postprocessor import OCRPostProcessor, PostProcessingResult


@dataclass
class OCRResult:
    """Complete OCR pipeline result."""
    # Final output
    text: str
    confidence: float
    quality_score: float

    # Stage results
    preprocessing: Optional[PreprocessingResult] = None
    detection: Optional[DetectionResult] = None
    recognition: Optional[FullRecognitionResult] = None
    postprocessing: Optional[PostProcessingResult] = None

    # Timing
    total_time_ms: float = 0.0
    stage_times: Dict[str, float] = field(default_factory=dict)

    # Metadata
    num_regions: int = 0
    image_size: Tuple[int, int] = (0, 0)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize to dict for API responses."""
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "quality_score": round(self.quality_score, 1),
            "num_regions": self.num_regions,
            "image_size": self.image_size,
            "total_time_ms": round(self.total_time_ms, 2),
            "stage_times": {
                k: round(v, 2) for k, v in self.stage_times.items()
            },
            "regions": [
                r.to_dict()
                for r in (
                    self.recognition.regions if self.recognition else []
                )
            ],
            "postprocessing": {
                "corrections_count": (
                    self.postprocessing.num_corrections
                    if self.postprocessing else 0
                ),
                "corrections": (
                    self.postprocessing.corrections_applied
                    if self.postprocessing else []
                ),
            },
            "image_quality": self.metadata.get("quality_metrics", {}),
        }

    def summary(self) -> str:
        lines = [
            "OCR Pipeline Result:",
            f"  Text length: {len(self.text)} chars",
            f"  Confidence: {self.confidence:.2%}",
            f"  Quality: {self.quality_score:.1f}/100",
            f"  Regions detected: {self.num_regions}",
            f"  Image size: {self.image_size}",
            f"  Total time: {self.total_time_ms:.0f}ms",
        ]
        for stage, t in self.stage_times.items():
            lines.append(f"    {stage}: {t:.0f}ms")
        return "\n".join(lines)


class OCRPipeline:
    """
    End-to-end OCR pipeline for certificate documents.

    Orchestrates:
    1. ImagePreprocessor — image enhancement
    2. CRAFTDetector — text region detection
    3. CRNNRecognizer — text recognition per region
    4. OCRPostProcessor — text cleanup and correction

    Parameters
    ----------
    languages : list of str
        OCR languages.
    gpu : bool
        Use GPU acceleration.
    preprocess : bool
        Apply image preprocessing.
    postprocess : bool
        Apply text post-processing.
    min_confidence : float
        Minimum region confidence to include.
    """

    def __init__(
        self,
        languages: Optional[List[str]] = None,
        gpu: bool = False,
        preprocess: bool = True,
        postprocess: bool = True,
        min_confidence: float = 0.1,
    ):
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.do_preprocess = preprocess
        self.do_postprocess = postprocess
        self.min_confidence = min_confidence

        # Initialize components
        self.preprocessor = ImagePreprocessor()
        self.recognizer = CRNNRecognizer(
            languages=self.languages,
            gpu=self.gpu,
            min_confidence=self.min_confidence,
        )
        self.postprocessor = OCRPostProcessor()

    def process(
        self,
        image: Union[str, np.ndarray],
        preprocess_steps: Optional[List[str]] = None,
    ) -> OCRResult:
        """
        Run the complete OCR pipeline on an image.

        Parameters
        ----------
        image : str or np.ndarray
            Path to an image file, or a numpy array (BGR).
        preprocess_steps : list of str, optional
            Specific preprocessing steps. Uses defaults if None.

        Returns
        -------
        result : OCRResult
        """
        total_start = time.time()
        stage_times = {}

        # Load image if path
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img = cv2.imread(image)
            if img is None:
                raise ValueError(
                    f"Could not read image: {image}"
                )
        else:
            img = image.copy()

        image_size = img.shape[:2]

        # Stage 0: Quality assessment
        t0 = time.time()
        quality_metrics = self.preprocessor.compute_quality_score(img)
        stage_times["quality_assessment"] = (
            (time.time() - t0) * 1000
        )

        # Stage 1: Preprocessing
        preprocess_result = None
        if self.do_preprocess:
            t1 = time.time()
            preprocess_result = self.preprocessor.preprocess(
                img, steps=preprocess_steps
            )
            processed_img = preprocess_result.processed_image
            stage_times["preprocessing"] = (
                (time.time() - t1) * 1000
            )
        else:
            processed_img = img

        # Stage 2+3: Recognition (CRAFT detection + CRNN recognition
        # are handled together by EasyOCR)
        t2 = time.time()

        # EasyOCR works best on the original color/grayscale image
        # rather than heavily preprocessed ones.
        # Use the preprocessed image for quality metrics, but the
        # original (possibly denoised + deskewed) for actual OCR.
        ocr_image = img
        if preprocess_result:
            # Use deskewed but minimally processed version
            light_result = self.preprocessor.preprocess(
                img, steps=["deskew", "normalize_size"]
            )
            ocr_image = light_result.processed_image

        recognition_result = self.recognizer.recognize(ocr_image)
        stage_times["detection_recognition"] = (
            (time.time() - t2) * 1000
        )

        # Stage 4: Post-processing
        postprocess_result = None
        final_text = recognition_result.full_text

        if self.do_postprocess and final_text:
            t3 = time.time()
            postprocess_result = self.postprocessor.process(final_text)
            final_text = postprocess_result.cleaned_text
            stage_times["postprocessing"] = (
                (time.time() - t3) * 1000
            )

        total_time = (time.time() - total_start) * 1000

        return OCRResult(
            text=final_text,
            confidence=float(recognition_result.avg_confidence),
            quality_score=quality_metrics.get("quality_score", 0.0),
            preprocessing=preprocess_result,
            detection=None,  # Detection is integrated in recognition
            recognition=recognition_result,
            postprocessing=postprocess_result,
            total_time_ms=round(total_time, 2),
            stage_times=stage_times,
            num_regions=recognition_result.num_regions,
            image_size=image_size,
            metadata={
                "quality_metrics": quality_metrics,
                "languages": self.languages,
                "gpu": self.gpu,
            },
        )

    def process_batch(
        self,
        images: List[Union[str, np.ndarray]],
    ) -> List[OCRResult]:
        """Process a batch of images."""
        return [self.process(img) for img in images]


# Module-level singleton for reuse across requests
_pipeline_instance = None


def get_ocr_pipeline(
    languages: Optional[List[str]] = None,
    gpu: bool = False,
) -> OCRPipeline:
    """Get or create singleton OCR pipeline."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = OCRPipeline(
            languages=languages, gpu=gpu
        )
    return _pipeline_instance


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("CertiNexus AI — OCR Pipeline Test")
    print("=" * 60)

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        pipeline = OCRPipeline(gpu=False)
        result = pipeline.process(image_path)
        print(result.summary())
        print(f"\nExtracted text:\n{result.text}")
    else:
        print("Usage: python -m ml.ocr.pipeline <image_path>")
        print("\nInitializing pipeline to verify imports...")
        pipeline = OCRPipeline(gpu=False)
        print("Pipeline initialized successfully!")
        print(f"  Languages: {pipeline.languages}")
        print(f"  GPU: {pipeline.gpu}")
        print(f"  Preprocess: {pipeline.do_preprocess}")
        print(f"  Postprocess: {pipeline.do_postprocess}")
