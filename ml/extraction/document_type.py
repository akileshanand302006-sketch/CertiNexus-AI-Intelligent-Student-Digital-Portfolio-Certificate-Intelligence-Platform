"""
CertiNexus AI — Document-Type Detection System

Separates Document-Type (Certificate vs Resume/CV vs Transcript vs General Document)
from Certificate Category classification (11 accredited categories).
"""

import re
from typing import Dict, Any, Tuple


class DocumentTypeDetector:
    """
    Detects whether an uploaded document is a Certificate, Resume/CV,
    Academic Transcript, or General Document.
    """

    # Formulaic certificate markers
    CERTIFICATE_MARKERS = [
        r"certificate\s+of\s+(?:completion|participation|achievement|excellence|merit|appreciation|recognition)",
        r"this\s+is\s+to\s+certify\s+that",
        r"is\s+hereby\s+awarded\s+to",
        r"has\s+successfully\s+completed",
        r"presented\s+to",
        r"in\s+recognition\s+of",
        r"certificate\s+of\s+training",
        r"internship\s+completion\s+certificate",
        r"participation\s+certificate",
        r"course\s+completion",
        r"credential\s+id",
        r"verification\s+code",
        r"authorized\s+signatory",
    ]

    # Resume/CV section markers
    RESUME_MARKERS = [
        r"\b(?:curriculum\s+vitae|resume|cv)\b",
        r"\b(?:work\s+experience|professional\s+experience|employment\s+history)\b",
        r"\b(?:technical\s+skills|core\s+competencies|key\s+skills)\b",
        r"\b(?:education|academic\s+background|qualifications)\b",
        r"\b(?:projects|personal\s+projects|academic\s+projects)\b",
        r"\b(?:profile|summary|career\s+objective|professional\s+summary)\b",
        r"\b(?:leetcode|github\.com|linkedin\.com|hackerrank)\b",
        r"\b(?:contact|phone|email)\b.*@.*(?:\+91|\d{10})",
    ]

    # Transcript / Marksheet markers
    TRANSCRIPT_MARKERS = [
        r"\b(?:statement\s+of\s+marks|grade\s+sheet|marksheet|academic\s+transcript|semester\s+grade\s+report)\b",
        r"\b(?:cumulative\s+grade\s+point|cgpa|sgpa|credits\s+earned|course\s+code)\b",
    ]

    def detect(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Analyze document text and filename to determine document type.
        """
        if not text:
            text = ""

        text_lower = text.lower()
        filename_lower = filename.lower()

        cert_score = 0
        resume_score = 0
        transcript_score = 0

        # Filename hints
        if any(w in filename_lower for w in ["resume", "cv", "curriculum_vitae"]):
            resume_score += 3
        if any(w in filename_lower for w in ["certificate", "cert", "diploma"]):
            cert_score += 3
        if any(w in filename_lower for w in ["transcript", "marksheet", "grade"]):
            transcript_score += 3

        # Match Certificate patterns
        for pattern in self.CERTIFICATE_MARKERS:
            if re.search(pattern, text_lower):
                cert_score += 2

        # Match Resume patterns
        for pattern in self.RESUME_MARKERS:
            if re.search(pattern, text_lower):
                resume_score += 2

        # Match Transcript patterns
        for pattern in self.TRANSCRIPT_MARKERS:
            if re.search(pattern, text_lower):
                transcript_score += 2

        # Additional resume heuristics: contact info density
        has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
        has_phone = bool(re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
        has_github_or_linkedin = "github" in text_lower or "linkedin" in text_lower or "leetcode" in text_lower

        if has_email and (has_phone or has_github_or_linkedin) and resume_score > 0:
            resume_score += 2

        # Decision logic
        if resume_score >= 4 and resume_score > cert_score:
            doc_type = "resume"
            is_certificate = False
            confidence = min(0.98, 0.6 + resume_score * 0.08)
            label = "Resume / CV"
            description = "Detected Resume / Curriculum Vitae profile document."
        elif transcript_score >= 4 and transcript_score > cert_score:
            doc_type = "transcript"
            is_certificate = False
            confidence = min(0.95, 0.6 + transcript_score * 0.08)
            label = "Academic Transcript"
            description = "Detected Academic Transcript or Marksheet record."
        elif cert_score >= 2 or (cert_score > 0 and resume_score <= 1):
            doc_type = "certificate"
            is_certificate = True
            confidence = min(0.98, 0.5 + cert_score * 0.1)
            label = "Certificate Credential"
            description = "Confirmed Certificate / Credential document."
        else:
            # Low confidence or ambiguous
            doc_type = "general_document"
            is_certificate = False
            confidence = 0.5
            label = "General Document"
            description = "Unclassified document. Needs review."

        return {
            "document_type": doc_type,
            "is_certificate": is_certificate,
            "confidence": round(confidence, 3),
            "label": label,
            "description": description,
            "cert_score": cert_score,
            "resume_score": resume_score,
            "transcript_score": transcript_score,
        }
