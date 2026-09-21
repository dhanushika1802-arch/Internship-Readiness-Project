import re
import os
from pypdf import PdfReader

# Core skills dictionary for parsing
SKILL_KEYWORDS = {
    'Python': ['python', 'py', 'pandas', 'numpy', 'scipy', 'django', 'flask', 'fastapi'],
    'Java': ['java', 'spring', 'springboot', 'maven', 'hibernate'],
    'SQL': ['sql', 'sqlite', 'mysql', 'postgresql', 'oracle', 'nosql', 'mongodb', 'queries'],
    'AI/ML': ['machine learning', 'ml', 'deep learning', 'dl', 'ai', 'artificial intelligence', 'pytorch', 'tensorflow', 'scikit-learn', 'keras', 'nlp', 'computer vision'],
    'Web Development': ['html', 'css', 'javascript', 'js', 'react', 'react.js', 'node.js', 'nodejs', 'express', 'angular', 'vue', 'bootstrap', 'jquery', 'frontend', 'backend', 'fullstack'],
    'Cyber Security': ['cybersecurity', 'cyber security', 'network security', 'cryptography', 'firewall', 'wireshark', 'linux', 'penetration testing', 'ethical hacking', 'metasploit']
}

ROLE_BENCHMARKS = {
    'Data Analyst': {
        'required_skills': ['SQL', 'Python', 'Web Development'],
        'targets': {'SQL': 80, 'Python': 70, 'Web Development': 65}
    },
    'Data Scientist': {
        'required_skills': ['Python', 'SQL', 'AI/ML'],
        'targets': {'Python': 85, 'AI/ML': 80, 'SQL': 75}
    },
    'AI Engineer': {
        'required_skills': ['AI/ML', 'Python', 'SQL'],
        'targets': {'AI/ML': 85, 'Python': 80, 'SQL': 70}
    },
    'Software Developer': {
        'required_skills': ['Java', 'Python', 'SQL'],
        'targets': {'Java': 80, 'Python': 75, 'SQL': 70}
    },
    'Full Stack Developer': {
        'required_skills': ['Web Development', 'SQL', 'Python', 'Java'],
        'targets': {'Web Development': 85, 'SQL': 75, 'Python': 70, 'Java': 65}
    },
    'Cyber Security Analyst': {
        'required_skills': ['Cyber Security', 'Python', 'SQL', 'Java'],
        'targets': {'Cyber Security': 85, 'Python': 70, 'SQL': 70, 'Java': 65}
    }
}

ROLE_REQUIREMENTS = {
    role: data['required_skills'] for role, data in ROLE_BENCHMARKS.items()
}

def parse_resume_from_pdf(pdf_path):
    """
    Extracts text from a PDF resume and parses skills, education, projects, and certifications.
    """
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        # Fallback to reading as text if file is not binary-encrypted or if it's plain text
        try:
            with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception as e2:
            print(f"Text fallback failed: {e2}")
            return None

    return parse_resume_text(text)

