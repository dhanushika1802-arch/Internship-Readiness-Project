import os
import uuid
import sqlite3
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, get_db_connection
import ai_engine
import pdf_generator

app = Flask(__name__)
CORS(app)

# Config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
init_db()

# Predefined Assessment Questions
ASSESSMENT_QUESTIONS = {
    'Python': [
        {
            "id": 1,
            "question": "Which of the following is mutable in Python?",
            "options": ["List", "Tuple", "String", "Integer"],
            "answer": "List",
            "explanation": "Lists can be modified after creation (appended, popped, etc.), unlike tuples, strings, or integers."
        },
        {
            "id": 2,
            "question": "What does the expression [x**2 for x in range(3)] output?",
            "options": ["[0, 1, 4]", "[1, 4, 9]", "[0, 1, 2]", "[0, 1, 8]"],
            "answer": "[0, 1, 4]",
            "explanation": "It squares 0, 1, and 2, resulting in a list: [0, 1, 4]."
        },
        {
            "id": 3,
            "question": "What is the purpose of the Python decorator '@classmethod'?",
            "options": [
                "To define a method that operates on the class itself rather than instances",
                "To prevent subclassing of a class method",
                "To turn a method into a static property",
                "To optimize class memory allocation"
            ],
            "answer": "To define a method that operates on the class itself rather than instances",
            "explanation": "A class method receives the class (cls) as its first argument rather than the instance (self)."
        },
        {
            "id": 4,
            "question": "Which block in Python error handling is always executed?",
            "options": ["finally", "except", "try", "else"],
            "answer": "finally",
            "explanation": "The 'finally' block executes regardless of whether an exception occurred or was handled."
        },
        {
            "id": 5,
            "question": "What is the GIL in Python?",
            "options": [
                "Global Interpreter Lock, which prevents multiple threads from executing Python code at once",
                "Graphical Interface Library, used for building GUI elements",
                "Garbage Integration Loop, which manages cyclic references",
                "Global Index Layout, used for array indices"
            ],
            "answer": "Global Interpreter Lock, which prevents multiple threads from executing Python code at once",
            "explanation": "The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes concurrently."
        }
    ],
    'Java': [
        {
            "id": 1,
            "question": "Which keyword is used to inherit a class in Java?",
            "options": ["extends", "implements", "inherits", "import"],
            "answer": "extends",
            "explanation": "'extends' is used to inherit classes, while 'implements' is used to implement interfaces."
        },
        {
            "id": 2,
            "question": "What is the default value of an uninitialized local object reference variable in Java?",
            "options": ["null", "void", "0", "None of the above (Compiler error)"],
            "answer": "None of the above (Compiler error)",
            "explanation": "Local variables in Java are not assigned default values. Accessing them uninitialized results in a compile-time error."
        },
        {
            "id": 3,
            "question": "Which of these is NOT a member of the Java Collections Framework?",
            "options": ["HashTree", "ArrayList", "HashMap", "HashSet"],
            "answer": "HashTree",
            "explanation": "Java collections include TreeSet and HashSet, but 'HashTree' is not a standard class in java.util."
        },
        {
            "id": 4,
            "question": "Which memory area in the JVM holds objects created using the 'new' keyword?",
            "options": ["Heap memory", "Stack memory", "Method Area", "Program Counter registers"],
            "answer": "Heap memory",
            "explanation": "All dynamically allocated Java objects reside in the Heap memory, managed by the Garbage Collector."
        },
        {
            "id": 5,
            "question": "What does a 'finally' block in Java do?",
            "options": [
                "Executes after try-catch blocks regardless of whether an exception is thrown",
                "Guarantees that a class cannot be extended further",
                "Runs only when an out-of-memory exception occurs",
                "Defines final variables for the class scope"
            ],
            "answer": "Executes after try-catch blocks regardless of whether an exception is thrown",
            "explanation": "The 'finally' block is guaranteed to run, making it ideal for cleaning up resources like database connections or open files."
        }
    ],
    'SQL': [
        {
            "id": 1,
            "question": "Which SQL statement is used to remove duplicate rows from a query result?",
            "options": ["SELECT DISTINCT", "SELECT UNIQUE", "SELECT DIFFERENT", "SELECT GROUP BY"],
            "answer": "SELECT DISTINCT",
            "explanation": "The DISTINCT keyword filters out duplicates from the returned column values."
        },
        {
            "id": 2,
            "question": "What is the difference between WHERE and HAVING in SQL?",
            "options": [
                "WHERE filters rows before grouping; HAVING filters groups after GROUP BY",
                "HAVING filters rows before grouping; WHERE filters groups after GROUP BY",
                "WHERE only supports integers; HAVING only supports strings",
                "There is no difference; they are interchangeable"
            ],
            "answer": "WHERE filters rows before grouping; HAVING filters groups after GROUP BY",
            "explanation": "WHERE filters raw table rows. HAVING is applied after rows are grouped (GROUP BY) to filter the aggregated results."
        },
        {
            "id": 3,
            "question": "Which SQL JOIN returns all rows from the left table and matched rows from the right?",
            "options": ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"],
            "answer": "LEFT JOIN",
            "explanation": "LEFT JOIN (or LEFT OUTER JOIN) returns all records from the left table, and the matched records from the right table. If no match, NULL values are returned."
        },
        {
            "id": 4,
            "question": "What is the purpose of an INDEX in a database table?",
            "options": [
                "To speed up data retrieval queries",
                "To enforce primary key uniqueness",
                "To encrypt sensitive data values",
                "To partition table columns into multiple databases"
            ],
            "answer": "To speed up data retrieval queries",
            "explanation": "Database indexes provide quick pointer pathways to row locations, speeding up SELECT queries at the cost of slower write/insert queries."
        },
        {
            "id": 5,
            "question": "Which function is used to calculate the number of rows in a query?",
            "options": ["COUNT()", "SUM()", "MAX()", "ROWS()"],
            "answer": "COUNT()",
            "explanation": "COUNT() is an aggregate function that returns the total count of matching rows in the result set."
        }
    ],
    'AI/ML': [
        {
            "id": 1,
            "question": "Which of these is a Supervised Learning task?",
            "options": ["Linear Regression", "K-Means Clustering", "Anomaly Detection", "Dimensionality Reduction"],
            "answer": "Linear Regression",
            "explanation": "Linear Regression models require labeled training inputs (supervision) to predict continuous numerical targets."
        },
        {
            "id": 2,
            "question": "What occurs when a model performs exceptionally on training data but poorly on unseen test data?",
            "options": ["Overfitting", "Underfitting", "High Bias", "Gradient Explosion"],
            "answer": "Overfitting",
            "explanation": "Overfitting happens when a model learns the noise and details of the training set too closely, failing to generalize to new data."
        },
        {
            "id": 3,
            "question": "What is the purpose of an activation function (like ReLU) in Neural Networks?",
            "options": [
                "To introduce non-linearity, allowing the network to learn complex patterns",
                "To scale weights into a range between 0 and 1",
                "To prevent backpropagation gradients from updating weights",
                "To compute loss values during testing"
            ],
            "answer": "To introduce non-linearity, allowing the network to learn complex patterns",
            "explanation": "Without activation functions, a multi-layer neural network behaves like a single linear regression model, regardless of depth."
        },
        {
            "id": 4,
            "question": "Which metric is commonly used to evaluate a classification model on imbalanced datasets?",
            "options": ["F1-Score", "Mean Squared Error", "R-Squared", "Mean Absolute Error"],
            "answer": "F1-Score",
            "explanation": "The F1-Score combines precision and recall, providing a balanced metric for evaluation when dataset classes are highly skewed."
        },
        {
            "id": 5,
            "question": "What does 'epoch' represent in deep learning model training?",
            "options": [
                "One full pass of the entire training dataset through the neural network",
                "The time taken to train one batch of samples",
                "The total training hours of a model",
                "The threshold value of learning rate decay"
            ],
            "answer": "One full pass of the entire training dataset through the neural network",
            "explanation": "An epoch represents training the network once with every single sample from the training dataset."
        }
    ],
    'Web Development': [
        {
            "id": 1,
            "question": "Which property is used in React to pass data down from parent to child components?",
            "options": ["props", "state", "context", "refs"],
            "answer": "props",
            "explanation": "'props' are read-only properties passed from parent to child. 'state' is internal component data."
        },
        {
            "id": 2,
            "question": "What is the purpose of the DOM (Document Object Model) in web browsers?",
            "options": [
                "To represent the HTML structure as a tree of objects that scripting languages can modify",
                "To speed up CSS styling animations",
                "To establish socket connections to backend databases",
                "To cache images and static assets locally"
            ],
            "answer": "To represent the HTML structure as a tree of objects that scripting languages can modify",
            "explanation": "The DOM is a programming API for HTML documents, structuring it in memory so Javascript can query and update elements dynamically."
        },
        {
            "id": 3,
            "question": "Which HTTP method is most appropriate for updating an existing database resource?",
            "options": ["PUT", "GET", "POST", "DELETE"],
            "answer": "PUT",
            "explanation": "PUT or PATCH is traditionally used for updates, GET for retrieving data, POST for creating new entries, and DELETE to remove resources."
        },
        {
            "id": 4,
            "question": "What does the CSS property 'display: flex' do?",
            "options": [
                "Sets up a flexbox container, enabling responsive space distribution and alignment of child items",
                "Allows the background color to bend around page elements",
                "Speeds up browser rendering of fonts",
                "Prevents javascript errors on the client side"
            ],
            "answer": "Sets up a flexbox container, enabling responsive space distribution and alignment of child items",
            "explanation": "Flexbox is a 1-dimensional layout model that provides space distribution and alignment capabilities among items in a container."
        },
        {
            "id": 5,
            "question": "What does a Promise represent in JavaScript?",
            "options": [
                "The eventual completion (or failure) of an asynchronous operation and its resulting value",
                "A guarantee that no syntax errors exist in the script",
                "An encryption scheme for security certificates",
                "A callback parameter for timer functions"
            ],
            "answer": "The eventual completion (or failure) of an asynchronous operation and its resulting value",
            "explanation": "Promises represent proxy values for asynchronous operations that are pending, fulfilled, or rejected."
        }
    ]
}

