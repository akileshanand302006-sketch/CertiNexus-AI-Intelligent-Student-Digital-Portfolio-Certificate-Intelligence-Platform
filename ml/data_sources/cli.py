"""
CertiNexus AI — Dataset Ingestion CLI
Command-line interface for dataset audit, inspection, bounded sampling, and storage reporting.
"""

import argparse
import json
import sys

from .budget import StorageBudgetManager
from .license_audit import DatasetLicenseAuditor
from .registry import DatasetRegistry
from .dataset_validator import DatasetValidator


def cmd_audit(args):
    """Audit all registered dataset sources and licenses."""
    adapters = DatasetRegistry.get_all_adapters()
    audit_results = DatasetLicenseAuditor.audit_all(adapters)
    print("\n=== CertiNexus AI — Dataset License & Governance Audit ===")
    print(f"Total Sources Registered: {len(audit_results)}\n")
    for a in audit_results:
        print(f"[{a['dataset_name']}]")
        print(f"  License:    {a['license']}")
        print(f"  Compliance: {a['compliance_status']}")
        print(f"  Notice:     {a['privacy_notice']}\n")


def cmd_inspect(args):
    """Inspect metadata and schema of a specific source."""
    adapter = DatasetRegistry.get_adapter(args.source)
    meta = adapter.get_metadata()
    print(f"\n=== Inspect Dataset: {meta.name} ===")
    print(json.dumps(meta.to_dict(), indent=2))


def cmd_sample(args):
    """Stream bounded samples from a specific source."""
    adapter = DatasetRegistry.get_adapter(args.source)
    limit = args.limit or 5
    print(f"\n=== Streaming {limit} Samples from {adapter.get_metadata().name} ===")
    count = 0
    for sample in adapter.stream_samples(limit=limit):
        count += 1
        print(f"\n--- Sample #{count} [{sample.sample_id}] ---")
        print(f"Task:          {sample.task}")
        print(f"Doc Type:      {sample.document_type}")
        print(f"Category:      {sample.certificate_category}")
        print(f"Language:      {sample.language}")
        sample_txt = (sample.ground_truth_text or "")[:120]
        print(f"Text Preview:  {sample_txt}...")
        if sample.ground_truth_fields:
            print(f"Fields:        {list(sample.ground_truth_fields.keys())}")


def cmd_validate(args):
    """Validate sample schemas and integrity across registered sources."""
    print("\n=== Validating Dataset Sources ===")
    validator = DatasetValidator()
    adapters = DatasetRegistry.get_all_adapters()
    for adapter in adapters:
        name = adapter.get_metadata().name
        res = adapter.validate(num_samples=args.limit or 3)
        status = "PASSED" if res["success"] else "WARNING"
        print(f"[{name}]: {status} ({res['samples_checked']} samples checked)")
        if res["errors"]:
            for err in res["errors"]:
                print(f"   Error: {err}")


def cmd_report(args):
    """Audit storage usage and generate DATA_STORAGE_REPORT.md."""
    manager = StorageBudgetManager()
    rep = manager.generate_storage_report()
    print("\n=== Generated DATA_STORAGE_REPORT.md ===")
    safe_rep = rep[:500].encode('ascii', errors='replace').decode('ascii')
    print(safe_rep + "\n...[Report written to DATA_STORAGE_REPORT.md]")


def main():
    parser = argparse.ArgumentParser(description="CertiNexus AI Dataset Ingestion CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # audit
    subparsers.add_parser("audit", help="Audit dataset licenses and governance")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect source metadata")
    p_inspect.add_argument("--source", required=True, choices=DatasetRegistry.list_sources())

    # sample
    p_sample = subparsers.add_parser("sample", help="Stream bounded samples")
    p_sample.add_argument("--source", required=True, choices=DatasetRegistry.list_sources())
    p_sample.add_argument("--limit", type=int, default=5)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate sample schemas")
    p_val.add_argument("--limit", type=int, default=3)

    # report
    subparsers.add_parser("report", help="Generate DATA_STORAGE_REPORT.md")

    parsed = parser.parse_args()
    if parsed.subcommand == "audit":
        cmd_audit(parsed)
    elif parsed.subcommand == "inspect":
        cmd_inspect(parsed)
    elif parsed.subcommand == "sample":
        cmd_sample(parsed)
    elif parsed.subcommand == "validate":
        cmd_validate(parsed)
    elif parsed.subcommand == "report":
        cmd_report(parsed)


if __name__ == "__main__":
    main()