def parse_resume_text(text):
    """
    NLP/Regex parsing logic to extract details from raw resume text.
    Computes deterministic competency score for each detected skill based on resume depth.
    """
    text_lower = text.lower()
    
    # 1. Extract Education first (used for context)
    education = "High School / Undergraduate"
    edu_patterns = [
        (r'(bachelor|b\.s\.|b\.e\.|b\.tech|undergraduate|degree in)\b', 'Bachelor of Science / Technology'),
        (r'(master|m\.s\.|m\.e\.|m\.tech|graduate)\b', 'Master of Science / Technology'),
        (r'(phd|doctorate)\b', 'Doctor of Philosophy (PhD)'),
        (r'(computer science|information technology|software engineering)\b', 'CS / IT Major')
    ]
    detected_edus = []
    for pattern, label in edu_patterns:
        if re.search(pattern, text_lower):
            detected_edus.append(label)
    if detected_edus:
        education = " & ".join(list(set(detected_edus))[:2])

    # 2. Extract Projects
    projects = []
    project_sections = re.split(r'\b(projects|experience|work history|personal projects)\b', text_lower)
    if len(project_sections) > 2:
        proj_text = project_sections[2][:1000]
        bullets = re.findall(r'(?:•|-|\*|\d\.)\s*([^\n\r]+)', proj_text)
        projects = [b.strip()[:100] for b in bullets if len(b.strip()) > 10][:4]
    
    if not projects:
        keywords = ["app", "website", "model", "system", "analyzer", "detector", "bot", "classifier", "dashboard"]
        for line in text.split("\n"):
            line_clean = line.strip()
            if any(kw in line_clean.lower() for kw in keywords) and 15 < len(line_clean) < 80:
                projects.append(line_clean)
            if len(projects) >= 3:
                break
    
    if not projects:
        projects = ["Personal Project Portfolio"]

    # 3. Extract Certifications
    certifications = []
    cert_keywords = ["certified", "certification", "aws", "coursera", "udemy", "azure", "google cloud", "comptia", "cisco", "ccna"]
    for line in text.split("\n"):
        line_clean = line.strip()
        if any(kw in line_clean.lower() for kw in cert_keywords) and 10 < len(line_clean) < 100:
            if not any(stop in line_clean.lower() for stop in ["required", "job", "responsibilities"]):
                certifications.append(line_clean)
        if len(certifications) >= 4:
            break
            
    if not certifications:
        certifications = ["Self-paced learning certificates"]

    # 4. Extract Skills and calculate evidence-based proficiency score (45% - 75%)
    extracted_skills_with_scores = {}
    for skill_name, keywords in SKILL_KEYWORDS.items():
        found = False
        occurrences = 0
        in_projects = False
        in_certs = False

        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                found = True
                occurrences += matches
                for p in projects:
                    if kw in p.lower():
                        in_projects = True
                for c in certifications:
                    if kw in c.lower():
                        in_certs = True

        if found:
            # Deterministic calculation based on resume evidence (no static 60% or random values):
            # Base mention in resume: 45%
            # Applied in verified projects/experience: +15%
            # Verified with certifications/coursework: +10%
            # Frequency of mentions (occurrences >= 3): +5%
            score = 45
            if in_projects:
                score += 15
            if in_certs:
                score += 10
            if occurrences >= 3:
                score += 5
            score = min(score, 75)
            extracted_skills_with_scores[skill_name] = score

    # Calculate Resume Quality Score based on formatting and content completeness
    quality_score = 40
    if len(extracted_skills_with_scores) >= 2: quality_score += 15
    if len(projects) >= 2: quality_score += 15
    if len(certifications) >= 1: quality_score += 15
    if len(text) > 500: quality_score += 15
    quality_score = min(quality_score, 100)

    return {
        "skills": list(extracted_skills_with_scores.keys()),
        "skill_scores": extracted_skills_with_scores,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "resume_quality": quality_score
    }

def calculate_readiness_score(skills, projects, certifications, resume_quality, assessment_scores):
    """
    Calculates overall score out of 100 and assigns readiness levels:
    0-40 Beginner, 41-70 Developing, 71-90 Internship Ready, 91-100 Industry Ready
    """
    # 1. Assessment Scores (35% weight)
    if assessment_scores:
        avg_assessment = sum(assessment_scores.values()) / len(assessment_scores)
    else:
        avg_assessment = 30  # Baseline when no assessment taken

    # 2. Skill Competency (25% weight)
    if skills:
        avg_skill = sum(skills.values()) / len(skills)
    else:
        avg_skill = 0

    # 3. Practical Experience (25% weight)
    projects_count = len(projects)
    project_score = min(projects_count * 25, 100)

    # 4. Resume Quality & Certifications (15% weight)
    cert_bonus = min(len(certifications) * 10, 20)
    resume_score = min(resume_quality + cert_bonus, 100)

    # Weighted calculation
    overall_score = round(
        (avg_assessment * 0.35) + 
        (avg_skill * 0.25) + 
        (project_score * 0.25) + 
        (resume_score * 0.15)
    )
    overall_score = max(0, min(overall_score, 100))

    # Determine readiness level
    if overall_score <= 40:
        level = "Beginner"
    elif overall_score <= 70:
        level = "Developing"
    elif overall_score <= 90:
        level = "Internship Ready"
    else:
        level = "Industry Ready"

    # Compile strengths & weaknesses
    strengths = []
    weaknesses = []

    if avg_assessment >= 75:
        strengths.append("High assessment performance indicating solid theoretical foundation.")
    if len(skills) >= 4:
        strengths.append(f"Diverse technical stack with {len(skills)} core skills identified.")
    if resume_quality >= 80:
        strengths.append("Strongly formatted resume containing key professional milestones.")
    if projects_count >= 3:
        strengths.append("Active hands-on experience demonstrated through multiple projects.")
    
    if not strengths:
        strengths.append("Motivated learner starting technical skill-building track.")

    if avg_assessment < 60:
        weaknesses.append("Theoretical concepts in core topics require review and practice.")
    if len(skills) < 3:
        weaknesses.append("Limited tech stack breadth. Consider learning additional languages/frameworks.")
    if projects_count < 2:
        weaknesses.append("Few practical projects documented. Need more project-based experience.")
    if resume_quality < 70:
        weaknesses.append("Resume detail can be improved. Focus on including metrics, projects, and certs.")
        
    if not weaknesses:
        weaknesses.append("None! Keep up the excellent work and continue building industry projects.")

    return {
        "overall_score": overall_score,
        "readiness_level": level,
        "strengths": strengths,
        "weaknesses": weaknesses
    }

