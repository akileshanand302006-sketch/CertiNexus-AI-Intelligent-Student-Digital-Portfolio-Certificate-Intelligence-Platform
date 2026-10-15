"""
CertiNexus AI — Category-Specific Field Extraction

Defines field templates for each certificate category and extracts
category-specific structured fields from text.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .rule_ner import RuleBasedNER, NERResult


@dataclass
class CertificateFields:
    """Structured fields extracted from a certificate."""
    category: str
    holder_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    certificate_id: Optional[str] = None

    # Category-specific fields
    event_name: Optional[str] = None
    course_name: Optional[str] = None
    duration: Optional[str] = None
    score: Optional[str] = None
    grade: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    rank: Optional[str] = None
    team_name: Optional[str] = None
    project_name: Optional[str] = None
    internship_role: Optional[str] = None
    company: Optional[str] = None

    completeness_score: float = 0.0

    def to_dict(self) -> Dict:
        d = {
            "category": self.category,
            "holder_name": self.holder_name,
            "issuing_organization": self.issuing_organization,
            "issue_date": self.issue_date,
            "certificate_id": self.certificate_id,
            "completeness_score": round(self.completeness_score, 2),
        }
        # Add non-None category-specific fields
        for f in ["event_name", "course_name", "duration", "score",
                   "grade", "skills", "rank", "team_name",
                   "project_name", "internship_role", "company"]:
            val = getattr(self, f)
            if val and val != []:
                d[f] = val
        return d


# Field templates per category
CATEGORY_TEMPLATES = {
    "Hackathon": {
        "required": ["holder_name", "event_name", "issuing_organization"],
        "optional": ["team_name", "project_name", "rank", "issue_date", "skills"],
    },
    "Internship": {
        "required": ["holder_name", "company", "duration"],
        "optional": ["internship_role", "skills", "issue_date"],
    },
    "Certification": {
        "required": ["holder_name", "course_name", "issuing_organization"],
        "optional": ["certificate_id", "score", "issue_date", "skills"],
    },
    "Workshop": {
        "required": ["holder_name", "event_name", "issuing_organization"],
        "optional": ["duration", "issue_date", "skills"],
    },
    "Conference": {
        "required": ["holder_name", "event_name"],
        "optional": ["issuing_organization", "issue_date"],
    },
    "Seminar": {
        "required": ["holder_name", "event_name"],
        "optional": ["issuing_organization", "issue_date"],
    },
    "Academic Achievement": {
        "required": ["holder_name", "issuing_organization"],
        "optional": ["grade", "score", "rank", "issue_date"],
    },
    "Technical Competition": {
        "required": ["holder_name", "event_name"],
        "optional": ["rank", "team_name", "project_name", "skills", "issue_date"],
    },
    "Sports": {
        "required": ["holder_name", "event_name"],
        "optional": ["rank", "issue_date", "issuing_organization"],
    },
    "Cultural Activity": {
        "required": ["holder_name", "event_name"],
        "optional": ["rank", "issue_date", "issuing_organization"],
    },
    "Volunteer Activity": {
        "required": ["holder_name", "event_name", "issuing_organization"],
        "optional": ["duration", "issue_date"],
    },
}


class CategoryFieldExtractor:
    """
    Extract category-specific structured fields from certificate text.

    Uses the NER output and category-specific templates to populate
    a CertificateFields object.
    """

    def __init__(self):
        self.ner = RuleBasedNER()

    def extract(
        self, text: str, category: str,
        ner_result: Optional[NERResult] = None,
    ) -> CertificateFields:
        """
        Extract structured fields for a given category.

        Parameters
        ----------
        text : str
            Certificate text.
        category : str
            Certificate category.
        ner_result : NERResult, optional
            Pre-computed NER result.

        Returns
        -------
        fields : CertificateFields
        """
        if ner_result is None:
            ner_result = self.ner.extract(text)

        fields = CertificateFields(category=category)

        # Map NER entities to fields
        persons = ner_result.get_by_type("PERSON_NAME")
        orgs = ner_result.get_by_type("ORGANIZATION")
        dates = ner_result.get_by_type("DATE")
        cert_ids = ner_result.get_by_type("CERTIFICATE_ID")
        durations = ner_result.get_by_type("DURATION")
        scores = ner_result.get_by_type("SCORE")
        grades = ner_result.get_by_type("GRADE")
        skills = ner_result.get_by_type("SKILL")

        # Common fields
        if persons:
            fields.holder_name = persons[0].text
        if orgs:
            fields.issuing_organization = orgs[0].text
        if dates:
            fields.issue_date = dates[0].text
        if cert_ids:
            fields.certificate_id = cert_ids[0].text
        if durations:
            fields.duration = durations[0].text
        if scores:
            fields.score = scores[0].text
        if grades:
            fields.grade = grades[0].text
        if skills:
            fields.skills = [s.text for s in skills]

        # Category-specific extraction
        if category == "Internship":
            fields.company = fields.issuing_organization
            self._extract_internship_role(text, fields)
        elif category in ("Hackathon", "Technical Competition"):
            self._extract_event_details(text, fields)
            self._extract_rank(text, fields)
        elif category in ("Workshop", "Conference", "Seminar"):
            self._extract_event_details(text, fields)
        elif category == "Certification":
            self._extract_course_name(text, fields)
        elif category == "Academic Achievement":
            self._extract_rank(text, fields)

        # Compute completeness
        fields.completeness_score = self._compute_completeness(
            fields, category
        )

        return fields

    def _extract_event_details(
        self, text: str, fields: CertificateFields
    ):
        """Extract event name from text context."""
        patterns = [
            r"(?:participated|participation)\s+in\s+(?:the\s+)?(.+?)(?:\.|,|held|organized|conducted)",
            r"(?:attended|attending)\s+(?:the\s+)?(.+?)(?:\.|,|held|organized|conducted)",
            r"(?:hackathon|competition|workshop|conference|seminar)\s*[:\-]?\s*(.+?)(?:\.|,|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                event = match.group(1).strip()
                if len(event) > 5 and len(event) < 100:
                    fields.event_name = event
                    break

    def _extract_course_name(
        self, text: str, fields: CertificateFields
    ):
        """Extract course name from certification text."""
        patterns = [
            r"(?:completed|completion\s+of)\s+(?:the\s+)?(?:course\s+)?(.+?)(?:\.|,|by|from|on|$)",
            r"(?:course|program|certification)\s*[:\-]?\s*(.+?)(?:\.|,|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                course = match.group(1).strip()
                if len(course) > 3 and len(course) < 100:
                    fields.course_name = course
                    break

    def _extract_internship_role(
        self, text: str, fields: CertificateFields
    ):
        """Extract internship role/position."""
        patterns = [
            r"(?:as\s+(?:a\s+)?|role\s*[:\-]?\s*)(.+?\s+intern(?:ship)?)",
            r"(\w+\s+(?:development|engineering|design|research)\s+intern)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields.internship_role = match.group(1).strip()
                break

    def _extract_rank(
        self, text: str, fields: CertificateFields
    ):
        """Extract rank/position from text."""
        patterns = [
            r"(?:secured|achieved|won)\s+(first|second|third|1st|2nd|3rd)\s+(?:place|position|rank|prize)",
            r"(winner|runner[\-\s]?up|finalist|champion)",
            r"rank\s*[:\-]?\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields.rank = match.group(1).strip()
                break

    def _compute_completeness(
        self, fields: CertificateFields, category: str
    ) -> float:
        """
        Compute field completeness score (0-100).
        Based on how many required and optional fields are filled.
        """
        template = CATEGORY_TEMPLATES.get(category, {})
        required = template.get("required", [])
        optional = template.get("optional", [])

        if not required and not optional:
            return 50.0  # Unknown category

        required_filled = sum(
            1 for f in required
            if getattr(fields, f, None) not in (None, "", [])
        )
        optional_filled = sum(
            1 for f in optional
            if getattr(fields, f, None) not in (None, "", [])
        )

        # Required fields worth 70%, optional worth 30%
        req_score = (
            (required_filled / len(required) * 70)
            if required else 35
        )
        opt_score = (
            (optional_filled / len(optional) * 30)
            if optional else 15
        )

        return min(req_score + opt_score, 100.0)
