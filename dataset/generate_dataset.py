"""
CertiNexus AI — Synthetic Certificate Dataset Generator

Generates a labeled dataset of synthetic certificate text samples
for multi-class text classification research.

Source: Synthetically generated for academic research
License: CC BY-SA 4.0
"""

import csv
import os
import random
import string
import uuid
from datetime import datetime, timedelta

# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42
SAMPLES_PER_CATEGORY = 55
OCR_NOISE_RATE = 0.15  # 15% of samples get OCR noise
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "certificates.csv")

random.seed(RANDOM_SEED)

# ============================================================
# Names, Organizations, and Template Data
# ============================================================

FIRST_NAMES = [
    "Akilesh", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Karthik", "Divya",
    "Arjun", "Meera", "Sanjay", "Kavitha", "Rohan", "Nithya", "Arun", "Lakshmi",
    "Deepak", "Swathi", "Naveen", "Pooja", "Suresh", "Harini", "Manoj", "Riya",
    "Ganesh", "Anjali", "Prasad", "Tanvi", "Venkat", "Shreya", "Ramesh", "Varsha",
    "Hari", "Madhavi", "Ashwin", "Shalini", "Rajesh", "Bhavana", "Mohan", "Keerthana",
    "Alex", "Sarah", "James", "Emily", "Michael", "Jennifer", "David", "Jessica",
    "Daniel", "Ashley", "William", "Amanda", "Christopher", "Stephanie", "Matthew", "Nicole"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Reddy", "Patel", "Nair", "Iyer", "Gupta", "Singh",
    "Rao", "Das", "Menon", "Verma", "Joshi", "Pillai", "Bhat", "Srinivasan",
    "Chatterjee", "Mukherjee", "Banerjee", "Agarwal", "Johnson", "Williams",
    "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson"
]

UNIVERSITIES = [
    "Indian Institute of Technology Madras", "Anna University",
    "VIT University", "SRM Institute of Science and Technology",
    "National Institute of Technology Trichy", "PSG College of Technology",
    "Amrita Vishwa Vidyapeetham", "BITS Pilani", "IIIT Hyderabad",
    "Manipal Institute of Technology", "SSN College of Engineering",
    "Coimbatore Institute of Technology", "Bharathiar University",
    "Madras Christian College", "Loyola College Chennai",
    "College of Engineering Guindy", "Thiagarajar College of Engineering",
    "Kongu Engineering College", "Kumaraguru College of Technology",
    "Sri Krishna College of Technology"
]

TECH_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Infosys", "TCS", "Wipro", "Zoho",
    "Freshworks", "HCL Technologies", "Cognizant", "IBM", "Oracle",
    "SAP Labs", "Adobe", "Cisco", "Intel", "Samsung", "Accenture",
    "Capgemini", "Tech Mahindra", "Mindtree", "Mphasis", "LTI",
    "Hexaware", "Persistent Systems", "PayPal", "Goldman Sachs",
    "JPMorgan Chase", "Deloitte", "KPMG"
]

TECH_ORGANIZATIONS = [
    "IEEE Computer Society", "ACM Student Chapter", "Google Developer Groups",
    "Microsoft Learn Student Ambassadors", "AWS Community",
    "GitHub Education", "Mozilla Developer Network", "Linux Foundation",
    "Apache Software Foundation", "NASSCOM", "CII", "FICCI",
    "Indian Society for Technical Education", "Computer Society of India",
    "Institution of Engineers India", "National Service Scheme",
    "Rotary Club", "Lions Club", "Red Cross Society", "UNICEF India"
]

PROGRAMMING_TOPICS = [
    "Python Programming", "Java Development", "Web Development",
    "Machine Learning", "Artificial Intelligence", "Data Science",
    "Cloud Computing", "DevOps", "Cybersecurity", "Blockchain",
    "Mobile App Development", "Full Stack Development",
    "React.js", "Node.js", "Deep Learning", "Natural Language Processing",
    "Computer Vision", "Database Management", "Software Engineering",
    "Agile Methodologies", "Microservices Architecture", "API Development",
    "Data Structures and Algorithms", "Internet of Things",
    "Augmented Reality", "Flutter Development", "Kubernetes",
    "Docker Containerization", "Big Data Analytics", "Ethical Hacking"
]

CERTIFICATIONS = [
    "AWS Certified Cloud Practitioner", "Google Cloud Associate Engineer",
    "Microsoft Azure Fundamentals AZ-900", "Oracle Certified Java Programmer",
    "Cisco Certified Network Associate", "CompTIA Security+",
    "Certified Kubernetes Administrator", "TensorFlow Developer Certificate",
    "Google Data Analytics Professional", "IBM Data Science Professional",
    "Meta Front-End Developer", "AWS Solutions Architect Associate",
    "Salesforce Administrator", "Scrum Master Certified",
    "PMP Project Management Professional", "ITIL Foundation",
    "Certified Ethical Hacker", "Red Hat Certified System Administrator",
    "MongoDB Certified Developer", "HashiCorp Terraform Associate"
]

SPORTS = [
    "Cricket", "Football", "Basketball", "Volleyball", "Badminton",
    "Table Tennis", "Athletics", "Swimming", "Chess", "Kabaddi",
    "Hockey", "Tennis", "Handball", "Carrom", "Throwball",
    "Marathon", "Cross Country Running", "Shot Put", "Long Jump", "Relay Race"
]

