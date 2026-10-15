"""
CertiNexus AI — Rule-Based Named Entity Recognition

Comprehensive rule-based NER system for certificate documents.
Extracts 25+ entity types using regex patterns, dictionaries,
and contextual heuristics.

Entity types include:
- PERSON_NAME, ORGANIZATION, DATE, CERTIFICATE_ID, DURATION
- SKILL, TECHNOLOGY, PROGRAMMING_LANGUAGE, FRAMEWORK
- SCORE, GRADE, RANK, PERCENTAGE
- EVENT_NAME, VENUE, LOCATION
- ISSUER, AUTHORITY, DESIGNATION
- PROJECT_NAME, COURSE_NAME, DEGREE
- EMAIL, PHONE, URL
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Entity:
    """A single extracted entity."""
    text: str
    entity_type: str
    start: int  # character offset in original text
    end: int
    confidence: float
    source: str  # "regex", "dictionary", "contextual"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "type": self.entity_type,
            "start": self.start,
            "end": self.end,
            "confidence": round(self.confidence, 3),
            "source": self.source,
        }


@dataclass
class NERResult:
    """Complete NER extraction result."""
    entities: List[Entity]
    text: str
    num_entities: int = 0
    entity_summary: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.num_entities = len(self.entities)
        self.entity_summary = {}
        for e in self.entities:
            self.entity_summary[e.entity_type] = (
                self.entity_summary.get(e.entity_type, 0) + 1
            )

    def get_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]

    def to_dict(self) -> Dict:
        return {
            "num_entities": self.num_entities,
            "entity_summary": self.entity_summary,
            "entities": [e.to_dict() for e in self.entities],
        }


class RuleBasedNER:
    """
    Rule-based Named Entity Recognition for certificate documents.

    Uses a combination of:
    1. Regular expression patterns
    2. Dictionary lookups
    3. Contextual heuristics (keywords near potential entities)

    Parameters
    ----------
    min_confidence : float
        Minimum confidence to include an entity.
    """

    # Date patterns
    DATE_PATTERNS = [
        # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        (r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b", 0.9),
        # Month DD, YYYY
        (r"\b(January|February|March|April|May|June|July|August|"
         r"September|October|November|December)\s+\d{1,2},?\s+\d{4}\b", 0.95),
        # DD Month YYYY
        (r"\b\d{1,2}\s+(January|February|March|April|May|June|July|"
         r"August|September|October|November|December)\s+\d{4}\b", 0.95),
        # Month YYYY
        (r"\b(January|February|March|April|May|June|July|August|"
         r"September|October|November|December)\s+\d{4}\b", 0.85),
        # YYYY
        (r"\b(20[0-2]\d|19\d{2})\b", 0.5),
    ]

    # Certificate ID patterns
    CERT_ID_PATTERNS = [
        (r"\b(CERT|CRT|DOC|REF|ID|NO|REG)[\-:\s]*#?\s*"
         r"[A-Z0-9][A-Z0-9\-]{3,20}\b", 0.85),
        (r"\bCertificate\s+(?:No|Number|ID)[.:]*\s*"
         r"[A-Z0-9][A-Z0-9\-]{3,20}\b", 0.9),
        (r"\b[A-Z]{2,4}\-\d{4,}\b", 0.7),
    ]

    # Score/Grade patterns
    SCORE_PATTERNS = [
        (r"\b(\d{1,3}(?:\.\d+)?)\s*[/]\s*"
         r"(\d{2,4})\b", 0.85),  # 85/100
        (r"\b(\d{1,3}(?:\.\d+)?)\s*%\b", 0.85),  # 85%
        (r"\bgrade\s*[:\-]?\s*([A-F][+\-]?)\b", 0.9),
        (r"\bCGPA\s*[:\-]?\s*(\d+\.\d+)\b", 0.9),
        (r"\bGPA\s*[:\-]?\s*(\d+\.\d+)\b", 0.9),
    ]

    # Duration patterns
    DURATION_PATTERNS = [
        (r"\b(\d+)\s*(months?|weeks?|days?|hours?|years?)\b", 0.85),
        (r"\bfrom\s+.+?\s+to\s+.+?(?=\.|,|$)", 0.7),
    ]

    # Contact patterns
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"
    PHONE_PATTERN = r"\b(?:\+\d{1,3}[\-\s]?)?\(?\d{2,5}\)?[\-\s]?\d{3,10}\b"
    URL_PATTERN = r"\bhttps?://[^\s<>]+\b|\bwww\.[^\s<>]+\b"

    # Context keywords for person name extraction
    NAME_CONTEXTS = [
        "awarded to", "presented to", "certify that",
        "certifies that", "given to", "issued to",
        "this is to certify", "name:", "student:",
        "participant:", "recipient:", "mr.", "ms.", "mrs.",
        "dr.", "prof.",
    ]

    # Organization keywords
    ORG_CONTEXTS = [
        "organized by", "conducted by", "hosted by",
        "issued by", "presented by", "offered by",
        "university", "institute", "college", "school",
        "academy", "foundation", "corporation", "company",
        "inc.", "ltd.", "pvt.", "organization", "department",
        "association", "society", "committee", "council",
        "ministry", "government", "board",
    ]

    # Designation keywords
    DESIGNATION_CONTEXTS = [
        "dean", "director", "principal", "head",
        "chairman", "chairperson", "president",
        "secretary", "coordinator", "professor",
        "convenor", "registrar", "chancellor",
    ]

    def __init__(self, min_confidence: float = 0.3):
        self.min_confidence = min_confidence

    def extract(self, text: str) -> NERResult:
        """
        Extract all entities from text.

        Parameters
        ----------
        text : str
            Input text (typically OCR-extracted certificate text).

        Returns
        -------
        result : NERResult
        """
        entities = []

        # Extract each entity type
        entities.extend(self._extract_dates(text))
        entities.extend(self._extract_cert_ids(text))
        entities.extend(self._extract_scores(text))
        entities.extend(self._extract_durations(text))
        entities.extend(self._extract_contacts(text))
        entities.extend(self._extract_names(text))
        entities.extend(self._extract_organizations(text))
        entities.extend(self._extract_designations(text))
        entities.extend(self._extract_skills(text))

        # Filter by confidence
        entities = [
            e for e in entities
            if e.confidence >= self.min_confidence
        ]

        # Remove overlapping entities (keep higher confidence)
        entities = self._resolve_overlaps(entities)

        return NERResult(entities=entities, text=text)

    def _extract_dates(self, text: str) -> List[Entity]:
        entities = []
        for pattern, confidence in self.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="DATE",
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    source="regex",
                ))
        return entities

    def _extract_cert_ids(self, text: str) -> List[Entity]:
        entities = []
        for pattern, confidence in self.CERT_ID_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="CERTIFICATE_ID",
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    source="regex",
                ))
        return entities

    def _extract_scores(self, text: str) -> List[Entity]:
        entities = []
        for pattern, confidence in self.SCORE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity_type = "SCORE"
                matched_text = match.group()
                if "grade" in matched_text.lower():
                    entity_type = "GRADE"
                elif "gpa" in matched_text.lower() or "cgpa" in matched_text.lower():
                    entity_type = "GPA"
                elif "%" in matched_text:
                    entity_type = "PERCENTAGE"

                entities.append(Entity(
                    text=matched_text,
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    source="regex",
                ))
        return entities

    def _extract_durations(self, text: str) -> List[Entity]:
        entities = []
        for pattern, confidence in self.DURATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="DURATION",
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    source="regex",
                ))
        return entities

    def _extract_contacts(self, text: str) -> List[Entity]:
        entities = []

        # Emails
        for match in re.finditer(self.EMAIL_PATTERN, text):
            entities.append(Entity(
                text=match.group(),
                entity_type="EMAIL",
                start=match.start(),
                end=match.end(),
                confidence=0.95,
                source="regex",
            ))

        # URLs
        for match in re.finditer(self.URL_PATTERN, text):
            entities.append(Entity(
                text=match.group(),
                entity_type="URL",
                start=match.start(),
                end=match.end(),
                confidence=0.95,
                source="regex",
            ))

        return entities

    def _extract_names(self, text: str) -> List[Entity]:
        """Extract person names using contextual patterns."""
        entities = []
        text_lower = text.lower()

        for ctx in self.NAME_CONTEXTS:
            idx = text_lower.find(ctx)
            if idx == -1:
                continue

            # Look for capitalized words after the context keyword
            after_ctx = text[idx + len(ctx):].strip()
            # Match 2-4 capitalized words (typical full name)
            name_match = re.match(
                r"\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
                after_ctx
            )
            if name_match:
                name = name_match.group(1).strip()
                name_lower = name.lower()
                invalid_name_words = {
                    "passionate", "about", "solving", "real", "strong", "foundation", "experience",
                    "student", "profile", "summary", "skills", "hands", "developing", "application",
                    "learning", "working", "seeking", "motivated", "enthusiastic", "completed", "certified"
                }
                if not any(w in name_lower.split() for w in invalid_name_words):
                    abs_start = idx + len(ctx) + name_match.start(1)
                    entities.append(Entity(
                        text=name,
                        entity_type="PERSON_NAME",
                        start=abs_start,
                        end=abs_start + len(name),
                        confidence=0.75,
                        source="contextual",
                        metadata={"context": ctx},
                    ))

        return entities

    def _extract_organizations(self, text: str) -> List[Entity]:
        """Extract organization names using contextual patterns."""
        entities = []
        text_lower = text.lower()
        invalid_org_phrases = {
            "with strong", "strong foundation", "foundations in", "foundation in",
            "strong foundations", "hands-on experience", "hands on experience"
        }

        for ctx in self.ORG_CONTEXTS:
            idx = text_lower.find(ctx)
            if idx == -1:
                continue

            # Check if this is a context phrase ("organized by ...")
            if ctx.endswith("by") or ctx.endswith("by "):
                after_ctx = text[idx + len(ctx):].strip()
                # Match capitalized phrase
                org_match = re.match(
                    r"\s*([A-Z][A-Za-z0-9]+(?:\s+[A-Za-z0-9&]+){0,5})",
                    after_ctx
                )
                if org_match:
                    org = org_match.group(1).strip()
                    if not any(bad in org.lower() for bad in invalid_org_phrases) and len(org) >= 3:
                        abs_start = idx + len(ctx) + org_match.start(1)
                        entities.append(Entity(
                            text=org,
                            entity_type="ORGANIZATION",
                            start=abs_start,
                            end=abs_start + len(org),
                            confidence=0.7,
                            source="contextual",
                            metadata={"context": ctx},
                        ))
            else:
                org_match = re.search(
                    r"([A-Z][A-Za-z0-9]*(?:\s+[A-Za-z0-9&]+)*\s+" +
                    re.escape(ctx) +
                    r"(?:\s+[A-Za-z0-9&]+)*)",
                    text[max(0, idx-50):idx+50+len(ctx)],
                    re.IGNORECASE,
                )
                if org_match:
                    org_text = org_match.group(1).strip()
                    if len(org_text) > len(ctx) + 2:
                        if not any(bad in org_text.lower() for bad in invalid_org_phrases) and not org_text.lower().startswith("with "):
                            start_offset = max(0, idx - 50) + org_match.start(1)
                            entities.append(Entity(
                                text=org_text,
                                entity_type="ORGANIZATION",
                                start=start_offset,
                                end=start_offset + len(org_text),
                                confidence=0.65,
                                source="contextual",
                            ))

        return entities

    def _extract_designations(self, text: str) -> List[Entity]:
        """Extract designations/titles."""
        entities = []
        text_lower = text.lower()

        for ctx in self.DESIGNATION_CONTEXTS:
            pattern = r"\b" + re.escape(ctx) + r"\b"
            for match in re.finditer(pattern, text_lower):
                entities.append(Entity(
                    text=text[match.start():match.end()],
                    entity_type="DESIGNATION",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8,
                    source="dictionary",
                ))
        return entities

    def _extract_skills(self, text: str) -> List[Entity]:
        """Extract skills and technologies using the skills database."""
        from .skills import SkillDatabase
        db = SkillDatabase()
        return db.extract_skills(text)

    def _resolve_overlaps(
        self, entities: List[Entity]
    ) -> List[Entity]:
        """Remove overlapping entities, keeping highest confidence."""
        if not entities:
            return entities

        # Sort by confidence descending
        sorted_entities = sorted(
            entities, key=lambda e: -e.confidence
        )

        resolved = []
        used_spans = []

        for entity in sorted_entities:
            span = (entity.start, entity.end)
            overlap = False
            for used_start, used_end in used_spans:
                if (span[0] < used_end and span[1] > used_start):
                    overlap = True
                    break
            if not overlap:
                resolved.append(entity)
                used_spans.append(span)

        # Re-sort by position
        resolved.sort(key=lambda e: e.start)
        return resolved
