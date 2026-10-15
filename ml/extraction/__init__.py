"""
CertiNexus AI — Entity Extraction Module

Rule-based NER for certificate documents with 25+ entity types.
"""
from .rule_ner import RuleBasedNER, Entity, NERResult
from .skills import SkillDatabase
from .certificate_fields import CategoryFieldExtractor
from .duplicate_detector import DuplicateDetector
from .metadata import ExtractionMetadata
