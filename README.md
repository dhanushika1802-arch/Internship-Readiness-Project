# AI-Powered Internship Readiness & Personalized Learning Roadmap System

An intelligent, full-stack web application designed to help students evaluate their readiness for internships, identify skill gaps for specific industry roles, follow a personalized weekly learning roadmap, complete coding assessments, and download comprehensive readiness reports.

---

## Technical Stack
*   **Frontend**: React.js (built with Vite), HTML5, CSS3, JavaScript ES6
*   **Backend**: Python Flask REST API
*   **Database**: SQLite
*   **AI Engine**: Custom Natural Language Processing (NLP) resume parser, readiness scoring matrices, and automated gap detection algorithms

---

## Project Folder Structure

```
Internship Readiness Project/
├── backend/
│   ├── uploads/            # Location for uploaded resume PDFs
│   ├── venv/               # Python virtual environment
│   ├── app.py              # Main Flask REST API & routes
│   ├── database.py         # Database initialization, schemas & seeding
│   ├── ai_engine.py        # Resume parser, scoring rules & chatbot
│   ├── pdf_generator.py    # ReportLab PDF report compiler
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI elements (Sidebar, ChatbotDrawer)
│   │   ├── pages/          # View panels (Dashboard, Assessments, GapDetector, etc.)
│   │   ├── styles/         # CSS variables & layouts
│   │   ├── App.jsx         # App shell & router
│   │   └── main.jsx        # Client entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── run.bat                 # Automated double-server startup script
└── README.md               # Documentation guide
```

---

## Database Schemas

The database initializes as `backend/database.db` with the following SQLite tables:

1.  **Users** (`id`, `name`, `email`, `password`, `degree`, `year`)
2.  **Skills** (`id`, `user_id`, `skill_name`, `score`)
3.  **Assessments** (`id`, `user_id`, `assessment_name`, `score`)
4.  **Resumes** (`id`, `user_id`, `file_path`)
5.  **Roadmaps** (`id`, `user_id`, `week`, `task`, `completed`)
6.  **Projects** (`id`, `title`, `description`, `difficulty`, `category`)
7.  **Progress** (`id`, `user_id`, `completion_percentage`, `skills_completed`, `courses_completed`, `projects_completed`)

---

## Installation & Setup

### Option 1: Quick Start (Recommended for Windows)
Double-click the `run.bat` file in the project root folder. This automatically opens two terminal sessions, launching the Flask backend API on `http://127.0.0.1:5000` and the Vite React frontend client on `http://localhost:5173`.

---

### Option 2: Manual Setup

#### 1. Backend API Setup
1.  Open your terminal and navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Create a Python virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
    *   **Windows (Command Prompt)**: `.\venv\Scripts\activate.bat`
    *   **macOS / Linux**: `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Start the Flask server:
    ```bash
    python app.py
    ```

#### 2. Frontend Client Setup
1.  Open a new terminal window and navigate to the `frontend` folder:
    ```bash
    cd frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Start the Vite developer server:
    ```bash
    npm run dev
    ```

---

## How to Test the Application Walkthrough

1.  **User Authentication**:
    *   Open `http://localhost:5173` in your browser.
    *   Choose **Sign Up**, enter your registration details, and submit.
    *   Sign in using your newly created email and password.
2.  **Dashboard View**:
    *   Observe your initial **Readiness Score** gauge (initialized based on empty inputs).
    *   Your target role defaults to **Software Developer**. You can change your goal from the sidebar dropdown (e.g., to **AI Engineer** or **Cyber Security Analyst**), which dynamically recalculates your preparation statistics.
3.  **Resume Analyzer**:
    *   Click on **Resume Analyzer** in the sidebar.
    *   Upload or drag-and-drop a PDF resume file.
    *   Click **Submit for AI Parsing**. The scanner will analyze text strings and output extracted details: Education Major, Skills found, Projects discovered, and Certifications found.
    *   This will automatically insert new competencies into your profile, increasing your dashboard scores!
4.  **Skill Assessments**:
    *   Go to **Skill Assessments**.
    *   Start the test of your choice (e.g. Python, SQL, or AI/ML).
    *   Answer the 5 multiple choice questions before the 5-minute timer counts down.
    *   Submit the quiz to see your graded percentage, along with detailed explanations for every single question.
5.  **Gap Detector**:
    *   Go to **Skill Gap Detector**.
    *   Observe how your skill ratings compare against target requirements for your selected career.
    *   Review the lists of "Matched Skills" and "Missing Core Skills".
6.  **Roadmap & Project Library**:
    *   Navigate to **Learning Roadmap**.
    *   View your customized **6-Week Study Schedule** designed to target your missing skills.
    *   Toggle task completion check-boxes. This recalculates your overall roadmap percentage on the dashboard.
    *   View recommended courses, credentials, and hands-on projects selected based on your difficulty level.
7.  **Generate Report**:
    *   From the **Learning Roadmap** tab, click **Download PDF Report**.
    *   A dynamic ReportLab PDF is generated and downloaded to your system containing a summary of your profile, readiness score, strengths/weaknesses, test grades, role gaps, and weekly roadmap.
8.  **AI Career Coach**:
    *   Click the floating **AI Career Coach** bubble in the bottom right corner.
    *   Ask questions like: "What skills am I missing?", "Recommend a project for me", or "How can I improve my resume quality?". The assistant will answer by looking at your active readiness status.