# Helper to verify auth tokens (using user_id directly as token for simplicity)
def get_user_from_headers():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        if auth_header.startswith("Bearer "):
            user_id = int(auth_header.split(" ")[1])
        else:
            user_id = int(auth_header)
        return user_id
    except ValueError:
        return None

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "online",
        "message": "ReadyUp AI Backend API is running successfully!",
        "endpoints": {
            "health": "/api/health",
            "auth_register": "/api/auth/register",
            "auth_login": "/api/auth/login",
            "dashboard": "/api/dashboard/stats"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

# Auth Endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    degree = data.get('degree', 'Computer Science')
    year = data.get('year', 2)
    target_role = data.get('target_role', 'Software Developer')

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO Users (name, email, password, degree, year, target_role) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, email, hashed_password, degree, int(year), target_role))
        user_id = cursor.lastrowid
        
        # Initialize Progress
        cursor.execute("INSERT INTO Progress (user_id, completion_percentage, skills_completed, courses_completed, projects_completed) VALUES (?, 0, '', '', '')", (user_id,))
        
        conn.commit()
        return jsonify({
            "message": "User registered successfully", 
            "user_id": user_id, 
            "name": name, 
            "email": email,
            "target_role": target_role
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        user_dict = dict(user)
        target_role = user_dict.get('target_role') or 'Software Developer'
        return jsonify({
            "message": "Login successful",
            "token": str(user['id']),  # Send user_id as token
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "degree": user['degree'],
                "year": user['year'],
                "target_role": target_role
            }
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/user/profile', methods=['GET', 'PUT'])
def profile():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT name, email, degree, year, target_role FROM Users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            u_dict = dict(user)
            if not u_dict.get('target_role'):
                u_dict['target_role'] = 'Software Developer'
            return jsonify(u_dict), 200
        return jsonify({"error": "User not found"}), 404

    elif request.method == 'PUT':
        data = request.json
        name = data.get('name')
        degree = data.get('degree')
        year = data.get('year')
        target_role = data.get('target_role')

        if target_role:
            cursor.execute("UPDATE Users SET name = ?, degree = ?, year = ?, target_role = ? WHERE id = ?", 
                           (name, degree, int(year), target_role, user_id))
        else:
            cursor.execute("UPDATE Users SET name = ?, degree = ?, year = ? WHERE id = ?", 
                           (name, degree, int(year), user_id))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Profile updated successfully"}), 200

@app.route('/api/user/target-role', methods=['POST'])
def update_target_role():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    target_role = data.get('target_role', 'Software Developer')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET target_role = ? WHERE id = ?", (target_role, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Target role saved", "target_role": target_role}), 200

# Dashboard Statistics
@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    target_role = request.args.get('target_role')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch User details
    cursor.execute("SELECT name, degree, year, email, target_role FROM Users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    if not target_role:
        target_role = user.get('target_role') or 'Software Developer'
    user['target_role'] = target_role

    # 2. Fetch User Skills
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}

    # 3. Fetch User Assessments
    cursor.execute("SELECT assessment_name, score FROM Assessments WHERE user_id = ?", (user_id,))
    assessments = {row['assessment_name']: row['score'] for row in cursor.fetchall()}

    # 4. Fetch Resume quality details
    cursor.execute("SELECT file_path, score FROM Resumes WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    resume_row = cursor.fetchone()
    resume_quality = 50 # Default baseline
    if resume_row and resume_row['score']:
        resume_quality = resume_row['score']

    # 5. Fetch Completed Items
    cursor.execute("SELECT * FROM Progress WHERE user_id = ?", (user_id,))
    progress_row = cursor.fetchone()
    
    completion_percentage = 0
    skills_completed = []
    courses_completed = []
    projects_completed = []

    if progress_row:
        completion_percentage = progress_row['completion_percentage']
        if progress_row['skills_completed']:
            skills_completed = progress_row['skills_completed'].split(',')
        if progress_row['courses_completed']:
            courses_completed = progress_row['courses_completed'].split(',')
        if progress_row['projects_completed']:
            projects_completed = progress_row['projects_completed'].split(',')

    # 6. Calculate composite readiness
    readiness = ai_engine.calculate_readiness_score(
        skills, 
        projects_completed, 
        courses_completed, 
        resume_quality, 
        assessments
    )

    # 7. Gap Analysis
    gaps = ai_engine.detect_skill_gaps(skills, target_role)

    # 8. Check how many roadmap items are completed
    cursor.execute("SELECT COUNT(*) as total, SUM(completed) as comp FROM Roadmaps WHERE user_id = ? AND week <= 6", (user_id,))
    roadmap_stats = cursor.fetchone()
    roadmap_count = roadmap_stats['total']
    roadmap_completed = roadmap_stats['comp'] or 0
    
    conn.close()

    return jsonify({
        "profile": user,
        "skills": skills,
        "assessments": assessments,
        "readiness": readiness,
        "gaps": gaps,
        "progress": {
            "completion_percentage": completion_percentage,
            "skills_completed": skills_completed,
            "courses_completed": courses_completed,
            "projects_completed": projects_completed,
            "roadmap_total": roadmap_count,
            "roadmap_completed": roadmap_completed
        }
    }), 200

# Resume Uploader & Extractor
@app.route('/api/resume/upload', methods=['POST'])
def upload_resume():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Please select a valid PDF document file."}), 400

    filename = secure_filename(f"user_{user_id}_{file.filename}")
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Fresh parse of the newly uploaded PDF resume
    parsed_report = ai_engine.parse_resume_from_pdf(save_path)
    if not parsed_report or parsed_report.get('error'):
        error_msg = parsed_report.get('error') if parsed_report else "Failed to parse resume text"
        return jsonify({"error": error_msg}), 400

    # Save details to DB
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Update Resume record with fresh score (clear previous resume for this user)
    cursor.execute("DELETE FROM Resumes WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO Resumes (user_id, file_path, score) VALUES (?, ?, ?)", 
                   (user_id, save_path, parsed_report.get('resume_quality', 60)))

    # 2. Add or update skills from resume with real calculated scores (no static 60%)
    skill_scores = parsed_report.get('skill_scores', {})
    for skill, resume_score in skill_scores.items():
        cursor.execute("SELECT id, score FROM Skills WHERE user_id = ? AND skill_name = ?", (user_id, skill))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("INSERT INTO Skills (user_id, skill_name, score) VALUES (?, ?, ?)", (user_id, skill, resume_score))
        else:
            # Check if user already took an assessment for this skill
            cursor.execute("SELECT score FROM Assessments WHERE user_id = ? AND assessment_name = ?", (user_id, skill))
            has_assessment = cursor.fetchone()
            if not has_assessment:
                cursor.execute("UPDATE Skills SET score = ? WHERE id = ?", (resume_score, existing['id']))
            else:
                cursor.execute("UPDATE Skills SET score = ? WHERE id = ?", (max(has_assessment['score'], resume_score), existing['id']))
            
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Resume uploaded and processed successfully",
        "parsed_data": parsed_report
    }), 200

