"""
CertiNexus AI — Document Type Classifier Training & Evaluation

Trains and evaluates the document type routing model across:
- Identity & Government: Aadhaar, PAN, Driving Licence, Vehicle RC, Patta
- Academic & Educational: Marksheet / Transcript, Timetable, Fee Receipt
- Financial: Bank Passbook
- Career: Resume / CV
- Accredited Credentials: 11-class Certificates
- Unknown / Abstention Fallbacks
"""

import json
import os
import sys
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from ml.classifiers.document_router import DocumentTypeRouter

# Sample test documents covering all Indian categories and noise
BENCHMARK_CORPUS = [
    # Aadhaar samples
    ("GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI Mera Aadhaar Meri Pehchan 1234 5678 9012 DOB 15/08/1998 Male Address New Delhi 110001", "aadhaar"),
    ("भारत सरकार UNIQUE IDENTIFICATION AUTHORITY OF INDIA Help 1947 VID 9876 5432 1098 7654 4433 2211 0099 DOB 01/01/1995 Female", "aadhaar"),
    ("Aadhaar Card Enrollment No 1234/56789/10111 8899 7766 5544 Year of Birth 2000 Address Chennai Tamil Nadu 600028", "aadhaar"),
    
    # PAN samples
    ("INCOME TAX DEPARTMENT GOVT. OF INDIA PERMANENT ACCOUNT NUMBER ABCDE1234F Name Rajesh Kumar Father's Name Suresh Kumar DOB 12/04/1990", "pan"),
    ("आयकर विभाग भारत सरकार Permanent Account Number Cardholder Priya Sharma BKZPS9876Q 24/11/1994", "pan"),
    ("Income Tax Department Govt of India PAN Card XYZPA5544K Date of Birth 05/09/1988", "pan"),
    
    # Driving Licence samples
    ("UNION OF INDIA DRIVING LICENCE FORM 7 Transport Department TN-01-20150001234 Holder Name Ramesh MCWG LMV Valid Till 10/05/2035", "driving_licence"),
    ("MOTOR VEHICLES DEPARTMENT DL04 20110012345 Driver's Licence Licensing Authority HMV TRANS Date of Issue 02/03/2012", "driving_licence"),
    
    # Vehicle RC samples
    ("CERTIFICATE OF REGISTRATION FORM 23 Motor Vehicles Department Registration No MH02AB1234 Chassis No Engine No Maker Maruti Suzuki Petrol", "vehicle_rc"),
    ("REGISTRATION CERTIFICATE DL-1C-AA-1111 Owner Name Vikramaditya Hyundai Creta Motor Car Seating Capacity 5 Fitness Valid", "vehicle_rc"),
    
    # Marksheet samples
    ("STATEMENT OF MARKS Anna University Bachelor of Technology Semester VII Course Code CS801 Total Marks 85/100 CGPA 8.75 Result PASS", "marksheet"),
    ("GRADE SHEET Academic Transcript Semester 5 Register No 710018104001 Cumulative Grade Point Average SGPA 9.1 Credits Earned 24", "marksheet"),
    ("BOARD OF SECONDARY EDUCATION Statement of Marks Candidate Name Roll No 455612 Maximum Marks 500 First Class with Distinction", "marksheet"),
    
    # Timetable samples
    ("DEPARTMENT OF COMPUTER SCIENCE CLASS TIMETABLE SEMESTER 6 Monday 09:00-10:00 Data Science Room 302 Tuesday 10:00-11:00 Period 2", "timetable"),
    ("ACADEMIC ROUTINE 2026 Time Table Section A Wed 11:00 Lab Thu 02:00 Project Friday 09:00", "timetable"),
    
    # Fee Receipt samples
    ("INSTITUTE OF TECHNOLOGY TUITION FEE RECEIPT Receipt No RCPT-2026-991 Paid Amount Rs 45000 Payment Mode Net Banking Transaction ID TXN8871", "fee_receipt"),
    ("FEE VOUCHER Challan No CH-4412 Payment Date 14/07/2026 Amount Paid INR 65000 Balance Fee Nil Bank Ref 990123", "fee_receipt"),
    
    # Bank Passbook samples
    ("STATE BANK OF INDIA PASSBOOK Savings Bank Account Number 12345678901 IFSC Code SBIN0001234 Branch Anna Nagar Statement of Account", "passbook"),
    ("HDFC BANK Pass Book Account No 50100234567890 CIF No Branch Code Current Account Ledger Balance", "passbook"),
    
    # Patta / Land Record samples
    ("REVENUE DEPARTMENT TAMIL NADU Patta Pass Book Patta No 1452 Survey Number 128/4A Pattadar Name Kandasamy Village Taluk", "patta"),
    ("LAND RECORDS Chitta Khatauni Survey No 89/2 Area 1.5 Acres Revenue Authority", "patta"),
    
    # Resume / CV samples
    ("CURRICULUM VITAE Student Scholar student@example.com +91-9876543210 Education B.Tech CSE Technical Skills Python PyTorch React Projects GitHub linkedin.com", "resume"),
    ("RESUME SDE Software Engineer Work Experience 2024-2026 Professional Experience Core Competencies Machine Learning LeetCode GitHub", "resume"),
    
    # Accredited Certificate samples
    ("Certificate of Completion This is to certify that Rahul has successfully completed Python for Data Science Workshop Authorized Signatory", "certificate"),
    ("Certificate of Achievement Presented to Maya for securing 1st Prize in Hackathon 2026 Technical Competition Credential ID CERT-9912", "certificate"),
    ("Certificate of Participation is hereby awarded to Candidate for actively attending Seminar on Cloud Computing", "certificate"),
]


def run_document_type_evaluation():
    print("=" * 70)
    print("CertiNexus AI — Evaluating Document Type Routing Model")
    print("=" * 70)

    router = DocumentTypeRouter()
    y_true = []
    y_pred = []

    for text, label in BENCHMARK_CORPUS:
        result = router.route(text)
        pred = result["document_type"]
        y_true.append(label)
        y_pred.append(pred)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="weighted")
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print(f"Total Benchmark Documents: {len(BENCHMARK_CORPUS)}")
    print(f"Overall Accuracy:          {acc:.4f} ({acc*100:.1f}%)")
    print(f"Weighted Macro F1 Score:   {f1:.4f}")
    print("\nDetailed Per-Class Performance:")
    print("-" * 70)
    for cls in sorted(list(set(y_true))):
        cls_data = report.get(cls, {})
        p = cls_data.get("precision", 0.0)
        r = cls_data.get("recall", 0.0)
        f = cls_data.get("f1-score", 0.0)
        s = cls_data.get("support", 0)
        print(f"  {cls:<20} Precision: {p:.2f} | Recall: {r:.2f} | F1: {f:.2f} | Support: {s}")

    # Save results
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "document_type_evaluation.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": round(float(acc), 4),
            "macro_f1": round(float(f1), 4),
            "total_samples": len(BENCHMARK_CORPUS),
            "per_class": report,
            "confusion_matrix": cm.tolist(),
        }, f, indent=2)

    print(f"\nSaved evaluation metrics to: {out_path}")
    return acc, f1


if __name__ == "__main__":
    run_document_type_evaluation()
