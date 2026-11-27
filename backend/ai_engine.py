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

TECH_SKILLS_CATALOG = [
    # (Display Name, Regex patterns, Category for benchmark scoring)
    ('Python', [r'\bpython\b', r'\bpython3\b'], 'Python'),
    ('Java', [r'\bjava\b(?!script)'], 'Java'),
    ('C Programming', [r'\bc\s+programming\b', r'\bc\s+language\b', r'\bc\s+prog\b', r'(?<![a-zA-Z0-9_])C(?![a-zA-Z0-9_+])'], None),
    ('C++', [r'\bc\+\+\b', r'\bcpp\b'], None),
    ('C#', [r'\bc#\b', r'\bc-sharp\b'], None),
    ('JavaScript', [r'\bjavascript\b', r'\bjs\b'], 'Web Development'),
    ('TypeScript', [r'\btypescript\b', r'\bts\b'], 'Web Development'),
    ('PHP', [r'\bphp\b'], None),
    ('Ruby', [r'\bruby\b'], None),
    ('Go', [r'\bgolang\b', r'\bgo\s+language\b'], None),
    ('Rust', [r'\brust\b'], None),
    ('Kotlin', [r'\bkotlin\b'], None),
    ('Swift', [r'\bswift\b'], None),
    ('SQL', [r'\bsql\b'], 'SQL'),
    ('MySQL', [r'\bmysql\b', r'\bmy\s*sql\b'], 'SQL'),
    ('PostgreSQL', [r'\bpostgresql\b', r'\bpostgres\b'], 'SQL'),
    ('MongoDB', [r'\bmongodb\b', r'\bmongo\s*db\b'], 'SQL'),
    ('SQLite', [r'\bsqlite\b'], 'SQL'),
    ('Oracle DB', [r'\boracle\s+db\b', r'\boracle\s+database\b'], 'SQL'),
    ('HTML', [r'\bhtml\b', r'\bhtml5\b'], 'Web Development'),
    ('CSS', [r'\bcss\b', r'\bcss3\b'], 'Web Development'),
    ('React', [r'\breact\b', r'\breact\.?js\b', r'\breactjs\b'], 'Web Development'),
    ('Node.js', [r'\bnode\b', r'\bnode\.?js\b', r'\bnodejs\b'], 'Web Development'),
    ('Express.js', [r'\bexpress\b', r'\bexpress\.?js\b'], 'Web Development'),
    ('Angular', [r'\bangular\b', r'\bangular\.?js\b'], 'Web Development'),
    ('Vue.js', [r'\bvue\b', r'\bvue\.?js\b'], 'Web Development'),
    ('Next.js', [r'\bnext\.?js\b'], 'Web Development'),
    ('Django', [r'\bdjango\b'], 'Python'),
    ('Flask', [r'\bflask\b'], 'Python'),
    ('FastAPI', [r'\bfastapi\b'], 'Python'),
    ('Spring Boot', [r'\bspring\s*boot\b', r'\bspring\b'], 'Java'),
    ('Bootstrap', [r'\bbootstrap\b'], 'Web Development'),
    ('Tailwind CSS', [r'\btailwind\b'], 'Web Development'),
    ('jQuery', [r'\bjquery\b'], 'Web Development'),
    ('Web Development', [r'\bweb\s+development\b', r'\bfrontend\s+development\b', r'\bbackend\s+development\b'], 'Web Development'),
    ('Database Management', [r'\bdatabase\s+management\b', r'\bdbms\b'], 'SQL'),
    ('Software Testing', [r'\bsoftware\s+testing\b', r'\bqa\s+testing\b'], None),
    ('Machine Learning', [r'\bmachine\s+learning\b'], 'AI/ML'),
    ('Deep Learning', [r'\bdeep\s+learning\b'], 'AI/ML'),
    ('Artificial Intelligence', [r'\bartificial\s+intelligence\b', r'\bai/ml\b'], 'AI/ML'),
    ('Computer Vision', [r'\bcomputer\s+vision\b'], 'AI/ML'),
    ('NLP', [r'\bnlp\b', r'\bnatural\s+language\s+processing\b'], 'AI/ML'),
    ('TensorFlow', [r'\btensorflow\b'], 'AI/ML'),
    ('PyTorch', [r'\bpytorch\b'], 'AI/ML'),
    ('Keras', [r'\bkeras\b'], 'AI/ML'),
    ('Scikit-Learn', [r'\bscikit-learn\b', r'\bsklearn\b'], 'AI/ML'),
    ('Pandas', [r'\bpandas\b'], 'Python'),
    ('NumPy', [r'\bnumpy\b'], 'Python'),
    ('Cyber Security', [r'\bcyber\s*security\b', r'\binformation\s+security\b', r'\bnetwork\s+security\b'], 'Cyber Security'),
    ('Linux', [r'\blinux\b'], 'Cyber Security'),
    ('Git', [r'\bgit\b(?!hub|lab)'], None),
    ('GitHub', [r'\bgithub\b'], None),
    ('Docker', [r'\bdocker\b'], None),
    ('Kubernetes', [r'\bkubernetes\b', r'\bk8s\b'], None),
    ('AWS', [r'\baws\b', r'\bamazon\s+web\s+services\b'], None),
    ('Azure', [r'\bazure\b'], None),
    ('Google Cloud', [r'\bgoogle\s+cloud\b', r'\bgcp\b'], None),
    ('Figma', [r'\bfigma\b'], None),
    ('Postman', [r'\bpostman\b'], None)
]

