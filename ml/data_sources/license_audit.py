"""
CertiNexus AI — Dataset License & Privacy Audit
Validates dataset licenses, redistribution permissions, and privacy constraints.
"""

from typing import Any, Dict, List
from .base import DatasetMetadata


class DatasetLicenseAuditor:
    """Audits licenses and terms of use for ingested datasets."""

    ALLOWED_PERMISSIVE_LICENSES = [
        "Apache-2.0",
        "MIT",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "OpenRail",
    ]

    RESTRICTED_RESEARCH_LICENSES = [
        "CC-BY-NC-4.0",
        "CC-BY-NC-SA-4.0",
        "Academic Research License",
    ]

    @classmethod
    def audit_metadata(cls, meta: DatasetMetadata) -> Dict[str, Any]:
        """Audit a single dataset's license."""
        lic = meta.license_id
        is_permissive = any(p.lower() in lic.lower() for p in cls.ALLOWED_PERMISSIVE_LICENSES)
        is_research_only = any(r.lower() in lic.lower() for r in cls.RESTRICTED_RESEARCH_LICENSES)

        compliance_status = "Approved for Commercial & Research" if is_permissive else (
            "Research & Academic Evaluation Only" if is_research_only else "Review Required"
        )

        return {
            "dataset_name": meta.name,
            "license": lic,
            "compliance_status": compliance_status,
            "is_permissive": is_permissive,
            "is_research_only": is_research_only,
            "privacy_notice": (
                "Synthetic or masked identity representations required; raw PII must never be stored in public model weights."
                if any(t in meta.tasks for t in ["kyc_extraction", "field_extraction"])
                else "Public document metadata."
            ),
        }

    @classmethod
    def audit_all(cls, adapters: List[Any]) -> List[Dict[str, Any]]:
        """Audit all registered adapters."""
        return [cls.audit_metadata(a.get_metadata()) for a in adapters]
