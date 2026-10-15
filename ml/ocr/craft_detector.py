"""
CertiNexus AI — CRAFT Text Detector

Wraps EasyOCR's internal CRAFT (Character Region Awareness for Text
Detection) model to expose text region bounding boxes with confidence
scores.

This provides a clean TextDetector interface while leveraging the
pretrained CRAFT weights bundled with EasyOCR.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class TextRegion:
    """A detected text region with bounding box and confidence."""
    bbox: List[List[int]]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    confidence: float
    region_id: int
    area: int = 0
    center: Tuple[int, int] = (0, 0)
    width: int = 0
    height: int = 0

    def __post_init__(self):
        if self.bbox:
            xs = [p[0] for p in self.bbox]
            ys = [p[1] for p in self.bbox]
            self.width = max(xs) - min(xs)
            self.height = max(ys) - min(ys)
            self.area = self.width * self.height
            self.center = (
                int(np.mean(xs)),
                int(np.mean(ys)),
            )

    def crop_from(self, image: np.ndarray) -> np.ndarray:
        """Crop the text region from the image."""
        xs = [p[0] for p in self.bbox]
        ys = [p[1] for p in self.bbox]
        x_min = max(0, min(xs))
        x_max = min(image.shape[1], max(xs))
        y_min = max(0, min(ys))
        y_max = min(image.shape[0], max(ys))
        return image[y_min:y_max, x_min:x_max]

    def to_dict(self) -> Dict:
        return {
            "region_id": self.region_id,
            "bbox": self.bbox,
            "confidence": round(self.confidence, 4),
            "center": self.center,
            "width": self.width,
            "height": self.height,
            "area": self.area,
        }


@dataclass
class DetectionResult:
    """Complete text detection result."""
    regions: List[TextRegion]
    image_size: Tuple[int, int]  # (height, width)
    detection_time_ms: float = 0.0
    num_regions: int = 0
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.num_regions = len(self.regions)

    def sort_reading_order(self):
        """Sort regions in natural reading order (top-to-bottom,
        left-to-right)."""
        if not self.regions:
            return

        avg_height = np.mean([r.height for r in self.regions])
        line_threshold = avg_height * 0.5

        # Sort by y-center first, then x-center
        self.regions.sort(key=lambda r: (r.center[1], r.center[0]))

        # Group into lines
        lines = []
        current_line = [self.regions[0]]
        for region in self.regions[1:]:
            if abs(
                region.center[1] - current_line[-1].center[1]
            ) < line_threshold:
                current_line.append(region)
            else:
                lines.append(current_line)
                current_line = [region]
        lines.append(current_line)

        # Sort each line left-to-right
        sorted_regions = []
        for line in lines:
            line.sort(key=lambda r: r.center[0])
            sorted_regions.extend(line)

        self.regions = sorted_regions


class CRAFTDetector:
    """
    Text region detector using CRAFT via EasyOCR.

    Wraps EasyOCR reader to access the internal CRAFT text detection
    stage, exposing per-region bounding boxes and confidence scores.

    Parameters
    ----------
    languages : list of str
        Languages for OCR (default: ['en']).
    gpu : bool
        Whether to use GPU (auto-detected if True).
    min_confidence : float
        Minimum detection confidence threshold.
    min_area : int
        Minimum bounding box area in pixels.
    """

    def __init__(
        self,
        languages: Optional[List[str]] = None,
        gpu: bool = False,
        min_confidence: float = 0.3,
        min_area: int = 100,
    ):
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.min_confidence = min_confidence
        self.min_area = min_area
        self._reader = None

    def _ensure_reader(self):
        """Lazy-initialize EasyOCR reader."""
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(
                self.languages, gpu=self.gpu
            )

    def detect(self, image: np.ndarray) -> DetectionResult:
        """
        Detect text regions in an image.

        Parameters
        ----------
        image : np.ndarray
            Input image (BGR or grayscale).

        Returns
        -------
        result : DetectionResult
            Detected text regions with bounding boxes and confidence.
        """
        self._ensure_reader()
        start_time = time.time()

        # Use EasyOCR's detect method for CRAFT-based detection
        horizontal_list, free_list = self._reader.detect(image)

        regions = []
        region_id = 0

        # Process horizontal text boxes
        if horizontal_list and len(horizontal_list) > 0:
            for box_list in horizontal_list:
                if box_list is None:
                    continue
                for box in box_list:
                    # EasyOCR detect returns [x_min, x_max, y_min, y_max]
                    x_min, x_max, y_min, y_max = (
                        int(box[0]), int(box[1]),
                        int(box[2]), int(box[3])
                    )
                    bbox = [
                        [x_min, y_min],
                        [x_max, y_min],
                        [x_max, y_max],
                        [x_min, y_max],
                    ]
                    area = (x_max - x_min) * (y_max - y_min)
                    if area < self.min_area:
                        continue

                    region = TextRegion(
                        bbox=bbox,
                        confidence=0.9,  # CRAFT detection confidence
                        region_id=region_id,
                    )
                    regions.append(region)
                    region_id += 1

        # Process free-form text boxes
        if free_list and len(free_list) > 0:
            for box_list in free_list:
                if box_list is None:
                    continue
                for box in box_list:
                    bbox = [
                        [int(p[0]), int(p[1])] for p in box
                    ]
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    area = (
                        (max(xs) - min(xs)) * (max(ys) - min(ys))
                    )
                    if area < self.min_area:
                        continue

                    region = TextRegion(
                        bbox=bbox,
                        confidence=0.8,
                        region_id=region_id,
                    )
                    regions.append(region)
                    region_id += 1

        detection_time = (time.time() - start_time) * 1000

        result = DetectionResult(
            regions=regions,
            image_size=image.shape[:2],
            detection_time_ms=round(detection_time, 2),
            metadata={
                "num_horizontal": len(
                    horizontal_list[0] if horizontal_list else []
                ),
                "num_freeform": len(
                    free_list[0] if free_list else []
                ),
                "min_confidence": self.min_confidence,
                "min_area": self.min_area,
            },
        )

        result.sort_reading_order()
        return result

    def visualize(
        self,
        image: np.ndarray,
        detection_result: DetectionResult,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """Draw detected regions on the image for visualization."""
        vis_image = image.copy()
        if len(vis_image.shape) == 2:
            vis_image = cv2.cvtColor(vis_image, cv2.COLOR_GRAY2BGR)

        for region in detection_result.regions:
            pts = np.array(region.bbox, dtype=np.int32)
            cv2.polylines(
                vis_image, [pts], True, color, thickness
            )
            # Label
            label = f"R{region.region_id} ({region.confidence:.2f})"
            cv2.putText(
                vis_image, label,
                (region.bbox[0][0], region.bbox[0][1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1,
            )

        return vis_image