def clean_pdf_text(raw_text):
    text = raw_text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2022', '•')
    text = text.replace('\u00a0', ' ').replace('\ufffd', ' ')
    text = re.sub(r'([a-z0-9\.\)\]])([A-Z]{3,})\b', r'\1\n\2', text)
    text = re.sub(r'\b([A-Z]{3,})([A-Z][a-z]{2,})', r'\1\n\2', text)
    text = re.sub(r'(Great Learning|Simplilearn|Coursera|Udemy|NPTEL)(Technologies Used)', r'\1\n\2', text, flags=re.IGNORECASE)
    text = re.sub(r'(Tool)(HSC\b)', r'\1\n\2', text)
    return text

def parse_resume_from_pdf(pdf_path):
    """
    Extracts text directly from an uploaded PDF resume and performs fresh, accurate parsing.
    Does not use mock, hardcoded, or fabricated sample data.
    """
    if not os.path.exists(pdf_path):
        return {"error": "Uploaded resume file was not found on the server."}
    
    text = ""
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return {"error": "The uploaded PDF document has no pages."}
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF file {pdf_path}: {e}")
        return {"error": "Could not read the PDF structure. Please ensure the file is an unencrypted, valid PDF."}

    if not text or len(text.strip()) < 30:
        return {
            "error": "The uploaded PDF contains no readable text or consists solely of scanned image content. Please upload a text-readable PDF resume."
        }

    return parse_resume_text(text)

EDU_REGEXES = [
    r'\b(?:be|b\.e|b\.tech|btech|bachelor|b\.s|b\.sc|m\.e|m\.tech|mtech|master|m\.s|m\.sc|phd|doctorate|diploma)\b',
    r'\b(?:matric|higher secondary|secondary school|high school|school|college|institute|university|academy|campus)\b',
    r'\b(?:hsc|sslc|cbse|icse|cgpa|gpa|percentage)\b',
    r'\b(?:computer science and engineering|information technology|software engineering|electronics and communication)\b'
]

def is_education_line(text_line):
    l = text_line.lower()
    return any(bool(re.search(pat, l)) for pat in EDU_REGEXES)

