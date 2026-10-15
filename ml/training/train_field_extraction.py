"""
CertiNexus AI — Structured Field Extraction Evaluation

Evaluates schema field extraction precision, coverage, and PII masking across:
- Aadhaar (UID masking, DOB, Gender, Address, Issuing Authority)
- PAN (PAN masking, Name, Guardian, DOB, Authority)
- Marksheet (Student Name, Roll Number, Degree, Semester, SGPA/CGPA, Result)
- Timetable & Fee Receipt
"""

import json
import os
import sys
from ml.extraction.indian_doc_extractor import IndianDocumentExtractor

TEST_CASES = [
    {
        "doc_type": "aadhaar",
        "text": "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI Mera Aadhaar 1234 5678 9012 DOB 15/08/1998 Male Address 42 MG Road Bengaluru 560001",
        "expected": {
            "aadhaar_number": "XXXX-XXXX-9012",
            "dob": "15/08/1998",
            "gender": "Male",
            "issuing_authority": "Unique Identification Authority of India (UIDAI)",
        }
    },
    {
        "doc_type": "pan",
        "text": "INCOME TAX DEPARTMENT GOVT. OF INDIA PERMANENT ACCOUNT NUMBER ABCDE1234F Name Rajesh Kumar Father's Name Suresh Kumar DOB 12/04/1990",
        "expected": {
            "pan_number": "ABCDE****F",
            "guardian_name": "Suresh Kumar",
            "dob": "12/04/1990",
            "issuing_authority": "Income Tax Department, Government of India",
        }
    },
    {
        "doc_type": "marksheet",
        "text": "STATEMENT OF MARKS Anna University Name of Candidate Anand Kumar Roll No 710018104001 Bachelor of Technology Semester V CGPA 8.75 Result PASS",
        "expected": {
            "student_name": "Anand Kumar",
            "roll_number": "710018104001",
            "degree_course": "Bachelor of Technology",
            "sgpa_cgpa": "CGPA: 8.75",
            "result_status": "PASS",
        }
    },
    {
        "doc_type": "fee_receipt",
        "text": "FEE RECEIPT Receipt No RCPT-2026-991 Amount Paid INR 45,000.00 Payment Date 12/10/2026 Payment Mode UPI",
        "expected": {
            "receipt_number": "RCPT-2026-991",
            "amount_paid": "INR 45,000.00",
            "payment_date": "12/10/2026",
        }
    },
    {
        "doc_type": "passbook",
        "text": "STATE BANK OF INDIA PASSBOOK Account No 12345678901 IFSC Code SBIN0001234 Primary Account Holder",
        "expected": {
            "account_number": "******8901",
            "bank_name": "State Bank Of India",
            "ifsc_code": "SBIN0001234",
        }
    }
]


def run_field_extraction_evaluation():
    print("=" * 70)
    print("CertiNexus AI — Evaluating Structured Field Extraction & PII Masking")
    print("=" * 70)

    extractor = IndianDocumentExtractor()
    total_fields = 0
    matched_fields = 0
    pii_masked_correctly = 0
    total_pii_fields = 0

    results = []

    for idx, case in enumerate(TEST_CASES):
        doc_type = case["doc_type"]
        text = case["text"]
        expected = case["expected"]

        res = extractor.extract(text, doc_type)
        fields = res["fields"]

        case_matches = 0
        for k, v_exp in expected.items():
            total_fields += 1
            v_act = fields.get(k)
            is_match = (v_act == v_exp)
            if is_match:
                matched_fields += 1
                case_matches += 1

            PII_FIELDS = {"aadhaar_number", "pan_number", "account_number", "dl_number", "phone"}
            if k in PII_FIELDS:
                total_pii_fields += 1
                if "*" in str(v_act) or "X" in str(v_act):
                    pii_masked_correctly += 1

        results.append({
            "doc_type": doc_type,
            "fields_evaluated": len(expected),
            "matches": case_matches,
            "extracted": fields,
        })
        print(f"  [{doc_type.upper():<12}] Matches: {case_matches}/{len(expected)} ({case_matches/len(expected)*100:.0f}%)")

    coverage = matched_fields / max(total_fields, 1)
    pii_compliance = pii_masked_correctly / max(total_pii_fields, 1)

    print("-" * 70)
    print(f"Total Fields Evaluated:     {total_fields}")
    print(f"Exact Match Field Coverage: {coverage:.4f} ({coverage*100:.1f}%)")
    print(f"PII Privacy Compliance:     {pii_compliance:.4f} ({pii_compliance*100:.1f}%)")

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "field_extraction_evaluation.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "field_coverage": round(coverage, 4),
            "pii_compliance": round(pii_compliance, 4),
            "total_fields": total_fields,
            "test_cases": results,
        }, f, indent=2)

    print(f"Saved evaluation report to: {out_path}")
    return coverage


if __name__ == "__main__":
    run_field_extraction_evaluation()
