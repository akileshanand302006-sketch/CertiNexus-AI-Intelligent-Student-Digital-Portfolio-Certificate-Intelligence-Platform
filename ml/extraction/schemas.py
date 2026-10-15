"""
CertiNexus AI — Category-Specific Extraction Schemas & PII Masking
Defines typed schemas and privacy-preserving masking for Indian Identity, Academic, and Financial records.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def mask_aadhaar(number_str: str) -> str:
    """Mask Aadhaar 12-digit number: XXXX-XXXX-1234."""
    if not number_str:
        return ""
    digits = re.sub(r"\D", "", number_str)
    if len(digits) == 12:
        return f"XXXX-XXXX-{digits[-4:]}"
    elif len(digits) >= 4:
        return f"XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX"


def mask_pan(pan_str: str) -> str:
    """Mask PAN 10-char alphanumeric string: ABCDE****F."""
    if not pan_str:
        return ""
    clean = re.sub(r"[^A-Za-z0-9]", "", pan_str.upper())
    if len(clean) == 10:
        return f"{clean[:5]}****{clean[-1]}"
    return clean


def mask_bank_account(acc_str: str) -> str:
    """Mask bank account number: ******1234."""
    if not acc_str:
        return ""
    digits = re.sub(r"\D", "", acc_str)
    if len(digits) > 4:
        return f"******{digits[-4:]}"
    return acc_str


def mask_phone_number(phone_str: str) -> str:
    """Mask phone number: +91-XXXXX-12345."""
    if not phone_str:
        return ""
    digits = re.sub(r"\D", "", phone_str)
    if len(digits) >= 10:
        return f"+91-XXXXX-{digits[-5:]}"
    return phone_str


@dataclass
class FieldDefinition:
    """Metadata for a schema field."""
    name: str
    display_label: str
    field_type: str = "string"  # "string", "date", "number", "list", "masked"
    required: bool = False
    is_pii: bool = False
    mask_function: Optional[Any] = None


class ExtractionSchemaRegistry:
    """Registry of extraction schemas for all supported document families."""

    SCHEMAS: Dict[str, List[FieldDefinition]] = {
        "aadhaar": [
            FieldDefinition("recipient_name", "Cardholder Full Name", required=True),
            FieldDefinition("aadhaar_number", "Aadhaar Number (Masked)", required=True, is_pii=True, mask_function=mask_aadhaar),
            FieldDefinition("dob", "Date of Birth / Year", required=True),
            FieldDefinition("gender", "Gender", required=False),
            FieldDefinition("guardian_name", "Father / Husband / Care Of", required=False),
            FieldDefinition("address", "Residential Address", required=False),
            FieldDefinition("issuing_authority", "Issuing Authority", required=True),
        ],
        "pan": [
            FieldDefinition("recipient_name", "Cardholder Full Name", required=True),
            FieldDefinition("pan_number", "Permanent Account Number (PAN)", required=True, is_pii=True, mask_function=mask_pan),
            FieldDefinition("guardian_name", "Father's Name", required=False),
            FieldDefinition("dob", "Date of Birth / Incorp Date", required=False),
            FieldDefinition("issuing_authority", "Income Tax Department, Govt of India", required=True),
        ],
        "driving_licence": [
            FieldDefinition("recipient_name", "Licence Holder Name", required=True),
            FieldDefinition("dl_number", "Driving Licence Number", required=True, is_pii=True),
            FieldDefinition("dob", "Date of Birth", required=False),
            FieldDefinition("issue_date", "Date of Issue", required=False),
            FieldDefinition("validity_date", "Validity / Expiry Date", required=False),
            FieldDefinition("vehicle_classes", "Authorized Vehicle Classes (MCWG, LMV)", required=False, field_type="list"),
            FieldDefinition("issuing_rto", "Issuing Licensing Authority / RTO", required=False),
        ],
        "vehicle_rc": [
            FieldDefinition("registration_number", "Vehicle Registration Number", required=True),
            FieldDefinition("owner_name", "Registered Owner Name", required=True),
            FieldDefinition("maker_model", "Maker & Model Description", required=False),
            FieldDefinition("vehicle_class", "Vehicle Class", required=False),
            FieldDefinition("fuel_type", "Fuel / Energy Source", required=False),
            FieldDefinition("registration_date", "Date of Registration", required=False),
            FieldDefinition("issuing_authority", "Registering Authority", required=False),
        ],
        "marksheet": [
            FieldDefinition("student_name", "Student Candidate Name", required=True),
            FieldDefinition("roll_number", "Roll / Registration Number", required=True),
            FieldDefinition("institution", "University / College / Board", required=True),
            FieldDefinition("degree_course", "Degree / Branch / Course", required=True),
            FieldDefinition("semester", "Semester / Academic Term", required=True),
            FieldDefinition("subjects", "Evaluated Subjects & Marks", required=False, field_type="list"),
            FieldDefinition("sgpa_cgpa", "SGPA / CGPA / Total Marks", required=False),
            FieldDefinition("result_status", "Result Outcome (PASS / PROMOTED)", required=False),
            FieldDefinition("issue_date", "Result Publication Date", required=False),
        ],
        "timetable": [
            FieldDefinition("institution", "Academic Institution", required=True),
            FieldDefinition("department", "Department / School", required=True),
            FieldDefinition("semester", "Semester / Year / Section", required=True),
            FieldDefinition("schedule_slots", "Time Slots & Class Distribution", required=False, field_type="list"),
            FieldDefinition("academic_year", "Academic Session / Year", required=False),
        ],
        "fee_receipt": [
            FieldDefinition("student_name", "Student / Payer Name", required=True),
            FieldDefinition("receipt_number", "Receipt Voucher / Challan No.", required=True),
            FieldDefinition("institution", "Institution / University", required=True),
            FieldDefinition("payment_date", "Payment Date", required=True),
            FieldDefinition("amount_paid", "Total Amount Paid (INR)", required=True),
            FieldDefinition("payment_mode", "Payment Mode (UPI/NetBanking/DD)", required=False),
        ],
        "passbook": [
            FieldDefinition("account_holder", "Account Holder Name", required=True),
            FieldDefinition("bank_name", "Bank & Branch Name", required=True),
            FieldDefinition("account_number", "Account Number (Masked)", required=True, is_pii=True, mask_function=mask_bank_account),
            FieldDefinition("ifsc_code", "IFSC Code", required=False),
        ],
        "patta": [
            FieldDefinition("owner_name", "Pattadar / Landholder Name", required=True),
            FieldDefinition("patta_number", "Patta Record Number", required=True),
            FieldDefinition("survey_number", "Survey / Subdivision Number", required=False),
            FieldDefinition("village_taluk", "Village, Taluk & District", required=False),
            FieldDefinition("extent_area", "Land Extent (Acres / Hectares)", required=False),
        ],
        "resume": [
            FieldDefinition("candidate_name", "Candidate Full Name", required=True),
            FieldDefinition("email", "Email Address", required=False),
            FieldDefinition("phone", "Phone Number (Masked)", required=False, is_pii=True, mask_function=mask_phone_number),
            FieldDefinition("skills", "Extracted Technical Skills", required=False, field_type="list"),
            FieldDefinition("education", "Education Profile", required=False, field_type="list"),
            FieldDefinition("experience", "Work & Internship Experience", required=False, field_type="list"),
        ],
        "certificate": [
            FieldDefinition("recipient_name", "Certificate Recipient", required=True),
            FieldDefinition("issuer", "Issuing Organization", required=True),
            FieldDefinition("title", "Certificate Title / Event", required=True),
            FieldDefinition("category", "Accredited Category", required=True),
            FieldDefinition("issue_date", "Issue Date", required=False),
            FieldDefinition("credential_id", "Credential / Verification ID", required=False),
            FieldDefinition("skills", "Extracted Skills", required=False, field_type="list"),
        ],
    }

    @classmethod
    def get_fields_for_type(cls, doc_type: str) -> List[FieldDefinition]:
        return cls.SCHEMAS.get(doc_type.lower().strip(), cls.SCHEMAS["certificate"])