def detect_skill_gaps(user_skills_dict, target_role):
    """
    Compares user skills to target role using real dynamic data.
    """
    role_info = ROLE_BENCHMARKS.get(target_role, {
        'required_skills': ['Java', 'Python', 'SQL'],
        'targets': {'Java': 80, 'Python': 75, 'SQL': 70}
    })
    required = role_info['required_skills']
    targets = role_info['targets']
    
    # user_skills_dict is {skill_name: score}
    matched = [s for s in required if s in user_skills_dict and user_skills_dict[s] > 0]
    missing = [s for s in required if s not in user_skills_dict or user_skills_dict[s] <= 0]
    
    match_percentage = round((len(matched) / len(required)) * 100) if required else 0
    
    competency_breakdown = []
    for sk in required:
        user_val = user_skills_dict.get(sk, 0)
        target_val = targets.get(sk, 70)
        competency_breakdown.append({
            "skill": sk,
            "current": user_val,
            "target": target_val,
            "status": "matched" if sk in matched else "missing",
            "satisfies": user_val >= target_val
        })
    
    return {
        "role": target_role,
        "required_skills": required,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage,
        "targets": targets,
        "competency_breakdown": competency_breakdown,
        "user_skills_count": len(user_skills_dict)
    }

def generate_personalized_roadmap(target_role, missing_skills):
    """
    Generates a 6-week learning curriculum based on target role and gaps.
    """
    # Base schedules based on target role
    base_roadmap = {
        'Data Analyst': [
            {"week": 1, "task": "Master SQL Fundamentals: SELECT, JOINs, GROUP BY, and Subqueries. Complete SQL assessment."},
            {"week": 2, "task": "Python Data Manipulation: Dive into pandas and NumPy. Practice cleaning dirty datasets."},
            {"week": 3, "task": "Data Visualization & Dashboards: Build interactive worksheets in Tableau/PowerBI or Streamlit."},
            {"week": 4, "task": "Capstone Project: Design a comprehensive E-Commerce sales analytics dashboard from scratch."},
            {"week": 5, "task": "Resume Building: Tailor your resume to highlight analytical projects, metrics, and SQL capabilities."},
            {"week": 6, "task": "Mock Interviews: Practice behavioral questions and analytical case studies using SQL."}
        ],
        'Data Scientist': [
            {"week": 1, "task": "Advanced Statistics & Pandas: Learn exploratory data analysis and hypothesis testing in Python."},
            {"week": 2, "task": "Introduction to Machine Learning: Study linear regression, decision trees, and classification algorithms."},
            {"week": 3, "task": "SQL & Model Integration: Retrieve training datasets from databases and evaluate machine learning models."},
            {"week": 4, "task": "Project Development: Build a Predictive Churn Classifier or Customer Segmentation System."},
            {"week": 5, "task": "Portfolio Design: Create a GitHub repository highlighting ML experiments and code quality."},
            {"week": 6, "task": "Technical Interviews: Study ML theory, model evaluation metrics, and algorithms."}
        ],
        'AI Engineer': [
            {"week": 1, "task": "Deep Learning Basics: Understand artificial neural networks, backpropagation, and optimization algorithms."},
            {"week": 2, "task": "PyTorch / TensorFlow Mastery: Implement convolutional neural networks for image classification."},
            {"week": 3, "task": "NLP & LLM Applications: Study text embedding models, vector search, and API integrations."},
            {"week": 4, "task": "AI Project implementation: Build a Handwritten Digit Classifier or a custom RAG Chatbot."},
            {"week": 5, "task": "Optimization & Deployment: Profile model speed, host models on HuggingFace, and structure APIs."},
            {"week": 6, "task": "AI Engineering Interviews: Review deep learning math, coding, and system design."}
        ],
        'Software Developer': [
            {"week": 1, "task": "Object-Oriented Programming (OOP): Master Java or Python OOP concepts, encapsulation, and inheritance."},
            {"week": 2, "task": "Data Structures & Algorithms: Study lists, stacks, queues, trees, searching, and sorting algorithms."},
            {"week": 3, "task": "Database Management & Git: Integrate SQL databases, practice query optimization, and master Git workflows."},
            {"week": 4, "task": "Practical Coding: Build a Student Registry Manager or a Multi-Threaded Web Crawler project."},
            {"week": 5, "task": "System Design Basics: Understand APIs, client-server models, and standard clean architecture principles."},
            {"week": 6, "task": "Coding Assessments: Practice LeetCode style problems and prepare for technical whiteboard interviews."}
        ],
        'Full Stack Developer': [
            {"week": 1, "task": "Web Foundation & React: Learn modern ES6+ JavaScript, CSS flexbox/grid, and basic React components."},
            {"week": 2, "task": "State Management & APIs: Connect React frontends with REST APIs using fetch/axios. Build routing."},
            {"week": 3, "task": "Backend Development: Write backend APIs in Python Flask, managing SQLite connections and CORS."},
            {"week": 4, "task": "Full-Stack Project: Build a complete Collaborative Task Planner or Personal Blog Platform."},
            {"week": 5, "task": "Security & Deployment: Implement basic user auth, password hashing, and deployment setups (e.g. Render)."},
            {"week": 6, "task": "Software Engineering Portfolio: Optimize your portfolio, host your full-stack projects, and review web security."}
        ],
        'Cyber Security Analyst': [
            {"week": 1, "task": "Networking & Protocols: Understand TCP/IP, OSI layers, DNS, and HTTP security headers."},
            {"week": 2, "task": "Linux System Administration: Learn bash scripting, file permissions, and directory controls."},
            {"week": 3, "task": "Security Tools & Scanning: Use Nmap and Wireshark to inspect network packets and audit open ports."},
            {"week": 4, "task": "Defensive Security Project: Implement a Local Port Scanner or an Intrusion Detection Shield."},
            {"week": 5, "task": "Security Compliance: Study OWASP Top 10 vulnerabilities and basic cryptography standards."},
            {"week": 6, "task": "Security Analyst Interviews: Practice security incident response exercises and mock scenarios."}
        ]
    }

    # Retrieve base roadmap or default to Software Developer
    roadmap = base_roadmap.get(target_role, base_roadmap['Software Developer'])
    
    # Inject missing skills suggestions dynamically
    if missing_skills:
        skills_str = ", ".join(missing_skills)
        roadmap[1] = {
            "week": 2,
            "task": f"Focus on Missing Skills ({skills_str}): Study dedicated courses and complete exercises to bridge this gap."
        }
        
    return roadmap

