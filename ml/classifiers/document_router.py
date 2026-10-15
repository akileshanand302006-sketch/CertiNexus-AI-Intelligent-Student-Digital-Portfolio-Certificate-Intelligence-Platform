"""
CertiNexus AI — Hierarchical Indian Document Type Classifier & Router

Routes incoming documents to their respective domain and schema:
- Identity & Government (Aadhaar, PAN, Driving Licence, Vehicle RC, Patta)
- Academic & Educational (Marksheet, Timetable, Fee Receipt)
- Financial (Bank Passbook)
- Career Profile (Resume / CV)
- Credential & Achievement (Accredited Certificate — 11 categories)
- Unknown / Abstention Fallback for human review
"""

import os
import re
from typing import Any, Dict, List, Tuple


class DocumentTypeRouter:
    """
    Hierarchical rule + pattern + feature classifier to determine
    the precise Indian document type before routing to schema extractors.
    """

    # Signature patterns per document family
    FAMILY_SIGNATURES = {
        "aadhaar": [
            r"\b(?:aadhaar|uidai|unique\s*identification\s*authority\s*of\s*india)\b",
            r"\b(?:mera\s*aadhaar|aam\s*aadmi\s*ka\s*adhikar|भारत\s*सरकार)\b",
            r"\b\d{4}\s\d{4}\s\d{4}\b",
            r"\b(?:vid\s*[:\s]?\s*\d{4}\s\d{4}\s\d{4}\s\d{4})\b",
            r"\b(?:help@uidai\.gov\.in|1947)\b",
        ],
        "pan": [
            r"\b(?:income\s*tax\s*department|govt\.?\s*of\s*india|permanent\s*account\s*number|आयकर\s*विभाग)\b",
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
            r"\b(?:father['’]?s\s*name|पिता\s*का\s*नाम)\b",
        ],
        "driving_licence": [
            r"\b(?:driving\s*licen[cs]e|driver['’]?s\s*licen[cs]e|motor\s*vehicles\s*department|union\s*of\s*india)\b",
            r"\b(?:transport\s*department|licensing\s*authority|form\s*7)\b",
            r"\b(?:mcwg|lmv|mcwog|hmv)\b",
            r"\b[A-Z]{2}[- ]?\d{2}[- ]?(?:19|20)\d{2}\s?\d{7}\b",
        ],
        "vehicle_rc": [
            r"\b(?:registration\s*certificate|certificate\s*of\s*registration|form\s*23)\b",
            r"\b(?:chassis\s*no|engine\s*no|maker['’]?s\s*name|cubic\s*capacity)\b",
            r"\b(?:fitness\s*valid|seating\s*capacity|laden\s*weight)\b",
        ],
        "marksheet": [
            r"\b(?:statement\s*of\s*marks|marksheet|grade\s*sheet|academic\s*transcript|grade\s*report)\b",
            r"\b(?:cumulative\s*grade\s*point|cgpa|sgpa|credits\s*earned|course\s*code)\b",
            r"\b(?:semester\s*grade|controller\s*of\s*examinations|board\s*of\s*examinations)\b",
            r"\b(?:total\s*marks|maximum\s*marks|result\s*[:\s]?(?:pass|fail|first\s*class))\b",
        ],
        "timetable": [
            r"\b(?:time\s*table|timetable|class\s*schedule|lecture\s*schedule|academic\s*routine)\b",
            r"\b(?:mon|tue|wed|thu|fri|sat)\b.*(?:\d{1,2}[:.]\d{2})",
            r"\b(?:period\s*[1-8]|slot\s*[a-z]|room\s*no\.?)\b",
        ],
        "fee_receipt": [
            r"\b(?:fee\s*receipt|tuition\s*fee|receipt\s*voucher|payment\s*receipt|challan)\b",
            r"\b(?:fee\s*details|amount\s*paid|payment\s*mode|transaction\s*id|reference\s*no\.?)\b",
            r"\b(?:paid\s*amount|balance\s*fee|bank\s*ref|payment\s*acknowledgement)\b",
        ],
        "passbook": [
            r"\b(?:passbook|pass\s*book|bank\s*statement|statement\s*of\s*account)\b",
            r"\b(?:account\s*number|a/c\s*no|ifsc\s*code|cif\s*no|branch\s*code)\b",
            r"\b(?:savings\s*bank|current\s*account|ledger\s*balance|clearing\s*cheque)\b",
        ],
        "patta": [
            r"\b(?:patta|chitta|land\s*records|patta\s*pass\s*book|revenue\s*department)\b",
            r"\b(?:survey\s*number|subdivision|pattadar|khatauni|खतौनी|பட்டா)\b",
        ],
        "resume": [
            r"\b(?:curriculum\s*vitae|resume|cv)\b",
            r"\b(?:work\s*experience|professional\s*experience|employment\s*history)\b",
            r"\b(?:technical\s*skills|core\s*competencies|key\s*skills)\b",
            r"\b(?:education|academic\s*background|qualifications)\b",
            r"\b(?:projects|personal\s*projects|academic\s*projects)\b",
            r"\b(?:github\.com|linkedin\.com|leetcode\.com)\b",
        ],
        "certificate": [
            r"\b(?:certificate\s*of\s*(?:completion|participation|achievement|excellence|merit|appreciation|recognition))\b",
            r"\b(?:this\s*is\s*to\s*certify\s*that|is\s*hereby\s*awarded\s*to|has\s*successfully\s*completed)\b",
            r"\b(?:presented\s*to|in\s*recognition\s*of|authorized\s*signatory|course\s*completion)\b",
            r"\b(?:hackathon|internship|workshop|webinar|conference|seminar)\b",
        ],
    }

    # Canonical human-friendly labels
    DISPLAY_LABELS = {
        "aadhaar": "Aadhaar Card",
        "pan": "PAN Card",
        "driving_licence": "Driving Licence",
        "vehicle_rc": "Vehicle RC",
        "marksheet": "Academic Marksheet / Transcript",
        "timetable": "Class Timetable",
        "fee_receipt": "Fee Payment Receipt",
        "passbook": "Bank Passbook",
        "patta": "Patta / Land Record",
        "resume": "Resume / Curriculum Vitae",
        "certificate": "Accredited Certificate",
        "unknown": "General Unclassified Document",
    }

    def route(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Classifies document text and filename into a supported Indian document family.
        Returns:
            document_type: str
            confidence: float (0.0 to 1.0)
            is_certificate: bool
            label: str
            scores: Dict[str, int]
            requires_review: bool
        """
        if not text:
            text = ""

        text_lower = text.lower()
        filename_lower = filename.lower()

        scores: Dict[str, int] = {k: 0 for k in self.FAMILY_SIGNATURES}

        # 1. Filename heuristic boosts
        filename_boosts = {
            "aadhaar": ["aadhaar", "aadhar", "uidai"],
            "pan": ["pancard", "pan_card", "pan"],
            "driving_licence": ["driving", "licence", "license", "dl"],
            "vehicle_rc": ["rc_book", "rc_card", "vehicle_rc", "rc"],
            "marksheet": ["marksheet", "transcript", "grade_sheet", "sem_result"],
            "timetable": ["timetable", "time_table", "routine", "schedule"],
            "fee_receipt": ["fee_receipt", "receipt", "challan", "fee_voucher"],
            "passbook": ["passbook", "bank_statement", "bank_book"],
            "patta": ["patta", "chitta", "land_record"],
            "resume": ["resume", "cv", "curriculum_vitae"],
            "certificate": ["certificate", "cert", "diploma", "credential"],
        }

        for doc_type, keywords in filename_boosts.items():
            if any(k in filename_lower for k in keywords):
                scores[doc_type] += 3

        # 2. Text regex match scoring
        for doc_type, patterns in self.FAMILY_SIGNATURES.items():
            for pat in patterns:
                matches = re.findall(pat, text_lower if doc_type != "pan" else text)
                if matches:
                    scores[doc_type] += 2 * len(matches)

        # 3. High-discriminator bonuses
        # Aadhaar: 12-digit spaced number + UIDAI
        if re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text):
            scores["aadhaar"] += 4
        # PAN: standard 10-char PAN
        if re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text):
            scores["pan"] += 5
        # Resume: contact info density (email + phone + github)
        if "@" in text and any(w in text_lower for w in ["github", "linkedin", "projects", "education"]):
            scores["resume"] += 3

        # 4. Determine winning candidate
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_type, best_score = sorted_scores[0]
        runner_up_type, runner_up_score = sorted_scores[1] if len(sorted_scores) > 1 else ("none", 0)

        # Confidence calculation
        if best_score == 0:
            assigned_type = "unknown"
            confidence = 0.35
            requires_review = True
        elif best_score >= 4 and best_score > runner_up_score + 1:
            assigned_type = best_type
            confidence = min(0.98, 0.65 + best_score * 0.05)
            requires_review = False
        elif best_score >= 2:
            assigned_type = best_type
            confidence = min(0.80, 0.50 + best_score * 0.06)
            requires_review = (best_score - runner_up_score) <= 1
        else:
            assigned_type = "unknown"
            confidence = 0.45
            requires_review = True

        is_certificate = (assigned_type == "certificate")

        return {
            "document_type": assigned_type,
            "confidence": round(confidence, 3),
            "is_certificate": is_certificate,
            "label": self.DISPLAY_LABELS.get(assigned_type, "Unknown Document"),
            "scores": scores,
            "requires_review": requires_review,
        }