SPORTS_EVENTS = [
    "Inter-College Sports Tournament", "State Level Championship",
    "University Sports Meet", "Annual Athletic Meet",
    "Zonal Level Competition", "National Level Tournament",
    "District Sports Festival", "Inter-Department Sports Day",
    "All India University Games", "South Zone Tournament"
]

CULTURAL_EVENTS = [
    "Dance Competition", "Music Festival", "Drama Performance",
    "Art Exhibition", "Poetry Recitation", "Debate Competition",
    "Elocution Contest", "Fashion Show", "Photography Contest",
    "Film Making Competition", "Literary Festival", "Quiz Competition",
    "Singing Competition", "Mimicry Show", "Rangoli Competition",
    "Mehendi Competition", "Cooking Competition", "Stand-up Comedy"
]

CULTURAL_FESTIVALS = [
    "Techofes", "Pragyan", "Riviera", "Milan", "Festember",
    "Saarang", "Mood Indigo", "Antaragni", "Spring Fest", "Oasis",
    "Cultural Week", "Arts Festival", "Annual Day Celebration",
    "College Fest", "Inter-College Cultural Meet"
]

HACKATHON_NAMES = [
    "Smart India Hackathon", "HackWithInfy", "CodeAgon",
    "Hack the Mountain", "AngelHack", "MLH Hackathon",
    "Google Hash Code", "Facebook Hacker Cup", "Code for Good",
    "HackerEarth Challenge", "DevPost Hackathon", "Innovation Challenge",
    "Build for Bharat", "SIH Grand Finale", "Code4Change",
    "TechGig Code Gladiators", "Flipkart Grid", "Amazon HackOn",
    "Microsoft Imagine Cup", "IEEE Xtreme"
]

COMPETITION_NAMES = [
    "ACM ICPC", "Google Code Jam", "CodeChef Long Challenge",
    "Codeforces Round", "TopCoder Open", "LeetCode Weekly Contest",
    "HackerRank Challenge", "National Coding Championship",
    "Inter-College Programming Contest", "CodeVita",
    "TCS CodeVita", "Infosys HackWithInfy", "Wipro Elite Challenge",
    "Paper Presentation Competition", "Project Expo",
    "Technical Quiz", "Debugging Challenge", "Circuit Design Competition",
    "Robotics Challenge", "AI Innovation Challenge"
]

POSITIONS = ["First Place", "Second Place", "Third Place", "Runner Up",
             "Winner", "Merit Award", "Special Mention", "Best Innovation",
             "Best Performance", "Excellence Award"]

VOLUNTEER_CAUSES = [
    "Blood Donation Camp", "Tree Plantation Drive", "Beach Cleanup Campaign",
    "Rural Education Program", "Health Awareness Camp",
    "Digital Literacy Program", "Food Distribution Drive",
    "COVID-19 Relief Work", "Disaster Relief Operations",
    "Environmental Awareness Campaign", "Water Conservation Drive",
    "Women Empowerment Workshop", "Child Education Initiative",
    "Senior Citizen Support Program", "Animal Welfare Campaign",
    "Swachh Bharat Mission", "Cleanliness Drive",
    "Road Safety Awareness", "Anti-Drug Campaign", "Skill Development Camp"
]

SKILLS_BY_CATEGORY = {
    "Academic Achievement": ["Research", "Analysis", "Critical Thinking", "Academic Writing", "Problem Solving"],
    "Certification": ["Cloud Computing", "Networking", "Database", "Programming", "Security", "DevOps"],
    "Internship": ["Software Development", "Testing", "Teamwork", "Communication", "Project Management"],
    "Workshop": ["Hands-on Skills", "Technical Knowledge", "Collaboration", "Innovation"],
    "Hackathon": ["Coding", "Problem Solving", "Teamwork", "Innovation", "Rapid Prototyping"],
    "Technical Competition": ["Competitive Programming", "Algorithm Design", "Data Structures", "Debugging"],
    "Seminar": ["Knowledge Acquisition", "Networking", "Subject Expertise"],
    "Conference": ["Research", "Presentation", "Networking", "Paper Writing", "Academic Communication"],
    "Sports": ["Teamwork", "Leadership", "Discipline", "Physical Fitness", "Sportsmanship"],
    "Cultural Activity": ["Creativity", "Performance", "Artistic Skills", "Stage Presence", "Expression"],
    "Volunteer Activity": ["Social Responsibility", "Leadership", "Community Service", "Empathy", "Teamwork"]
}


