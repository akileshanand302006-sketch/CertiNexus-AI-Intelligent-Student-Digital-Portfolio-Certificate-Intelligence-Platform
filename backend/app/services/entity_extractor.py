"""
CertiNexus AI — Intelligent Certificate Entity Extractor

Extracts structured information from OCR text:
- Recipient / Candidate Name
- Issuing Organization / Company
- Educational Institution
- Program / Domain / Event
- Issue Date and Duration
- Certificate / Credential ID
- Technical & Professional Skills
- Executive AI Summary
"""

import re
from typing import Dict, List, Optional, Any


SKILL_DATABASE = {
    # Programming & Tech
    "python": "Python", "java": "Java", "javascript": "JavaScript", "typescript": "TypeScript",
    "c++": "C++", "c#": "C#", "ruby": "Ruby", "go": "Go", "rust": "Rust", "php": "PHP",
    "html": "HTML", "css": "CSS", "sql": "SQL", "nosql": "NoSQL", "mongodb": "MongoDB",
    
    # Domains & Frameworks
    "react": "React", "angular": "Angular", "node.js": "Node.js", "nodejs": "Node.js",
    "express": "Express", "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "software development": "Software Development", "software product development": "Product Development",
    "software engineering": "Software Engineering", "web development": "Web Development",
    "mobile development": "Mobile Development", "full stack": "Full Stack Development",
    "frontend": "Frontend Development", "backend": "Backend Development",
    
    # AI / ML / Data
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "artificial intelligence": "AI", "ai": "AI", "data science": "Data Science",
    "data analytics": "Data Analytics", "big data": "Big Data", "computer vision": "Computer Vision",
    "natural language processing": "NLP", "nlp": "NLP", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    
    # Cloud & DevOps
    "cloud computing": "Cloud Computing", "aws": "AWS", "azure": "Azure", "gcp": "Google Cloud",
    "docker": "Docker", "kubernetes": "Kubernetes", "devops": "DevOps", "git": "Git",
    "linux": "Linux", "cybersecurity": "Cybersecurity", "blockchain": "Blockchain",
    "iot": "Internet of Things", "internet of things": "IoT",
    
    # Core Professional Competencies
    "problem solving": "Problem Solving", "critical thinking": "Critical Thinking",
    "teamwork": "Teamwork", "collaboration": "Collaboration",
    "leadership": "Leadership", "communication": "Communication",
    "professionalism": "Professionalism", "project management": "Project Management",
    "agile": "Agile", "scrum": "Scrum", "dedication": "Dedication",
    "analytical thinking": "Analytical Thinking",
}