# MCQ Assessment Endpoint
@app.route('/api/assessments/questions', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    if not category or category not in ASSESSMENT_QUESTIONS:
        return jsonify({"error": "Invalid or missing assessment category"}), 400
    
    # Return questions without raw answer codes to prevent cheating
    safe_questions = []
    for q in ASSESSMENT_QUESTIONS[category]:
        safe_questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    return jsonify(safe_questions), 200

@app.route('/api/assessments/submit', methods=['POST'])
def submit_assessment():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    category = data.get('category')
    answers = data.get('answers')  # Dictionary of {question_id: selected_option}

    if not category or category not in ASSESSMENT_QUESTIONS or not answers:
        return jsonify({"error": "Missing assessment details"}), 400

    correct_count = 0
    questions = ASSESSMENT_QUESTIONS[category]
    results_detail = []

    for q in questions:
        q_id_str = str(q["id"])
        user_choice = answers.get(q_id_str)
        is_correct = (user_choice == q["answer"])
        if is_correct:
            correct_count += 1
        
        results_detail.append({
            "id": q["id"],
            "question": q["question"],
            "your_choice": user_choice,
            "correct_choice": q["answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    score = round((correct_count / len(questions)) * 100)

    # Save assessment and update user skill capability rating directly
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert Assessment row
    cursor.execute("INSERT INTO Assessments (user_id, assessment_name, score) VALUES (?, ?, ?)", 
                   (user_id, category, score))
    
    # Update Skills score: test score validates student capability rating directly (real dynamic score)
    cursor.execute("SELECT id, score FROM Skills WHERE user_id = ? AND skill_name = ?", (user_id, category))
    existing_skill = cursor.fetchone()
    if existing_skill:
        cursor.execute("UPDATE Skills SET score = ? WHERE id = ?", (score, existing_skill['id']))
    else:
        cursor.execute("INSERT INTO Skills (user_id, skill_name, score) VALUES (?, ?, ?)", (user_id, category, score))

    conn.commit()
    conn.close()

    return jsonify({
        "score": score,
        "correct_count": correct_count,
        "total_count": len(questions),
        "results": results_detail
    }), 200

# Gap Analysis Endpoint
@app.route('/api/gap-analysis', methods=['GET'])
def get_gap_analysis():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    target_role = request.args.get('target_role')
    if not target_role:
        cursor.execute("SELECT target_role FROM Users WHERE id = ?", (user_id,))
        u_row = cursor.fetchone()
        target_role = u_row['target_role'] if u_row and u_row['target_role'] else 'Software Developer'

    # Check if user has uploaded/analyzed a resume
    cursor.execute("SELECT COUNT(*) as count FROM Resumes WHERE user_id = ?", (user_id,))
    resumes_count = cursor.fetchone()['count']

    # Fetch user skills
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
    conn.close()

    # If resume has not been analyzed yet
    if resumes_count == 0:
        return jsonify({
            "has_analyzed_resume": False,
            "has_skills": False,
            "role": target_role,
            "message": "Analyze your resume first to view your skill gap."
        }), 200

    # If resume was analyzed but 0 technical skills were detected
    if len(skills) == 0:
        return jsonify({
            "has_analyzed_resume": True,
            "has_skills": False,
            "role": target_role,
            "message": "No technical skills detected yet. Upload and analyze your resume."
        }), 200

    gaps = ai_engine.detect_skill_gaps(skills, target_role)
    gaps["has_analyzed_resume"] = True
    gaps["has_skills"] = True
    return jsonify(gaps), 200

# Learning Roadmap
@app.route('/api/roadmap', methods=['GET'])
def get_roadmap():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    target_role = request.args.get('target_role', 'Software Developer')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch current stored roadmap tasks
    cursor.execute("SELECT id, week, task, completed FROM Roadmaps WHERE user_id = ? ORDER BY week ASC", (user_id,))
    db_roadmap = cursor.fetchall()

    # If database doesn't have it, generate and save it
    if not db_roadmap:
        # Fetch user missing skills
        cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
        skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
        gaps = ai_engine.detect_skill_gaps(skills, target_role)
        
        generated = ai_engine.generate_personalized_roadmap(target_role, gaps['missing_skills'])
        for item in generated:
            cursor.execute("INSERT INTO Roadmaps (user_id, week, task, completed) VALUES (?, ?, ?, 0)",
                           (user_id, item['week'], item['task']))
        conn.commit()
        
        cursor.execute("SELECT id, week, task, completed FROM Roadmaps WHERE user_id = ? ORDER BY week ASC", (user_id,))
        db_roadmap = cursor.fetchall()

    roadmap_list = [dict(row) for row in db_roadmap]
    
    # 2. Fetch missing skills details
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
    gaps = ai_engine.detect_skill_gaps(skills, target_role)
    
    # Get courses & cert suggestions
    suggestions = ai_engine.get_suggested_learning_details(target_role, gaps['missing_skills'])
    
    conn.close()

    return jsonify({
        "roadmap": roadmap_list,
        "suggestions": suggestions
    }), 200

@app.route('/api/roadmap/update', methods=['POST'])
def update_roadmap():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    roadmap_id = data.get('id')
    completed = data.get('completed', 0)

    if not roadmap_id:
        return jsonify({"error": "Missing roadmap task ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE Roadmaps SET completed = ? WHERE id = ? AND user_id = ?", (completed, roadmap_id, user_id))
    
    # Recalculate overall progress
    cursor.execute("SELECT COUNT(*) as total, SUM(completed) as comp FROM Roadmaps WHERE user_id = ?", (user_id,))
    stats = cursor.fetchone()
    total = stats['total']
    comp = stats['comp'] or 0
    
    completion_percentage = round((comp / total) * 100) if total > 0 else 0
    cursor.execute("UPDATE Progress SET completion_percentage = ? WHERE user_id = ?", (completion_percentage, user_id))
    
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Roadmap item updated successfully",
        "completion_percentage": completion_percentage
    }), 200

# Recommended Projects
@app.route('/api/projects/recommended', methods=['GET'])
def get_recommended_projects():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    target_role = request.args.get('target_role', 'Software Developer')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch user skills
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
    
    # Match criteria
    gaps = ai_engine.detect_skill_gaps(skills, target_role)
    missing = gaps['missing_skills']
    
    # Simple recommendation heuristics:
    # 1. Match category to target_role
    # 2. Sort by difficulty (Beginner if score low, Advanced if score high)
    cursor.execute("SELECT * FROM Projects WHERE category = ?", (target_role,))
    projects = [dict(row) for row in cursor.fetchall()]
    
    # Fallback to general category projects if none matching
    if not projects:
        cursor.execute("SELECT * FROM Projects LIMIT 6")
        projects = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return jsonify(projects), 200

# Career Advisor Chat
@app.route('/api/chat', methods=['POST'])
def chat():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    query = data.get('query', '')
    target_role = request.args.get('target_role', 'Software Developer')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # User profile
    cursor.execute("SELECT name, degree, year, email FROM Users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    user['target_role'] = target_role
    
    # User skills
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
    
    # User assessments
    cursor.execute("SELECT assessment_name, score FROM Assessments WHERE user_id = ?", (user_id,))
    assessments = {row['assessment_name']: row['score'] for row in cursor.fetchall()}
    
    conn.close()

    # Gap metrics
    gaps = ai_engine.detect_skill_gaps(skills, target_role)
    
    # Readiness Score
    readiness = ai_engine.calculate_readiness_score(skills, [], [], 80, assessments)
    
    # AI advice generator
    ai_response = ai_engine.ai_chatbot_response(
        query, 
        user, 
        skills, 
        readiness['overall_score'], 
        gaps['missing_skills']
    )

    return jsonify({"response": ai_response}), 200

# PDF Report Download
@app.route('/api/report/download', methods=['GET'])
def download_report():
    user_id = get_user_from_headers()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    target_role = request.args.get('target_role', 'Software Developer')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch User Profile
    cursor.execute("SELECT name, email, degree, year FROM Users WHERE id = ?", (user_id,))
    profile_data = dict(cursor.fetchone())
    profile_data['target_role'] = target_role
    
    # Fetch Skills
    cursor.execute("SELECT skill_name, score FROM Skills WHERE user_id = ?", (user_id,))
    skills = {row['skill_name']: row['score'] for row in cursor.fetchall()}
    
    # Fetch Assessments
    cursor.execute("SELECT assessment_name, score FROM Assessments WHERE user_id = ?", (user_id,))
    assessments = {row['assessment_name']: row['score'] for row in cursor.fetchall()}
    
    # Fetch Progress
    cursor.execute("SELECT * FROM Progress WHERE user_id = ?", (user_id,))
    progress_row = cursor.fetchone()
    completed_projects = []
    if progress_row and progress_row['projects_completed']:
        completed_projects = progress_row['projects_completed'].split(',')

    # Fetch Roadmap tasks
    cursor.execute("SELECT week, task, completed FROM Roadmaps WHERE user_id = ? ORDER BY week ASC", (user_id,))
    roadmap_tasks = [dict(row) for row in cursor.fetchall()]
    
    # Fetch suggested projects from catalog
    cursor.execute("SELECT * FROM Projects WHERE category = ?", (target_role,))
    projects = [dict(row) for row in cursor.fetchall()]
    
    conn.close()

    # Calculate Gaps & Readiness
    gaps = ai_engine.detect_skill_gaps(skills, target_role)
    readiness = ai_engine.calculate_readiness_score(skills, completed_projects, [], 85, assessments)

    # Compile PDF file
    pdf_filename = f"Readiness_Report_{user_id}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    
    success = pdf_generator.generate_pdf_report(
        pdf_path, 
        profile_data, 
        skills, 
        assessments, 
        readiness, 
        gaps, 
        roadmap_tasks, 
        projects
    )
    
    if success:
        return send_file(pdf_path, as_attachment=True, download_name="Internship_Readiness_Report.pdf")
    else:
        return jsonify({"error": "Could not generate PDF report"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