# ============================================================
# Utility Functions
# ============================================================

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_date(start_year=2020, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    d = start + timedelta(days=random_days)
    formats = ["%d %B %Y", "%B %d, %Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]
    return d.strftime(random.choice(formats))

def random_cert_id():
    prefix = random.choice(["CERT", "CRT", "DOC", "REF", "ID", "NO"])
    num = random.randint(1000, 99999)
    suffix = ''.join(random.choices(string.ascii_uppercase, k=random.randint(0, 3)))
    sep = random.choice(["-", "/", ""])
    return f"{prefix}{sep}{num}{suffix}"

def random_duration():
    units = random.choice(["days", "weeks", "months"])
    if units == "days":
        return f"{random.randint(1, 5)} days"
    elif units == "weeks":
        return f"{random.randint(1, 12)} weeks"
    else:
        return f"{random.randint(1, 6)} months"

def add_ocr_noise(text, noise_rate=0.03):
    """Simulate OCR artifacts: char swaps, deletions, extra spaces."""
    chars = list(text)
    result = []
    for c in chars:
        r = random.random()
        if r < noise_rate * 0.4:
            # Character swap
            if c.isalpha():
                swaps = {'a': 'o', 'e': 'c', 'i': 'l', 'o': '0', 'l': '1',
                         'n': 'ri', 'm': 'rn', 'h': 'b', 'r': 'n', 'c': 'e',
                         'O': '0', 'I': '1', 'S': '5', 'B': '8'}
                result.append(swaps.get(c, c))
            else:
                result.append(c)
        elif r < noise_rate * 0.6:
            # Extra space
            result.append(c)
            result.append(' ')
        elif r < noise_rate * 0.8:
            # Skip character (deletion)
            pass
        else:
            result.append(c)
    return ''.join(result)


# ============================================================
# Category Template Generators
# ============================================================

def gen_academic_achievement():
    name = random_name()
    org = random.choice(UNIVERSITIES)
    date = random_date()

    templates = [
        f"This is to certify that {name} has achieved outstanding academic performance and is awarded the Certificate of Academic Excellence by {org}. Date: {date}. The student has demonstrated exceptional skills in coursework and examination. Certificate ID: {random_cert_id()}",

        f"Certificate of Merit. {org} hereby certifies that {name} has secured First Class with Distinction in the semester examinations held during the academic year. The student is recognized for outstanding academic achievement. Issued on {date}.",

        f"ACADEMIC ACHIEVEMENT AWARD. Awarded to {name} for securing the highest marks in the Department of Computer Science at {org}. This certificate is presented in recognition of academic excellence and scholarly dedication. Date of Issue: {date}. Ref: {random_cert_id()}",

        f"Dean's List Certificate. {name} is hereby placed on the Dean's List for the academic semester at {org} in recognition of exceptional academic performance and maintaining a GPA above 9.0 out of 10.0. {date}",

        f"This certificate is awarded to {name} for achieving the Best Outgoing Student Award from the Department of Information Technology, {org}. The student has shown outstanding performance in academics, research, and extracurricular activities throughout their program. Dated: {date}",

        f"CERTIFICATE OF ACADEMIC EXCELLENCE. {org}. This is to certify that {name} has been awarded a Gold Medal for securing the highest aggregate marks in the B.Tech Computer Science and Engineering program. Convocation held on {date}. Registration No: {random_cert_id()}",

        f"To Whom It May Concern. This is to certify that {name}, a student of {org}, has successfully completed the Honours Program in Data Science with a grade of A+. The student has demonstrated exceptional analytical and research capabilities. Issued on: {date}",

        f"SCHOLARSHIP CERTIFICATE. {name} has been awarded the Merit Scholarship for Academic Excellence by {org} for maintaining an outstanding academic record. The scholarship covers tuition and academic fees. Academic Year 2024-2025. Certificate No: {random_cert_id()}. Date: {date}",

        f"This certificate is proudly presented to {name} for achieving Rank 1 in the university examinations conducted by {org}. The student has exhibited remarkable dedication to academic pursuits and intellectual growth. {date}",

        f"Certificate of Achievement. {org} recognizes {name} for outstanding performance in the final year research project titled 'Machine Learning Applications in Healthcare'. Grade: Outstanding. Supervisor commendation received. Date: {date}. Project ID: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": "Academic Achievement Certificate",
        "event": "Academic Examinations",
        "text": text
    }


def gen_certification():
    name = random_name()
    cert_name = random.choice(CERTIFICATIONS)
    org = random.choice(TECH_COMPANIES + ["Coursera", "Udemy", "edX", "LinkedIn Learning", "Pluralsight", "Udacity"])
    date = random_date()

    templates = [
        f"This certifies that {name} has successfully completed the {cert_name} certification program offered by {org}. The candidate has demonstrated proficiency in all required domains and passed the certification examination. Certificate ID: {random_cert_id()}. Date of certification: {date}. This credential is valid for 3 years.",

        f"PROFESSIONAL CERTIFICATION. {org} hereby certifies that {name} has earned the {cert_name} credential. Examination Score: {random.randint(750, 950)}/1000. Certification Date: {date}. Validation Code: {random_cert_id()}. Verify at {org.lower().replace(' ', '')}.com/verify",

        f"Certificate of Completion. {name} has successfully completed the {cert_name} course on {org}. Duration: {random_duration()}. Modules completed: {random.randint(8, 20)}. Final assessment score: {random.randint(80, 100)}%. Issued: {date}. Certificate No: {random_cert_id()}",

        f"VERIFIED CERTIFICATE. This is to confirm that {name} has passed the {cert_name} examination and is certified by {org}. The certification validates expertise in the relevant domain and demonstrates commitment to professional development. Issue Date: {date}",

        f"{org} Learning Platform. CERTIFICATE OF ACHIEVEMENT. This certificate is awarded to {name} for completing the {cert_name} Professional Certificate program. The learner has completed all required courses, hands-on labs, and assessments. Hours of learning: {random.randint(40, 200)}. Completed on: {date}",

        f"Digital Certificate. {name} is now a certified professional. Certification: {cert_name}. Issuing Organization: {org}. Exam passed on: {date}. Score: Pass. Badge earned. Credential ID: {random_cert_id()}. This certificate does not expire.",

        f"CONTINUING EDUCATION CERTIFICATE. {name} has earned {random.randint(20, 50)} Professional Development Units by completing the {cert_name} program at {org}. Areas covered include theoretical foundations and practical applications. Date: {date}",

        f"This document certifies that {name} has met all requirements for the {cert_name} credential as administered by {org}. The certification process included written examination, practical assessment, and project submission. Certified on {date}. ID: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": cert_name,
        "event": "Certification Examination",
        "text": text
    }


def gen_internship():
    name = random_name()
    company = random.choice(TECH_COMPANIES)
    role = random.choice([
        "Software Development Intern", "Data Science Intern", "Machine Learning Intern",
        "Web Development Intern", "Backend Development Intern", "Frontend Development Intern",
        "Mobile App Development Intern", "Cloud Engineering Intern", "DevOps Intern",
        "Quality Assurance Intern", "UI/UX Design Intern", "Product Management Intern",
        "Research Intern", "AI Engineering Intern", "Full Stack Development Intern"
    ])
    date = random_date()
    duration = random_duration()

    templates = [
        f"INTERNSHIP COMPLETION CERTIFICATE. This is to certify that {name} has successfully completed an internship at {company} as a {role}. Duration: {duration}. During the internship, the candidate worked on real-world projects and demonstrated strong technical skills and professional conduct. Date: {date}. HR Reference: {random_cert_id()}",

        f"Certificate of Internship. {company} hereby certifies that {name} served as a {role} from the period of {duration}. The intern contributed to the development team and successfully delivered assigned project milestones. Performance rating: Excellent. Issued on {date}.",

        f"TO WHOM IT MAY CONCERN. This is to certify that {name} was employed as a {role} at {company} for a duration of {duration}. The intern demonstrated competence in software development practices, collaborative teamwork, and technical problem-solving. We wish them success in future endeavors. Date: {date}. Employee ID: {random_cert_id()}",

        f"LETTER OF COMPLETION. {name} has completed the {role} program at {company}. Duration: {duration}. Project: {random.choice(['E-Commerce Platform', 'Customer Analytics Dashboard', 'API Gateway Service', 'Mobile Application', 'Cloud Migration Tool', 'Data Pipeline Framework'])}. Technologies used: Python, JavaScript, SQL, Cloud Services. Manager signature included. Date: {date}",

        f"SUMMER INTERNSHIP CERTIFICATE. {company}. We are pleased to certify that {name} has undergone industrial training as a {role} at our organization for {duration}. The training was conducted under the supervision of senior engineers and the intern performed satisfactorily. Certificate No: {random_cert_id()}. Date: {date}",

        f"This certificate is awarded to {name} for successful completion of the {role} internship program at {company}. The intern worked for {duration} and gained hands-on experience in software engineering, agile development, and deployment processes. The work was of high quality and met professional standards. Signed by the Engineering Director. {date}",

        f"INTERNSHIP EXPERIENCE LETTER. {company}. {name} worked with us as a {role} for {duration}. Key responsibilities included coding, testing, documentation, and participation in sprint planning. The intern showed dedication and strong learning ability. Recommendation: Strong. Date of issue: {date}",

        f"Industrial Training Certificate. This certifies that {name} has completed industrial training at {company} in the capacity of {role}. Training duration: {duration}. The candidate demonstrated satisfactory performance and professional ethics. Grade: A. Issued: {date}. Reference: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": company, "date": date,
        "title": f"{role} - {company}",
        "event": "Internship",
        "text": text
    }


def gen_workshop():
    name = random_name()
    topic = random.choice(PROGRAMMING_TOPICS)
    org = random.choice(UNIVERSITIES + TECH_ORGANIZATIONS[:10])
    date = random_date()
    duration = random.choice(["1 day", "2 days", "3 days", "5 days", "1 week"])

    templates = [
        f"Certificate of Participation. This is to certify that {name} has successfully participated in the workshop on {topic} organized by {org}. Duration: {duration}. The workshop covered theoretical concepts and hands-on exercises. Date: {date}. Certificate ID: {random_cert_id()}",

        f"WORKSHOP COMPLETION CERTIFICATE. {org} certifies that {name} has completed the {duration} hands-on workshop on {topic}. The participant demonstrated practical understanding and completed all assigned exercises. Issued on {date}.",

        f"We hereby certify that {name} attended the workshop titled '{topic}: From Theory to Practice' conducted by {org} on {date}. The workshop spanned {duration} and included lectures, demonstrations, and lab sessions. Certificate No: {random_cert_id()}",

        f"HANDS-ON TRAINING WORKSHOP. Certificate awarded to {name} for active participation in the {topic} workshop organized by the Department of Computer Science, {org}. Duration: {duration}. Topics covered: Introduction, Core Concepts, Advanced Techniques, Real-world Applications. Date: {date}",

        f"This certificate is presented to {name} for attending the Faculty Development Programme and Workshop on {topic} held at {org}. The {duration} program covered latest trends and practical implementation strategies. Resource persons from industry and academia contributed. {date}",

        f"TECHNICAL WORKSHOP CERTIFICATE. {name} successfully participated in the {topic} bootcamp organized by {org}. The {duration} intensive training included project-based learning and assessment. Final project submitted and evaluated. Score: {random.randint(70, 100)}/100. Date: {date}",

        f"Certificate of Attendance. {org} conducted a workshop on {topic} on {date}. This certificate confirms that {name} attended all sessions spanning {duration}. The workshop provided comprehensive training in both theoretical foundations and practical applications.",

        f"SHORT TERM TRAINING PROGRAM. {org} certifies that {name} has completed the Short Term Training Program on {topic}. Duration: {duration}. The program included expert lectures, lab sessions, and mini-project development. Attendance: 100%. Issued: {date}. Ref: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": f"Workshop on {topic}",
        "event": f"Workshop: {topic}",
        "text": text
    }


def gen_hackathon():
    name = random_name()
    hackathon = random.choice(HACKATHON_NAMES)
    org = random.choice(UNIVERSITIES[:10] + TECH_COMPANIES[:10] + TECH_ORGANIZATIONS[:5])
    date = random_date()
    position = random.choice(POSITIONS + ["Participant"] * 5)
    duration = random.choice(["24 hours", "36 hours", "48 hours", "3 days"])

    templates = [
        f"This certificate is awarded to {name} for successfully participating in the {hackathon} organized by {org}. The hackathon was held on {date} and lasted {duration}. The participant demonstrated innovative problem-solving and coding skills. Position: {position}. Certificate ID: {random_cert_id()}",

        f"HACKATHON CERTIFICATE. {hackathon}. {org} certifies that {name} participated in the {duration} hackathon challenge and developed a working prototype addressing the problem statement. Theme: {random.choice(['Healthcare', 'Education', 'Sustainability', 'FinTech', 'Smart City', 'Agriculture'])}. Date: {date}. Achievement: {position}",

        f"Certificate of Achievement. {name} and team are recognized for their participation in {hackathon}. Organized by {org} on {date}. Duration: {duration}. The team built an innovative solution using modern technology stack. Standing: {position}. Team Size: {random.randint(2, 5)} members.",

        f"NATIONAL LEVEL HACKATHON CERTIFICATE. {hackathon} organized by {org}. This certificate is proudly presented to {name} for outstanding coding performance and innovative thinking during the {duration} hackathon competition. The participant worked on real-world challenges and presented a functional solution. {position}. Date: {date}",

        f"We certify that {name} participated in {hackathon} conducted by {org}. This was a {duration} competitive coding and innovation challenge where participants built solutions from scratch. The event promoted creativity, teamwork, and rapid development. Position secured: {position}. Date: {date}. ID: {random_cert_id()}",

        f"CODING HACKATHON ACHIEVEMENT. {hackathon}. Certificate for {name}. Organized at {org} on {date}. Challenge type: Build and deploy a working application in {duration}. Technologies used: Python, JavaScript, APIs, Cloud. Result: {position}. Judge panel commendation received.",

        f"{hackathon} Certificate of Participation. {name} is commended for participating in the coding hackathon organized by {org}. The hackathon brought together talented developers to solve pressing challenges through technology and innovation. Duration: {duration}. Date: {date}. Ref: {random_cert_id()}",

        f"HACKATHON WINNER CERTIFICATE. This is to certify that {name} secured {position} at {hackathon} organized by {org} on {date}. The {duration} intensive competition tested skills in problem analysis, solution design, coding, and presentation. Prize category: Best Technical Implementation."
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": hackathon,
        "event": hackathon,
        "text": text
    }


def gen_technical_competition():
    name = random_name()
    competition = random.choice(COMPETITION_NAMES)
    org = random.choice(UNIVERSITIES[:10] + TECH_COMPANIES[:5] + TECH_ORGANIZATIONS[:5])
    date = random_date()
    position = random.choice(POSITIONS + ["Participant"] * 4)

    templates = [
        f"Certificate of Participation. This is to certify that {name} participated in {competition} organized by {org} held on {date}. The competition tested skills in algorithms, data structures, and problem solving. Position: {position}. Certificate No: {random_cert_id()}",

        f"TECHNICAL COMPETITION CERTIFICATE. {competition}. {org} certifies that {name} competed in the technical competition and demonstrated strong analytical and programming skills. Round cleared: {random.choice(['Preliminary', 'Semi-Final', 'Final'])}. Result: {position}. Date: {date}",

        f"{name} is hereby awarded this certificate for participation in {competition} conducted by {org}. The contest challenged participants with complex algorithmic problems requiring efficient solutions within time constraints. Standing: {position}. Contest Date: {date}",

        f"CODING COMPETITION CERTIFICATE. {competition} organized by {org}. Participant: {name}. Problems solved: {random.randint(2, 8)} out of {random.randint(5, 10)}. Rank: {random.randint(1, 500)} out of {random.randint(500, 5000)} participants. Date: {date}. Achievement: {position}",

        f"This certificate recognizes {name} for excellence in {competition} organized by {org} on {date}. The competition involved multiple rounds of technical challenges including coding, debugging, and system design. Final standing: {position}. Certificate ID: {random_cert_id()}",

        f"INTER-COLLEGE TECHNICAL COMPETITION. {competition}. Certificate awarded to {name} from {random.choice(UNIVERSITIES)} for participating in the competition hosted by {org}. Event type: Technical. Category: Programming. Level: College/University. Result: {position}. Date: {date}",

        f"Certificate of Merit. {name} demonstrated exceptional technical prowess in {competition} organized by {org}. The contest featured challenging problems in computer science and software engineering. Achievement: {position}. Date of competition: {date}. Ref: {random_cert_id()}",

        f"NATIONAL LEVEL TECHNICAL CONTEST. {competition}. This certifies that {name} represented their institution at the national level competition organized by {org}. The event tested algorithmic thinking, coding speed, and accuracy. Result: {position}. {date}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": competition,
        "event": competition,
        "text": text
    }


def gen_seminar():
    name = random_name()
    topic = random.choice(PROGRAMMING_TOPICS + [
        "Quantum Computing", "5G Technology", "Edge Computing",
        "Green Computing", "Sustainable Technology", "Digital Transformation",
        "Industry 4.0", "Metaverse Technologies", "Generative AI",
        "Responsible AI", "Tech Ethics", "Future of Work"
    ])
    org = random.choice(UNIVERSITIES + TECH_ORGANIZATIONS[:10])
    speaker = random_name()
    date = random_date()

    templates = [
        f"Certificate of Attendance. This is to certify that {name} attended the seminar on '{topic}' organized by {org} on {date}. The seminar was delivered by {speaker} and covered recent advancements and future directions in the field. Certificate ID: {random_cert_id()}",

        f"SEMINAR ATTENDANCE CERTIFICATE. {org} certifies that {name} attended the guest lecture and seminar on {topic} held on {date}. Speaker: {speaker}. Duration: {random.choice(['2 hours', '3 hours', 'half day'])}. The session provided insights into current trends and research.",

        f"This certifies that {name} attended the technical seminar titled '{topic}: Current Trends and Future Prospects' conducted by {org}. The seminar featured industry expert {speaker} and covered topics of current relevance. Date: {date}",

        f"GUEST LECTURE CERTIFICATE. {name} attended the guest lecture on {topic} delivered by {speaker} at {org} on {date}. The lecture covered foundational concepts and state-of-the-art developments. Organized by the Department of Computer Science.",

        f"Certificate of Participation. Seminar on {topic}. Participant: {name}. Venue: {org}. Date: {date}. Keynote Speaker: {speaker}. The seminar explored theoretical underpinnings and practical applications of the subject. Ref: {random_cert_id()}",

        f"NATIONAL SEMINAR CERTIFICATE. {org} organized a National Level Seminar on {topic} on {date}. This certificate is issued to {name} for attending all sessions of the seminar. Eminent speakers from academia and industry shared their expertise. Chief Guest: {speaker}.",

        f"Webinar Attendance Certificate. This certificate confirms that {name} attended the online seminar on {topic} organized by {org}. Date: {date}. Duration: {random.choice(['1 hour', '2 hours', '90 minutes'])}. The webinar featured interactive sessions and Q&A with speaker {speaker}.",

        f"INVITED TALK CERTIFICATE. {name} is certified to have attended the invited talk on {topic} by {speaker} organized by {org}. The talk discussed emerging trends, challenges, and opportunities in the field. {date}. No: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": f"Seminar on {topic}",
        "event": f"Seminar: {topic}",
        "text": text
    }


def gen_conference():
    name = random_name()
    conf_names = [
        "International Conference on Machine Learning and Applications",
        "National Conference on Information Technology",
        "IEEE International Conference on Computing and Communication",
        "ACM Conference on Software Engineering",
        "International Conference on Artificial Intelligence",
        "National Symposium on Data Science",
        "International Conference on Cloud Computing and Big Data",
        "Conference on Advances in Computer Vision",
        "National Conference on Cyber Security",
        "International Symposium on Internet of Things",
        "Conference on Natural Language Processing",
        "National Conference on Software Systems"
    ]
    conf = random.choice(conf_names)
    org = random.choice(UNIVERSITIES + TECH_ORGANIZATIONS[:5])
    date = random_date()
    paper_topic = random.choice(PROGRAMMING_TOPICS)

    templates = [
        f"Certificate of Participation. This certifies that {name} participated in the {conf} organized by {org} held on {date}. The conference featured paper presentations, keynote addresses, and panel discussions on emerging technologies. Certificate No: {random_cert_id()}",

        f"CONFERENCE PRESENTATION CERTIFICATE. {conf}. This is to certify that {name} presented a paper titled 'Advances in {paper_topic}' at the conference organized by {org} on {date}. The paper was reviewed and accepted by the technical program committee. Paper ID: {random_cert_id()}",

        f"Certificate of Paper Presentation. {name} presented research work on the topic of {paper_topic} at {conf} organized by {org}. The presentation was well received by the academic community. Conference Date: {date}. Session: Technical Track {random.randint(1, 5)}.",

        f"ACADEMIC CONFERENCE CERTIFICATE. {conf} hosted by {org}. Participant: {name}. Role: {random.choice(['Paper Presenter', 'Poster Presenter', 'Attendee', 'Session Chair'])}. Date: {date}. The conference brought together researchers and practitioners from across the country to discuss advances in technology.",

        f"This certificate is awarded to {name} for attending the {conf} held at {org} on {date}. The conference covered cutting-edge research in computer science and engineering. Total papers presented: {random.randint(50, 200)}. Keynote sessions: {random.randint(3, 8)}. Certificate ID: {random_cert_id()}",

        f"INTERNATIONAL CONFERENCE CERTIFICATE. {conf}. We certify that {name} attended the international conference organized by {org}. The conference was held on {date} with participation from researchers across the globe. Theme: Innovations in Computing.",

        f"Certificate of Publication. {name} has published a research paper in the proceedings of {conf} organized by {org}. Paper title: 'A Study on {paper_topic} using Machine Learning Approaches'. Published on: {date}. DOI: 10.{random.randint(1000, 9999)}/{random_cert_id().lower()}",

        f"SYMPOSIUM PARTICIPATION CERTIFICATE. {conf}. Organized by {org}. Date: {date}. This certificate acknowledges the participation of {name} in the national symposium. The event included invited talks, panel discussions, and poster presentations on recent developments."
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": conf,
        "event": conf,
        "text": text
    }


def gen_sports():
    name = random_name()
    sport = random.choice(SPORTS)
    event = random.choice(SPORTS_EVENTS)
    org = random.choice(UNIVERSITIES[:10])
    date = random_date()
    position = random.choice(POSITIONS[:5] + ["Participant"] * 5)

    templates = [
        f"SPORTS ACHIEVEMENT CERTIFICATE. This is to certify that {name} participated in {sport} at the {event} organized by {org}. Position secured: {position}. The tournament was held on {date}. Certificate No: {random_cert_id()}",

        f"Certificate of Sports Participation. {name} represented their department in {sport} at the {event} hosted by {org} on {date}. The player demonstrated excellent sportsmanship and athletic skills. Achievement: {position}.",

        f"{event}. Certificate awarded to {name} for outstanding performance in {sport}. Organized by {org}. The tournament featured teams from multiple institutions and departments. Result: {position}. Date: {date}. Ref: {random_cert_id()}",

        f"ATHLETIC ACHIEVEMENT CERTIFICATE. {org} Sports Committee certifies that {name} participated in the {sport} competition during the {event} on {date}. The event promoted physical fitness, teamwork, and healthy competition among students. Standing: {position}.",

        f"This certificate is presented to {name} for participation in {sport} at the {event} conducted by {org}. The student demonstrated dedication and skill throughout the tournament. Level: {random.choice(['Department', 'College', 'University', 'State', 'National'])}. Position: {position}. {date}",

        f"UNIVERSITY SPORTS CERTIFICATE. {org} awards this certificate to {name} for representing the institution in {sport} at the {event}. The athlete showed remarkable performance and competitive spirit. Result: {position}. Event Date: {date}. Player ID: {random_cert_id()}",

        f"Certificate of Achievement in Sports. Player: {name}. Sport: {sport}. Event: {event}. Venue: {org}. Date: {date}. Category: {random.choice(['Individual', 'Team'])}. Level: Inter-College. Result: {position}. Signed by: Sports Director.",

        f"ANNUAL SPORTS DAY CERTIFICATE. {org}. This certificate is awarded to {name} for participating in {sport} during the Annual Sports Day held on {date}. The event promoted athletic excellence and team spirit among students. Achievement: {position}."
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": f"{sport} - {event}",
        "event": event,
        "text": text
    }


def gen_cultural_activity():
    name = random_name()
    event = random.choice(CULTURAL_EVENTS)
    festival = random.choice(CULTURAL_FESTIVALS)
    org = random.choice(UNIVERSITIES[:10])
    date = random_date()
    position = random.choice(POSITIONS[:5] + ["Participant"] * 5)

    templates = [
        f"CULTURAL ACTIVITY CERTIFICATE. This is to certify that {name} participated in {event} at {festival} organized by {org}. The student demonstrated exceptional artistic talent and creativity. Position: {position}. Date: {date}. Certificate ID: {random_cert_id()}",

        f"Certificate of Participation. {name} participated in the {event} during {festival} held at {org} on {date}. The event showcased the artistic abilities and cultural talents of students from various departments. Achievement: {position}.",

        f"{festival}. {org}. Certificate of Achievement. Awarded to {name} for participation in {event}. The cultural event brought together talented performers and artists from across the institution. Standing: {position}. Date: {date}",

        f"PERFORMING ARTS CERTIFICATE. {name} is awarded this certificate for outstanding performance in {event} at {festival} conducted by {org}. The performance demonstrated creativity, dedication, and artistic expression. Category: Cultural. Date: {date}. Ref: {random_cert_id()}",

        f"INTER-COLLEGE CULTURAL FEST CERTIFICATE. {festival} organized by {org}. This certificate recognizes {name} for participation in {event}. The festival celebrated diversity in arts, culture, and creative expression. Result: {position}. Event Date: {date}",

        f"Certificate of Cultural Excellence. {name} participated in {event} at {festival}. Organized by {org} on {date}. The event featured participants from {random.randint(10, 50)} colleges. Category: {random.choice(['Solo', 'Group', 'Duo'])}. Achievement: {position}.",

        f"This certificate is presented to {name} in recognition of artistic contribution to {event} held during {festival} at {org}. The participant exhibited remarkable talent and stage presence. Judge remarks: Commendable performance. Date: {date}",

        f"COLLEGE FEST PARTICIPATION CERTIFICATE. {festival}. Event: {event}. Participant: {name}. College: {org}. Date: {date}. The annual cultural festival celebrated the artistic and creative spirit of students. Position: {position}. Certificate No: {random_cert_id()}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": f"{event} - {festival}",
        "event": festival,
        "text": text
    }


def gen_volunteer_activity():
    name = random_name()
    cause = random.choice(VOLUNTEER_CAUSES)
    org = random.choice(TECH_ORGANIZATIONS[10:] + UNIVERSITIES[:5] + [
        "National Service Scheme", "NSS Unit", "NCC Battalion",
        "Rotaract Club", "Leo Club", "Youth Red Cross"
    ])
    date = random_date()
    hours = random.randint(10, 200)

    templates = [
        f"VOLUNTEER SERVICE CERTIFICATE. This is to certify that {name} volunteered for the {cause} organized by {org}. The volunteer contributed {hours} hours of service. Date: {date}. The volunteer demonstrated exceptional commitment to community service. Certificate ID: {random_cert_id()}",

        f"Certificate of Volunteering. {org} certifies that {name} served as a volunteer for the {cause} conducted on {date}. The volunteer helped in organizing, coordinating, and executing the event. Hours contributed: {hours}. Ref: {random_cert_id()}",

        f"COMMUNITY SERVICE CERTIFICATE. {name} is recognized for selfless volunteer service during the {cause} organized by {org}. The event served {random.randint(50, 500)} beneficiaries. Duration of service: {hours} hours. Date: {date}. Commendation: Exemplary service.",

        f"SOCIAL SERVICE CERTIFICATE. Awarded to {name} for participating in the {cause} conducted by {org} on {date}. The volunteer actively participated in planning and execution. This certificate acknowledges the spirit of social responsibility. Hours: {hours}.",

        f"NSS/NCC CERTIFICATE. This certifies that {name} has actively participated in the {cause} organized by {org}. The activity was part of the community outreach program aimed at social welfare. Service hours: {hours}. Date: {date}. Unit: {random_cert_id()}",

        f"Certificate of Appreciation. {org} appreciates the voluntary service of {name} during the {cause}. The volunteer played a key role in the success of the initiative. Impact: {random.choice(['Significant', 'High', 'Notable'])}. Date: {date}.",

        f"HUMANITARIAN SERVICE CERTIFICATE. {name} contributed to the {cause} organized by {org}. This certificate recognizes the volunteer's commitment to making a positive impact on society. Service period: {hours} hours. Issued on: {date}. Certificate No: {random_cert_id()}",

        f"OUTREACH PROGRAM CERTIFICATE. {org} conducted a {cause} event. Volunteer: {name}. Role: {random.choice(['Coordinator', 'Volunteer', 'Team Lead', 'Field Worker'])}. The event was aimed at community welfare and social upliftment. Hours: {hours}. Date: {date}"
    ]

    text = random.choice(templates)
    return {
        "name": name, "org": org, "date": date,
        "title": cause,
        "event": cause,
        "text": text
    }


# ============================================================
# Category Generator Mapping
# ============================================================

CATEGORY_GENERATORS = {
    "Academic Achievement": gen_academic_achievement,
    "Certification": gen_certification,
    "Internship": gen_internship,
    "Workshop": gen_workshop,
    "Hackathon": gen_hackathon,
    "Technical Competition": gen_technical_competition,
    "Seminar": gen_seminar,
    "Conference": gen_conference,
    "Sports": gen_sports,
    "Cultural Activity": gen_cultural_activity,
    "Volunteer Activity": gen_volunteer_activity,
}


# ============================================================
# Main Dataset Generation
# ============================================================

def generate_dataset(samples_per_category=SAMPLES_PER_CATEGORY, noise_rate=OCR_NOISE_RATE):
    """Generate the full synthetic certificate dataset."""
    records = []

    for category, generator in CATEGORY_GENERATORS.items():
        for i in range(samples_per_category):
            sample = generator()
            raw_text = sample["text"]

            # Apply OCR noise to a fraction of samples
            if random.random() < noise_rate:
                raw_text = add_ocr_noise(raw_text)

            record = {
                "document_id": str(uuid.uuid4())[:12],
                "raw_text": raw_text,
                "clean_text": "",  # Will be filled by preprocessing
                "certificate_title": sample["title"],
                "organization": sample["org"],
                "event": sample["event"],
                "date": sample["date"],
                "category": category,
                "source": "synthetic_v1"
            }
            records.append(record)

    # Shuffle
    random.shuffle(records)
    return records


def save_dataset(records, output_file=OUTPUT_FILE):
    """Save the dataset to CSV."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    fieldnames = [
        "document_id", "raw_text", "clean_text", "certificate_title",
        "organization", "event", "date", "category", "source"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Dataset saved to {output_file}")
    print(f"Total samples: {len(records)}")

    # Print category distribution
    from collections import Counter
    cat_counts = Counter(r["category"] for r in records)
    print("\nCategory Distribution:")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    print("=" * 60)
    print("CertiNexus AI — Synthetic Dataset Generator")
    print("=" * 60)

    records = generate_dataset()
    save_dataset(records)

    print("\n✓ Dataset generation complete!")
    print(f"  Samples per category: {SAMPLES_PER_CATEGORY}")
    print(f"  Total categories: {len(CATEGORY_GENERATORS)}")
    print(f"  OCR noise rate: {OCR_NOISE_RATE * 100}%")
    print(f"  Random seed: {RANDOM_SEED}")