def get_suggested_learning_details(target_role, missing_skills):
    """
    Returns suggested courses, certifications, practice problems, and projects
    """
    courses = {
        'Data Analyst': ['Google Data Analytics Professional Certificate', 'SQL for Data Science (UC Davis)', 'Python for Data Analysis (Dataquest)'],
        'Data Scientist': ['Machine Learning Zoomcamp', 'Applied Data Science with Python (University of Michigan)', 'Introduction to Machine Learning (Coursera)'],
        'AI Engineer': ['Deep Learning Specialization (DeepLearning.AI)', 'PyTorch tutorials (Official website)', 'Natural Language Processing (Stanford)'],
        'Software Developer': ['Java Programming and Software Engineering Fundamentals (Duke)', 'Python for Everybody (University of Michigan)', 'Algorithms Specialization (Stanford)'],
        'Full Stack Developer': ['The Complete Web Developer Course (Udemy)', 'Full Stack Open (University of Helsinki)', 'React - The Complete Guide'],
        'Cyber Security Analyst': ['Google Cybersecurity Professional Certificate', 'CompTIA Security+ Prep Course', 'Introduction to IT & Cybersecurity (Cybrary)']
    }

    certs = {
        'Data Analyst': ['Google Data Analytics Certificate', 'Microsoft Certified: Power BI Data Analyst'],
        'Data Scientist': ['IBM Data Science Professional Certificate', 'Google Professional Data Engineer'],
        'AI Engineer': ['TensorFlow Developer Certificate', 'AWS Certified Machine Learning - Specialty'],
        'Software Developer': ['Oracle Certified Associate (Java)', 'AWS Certified Developer - Associate'],
        'Full Stack Developer': ['Meta Front-End & Back-End Developer Certificates', 'AWS Certified Cloud Practitioner'],
        'Cyber Security Analyst': ['CompTIA Security+', 'Certified Ethical Hacker (CEH)', 'CCNA (Cisco)']
    }

    problems = {
        'Data Analyst': ['StrataScratch SQL challenges', 'HackerRank SQL (Basic/Intermediate)', 'Kaggle exploratory notebooks'],
        'Data Scientist': ['Kaggle House Prices competition', 'LeetCode Pandas challenges', 'UCI ML repository datasets'],
        'AI Engineer': ['MNIST digit classifier from scratch', 'Train custom sentiment analyzer on IMDb', 'Deploy custom REST model API'],
        'Software Developer': ['LeetCode Easy/Medium collection', 'HackerRank Problem Solving Track', 'Exercism Java tracks'],
        'Full Stack Developer': ['Frontend Mentor challenges', 'Build a CRUD app in 24 hours', 'API verification with Postman'],
        'Cyber Security Analyst': ['OverTheWire (Bandit) Linux challenges', 'TryHackMe basic security modules', 'PicoCTF cryptography challenges']
    }

    return {
        "courses": courses.get(target_role, courses['Software Developer']),
        "certifications": certs.get(target_role, certs['Software Developer']),
        "practice_problems": problems.get(target_role, problems['Software Developer'])
    }