def extract_certificate_entities(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Intelligently parses unstructured certificate OCR text into structured entities.
    """
    if not text:
        text = ""

    normalized = re.sub(r'\s+', ' ', text).strip()

    recipient_name = _extract_recipient_name(normalized)
    organization = _extract_organization(normalized)
    institution = _extract_institution(normalized)
    program = _extract_program(normalized)
    dates = _extract_dates(normalized)
    credential_id = _extract_credential_id(normalized)
    skills = _extract_skills(normalized)
    
    # Generate human-friendly executive summary
    summary = _generate_summary(
        recipient_name=recipient_name,
        organization=organization,
        institution=institution,
        program=program,
        dates=dates,
        skills=skills
    )

    return {
        "recipient_name": recipient_name,
        "organization": organization,
        "institution": institution,
        "event": program,
        "issue_date": dates.get("issue_date"),
        "duration": dates.get("duration"),
        "certificate_id_extracted": credential_id,
        "extracted_skills": skills,
        "ai_summary": summary,
    }


def _extract_recipient_name(text: str) -> Optional[str]:
    """Extract candidate / student name."""
    patterns = [
        r'(?:certify\s+that|awarded\s+to|presented\s+to|certifies\s+that)\s+(?:Mr\.|Ms\.|Mrs\.|Dr\.)?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z](?:\.|\b|[a-zA-Z]+)){0,3})(?:,|\s+a\b|\s+has\b|\s+of\b|\s+for\b|\s+student\b)',
        r'(?:Ms\.|Mr\.|Mrs\.)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z](?:\.|\b|[a-zA-Z]+)){0,3})',
        r'This\s+is\s+to\s+certify\s+([A-Z][a-zA-Z\.\'\-]+(?:\s+[A-Z][a-zA-Z\.\'\-]+){1,3})',
        r'Name\s*[:\-]\s*([A-Z][a-zA-Z\.\'\-]+(?:\s+[A-Z][a-zA-Z\.\'\-]+){1,3})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'[,;:\.]+$', '', name).strip()
            if len(name) >= 3 and not any(w.lower() in name.lower() for w in ['whomsoever', 'certify', 'completion', 'student', 'institute']):
                return name
    return None


def _extract_organization(text: str) -> Optional[str]:
    """Extract issuing company or organization."""
    patterns = [
        r'(?:with|at|by|from)\s+([A-Z][A-Za-z0-9\s\.&]{1,40}?\s+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|LLC|Inc\.?))',
        r'(?:with|at|by|from)\s+([A-Z][A-Za-z0-9\s\.&]{1,40}?\s+(?:Technologies|Technolabs|Solutions|Corporation|Services|Labs|Group))',
        r'([A-Z][A-Za-z0-9\s\.&]{1,40}?\s+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|LLC|Inc\.?))',
        r'(?:Organized\s+by|Conducted\s+by|Offered\s+by)\s*[:\-]?\s*([A-Z][A-Za-z0-9\s\.\&]{3,40})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            org = match.group(1).strip()
            org = re.sub(r'[,;:\.]+$', '', org).strip()
            if len(org) >= 4:
                return org
    return None


def _extract_institution(text: str) -> Optional[str]:
    """Extract academic college or university."""
    patterns = [
        r'(?:at|from)\s+([A-Z][A-Za-z\s]{3,45}?(?:Institute\s+of\s+Technology|University|College\s+of\s+Engineering|Polytechnic))',
        r'([A-Z][A-Za-z\s]{3,45}?(?:Institute\s+of\s+Technology|University|College\s+of\s+Engineering|Polytechnic))',
        r'student\s+at\s+([A-Z][A-Za-z\s]{3,45}?(?:Institute|College|University))',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            inst = match.group(1).strip()
            inst = re.sub(r'[,;:\.]+$', '', inst).strip()
            return inst
    return None


def _extract_program(text: str) -> Optional[str]:
    """Extract the specific course, domain, or role."""
    patterns = [
        r'(?:internship\s+program\s+in|training\s+in|course\s+in|workshop\s+on|specialization\s+in|hands[- ]on\s+session\s+on)\s+([A-Z][A-Za-z\s\/\&]{2,35}?)(?:\s+with|\s+at|\s+from|\s+dated|\s+during|\.|\,)',
        r'(?:completed\s+her|completed\s+his|completed\s+their)\s+([A-Za-z\s]{3,30}?)(?:\s+with|\s+at|\s+from|\s+in)',
        r'(?:in\s+the\s+field\s+of|domain\s+of)\s+([A-Z][A-Za-z\s]{3,30})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            prog = match.group(1).strip()
            prog = re.sub(r'[,;:\.]+$', '', prog).strip()
            if len(prog) >= 3 and not any(w in prog.lower() for w in ['successfully', 'during', 'whomsoever']):
                return prog.title()
    return None


def _extract_dates(text: str) -> Dict[str, Optional[str]]:
    """Extract dates including issue date and duration."""
    dates_found = {}
    
    # 1. Duration range: "from 19th May 2026 to 09th June 2026"
    duration_match = re.search(
        r'from\s+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{2,4})\s+to\s+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{2,4})',
        text, re.IGNORECASE
    )
    if duration_match:
        start_date = duration_match.group(1).strip()
        end_date = duration_match.group(2).strip()
        dates_found["duration"] = f"{start_date} - {end_date}"
        dates_found["issue_date"] = end_date

    # 2. Explicit Dated: "Dated: 9h June 2026" or "Date: 09/06/2026"
    if "issue_date" not in dates_found:
        date_match = re.search(
            r'(?:Dated?|Date of Issue|Issued on)[:\s]*(\d{1,2}(?:st|nd|rd|th|h)?\s+[A-Za-z]+\s+\d{2,4}|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            text, re.IGNORECASE
        )
        if date_match:
            dates_found["issue_date"] = date_match.group(1).strip()

    # 3. Fallback generic date
    if "issue_date" not in dates_found:
        generic = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', text, re.IGNORECASE)
        if generic:
            dates_found["issue_date"] = generic.group(1).strip()

    return dates_found


def _extract_credential_id(text: str) -> Optional[str]:
    """Extract credential ID, Certificate ID, or verification code."""
    patterns = [
        r'(?:Synctag|Certificate\s*ID|Credential\s*ID|Ref\s*No\.?|Certificate\s*No\.?|Reg\s*No\.?)[:\s]*([A-Za-z0-9\-_]{4,25})',
        r'ID\s*[:\-]\s*([A-Za-z0-9\-_]{4,20})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_skills(text: str) -> List[str]:
    """Extract verified skill keywords from text."""
    text_lower = text.lower()
    found = []
    
    sorted_keywords = sorted(SKILL_DATABASE.keys(), key=lambda x: len(x), reverse=True)
    
    for kw in sorted_keywords:
        skill_name = SKILL_DATABASE[kw]
        if len(kw) <= 2:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                if skill_name not in found:
                    found.append(skill_name)
        else:
            if kw in text_lower:
                if skill_name not in found:
                    found.append(skill_name)
                    
    return found


def _generate_summary(recipient_name: Optional[str],
                      organization: Optional[str],
                      institution: Optional[str],
                      program: Optional[str],
                      dates: Dict[str, Optional[str]],
                      skills: List[str]) -> str:
    """Create a human-friendly executive summary statement."""
    name_str = recipient_name or "The candidate"
    org_str = f" at {organization}" if organization else ""
    inst_str = f" from {institution}" if institution else ""
    prog_str = f" in {program}" if program else ""
    date_str = f" completed during {dates.get('duration') or dates.get('issue_date')}" if (dates.get('duration') or dates.get('issue_date')) else ""
    
    summary = f"{name_str}{inst_str} has successfully demonstrated achievement{prog_str}{org_str}{date_str}."
    
    if skills:
        top_skills = ", ".join(skills[:4])
        summary += f" Key competencies verified include {top_skills}."
        
    return summary
