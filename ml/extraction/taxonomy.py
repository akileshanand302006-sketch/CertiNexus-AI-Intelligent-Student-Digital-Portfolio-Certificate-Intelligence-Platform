"""
CertiNexus AI — Unified Indian Document Taxonomy
Comprehensive classification hierarchy covering Indian Government/Identity,
Academic, Financial, Professional, and Certificate credentials.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DocumentTaxonomyNode:
    """Node in the document taxonomy hierarchy."""
    code: str
    domain: str  # "identity_government", "academic_educational", "professional_career", "financial", "certificate"
    display_name: str
    description: str
    aliases: List[str] = field(default_factory=list)
    privacy_sensitive: bool = False
    requires_masking: bool = False
    default_route: str = "indian_doc_extractor"  # "indian_doc_extractor" | "certificate_classifier" | "resume_extractor"


class IndianDocumentTaxonomy:
    """Master taxonomy registry."""

    NODES: Dict[str, DocumentTaxonomyNode] = {
        # --- IDENTITY & GOVERNMENT ---
        "aadhaar": DocumentTaxonomyNode(
            code="aadhaar",
            domain="identity_government",
            display_name="Aadhaar Card",
            description="Unique Identification Authority of India (UIDAI) 12-digit biometric identity card.",
            aliases=["aadhar", "uidai", "aadhaar_card", "e_aadhaar"],
            privacy_sensitive=True,
            requires_masking=True,
            default_route="indian_doc_extractor",
        ),
        "pan": DocumentTaxonomyNode(
            code="pan",
            domain="identity_government",
            display_name="PAN Card",
            description="Income Tax Department Permanent Account Number card.",
            aliases=["pan_card", "pancard", "permanent_account_number"],
            privacy_sensitive=True,
            requires_masking=True,
            default_route="indian_doc_extractor",
        ),
        "driving_licence": DocumentTaxonomyNode(
            code="driving_licence",
            domain="identity_government",
            display_name="Driving Licence (DL)",
            description="Regional Transport Office motor vehicle driving authorization.",
            aliases=["dl", "driving_license", "driving_licence"],
            privacy_sensitive=True,
            requires_masking=True,
            default_route="indian_doc_extractor",
        ),
        "vehicle_rc": DocumentTaxonomyNode(
            code="vehicle_rc",
            domain="identity_government",
            display_name="Vehicle Registration (RC)",
            description="Certificate of registration for motor vehicles in India.",
            aliases=["rc", "registration_certificate", "rc_book"],
            privacy_sensitive=True,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),
        "income_certificate": DocumentTaxonomyNode(
            code="income_certificate",
            domain="identity_government",
            display_name="Income Certificate",
            description="State revenue department certificate verifying annual family income.",
            aliases=["income_cert", "revenue_income_certificate"],
            privacy_sensitive=True,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),
        "residence_certificate": DocumentTaxonomyNode(
            code="residence_certificate",
            domain="identity_government",
            display_name="Residence / Domicile Certificate",
            description="Official certificate proving permanent or continuous residency in a state/UT.",
            aliases=["domicile", "residence_cert", "nativity_certificate"],
            privacy_sensitive=False,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),
        "patta": DocumentTaxonomyNode(
            code="patta",
            domain="identity_government",
            display_name="Patta / Land Records",
            description="Official land revenue record and ownership title document issued by the Tahsildar.",
            aliases=["land_record", "patta_chitta", "7_12_extract", "khatauni"],
            privacy_sensitive=False,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),

        # --- ACADEMIC & EDUCATIONAL ---
        "marksheet": DocumentTaxonomyNode(
            code="marksheet",
            domain="academic_educational",
            display_name="Semester Marksheet / Grade Sheet",
            description="University or board grade card with subject-wise evaluation, credits, and SGPA/CGPA.",
            aliases=["grade_sheet", "semester_result", "mark_sheet", "score_card"],
            privacy_sensitive=False,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),
        "timetable": DocumentTaxonomyNode(
            code="timetable",
            domain="academic_educational",
            display_name="Academic Schedule / Timetable",
            description="Institutional class scheduling, course slots, room assignments, and academic timetable.",
            aliases=["time_table", "class_schedule", "course_schedule"],
            privacy_sensitive=False,
            requires_masking=False,
            default_route="indian_doc_extractor",
        ),
        "fee_receipt": DocumentTaxonomyNode(
            code="fee_receipt",
            domain="academic_educational",
            display_name="Educational Fee Receipt",
            description="Tuition, examination, or university fee acknowledgement and payment voucher.",
            aliases=["tuition_receipt", "payment_receipt", "challan"],
            privacy_sensitive=True,
            requires_masking=True,
            default_route="indian_doc_extractor",
        ),

        # --- FINANCIAL ---
        "passbook": DocumentTaxonomyNode(
            code="passbook",
            domain="financial",
            display_name="Bank Passbook",
            description="Official bank account passbook detailing account holder, IFSC, and transactions.",
            aliases=["bank_passbook", "bank_statement"],
            privacy_sensitive=True,
            requires_masking=True,
            default_route="indian_doc_extractor",
        ),

        # --- PROFESSIONAL / CAREER ---
        "resume": DocumentTaxonomyNode(
            code="resume",
            domain="professional_career",
            display_name="Candidate Resume / CV",
            description="Curriculum vitae profiling student skills, education, projects, and work experience.",
            aliases=["cv", "curriculum_vitae", "candidate_profile"],
            privacy_sensitive=True,
            requires_masking=False,
            default_route="resume_extractor",
        ),

        # --- ACCREDITED CERTIFICATE (11 CATEGORIES) ---
        "certificate": DocumentTaxonomyNode(
            code="certificate",
            domain="certificate",
            display_name="Accredited Certificate",
            description="Student achievement or participation certificate in 1 of 11 accredited verticals.",
            aliases=["academic_achievement", "certification", "conference", "cultural_activity",
                     "hackathon", "internship", "seminar", "sports", "technical_competition",
                     "volunteer_activity", "workshop"],
            privacy_sensitive=False,
            requires_masking=False,
            default_route="certificate_classifier",
        ),
    }

    @classmethod
    def get_node(cls, code: str) -> Optional[DocumentTaxonomyNode]:
        code_clean = code.lower().strip()
        if code_clean in cls.NODES:
            return cls.NODES[code_clean]
        for node in cls.NODES.values():
            if code_clean in [a.lower() for a in node.aliases]:
                return node
        return None

    @classmethod
    def list_all_nodes(cls) -> List[DocumentTaxonomyNode]:
        return list(cls.NODES.values())
