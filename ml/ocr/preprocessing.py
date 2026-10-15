"""
CertiNexus AI — Image Preprocessing for OCR

Provides image enhancement operations to improve OCR accuracy:
- Grayscale conversion
- Noise reduction (bilateral filter)
- Deskewing (Hough transform based)
- Adaptive thresholding
- Contrast enhancement (CLAHE)
- Resolution normalization
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class PreprocessingResult:
    """Result of image preprocessing."""
    original_image: np.ndarray
    processed_image: np.ndarray
    steps_applied: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    @property
    def original_size(self) -> Tuple[int, int]:
        return self.original_image.shape[:2]

    @property
    def processed_size(self) -> Tuple[int, int]:
        return self.processed_image.shape[:2]


class ImagePreprocessor:
    """
    Certificate image preprocessor for OCR enhancement.

    Applies a configurable pipeline of image processing steps
    to maximize OCR accuracy on certificate documents.

    Parameters
    ----------
    target_dpi : int
        Target resolution for normalization (default: 300 DPI).
    denoise_strength : int
        Bilateral filter diameter (higher = more smoothing).
    clahe_clip_limit : float
        CLAHE contrast limit (higher = more contrast).
    clahe_grid_size : tuple
        CLAHE tile grid size.
    adaptive_block_size : int
        Block size for adaptive thresholding (must be odd).
    adaptive_c : int
        Constant subtracted from adaptive threshold mean.
    enable_deskew : bool
        Whether to attempt automatic deskewing.
    deskew_angle_threshold : float
        Maximum deskew angle in degrees (larger angles are ignored).
    """

    def __init__(
        self,
        target_dpi: int = 300,
        denoise_strength: int = 9,
        clahe_clip_limit: float = 2.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
        adaptive_block_size: int = 11,
        adaptive_c: int = 2,
        enable_deskew: bool = True,
        deskew_angle_threshold: float = 15.0,
    ):
        self.target_dpi = target_dpi
        self.denoise_strength = denoise_strength
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_grid_size = clahe_grid_size
        self.adaptive_block_size = adaptive_block_size
        self.adaptive_c = adaptive_c
        self.enable_deskew = enable_deskew
        self.deskew_angle_threshold = deskew_angle_threshold

    def preprocess(
        self,
        image: np.ndarray,
        steps: Optional[List[str]] = None,
    ) -> PreprocessingResult:
        """
        Apply preprocessing pipeline to an image.

        Parameters
        ----------
        image : np.ndarray
            Input image (BGR or grayscale).
        steps : list of str, optional
            Specific steps to apply. If None, applies full pipeline:
            ["grayscale", "denoise", "clahe", "deskew", "normalize_size"]

        Returns
        -------
        result : PreprocessingResult
        """
        if steps is None:
            steps = [
                "grayscale", "denoise", "clahe",
                "deskew", "normalize_size"
            ]

        result = PreprocessingResult(
            original_image=image.copy(),
            processed_image=image.copy(),
        )

        step_map = {
            "grayscale": self._to_grayscale,
            "denoise": self._denoise,
            "clahe": self._apply_clahe,
            "deskew": self._deskew,
            "threshold": self._adaptive_threshold,
            "normalize_size": self._normalize_size,
        }

        for step_name in steps:
            if step_name in step_map:
                result.processed_image = step_map[step_name](
                    result.processed_image, result.metadata
                )
                result.steps_applied.append(step_name)

        return result

    def _to_grayscale(self, image: np.ndarray,
                      metadata: Dict) -> np.ndarray:
        """Convert to grayscale if needed."""
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            metadata["converted_to_grayscale"] = True
            return gray
        elif len(image.shape) == 3 and image.shape[2] == 4:
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
            metadata["converted_to_grayscale"] = True
            return gray
        metadata["converted_to_grayscale"] = False
        return image

    def _denoise(self, image: np.ndarray,
                 metadata: Dict) -> np.ndarray:
        """Apply bilateral filtering for noise reduction while
        preserving edges."""
        if len(image.shape) == 2:
            # Grayscale
            denoised = cv2.bilateralFilter(
                image,
                d=self.denoise_strength,
                sigmaColor=75,
                sigmaSpace=75,
            )
        else:
            denoised = cv2.bilateralFilter(
                image,
                d=self.denoise_strength,
                sigmaColor=75,
                sigmaSpace=75,
            )
        metadata["denoise_strength"] = self.denoise_strength
        return denoised

    def _apply_clahe(self, image: np.ndarray,
                     metadata: Dict) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization."""
        if len(image.shape) == 3:
            # Convert to LAB, apply CLAHE to L channel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(
                clipLimit=self.clahe_clip_limit,
                tileGridSize=self.clahe_grid_size,
            )
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(
                clipLimit=self.clahe_clip_limit,
                tileGridSize=self.clahe_grid_size,
            )
            enhanced = clahe.apply(image)
        metadata["clahe_clip_limit"] = self.clahe_clip_limit
        return enhanced

    def _deskew(self, image: np.ndarray,
                metadata: Dict) -> np.ndarray:
        """Deskew image using Hough line detection."""
        if not self.enable_deskew:
            metadata["deskew_applied"] = False
            return image

        # Ensure grayscale for edge detection
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Hough line detection
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=min(image.shape[:2]) // 4,
            maxLineGap=10,
        )

        if lines is None or len(lines) == 0:
            metadata["deskew_applied"] = False
            metadata["deskew_angle"] = 0.0
            return image

        # Calculate dominant angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            # Only consider near-horizontal lines
            if abs(angle) < self.deskew_angle_threshold:
                angles.append(angle)

        if not angles:
            metadata["deskew_applied"] = False
            metadata["deskew_angle"] = 0.0
            return image

        median_angle = np.median(angles)

        # Only deskew if angle is significant
        if abs(median_angle) < 0.5:
            metadata["deskew_applied"] = False
            metadata["deskew_angle"] = float(median_angle)
            return image

        # Rotate image
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        metadata["deskew_applied"] = True
        metadata["deskew_angle"] = float(median_angle)
        return rotated

    def _adaptive_threshold(self, image: np.ndarray,
                            metadata: Dict) -> np.ndarray:
        """Apply adaptive thresholding for binarization."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        thresh = cv2.adaptiveThreshold(
            gray,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=self.adaptive_block_size,
            C=self.adaptive_c,
        )
        metadata["threshold_applied"] = True
        return thresh

    def _normalize_size(self, image: np.ndarray,
                        metadata: Dict) -> np.ndarray:
        """
        Normalize image size — ensure minimum resolution
        for OCR without excessive upscaling.
        """
        h, w = image.shape[:2]
        min_dim = 800  # Minimum dimension for OCR
        max_dim = 4000  # Maximum dimension to prevent memory issues

        metadata["original_dimensions"] = (h, w)

        # Upscale if too small
        if min(h, w) < min_dim:
            scale = min_dim / min(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(
                image, (new_w, new_h), interpolation=cv2.INTER_CUBIC
            )
            metadata["upscaled"] = True
            metadata["scale_factor"] = scale

        # Downscale if too large
        elif max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(
                image, (new_w, new_h), interpolation=cv2.INTER_AREA
            )
            metadata["downscaled"] = True
            metadata["scale_factor"] = scale
        else:
            metadata["resize_applied"] = False

        metadata["final_dimensions"] = image.shape[:2]
        return image

    def compute_quality_score(self, image: np.ndarray) -> Dict:
        """
        Compute image quality metrics for OCR suitability.

        Returns
        -------
        dict with keys:
            - sharpness : float (Laplacian variance, higher = sharper)
            - contrast : float (std deviation, higher = more contrast)
            - brightness : float (mean pixel value, 0-255)
            - noise_estimate : float (lower = cleaner)
            - quality_score : float (0-100 composite score)
            - quality_level : str ("high", "medium", "low")
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var())

        # Contrast (std deviation)
        contrast = float(gray.std())

        # Brightness (mean)
        brightness = float(gray.mean())

        # Noise estimate (using difference between original and smoothed)
        smoothed = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = float(np.abs(
            gray.astype(float) - smoothed.astype(float)
        ).mean())

        # Composite quality score (0-100)
        # Sharpness: ideal > 100
        sharpness_score = min(sharpness / 100, 1.0) * 30
        # Contrast: ideal > 50
        contrast_score = min(contrast / 50, 1.0) * 25
        # Brightness: ideal 100-180
        brightness_deviation = abs(brightness - 140) / 140
        brightness_score = (1 - min(brightness_deviation, 1.0)) * 25
        # Noise: ideal < 5
        noise_score = max(1 - noise / 10, 0) * 20

        quality_score = (
            sharpness_score + contrast_score +
            brightness_score + noise_score
        )

        quality_level = (
            "high" if quality_score >= 70 else
            "medium" if quality_score >= 40 else
            "low"
        )

        return {
            "sharpness": round(sharpness, 2),
            "contrast": round(contrast, 2),
            "brightness": round(brightness, 2),
            "noise_estimate": round(noise, 2),
            "quality_score": round(quality_score, 1),
            "quality_level": quality_level,
        }