def ai_chatbot_response(query, user_profile, skills, readiness_score, missing_skills):
    """
    Generates tailored career advice.
    """
    name = user_profile.get('name', 'Student')
    role = user_profile.get('target_role', 'Software Developer')
    degree = user_profile.get('degree', 'Computer Science')
    year = user_profile.get('year', '2')
    
    q_lower = query.lower()
    
    # 1. Greetings
    if any(greet in q_lower for greet in ['hello', 'hi', 'hey', 'greetings']):
        return f"Hello {name}! I am your AI Career Assistant. I see you are a Year {year} student studying {degree}, aiming for a **{role}** role. Your current Internship Readiness Score is **{readiness_score}/100**. How can I help you accelerate your learning today?"

    # 2. Score questions
    if 'score' in q_lower or 'readiness' in q_lower or 'level' in q_lower:
        level_str = "Beginner"
        if readiness_score > 40: level_str = "Developing"
        if readiness_score > 70: level_str = "Internship Ready"
        if readiness_score > 90: level_str = "Industry Ready"
        
        advice = ""
        if level_str == "Beginner" or level_str == "Developing":
            advice = f"Since you are in the **{level_str}** level, you should focus on finishing the online MCQ assessments to identify your core knowledge base, and upload an updated resume to list any projects you have done."
        else:
            advice = "You are in a great position! To reach the next level, continue building the recommended advanced projects and refine your resume bullet points with quantifiable results."
            
        return f"Your current readiness score is **{readiness_score}/100** ({level_str}). {advice}"

    # 3. Gap or Missing Skills questions
    if 'gap' in q_lower or 'missing' in q_lower or 'need to learn' in q_lower:
        if not missing_skills:
            return f"Fantastic news! Based on our analysis, your current skills match the standard baseline requirements for a **{role}**! You can focus on advanced capstone projects to strengthen your resume."
        else:
            skills_list = ", ".join(missing_skills)
            return f"To qualify as an internship-ready **{role}**, you should focus on building skills in: **{skills_list}**. I recommend starting with the Week 2 tasks on your learning roadmap, which is custom-tailored to cover these exact topics."

    # 4. Resume questions
    if 'resume' in q_lower or 'upload' in q_lower or 'cv' in q_lower:
        return "You can upload a PDF resume using our **Resume Analyzer** tab. I will scan it to extract your technical skills, projects, and education. This will update your profile skills, which dynamically improves your readiness score!"

    # 5. Project questions
    if 'project' in q_lower or 'recommend' in q_lower:
        return f"For a **{role}** role, I recommend checking out the recommended projects listed at the bottom of your Learning Roadmap page. They are custom-selected based on your skill level and will directly address your missing skills."

    # 6. Default response
    return f"Great question! As an aspiring **{role}**, here is my top advice: focus on core hands-on projects, commit them to GitHub, and practice coding assessments regularly. Let me know if you need specific resources on learning new topics!"
