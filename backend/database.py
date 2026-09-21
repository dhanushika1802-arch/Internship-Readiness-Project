import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            degree TEXT,
            year INTEGER,
            target_role TEXT DEFAULT 'Software Developer'
        )
    ''')

    # Ensure target_role column exists in existing DBs
    cursor.execute("PRAGMA table_info(Users)")
    columns = [row['name'] for row in cursor.fetchall()]
    if 'target_role' not in columns:
        cursor.execute("ALTER TABLE Users ADD COLUMN target_role TEXT DEFAULT 'Software Developer'")

    # Skills Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    ''')

    # Assessments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            assessment_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    ''')

    # Resumes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_path TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    ''')

    # Roadmaps Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER NOT NULL,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    ''')

    # Projects Table (Global library of project suggestions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Progress Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            completion_percentage INTEGER DEFAULT 0,
            skills_completed TEXT,  -- Comma-separated list of completed skill names
            courses_completed TEXT, -- Comma-separated list of completed course names
            projects_completed TEXT, -- Comma-separated list of completed project titles
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    ''')

    # Seed initial projects catalog if empty
    cursor.execute("SELECT COUNT(*) FROM Projects")
    if cursor.fetchone()[0] == 0:
        seed_projects = [
            # Python / Data Analyst
            ("Data Analyzer Dash", "Build a dashboard to analyze CSV files, plot charts, and calculate statistical data.", "Beginner", "Data Analyst"),
            ("SQL Sales Optimization", "Analyze historical store sales using SQL queries, creating joins, aggregations, and subqueries.", "Beginner", "Data Analyst"),
            ("E-Commerce BI Report", "Create an interactive dashboard matching sales KPIs using Tableau or PowerBI.", "Intermediate", "Data Analyst"),
            ("Financial Trend Forecaster", "Perform time-series data analysis on stock market datasets using pandas, NumPy, and statsmodels.", "Advanced", "Data Analyst"),

            # Python / Data Scientist
            ("House Price Predictor", "Build a linear regression model to predict housing prices using scikit-learn and pandas.", "Beginner", "Data Scientist"),
            ("Customer Segmentation System", "Create a K-Means clustering model to group customers based on purchasing behavior.", "Intermediate", "Data Scientist"),
            ("Predictive Churn Classifier", "Implement an end-to-end classification model using Random Forest/XGBoost to predict customer churn.", "Advanced", "Data Scientist"),

            # AI Engineer
            ("Handwritten Digit Classifier", "Train a Convolutional Neural Network (CNN) on the MNIST dataset using PyTorch or TensorFlow.", "Beginner", "AI Engineer"),
            ("Movie Sentiment Analyzer", "Build a sentiment classification model for text reviews using LSTM or Transformer networks.", "Intermediate", "AI Engineer"),
            ("RAG Medical Chatbot", "Implement a Retrieval-Augmented Generation chatbot using LangChain, Vector DB, and a local LLM API.", "Advanced", "AI Engineer"),

            # Software Developer (Java / Python / C++)
            ("Student Registry Manager", "Create a command-line application to manage student profiles using OOP concepts and files in Java.", "Beginner", "Software Developer"),
            ("Multi-Threaded Web Crawler", "Build a concurrent web scraper in Java or Python that downloads webpages and extracts text links safely.", "Intermediate", "Software Developer"),
            ("Distributed Key-Value Store", "Design a custom TCP-based distributed storage node supporting CRUD operations with consensus logging.", "Advanced", "Software Developer"),

            # Full Stack Developer
            ("Personal Blog Platform", "Develop a simple multi-user blogging site using React frontend, Flask API, and SQLite DB.", "Beginner", "Full Stack Developer"),
            ("Collaborative Task Planner", "Build a Trello-like task manager with drag-and-drop boards, user authentication, and real-time updates.", "Intermediate", "Full Stack Developer"),
            ("Enterprise E-Learning Portal", "Construct a fully featured learning portal with video streaming, quiz scoring, and interactive progress bars.", "Advanced", "Full Stack Developer"),

            # Cyber Security Analyst
            ("Local Port Scanner", "Write a Python script that probes a target IP for open ports and identifies active protocols.", "Beginner", "Cyber Security Analyst"),
            ("Network Packet sniffer", "Create a command-line tool using Scapy to capture and inspect TCP/IP packet headers on a local network.", "Intermediate", "Cyber Security Analyst"),
            ("Intrusion Detection Shield", "Build a rule-based network intrusion detection system using log analysis, reporting alerts to a dashboard.", "Advanced", "Cyber Security Analyst")
        ]
        cursor.executemany("INSERT INTO Projects (title, description, difficulty, category) VALUES (?, ?, ?, ?)", seed_projects)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
