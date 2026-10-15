"""
CertiNexus AI — OCR Pipeline Module

CRAFT-based text detection + CRNN-based text recognition,
implemented as a modular pipeline wrapping EasyOCR internals.
"""
from .pipeline import OCRPipeline, OCRResult
from .preprocessing import ImagePreprocessor
from .postprocessor import OCRPostProcessor
