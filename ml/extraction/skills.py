"""
CertiNexus AI — Skill Database & Extractor

Comprehensive skill/technology database organized by categories,
with extraction logic for certificate text.
"""

import re
from typing import Dict, List

from .rule_ner import Entity


class SkillDatabase:
    """
    Database of skills and technologies organized by category.
    Used for extracting skills from certificate text.
    """

    SKILLS = {
        "PROGRAMMING_LANGUAGE": [
            "Python", "Java", "JavaScript", "TypeScript", "C",
            "C++", "C#", "Go", "Rust", "Kotlin", "Swift",
            "Ruby", "PHP", "Scala", "R", "MATLAB", "Perl",
            "Dart", "Lua", "Assembly", "Haskell", "Elixir",
            "Shell", "Bash", "PowerShell", "SQL",
        ],
        "WEB_FRAMEWORK": [
            "React", "Angular", "Vue", "Next.js", "Nuxt",
            "Django", "Flask", "FastAPI", "Spring Boot",
            "Express", "Node.js", "Rails", "Laravel",
            "ASP.NET", "Svelte", "Remix", "Gatsby",
        ],
        "CLOUD_PLATFORM": [
            "AWS", "Azure", "Google Cloud", "GCP", "Firebase",
            "Heroku", "DigitalOcean", "Vercel", "Netlify",
            "Cloudflare",
        ],
        "DATA_SCIENCE": [
            "Machine Learning", "Deep Learning", "Neural Networks",
            "Natural Language Processing", "NLP",
            "Computer Vision", "Data Science", "Data Analytics",
            "Data Engineering", "Big Data", "Statistics",
            "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
            "Pandas", "NumPy", "Matplotlib", "OpenCV",
            "Hugging Face", "NLTK", "SpaCy",
        ],
        "DEVOPS": [
            "Docker", "Kubernetes", "CI/CD", "Jenkins",
            "GitHub Actions", "GitLab CI", "Terraform",
            "Ansible", "Prometheus", "Grafana", "Linux",
            "Nginx", "Apache",
        ],
        "DATABASE": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "SQLite", "Oracle", "SQL Server", "Cassandra",
            "DynamoDB", "Elasticsearch", "Neo4j", "InfluxDB",
        ],
        "CYBERSECURITY": [
            "Cybersecurity", "Ethical Hacking", "Penetration Testing",
            "Network Security", "Cryptography", "OWASP",
            "Firewall", "SIEM", "SOC", "Malware Analysis",
            "Digital Forensics", "Vulnerability Assessment",
        ],
        "MOBILE": [
            "Android", "iOS", "Flutter", "React Native",
            "Xamarin", "SwiftUI", "Jetpack Compose",
        ],
        "SOFT_SKILL": [
            "Leadership", "Teamwork", "Communication",
            "Problem Solving", "Critical Thinking",
            "Project Management", "Agile", "Scrum",
            "Time Management", "Public Speaking",
            "Presentation", "Collaboration",
        ],
        "CERTIFICATION": [
            "AWS Certified", "Azure Certified",
            "Google Certified", "CompTIA", "Cisco",
            "CCNA", "CCNP", "CEH", "CISSP", "PMP",
            "ITIL", "Six Sigma", "Salesforce",
            "Oracle Certified", "RHCE",
        ],
    }

    def __init__(self):
        # Build a lookup dict for fast matching
        self._skill_lookup = {}
        for category, skills in self.SKILLS.items():
            for skill in skills:
                self._skill_lookup[skill.lower()] = (skill, category)

        # Sort by length descending (match longest first)
        self._sorted_skills = sorted(
            self._skill_lookup.keys(),
            key=len,
            reverse=True,
        )

    def extract_skills(self, text: str) -> List[Entity]:
        """
        Extract skills from text using dictionary matching.

        Parameters
        ----------
        text : str
            Input text.

        Returns
        -------
        entities : list of Entity
        """
        entities = []
        text_lower = text.lower()
        used_spans = set()

        for skill_lower in self._sorted_skills:
            # Use word boundary matching
            pattern = r"\b" + re.escape(skill_lower) + r"\b"
            for match in re.finditer(pattern, text_lower):
                span = (match.start(), match.end())
                # Check for overlaps
                overlap = False
                for us, ue in used_spans:
                    if span[0] < ue and span[1] > us:
                        overlap = True
                        break
                if overlap:
                    continue

                canonical, category = self._skill_lookup[skill_lower]
                entities.append(Entity(
                    text=canonical,
                    entity_type="SKILL",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    source="dictionary",
                    metadata={"skill_category": category},
                ))
                used_spans.add(span)

        return entities

    def get_all_skills(self) -> Dict[str, List[str]]:
        """Return all skills organized by category."""
        return self.SKILLS.copy()

    def get_category_skills(self, category: str) -> List[str]:
        """Get skills for a specific category."""
        return self.SKILLS.get(category, [])