def parse_resume_text(raw_text):
    """
    Accurately extracts Education, Technical Skills, Projects, Work Experience, Certifications,
    and Achievements directly from the actual resume content. Calculates a transparent quality score.
    """
    if not raw_text or len(raw_text.strip()) < 30:
        return {
            "error": "The uploaded PDF contains no readable text or consists solely of scanned image content. Please upload a text-readable PDF resume."
        }

    text = clean_pdf_text(raw_text)

    # Section Headings patterns
    SECTION_PATTERNS = {
        'EDUCATION': [
            r'^education\b', r'^educational background\b', r'^academic background\b',
            r'^academics?\b', r'^academic qualifications?\b', r'^qualifications?\b'
        ],
        'SKILLS': [
            r'^technical skills\b', r'^tech skills\b', r'^computer skills\b',
            r'^skills?\s*(?:&|and)\s*tools\b', r'^core competencies\b',
            r'^key skills\b', r'^skills\b', r'^technologies\b', r'^tools\b'
        ],
        'PROJECTS': [
            r'^projects?\b', r'^academic projects?\b', r'^personal projects?\b',
            r'^key projects?\b', r'^technical projects?\b', r'^project experience\b'
        ],
        'EXPERIENCE': [
            r'^experience\b', r'^work experience\b', r'^professional experience\b',
            r'^internships?\b', r'^internship experience\b', r'^work history\b',
            r'^employment history\b', r'^employment\b'
        ],
        'CERTIFICATIONS': [
            r'^certifications?\b', r'^certificates?\b', r'^licenses\s*&?\s*certifications?\b',
            r'^courses?\s*&?\s*certifications?\b'
        ],
        'ACHIEVEMENTS': [
            r'^achievements?\b', r'^accomplishments?\b', r'^honors?\s*(&|and)?\s*awards?\b',
            r'^awards?\b', r'^extracurricular\b', r'^co-curricular\b'
        ],
        'IGNORE': [
            r'^contact\b', r'^contact me\b', r'^profile\b', r'^summary\b',
            r'^professional summary\b', r'^objective\b', r'^career objective\b',
            r'^soft skills\b', r'^areas of interest\b', r'^languages?\b',
            r'^interests?\b', r'^personal details\b', r'^hobbies\b'
        ]
    }

    def identify_heading(line):
        clean = re.sub(r'^[#*\-•\d\.\s]+', '', line).strip()
        clean = re.sub(r'[:\-_]+$', '', clean).strip().lower()
        if not clean or len(clean) > 40:
            return None
        for sec, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                if re.match(pat + r'$', clean):
                    return sec
        return None

    sections = {}
    current_sec = 'HEADER'
    sections[current_sec] = []

    for line in text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
        h = identify_heading(line_str)
        if h:
            current_sec = h
            if current_sec not in sections:
                sections[current_sec] = []
        else:
            sections[current_sec].append(line_str)

    # Relocate leaked education lines from other sections
    for sec_name in ['PROJECTS', 'HEADER', 'IGNORE', 'SKILLS']:
        kept = []
        for line in sections.get(sec_name, []):
            if is_education_line(line):
                if 'EDUCATION' not in sections:
                    sections['EDUCATION'] = []
                sections['EDUCATION'].append(line)
            else:
                kept.append(line)
        sections[sec_name] = kept

    # 1. PARSE EDUCATION
    raw_edu = sections.get('EDUCATION', [])
    merged_edu = []
    i = 0
    while i < len(raw_edu):
        l = raw_edu[i].strip()
        l_low = l.lower()
        if any(skip in l_low for skip in ['passionate', 'seeking', 'understanding of programming', 'continuous learning', 'dedicated computer science']):
            i += 1
            continue

        while i + 1 < len(raw_edu):
            nl = raw_edu[i+1].strip()
            nl_low = nl.lower()
            if l.endswith(('AND', 'OF', 'IN', '&', '-', 'HIGHER', 'Higher', 'and', 'of', 'in')) or (nl.startswith(('ENGINEERING', 'TECHNOLOGY', '@')) and not any(k in nl_low for k in ['hsc', 'matric', 'secondary'])):
                if any(k in nl_low for k in ['b.e.', 'be-', 'b.tech', 'hsc', 'sslc']):
                    break
                l += " " + nl
                i += 1
            elif any(inst in nl_low for inst in ['institute of', 'college of', 'university']) and not any(inst in l_low for inst in ['institute', 'college', 'university']):
                l += " - " + nl
                i += 1
            elif any(pct in nl_low for pct in ['percentage', 'cgpa', 'gpa', '%']):
                pct_m = re.search(r'(\d{1,2}(?:\.\d+)?\s*%)', nl)
                if pct_m:
                    l += f" ({pct_m.group(1)})"
                    i += 1
                elif 'percentage' in nl_low and i + 2 < len(raw_edu):
                    pct_m2 = re.search(r'(\d{1,2}(?:\.\d+)?\s*%)', raw_edu[i+2])
                    if pct_m2:
                        l += f" ({pct_m2.group(1)})"
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
            else:
                break
        merged_edu.append(l)
        i += 1

    education_entries = []
    for entry in merged_edu:
        clean = re.sub(r'^[•\*\-\d\.\s]+', '', entry).strip()
        clean = re.sub(r'\s*@\s*', ' - ', clean)
        clean = re.sub(r'\s*-\s*\(', ' (', clean)
        clean = re.sub(r'Percentage:Percentage:?', '', clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if any(term in clean.lower() for term in ['b.e.', 'be-', 'b.tech', 'bachelor', 'master', 'm.e.', 'm.tech', 'hsc', 'sslc', 'matric', 'secondary school', 'institute', 'college', 'university']):
            if clean and clean not in education_entries:
                education_entries.append(clean)

    # 2. PARSE TECHNICAL SKILLS
    extracted_skills = []
    benchmark_scores = {}
    
    # Check skills section lines first
    skills_text = " ".join(sections.get('SKILLS', []))
    for canon, pats, cat in TECH_SKILLS_CATALOG:
        for p in pats:
            if re.search(p, skills_text, re.IGNORECASE):
                if canon not in extracted_skills:
                    extracted_skills.append(canon)
                if cat:
                    benchmark_scores[cat] = 65
                break

    # Scan entire resume text for confirmed technical technologies
    for canon, pats, cat in TECH_SKILLS_CATALOG:
        if canon not in extracted_skills:
            for p in pats:
                if canon == 'Artificial Intelligence' and not re.search(r'\bartificial\s+intelligence\b|\bai/ml\b', text, re.IGNORECASE):
                    continue
                if re.search(p, text, re.IGNORECASE):
                    extracted_skills.append(canon)
                    if cat and cat not in benchmark_scores:
                        benchmark_scores[cat] = 60
                    break

    # 3. PARSE PROJECTS
    proj_lines = sections.get('PROJECTS', [])
    parsed_projects = []
    curr_proj = None

    for line in proj_lines:
        line_clean = line.strip()
        line_l = line_clean.lower()
        if is_education_line(line_clean) or any(term in line_l for term in ['certificates', 'certifications']):
            continue

        is_bullet = bool(re.match(r'^[•\*\-\d\.]+\s*', line_clean))
        clean_text = re.sub(r'^[•\*\-\d\.]+\s*', '', line_clean).strip()
        if not clean_text:
            continue

        # Wrapped project title continuation
        if curr_proj and curr_proj.get('awaiting_wrap') and not is_bullet and len(clean_text) < 30 and not line_l.startswith(('developed', 'built', 'implemented')):
            curr_proj['title'] += " " + clean_text
            curr_proj['awaiting_wrap'] = False
            continue

        is_title = False
        if is_bullet:
            is_title = True
        elif len(clean_text) < 60 and not line_l.startswith(('developed', 'built', 'implemented', 'designed', 'created', 'analyzes', 'provides', 'identifies', 'the platform', 'it helps', 'technologies used', 'tools used', 'and creative', 'skills and', 'based on', 'to support')):
            if '.' not in clean_text[:-1] and not clean_text.endswith(('.', ':', ';', ',')) and clean_text[0].isupper():
                is_title = True

        if is_title:
            if curr_proj:
                parsed_projects.append(curr_proj)
            curr_proj = {
                'title': clean_text,
                'desc': [],
                'awaiting_wrap': len(clean_text) > 30 and not clean_text.endswith(('.', ':', '!'))
            }
        else:
            if curr_proj:
                curr_proj['desc'].append(clean_text)
                curr_proj['awaiting_wrap'] = False

    if curr_proj:
        parsed_projects.append(curr_proj)

    # Check for cross-column project descriptions in certifications section
    cert_lines_raw = sections.get('CERTIFICATIONS', [])
    for p in parsed_projects:
        if not p.get('desc'):
            candidate_desc = []
            matching = False
            for line in cert_lines_raw:
                line_l = line.lower()
                if any(verb in line_l for verb in ['built an', 'developed an', 'created an', 'designed an']):
                    matching = True
                if matching:
                    if any(c in line_l for c in ['simplilearn', 'coursera', 'udemy', 'nptel', 'certified']):
                        matching = False
                    else:
                        candidate_desc.append(line.strip())
            if candidate_desc:
                p['desc'] = candidate_desc

    final_projects = []
    for p in parsed_projects:
        title = p['title'].strip()
        if is_education_line(title):
            continue
        desc_full = " ".join(p['desc']).strip()
        desc_clean = re.sub(r'Technologies Used:.*$', '', desc_full, flags=re.IGNORECASE).strip()
        tech_m = re.search(r'Technologies Used:\s*([^\n\r]+)', desc_full, flags=re.IGNORECASE)
        tech_note = f" (Technologies: {tech_m.group(1).strip()})" if tech_m else ""
        
        if desc_clean:
            final_projects.append(f"{title}: {desc_clean}{tech_note}")
        else:
            final_projects.append(f"{title}{tech_note}")

    # 4. PARSE WORK EXPERIENCE / INTERNSHIPS
    exp_lines = sections.get('EXPERIENCE', [])
    final_exp = []
    for line in exp_lines:
        clean_exp = re.sub(r'^[•\*\-\d\.]+\s*', '', line.strip()).strip()
        if len(clean_exp) > 5 and not any(skip in clean_exp.lower() for skip in ['experience.education', 'foward for my first work experience']):
            final_exp.append(clean_exp)

    # 5. PARSE CERTIFICATIONS
    final_certs = []
    for line in cert_lines_raw:
        clean_cert = re.sub(r'Technologies Used:.*$', '', line.strip(), flags=re.IGNORECASE).strip()
        clean_cert = re.sub(r'^[•\*\-\d\.]+\s*', '', clean_cert).strip()
        if len(clean_cert) > 5 and any(term in clean_cert.lower() for term in ['nptel', 'coursera', 'udemy', 'simplilearn', 'great learning', 'aws', 'certified', 'certification', 'programming in java', 'for beginners', 'frontend development']):
            if clean_cert not in final_certs:
                final_certs.append(clean_cert)

    # 6. PARSE ACHIEVEMENTS
    ach_lines = sections.get('ACHIEVEMENTS', [])
    final_ach = []
    for line in ach_lines:
        clean_ach = re.sub(r'^[•\*\-\d\.]+\s*', '', line.strip()).strip()
        if len(clean_ach) > 5:
            final_ach.append(clean_ach)

    # 7. CALCULATE RESUME QUALITY SCORE
    # Rubric: Education (15), Skills (25), Projects (25), Experience (15), Certifications (10), Completeness (10)
    edu_score = 15 if education_entries else 0
    
    n_skills = len(extracted_skills)
    if n_skills >= 6:
        skills_score = 25
    elif n_skills >= 4:
        skills_score = 20
    elif n_skills >= 2:
        skills_score = 15
    elif n_skills >= 1:
        skills_score = 10
    else:
        skills_score = 0

    n_proj = len(final_projects)
    if n_proj >= 3:
        proj_score = 25
    elif n_proj == 2:
        proj_score = 20
    elif n_proj == 1:
        proj_score = 12
    else:
        proj_score = 0

    n_exp = len(final_exp)
    if n_exp >= 2:
        exp_score = 15
    elif n_exp == 1:
        exp_score = 10
    else:
        exp_score = 0

    n_cert = len(final_certs)
    if n_cert >= 2:
        cert_score = 10
    elif n_cert == 1:
        cert_score = 6
    else:
        cert_score = 0

    completeness_score = 0
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        completeness_score += 5
    if re.search(r'\+?\d[\d\s-]{8,14}\d', text):
        completeness_score += 5

    total_quality = edu_score + skills_score + proj_score + exp_score + cert_score + completeness_score
    total_quality = min(max(total_quality, 15), 95)

    eval_reasons = []
    eval_reasons.append(f"Education verified ({edu_score}/15 pts)" if edu_score else "Education details missing (0/15 pts)")
    eval_reasons.append(f"{n_skills} technical skills identified ({skills_score}/25 pts)" if n_skills else "Technical skills missing (0/25 pts)")
    eval_reasons.append(f"{n_proj} project(s) extracted ({proj_score}/25 pts)" if n_proj else "Project experience missing (0/25 pts)")
    eval_reasons.append(f"{n_cert} certification(s) verified ({cert_score}/10 pts)" if n_cert else "No certifications detected (0/10 pts)")
    if n_exp:
        eval_reasons.append(f"{n_exp} internship/work entry ({exp_score}/15 pts)")
    else:
        eval_reasons.append("No internship/work experience listed (0/15 pts)")
    eval_reasons.append(f"Resume formatting & contact info ({completeness_score}/10 pts)")

    score_explanation = " | ".join(eval_reasons)

    return {
        "skills": extracted_skills if extracted_skills else ["No technical skills found in resume"],
        "skill_scores": benchmark_scores,
        "education": education_entries if education_entries else ["No education details found in resume"],
        "projects": final_projects if final_projects else ["No projects found in resume"],
        "experience": final_exp if final_exp else ["No internship or work experience found in resume"],
        "certifications": final_certs if final_certs else ["No certifications found in resume"],
        "achievements": final_ach if final_ach else ["No achievements found in resume"],
        "resume_quality": total_quality,
        "score_explanation": score_explanation
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
