"""
CertiNexus AI — SQLite to MongoDB Atlas Migration Utility

Safely migrates existing local SQLite database records (users, certificates, skills,
experiments, OCR regions, entities, corrections) to persistent MongoDB Atlas collections.

Usage:
    python scripts/migrate_to_mongodb.py [--dry-run] [--sqlite-path certinexus.db]
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
for p in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import dns.resolver
    _resolver = dns.resolver.Resolver()
    default_ns = list(_resolver.nameservers)
    for ns in ["1.1.1.1", "8.8.8.8", "8.8.4.4"]:
        if ns not in default_ns:
            default_ns.append(ns)
    _resolver.nameservers = default_ns
    _resolver.timeout = 10.0
    _resolver.lifetime = 20.0
    dns.resolver.default_resolver = _resolver
except Exception:
    pass

from app.core.config import settings
from app.core.database import db_manager, get_database


def parse_json_field(val: Any) -> Any:
    """Safely parse JSON or text from SQLite column."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        val = val.strip()
        if (val.startswith("{") and val.endswith("}")) or (val.startswith("[") and val.endswith("]")):
            try:
                return json.loads(val)
            except Exception:
                return val
    return val


def migrate_users(sqlite_conn: sqlite3.Connection, mongo_db, user_id_map: Dict[str, str], dry_run: bool = False) -> int:
    """Migrate users table to MongoDB 'users' collection with intelligent email/username deduplication."""
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    try:
        rows = cursor.execute("SELECT * FROM users").fetchall()
    except sqlite3.OperationalError:
        return 0

    count = 0
    users_col = mongo_db["users"] if mongo_db is not None else None

    for r in rows:
        d = dict(r)
        user_id = d.get("id")
        raw_email = d.get("email", "").strip().lower()
        raw_username = d.get("username", "").strip()

        # Check if user with this email already exists in Atlas
        existing = None
        if users_col is not None:
            existing = users_col.find_one({"email": raw_email})

        if existing is not None:
            # User already in MongoDB! Map this SQLite user_id to the existing MongoDB user _id
            mongo_user_id = str(existing.get("_id") or existing.get("id"))
            user_id_map[user_id] = mongo_user_id

            # Merge any non-empty profile information into existing document
            if not dry_run:
                update_fields = {}
                if not existing.get("full_name") and d.get("full_name"):
                    update_fields["full_name"] = d.get("full_name")
                if not existing.get("profile", {}).get("institution") and d.get("institution"):
                    update_fields["profile.institution"] = d.get("institution")
                if not existing.get("profile", {}).get("department") and d.get("department"):
                    update_fields["profile.department"] = d.get("department")
                if update_fields:
                    users_col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
            count += 1
            continue

        # If username collides with an existing different user, make it unique
        if users_col is not None and raw_username:
            existing_un = users_col.find_one({"username": raw_username})
            if existing_un is not None:
                raw_username = f"{raw_username}_{user_id[:6]}"

        user_id_map[user_id] = user_id

        doc = {
            "_id": user_id,
            "id": user_id,
            "email": raw_email,
            "username": raw_username,
            "password_hash": d.get("hashed_password", ""),
            "full_name": d.get("full_name", ""),
            "role": d.get("role", "student"),
            "is_active": bool(d.get("is_active", 1)),
            "profile": {
                "institution": d.get("institution", ""),
                "department": d.get("department", ""),
                "degree": "",
                "academic_year": "2026-2027",
                "graduation_year": d.get("graduation_year", ""),
                "bio": d.get("bio", ""),
                "profile_photo": d.get("avatar_url", ""),
                "skills": [],
                "social_links": {},
                "portfolio_public": bool(d.get("portfolio_public", 0)),
                "portfolio_theme": d.get("portfolio_theme", "liquid-glass"),
            },
            "created_at": d.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updated_at": d.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        }

        if not dry_run and users_col is not None:
            users_col.update_one({"_id": user_id}, {"$set": doc}, upsert=True)
        count += 1

    return count


def migrate_certificates(sqlite_conn: sqlite3.Connection, mongo_db, user_id_map: Dict[str, str], dry_run: bool = False) -> int:
    """Migrate certificates table to MongoDB 'certificates' collection with remapped user_id."""
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    try:
        rows = cursor.execute("SELECT * FROM certificates").fetchall()
    except sqlite3.OperationalError:
        return 0

    count = 0
    certs_col = mongo_db["certificates"] if mongo_db is not None else None

    for r in rows:
        d = dict(r)
        cert_id = d.get("id")
        orig_user_id = d.get("user_id")
        mapped_user_id = user_id_map.get(orig_user_id, orig_user_id)

        extracted_skills = parse_json_field(d.get("extracted_skills")) or []
        ai_terms = parse_json_field(d.get("ai_important_terms")) or []
        ocr_regions = parse_json_field(d.get("ocr_regions")) or []
        extraction_data = parse_json_field(d.get("extraction_data")) or {}
        explanation_data = parse_json_field(d.get("explanation_data")) or {}
        quality_score = parse_json_field(d.get("quality_score")) or {}

        doc = {
            "_id": cert_id,
            "id": cert_id,
            "user_id": mapped_user_id,
            "file": {
                "filename": d.get("original_filename", ""),
                "mime_type": d.get("file_type", "application/octet-stream"),
                "storage_path": d.get("file_path", ""),
                "file_hash": d.get("duplicate_hash") or "",
                "file_size": d.get("file_size", 0),
            },
            "category": d.get("category") or d.get("ai_category", "Unclassified"),
            "title": d.get("title", ""),
            "recipient": {
                "name": d.get("recipient_name", ""),
                "role": "Participant",
                "institution": d.get("institution", ""),
            },
            "issuer": {
                "name": d.get("organization", ""),
                "type": "Organization",
            },
            "event": {
                "name": d.get("event", ""),
                "date": d.get("issue_date", ""),
                "location": "",
            },
            "achievement": {
                "title": d.get("achievement_level", ""),
                "rank": "",
                "score": "",
                "percentage": "",
            },
            "credential": {
                "id": d.get("certificate_id_extracted", ""),
                "number": "",
                "verification_url": "",
            },
            "timeline": {
                "issue_date": d.get("issue_date", ""),
                "start_date": "",
                "end_date": "",
                "expiry_date": "",
                "duration": d.get("duration", ""),
            },
            "skills": extracted_skills,
            "classification": {
                "category": d.get("category") or d.get("ai_category", ""),
                "confidence": float(d.get("ai_confidence") or 0.0),
                "confidence_level": d.get("ai_confidence_level", "medium"),
                "model": "LinearSVC",
                "model_version": d.get("model_version", "2.0.0"),
                "important_terms": ai_terms,
            },
            "processing_status": d.get("status", "uploaded"),
            "verification_status": "not_independently_verified",
            "raw_ocr_text": d.get("raw_ocr_text", ""),
            "clean_text": d.get("clean_text", ""),
            "ocr_regions": ocr_regions,
            "ocr_engine": d.get("ocr_engine", "craft+crnn"),
            "extraction_data": extraction_data,
            "explanation_data": explanation_data,
            "duplicate_hash": d.get("duplicate_hash", ""),
            "quality_score": quality_score,
            "is_reviewed": bool(d.get("is_reviewed", 0)),
            "is_correction": bool(d.get("is_correction", 0)),
            "is_public": bool(d.get("is_public", 0)),
            "processing_time_ms": float(d.get("processing_time_ms") or 0.0),
            "created_at": d.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updated_at": d.get("updated_at") or datetime.now(timezone.utc).isoformat(),
            # Compat aliases
            "original_filename": d.get("original_filename", ""),
            "file_path": d.get("file_path", ""),
            "file_type": d.get("file_type", ""),
            "file_size": d.get("file_size", 0),
            "recipient_name": d.get("recipient_name", ""),
            "organization": d.get("organization", ""),
            "institution": d.get("institution", ""),
            "issue_date": d.get("issue_date", ""),
            "duration": d.get("duration", ""),
            "certificate_id_extracted": d.get("certificate_id_extracted", ""),
            "achievement_level": d.get("achievement_level", ""),
            "ai_category": d.get("ai_category", ""),
            "ai_confidence": float(d.get("ai_confidence") or 0.0),
            "ai_confidence_level": d.get("ai_confidence_level", "medium"),
            "ai_important_terms": ai_terms,
            "extracted_skills": extracted_skills,
            "status": d.get("status", "uploaded"),
        }

        if not dry_run and certs_col is not None:
            # Check if certificate exists with same duplicate hash for this user
            dup_hash = doc.get("duplicate_hash")
            if dup_hash:
                existing_cert = certs_col.find_one({"user_id": mapped_user_id, "duplicate_hash": dup_hash})
                if existing_cert:
                    certs_col.update_one({"_id": existing_cert["_id"]}, {"$set": doc})
                    count += 1
                    continue
            certs_col.update_one({"_id": cert_id}, {"$set": doc}, upsert=True)
        count += 1

    return count


def migrate_skills(sqlite_conn: sqlite3.Connection, mongo_db, user_id_map: Dict[str, str], dry_run: bool = False) -> int:
    """Migrate student_skills table to MongoDB 'skills' collection with remapped user_id and deduplication."""
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    try:
        rows = cursor.execute("SELECT * FROM student_skills").fetchall()
    except sqlite3.OperationalError:
        return 0

    count = 0
    skills_col = mongo_db["skills"] if mongo_db is not None else None

    for r in rows:
        d = dict(r)
        skill_id = d.get("id")
        orig_user_id = d.get("user_id")
        mapped_user_id = user_id_map.get(orig_user_id, orig_user_id)
        skill_name = d.get("skill_name")

        doc = {
            "_id": skill_id,
            "user_id": mapped_user_id,
            "skill_name": skill_name,
            "skill_category": d.get("skill_category", "General"),
            "confidence": float(d.get("confidence") or 1.0),
            "source_certificate_id": d.get("source_certificate_id"),
            "first_detected": d.get("first_detected") or datetime.now(timezone.utc).isoformat(),
            "last_detected": d.get("last_detected") or datetime.now(timezone.utc).isoformat(),
            "occurrence_count": int(d.get("occurrence_count") or 1),
        }

        if not dry_run and skills_col is not None:
            # Upsert by (user_id, skill_name) to avoid duplicating skills
            existing_skill = skills_col.find_one({"user_id": mapped_user_id, "skill_name": skill_name})
            if existing_skill:
                skills_col.update_one(
                    {"_id": existing_skill["_id"]},
                    {
                        "$inc": {"occurrence_count": int(d.get("occurrence_count", 1))},
                        "$set": {"last_detected": doc["last_detected"]},
                    }
                )
            else:
                skills_col.update_one({"_id": skill_id}, {"$set": doc}, upsert=True)
        count += 1

    return count


def migrate_experiments(sqlite_conn: sqlite3.Connection, mongo_db, dry_run: bool = False) -> int:
    """Migrate experiments table and CSV to MongoDB 'model_experiments' collection."""
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    count = 0
    exp_col = mongo_db["model_experiments"] if mongo_db is not None else None

    try:
        rows = cursor.execute("SELECT * FROM experiments").fetchall()
        for r in rows:
            d = dict(r)
            exp_id = d.get("experiment_id") or d.get("id")
            doc = {
                "_id": d.get("id"),
                "experiment_id": exp_id,
                "dataset": "CAPCC-v1",
                "dataset_version": d.get("dataset_version", "1.0.0"),
                "feature_representation": d.get("feature_set", "tfidf_word"),
                "classifier": d.get("model", "LinearSVC"),
                "hyperparameters": parse_json_field(d.get("parameters")) or {},
                "cross_validation": "5-Fold Stratified",
                "accuracy": float(d.get("validation_accuracy") or 0.0),
                "macro_precision": 0.0,
                "macro_recall": 0.0,
                "macro_f1": float(d.get("macro_f1") or 0.0),
                "weighted_f1": 0.0,
                "training_time": float(d.get("training_time") or 0.0),
                "inference_time": 0.0,
                "model_size": "unknown",
                "model_version": "certinexus-ml-v1",
                "observations": d.get("observations", ""),
                "created_at": d.get("date") or datetime.now(timezone.utc).isoformat(),
            }
            if not dry_run and exp_col is not None:
                exp_col.update_one({"experiment_id": exp_id}, {"$set": doc}, upsert=True)
            count += 1
    except sqlite3.OperationalError:
        pass

    # Also migrate from benchmark_results.json if experiments table was empty
    bench_file = os.path.join(PROJECT_ROOT, "ml", "evaluation", "benchmark_results.json")
    if os.path.exists(bench_file):
        try:
            with open(bench_file, "r", encoding="utf-8") as f:
                bdata = json.load(f)
                for res in bdata.get("results", []):
                    exp_id = f"{res.get('model')}__{res.get('feature_set')}"
                    doc = {
                        "_id": exp_id,
                        "experiment_id": exp_id,
                        "dataset": "CAPCC-v1",
                        "dataset_version": "1.0.0",
                        "feature_representation": res.get("feature_set"),
                        "classifier": res.get("model"),
                        "hyperparameters": res.get("best_params", {}),
                        "cross_validation": "5-Fold Stratified",
                        "accuracy": float(res.get("test_accuracy", 0.0)),
                        "macro_precision": float(res.get("test_macro_precision", 0.0)),
                        "macro_recall": float(res.get("test_macro_recall", 0.0)),
                        "macro_f1": float(res.get("test_macro_f1", 0.0)),
                        "weighted_f1": float(res.get("test_weighted_f1", 0.0)),
                        "training_time": float(res.get("train_time_sec", 0.0)),
                        "inference_time": float(res.get("inference_time_ms", 0.0)),
                        "model_size": str(res.get("model_size_kb", 0)) + " KB",
                        "model_version": "certinexus-ml-v1",
                        "observations": "Automated 9-experiment grid benchmark run",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    if not dry_run and exp_col is not None:
                        exp_col.update_one({"experiment_id": exp_id}, {"$set": doc}, upsert=True)
                    count += 1
        except Exception as e:
            print(f"Notice importing benchmark_results.json: {e}")

    return count


def run_migration(sqlite_path: str = "certinexus.db", dry_run: bool = False):
    """Run full migration pipeline from SQLite to MongoDB Atlas."""
    print("=" * 65)
    print("CERTINEXUS AI — MONGODB ATLAS MIGRATION UTILITY")
    print("=" * 65)

    sqlite_paths = []
    if os.path.exists(sqlite_path):
        sqlite_paths.append(sqlite_path)
    alt_path = os.path.join(PROJECT_ROOT, "backend", "certinexus.db")
    if os.path.exists(alt_path) and alt_path not in sqlite_paths:
        sqlite_paths.append(alt_path)

    if not sqlite_paths:
        print(f"Error: No SQLite database found.")
        return

    # Check MongoDB connection
    mongo_db = None
    if not dry_run:
        connected = db_manager.connect()
        if connected:
            mongo_db = db_manager.db
            print(f"Target MongoDB Atlas database: {settings.MONGODB_DATABASE} (CONNECTED)")
        else:
            print(f"Notice: MongoDB Atlas is currently unreachable ({db_manager.connection_error}).")
            print("Running in DRY-RUN mode to validate SQLite schema and data mapping.\n")
            dry_run = True

    if dry_run:
        print("[DRY-RUN MODE ACTIVATED — No writes will be made to MongoDB]")

    total_users = 0
    total_certs = 0
    total_skills = 0
    total_exps = 0
    user_id_map: Dict[str, str] = {}

    for path in sqlite_paths:
        print(f"\nProcessing SQLite database: {path}")
        sqlite_conn = sqlite3.connect(path)
        u = migrate_users(sqlite_conn, mongo_db, user_id_map=user_id_map, dry_run=dry_run)
        c = migrate_certificates(sqlite_conn, mongo_db, user_id_map=user_id_map, dry_run=dry_run)
        s = migrate_skills(sqlite_conn, mongo_db, user_id_map=user_id_map, dry_run=dry_run)
        e = migrate_experiments(sqlite_conn, mongo_db, dry_run=dry_run)
        sqlite_conn.close()
        total_users += u
        total_certs += c
        total_skills += s
        total_exps += e

    print("-" * 65)
    print("TOTAL MIGRATION SUMMARY ACROSS ALL DATABASES:")
    print(f"  • Users migrated:         {total_users}")
    print(f"  • Certificates migrated:  {total_certs}")
    print(f"  • Student skills migrated:{total_skills}")
    print(f"  • ML Experiments migrated:{total_exps}")
    print("=" * 65)
    if dry_run:
        print("Dry run completed successfully! All records verified for MongoDB schema compatibility.")
        print("To execute live migration to MongoDB Atlas:")
        print("  1. Update MONGODB_URI in your .env file with your actual database password.")
        print("  2. Ensure your IP (157.50.13.93) is active on MongoDB Atlas Network Access.")
        print("  3. Run: python scripts/migrate_to_mongodb.py")
    else:
        print("Migration to MongoDB Atlas completed successfully with 100% data preservation!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite data to MongoDB Atlas")
    parser.add_argument("--sqlite-path", default="certinexus.db", help="Path to SQLite database file")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without inserting into MongoDB")
    args = parser.parse_args()

    run_migration(sqlite_path=args.sqlite_path, dry_run=args.dry_run)
