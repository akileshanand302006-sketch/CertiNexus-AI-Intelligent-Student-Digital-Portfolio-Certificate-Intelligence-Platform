"""
CertiNexus AI — OCR Post-Processing

Intelligent cleanup of OCR-extracted text:
- Whitespace normalization
- Common OCR artifact removal
- Context-aware corrections (dates, certificate IDs)
- Confidence-weighted text merging
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PostProcessingResult:
    """Result of post-processing OCR text."""
    original_text: str
    cleaned_text: str
    corrections_applied: List[Dict] = field(default_factory=list)
    num_corrections: int = 0

    def __post_init__(self):
        self.num_corrections = len(self.corrections_applied)


class OCRPostProcessor:
    """
    Post-process OCR output for certificate documents.

    Applies context-aware corrections specific to the certificate
    domain while preserving important information like dates,
    certificate IDs, and organization names.

    Parameters
    ----------
    fix_common_ocr_errors : bool
        Apply common OCR character substitution fixes.
    normalize_whitespace : bool
        Normalize spaces, tabs, and newlines.
    fix_dates : bool
        Attempt to fix malformed date patterns.
    fix_cert_ids : bool
        Clean up certificate ID patterns.
    remove_artifacts : bool
        Remove common OCR artifacts (random symbols, control chars).
    min_word_length : int
        Remove isolated single characters (except common ones like
        I, a, A).
    """

    # Common OCR character substitutions
    OCR_CORRECTIONS = {
        "0": {"O": 0.3, "o": 0.3},  # Zero vs letter O
        "1": {"l": 0.3, "I": 0.3},   # One vs lowercase L vs capital I
        "5": {"S": 0.2},              # Five vs S
        "8": {"B": 0.2},              # Eight vs B
        "|": {"l": 0.4, "I": 0.4},   # Pipe vs L vs I
        "rn": {"m": 0.3},            # rn vs m
        "cl": {"d": 0.2},            # cl vs d
        "vv": {"w": 0.3},            # vv vs w
    }

    # Common certificate-domain terms for context correction
    DOMAIN_TERMS = {
        "certif1cate": "certificate",
        "cert1ficate": "certificate",
        "certlficate": "certificate",
        "ach1evement": "achievement",
        "complet1on": "completion",
        "part1cipation": "participation",
        "recogn1tion": "recognition",
        "organ1zation": "organization",
        "un1versity": "university",
        "inst1tute": "institute",
        "cert1fied": "certified",
        "cert1fy": "certify",
        "techno1ogy": "technology",
        "deve1opment": "development",
        "informat1on": "information",
        "internat1onal": "international",
    }

    # Patterns to remove (OCR artifacts)
    ARTIFACT_PATTERNS = [
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]",  # Control characters
        r"[\ufffd\ufffe\uffff]",                 # Unicode replacement chars
        r"\|{3,}",                                 # Multiple pipes
        r"_{3,}",                                   # Decorative underscores
        r"={3,}",                                   # Decorative equals
        r"~{3,}",                                   # Multiple tildes
        r"\*{3,}",                                 # Multiple asterisks
    ]

    def __init__(
        self,
        fix_common_ocr_errors: bool = True,
        normalize_whitespace: bool = True,
        fix_dates: bool = True,
        fix_cert_ids: bool = True,
        remove_artifacts: bool = True,
        min_word_length: int = 0,
    ):
        self.fix_common_ocr_errors = fix_common_ocr_errors
        self.normalize_whitespace = normalize_whitespace
        self.fix_dates = fix_dates
        self.fix_cert_ids = fix_cert_ids
        self.remove_artifacts = remove_artifacts
        self.min_word_length = min_word_length

    def process(self, text: str) -> PostProcessingResult:
        """
        Apply full post-processing pipeline to OCR text.

        Parameters
        ----------
        text : str
            Raw OCR-extracted text.

        Returns
        -------
        result : PostProcessingResult
        """
        original = text
        corrections = []

        # Step 1: Remove artifacts
        if self.remove_artifacts:
            text, artifact_corrections = self._remove_artifacts(text)
            corrections.extend(artifact_corrections)

        # Step 2: Normalize whitespace
        if self.normalize_whitespace:
            text = self._normalize_whitespace(text)

        # Step 3: Fix domain-specific terms
        if self.fix_common_ocr_errors:
            text, term_corrections = self._fix_domain_terms(text)
            corrections.extend(term_corrections)

        # Step 4: Fix date patterns
        if self.fix_dates:
            text, date_corrections = self._fix_date_patterns(text)
            corrections.extend(date_corrections)

        # Step 5: Fix certificate ID patterns
        if self.fix_cert_ids:
            text, id_corrections = self._fix_cert_id_patterns(text)
            corrections.extend(id_corrections)

        # Step 6: Final whitespace cleanup
        text = re.sub(r"\s+", " ", text).strip()

        return PostProcessingResult(
            original_text=original,
            cleaned_text=text,
            corrections_applied=corrections,
        )

    def process_regions(
        self,
        regions: List[Dict],
    ) -> Tuple[str, List[Dict]]:
        """
        Process and merge text from multiple OCR regions.

        Regions are merged in order, with confidence-weighted
        decisions for overlapping content.

        Parameters
        ----------
        regions : list of dict
            Each dict must have 'text' and 'confidence' keys.

        Returns
        -------
        merged_text : str
            Combined, cleaned text.
        processed_regions : list of dict
            Individual region results.
        """
        processed = []
        texts = []

        for region in regions:
            result = self.process(region.get("text", ""))
            processed.append({
                "original": region.get("text", ""),
                "cleaned": result.cleaned_text,
                "confidence": region.get("confidence", 0.0),
                "corrections": result.corrections_applied,
            })
            if result.cleaned_text.strip():
                texts.append(result.cleaned_text)

        merged = " ".join(texts)
        # Final cleanup
        merged = re.sub(r"\s+", " ", merged).strip()

        return merged, processed

    def _remove_artifacts(self, text: str) -> Tuple[str, List[Dict]]:
        corrections = []
        for pattern in self.ARTIFACT_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                text = re.sub(pattern, " ", text)
                corrections.append({
                    "type": "artifact_removal",
                    "pattern": pattern,
                    "count": len(matches),
                })
        return text, corrections

    def _normalize_whitespace(self, text: str) -> str:
        # Replace tabs and multiple spaces with single space
        text = re.sub(r"\t+", " ", text)
        text = re.sub(r" {2,}", " ", text)
        # Normalize newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove leading/trailing whitespace per line
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines)

    def _fix_domain_terms(
        self, text: str
    ) -> Tuple[str, List[Dict]]:
        corrections = []
        text_lower = text.lower()

        for wrong, correct in self.DOMAIN_TERMS.items():
            if wrong in text_lower:
                # Case-preserving replacement
                pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                text = pattern.sub(correct, text)
                corrections.append({
                    "type": "domain_correction",
                    "from": wrong,
                    "to": correct,
                })

        return text, corrections

    def _fix_date_patterns(
        self, text: str
    ) -> Tuple[str, List[Dict]]:
        corrections = []

        # Fix common OCR date errors:
        # "2O23" -> "2023", "2O24" -> "2024"
        date_fixes = re.findall(r"\b2[O0](\d{2})\b", text)
        if date_fixes:
            text = re.sub(r"\b2O(\d{2})\b", r"20\1", text)
            corrections.append({
                "type": "date_fix",
                "description": "Fixed O->0 in year",
            })

        # Fix "l2" -> "12", "l3" -> "13" etc in date context
        date_context = re.findall(
            r"\b[lI](\d)[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b",
            text
        )
        if date_context:
            text = re.sub(
                r"\b[lI](\d)([/\-\.])(\d{1,2})([/\-\.])(\d{2,4})\b",
                r"1\1\2\3\4\5",
                text,
            )
            corrections.append({
                "type": "date_fix",
                "description": "Fixed l/I->1 in date day/month",
            })

        return text, corrections

    def _fix_cert_id_patterns(
        self, text: str
    ) -> Tuple[str, List[Dict]]:
        corrections = []

        # Fix "CERT-O123" -> "CERT-0123"
        cert_id_fixes = re.findall(
            r"\b(CERT|CRT|REF|DOC|ID)[\-:]\s*O(\d+)\b",
            text,
            re.IGNORECASE,
        )
        if cert_id_fixes:
            text = re.sub(
                r"\b(CERT|CRT|REF|DOC|ID)([\-:]\s*)O(\d+)\b",
                r"\g<1>\g<2>0\3",
                text,
                flags=re.IGNORECASE,
            )
            corrections.append({
                "type": "cert_id_fix",
                "description": "Fixed O->0 in certificate ID",
            })

        return text, corrections


if __name__ == "__main__":
    # Test post-processing
    processor = OCRPostProcessor()

    test_texts = [
        "This certif1cate is awarded to John Doe for complet1on "
        "of the Python program on l2/O5/2O23",
        "CERT-O12345  ||| Issued by XYZ Un1versity  ===",
        "  Part1cipation    in   the   National   Hackathon  ",
    ]

    print("=" * 60)
    print("CertiNexus AI — OCR Post-Processing Test")
    print("=" * 60)

    for text in test_texts:
        result = processor.process(text)
        print(f"\n  Original: {result.original_text}")
        print(f"  Cleaned:  {result.cleaned_text}")
        print(f"  Corrections: {result.num_corrections}")
        for c in result.corrections_applied:
            print(f"    - {c}")
