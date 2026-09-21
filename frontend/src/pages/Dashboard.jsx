import React, { useState, useEffect } from 'react';
import './Dashboard.css';

export default function Dashboard({ targetRole, setActiveTab }) {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchStats = async () => {
        setLoading(true);
        setError("");
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/dashboard/stats?target_role=${encodeURIComponent(targetRole)}`, {
                headers: {
                    'Authorization': token
                }
            });

            if (response.ok) {
                const data = await response.json();
                setStats(data);
            } else {
                setError("Failed to fetch dashboard statistics.");
            }
        } catch (err) {
            setError("Cannot reach backend server. Please make sure the Flask API is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, [targetRole]);

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner"></div>
                <p>Analyzing readiness parameters...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-error glass-panel">
                <h3>⚠️ Connection Error</h3>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={fetchStats}>Retry Connection</button>
            </div>
        );
    }

    const { readiness, skills, progress } = stats || {};
    const score = readiness?.overall_score || 0;
    const level = readiness?.readiness_level || "Beginner";
    const strengths = readiness?.strengths || [];
    const weaknesses = readiness?.weaknesses || [];

    // Calculate SVG circle dashoffset
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    // Get color theme for readiness level
    const getLevelColorClass = (lvl) => {
        if (lvl === 'Beginner') return 'level-beginner';
        if (lvl === 'Developing') return 'level-developing';
        if (lvl === 'Internship Ready') return 'level-ready';
        return 'level-industry';
    };

    return (
        <div className="dashboard-wrapper animated-card">
            <header className="dashboard-header">
                <div>
                    <h1 className="page-title">Welcome Back, {stats?.profile?.name || 'Student'}!</h1>
                    <p className="page-subtitle">Track your preparation, bridge gaps, and earn your internship role.</p>
                </div>
            </header>

            {/* Quick Metrics Row */}
            <section className="metrics-summary-row">
                <div className="metric-card glass-panel">
                    <div className="metric-icon">🎯</div>
                    <div className="metric-details">
                        <p className="metric-label">Target Role</p>
                        <h4 className="metric-val">{targetRole}</h4>
                    </div>
                </div>
                
                <div className="metric-card glass-panel">
                    <div className="metric-icon">✍️</div>
                    <div className="metric-details">
                        <p className="metric-label">Tests Finished</p>
                        <h4 className="metric-val">{Object.keys(stats?.assessments || {}).length} / 5</h4>
                    </div>
                </div>

                <div className="metric-card glass-panel">
                    <div className="metric-icon">📈</div>
                    <div className="metric-details">
                        <p className="metric-label">Roadmap Completion</p>
                        <h4 className="metric-val">{progress?.completion_percentage || 0}%</h4>
                    </div>
                </div>
            </section>

            {/* Main Content Layout Grid */}
            <div className="dashboard-grid">
                
                {/* Left Panel: Circular readiness score & key insights */}
                <div className="left-panel-grid">
                    
                    <div className="glass-panel score-analysis-card">
                        <h3>Readiness Scoring Engine</h3>
                        <p className="section-desc">Calculated in real-time using resume checks, completed courses, and testing results.</p>
                        
                        <div className="score-viz-block">
                            <div className="radial-progress-container">
                                <svg className="radial-progress-svg" width="160" height="160">
                                    <defs>
                                        <linearGradient id="teal-blue-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" stopColor="#2563EB" />
                                            <stop offset="100%" stopColor="#14B8A6" />
                                        </linearGradient>
                                    </defs>
                                    <circle className="radial-progress-bg" cx="80" cy="80" r={radius} />
                                    <circle 
                                        className="radial-progress-bar" 
                                        cx="80" 
                                        cy="80" 
                                        r={radius} 
                                        strokeDasharray={circumference}
                                        strokeDashoffset={strokeDashoffset}
                                    />
                                </svg>
                                <div className="radial-progress-text">
                                    <span className="radial-score">{score}</span>
                                    <span className="radial-label">Readiness</span>
                                </div>
                            </div>

                            <div className="score-details-text">
                                <div className={`badge-readiness ${getLevelColorClass(level)}`}>
                                    {level}
                                </div>
                                <p className="readiness-descriptor">
                                    {score <= 40 && "You are beginning your internship journey. Try completing MCQ tests and uploading your resume to check your initial standing."}
                                    {score > 40 && score <= 70 && "You are developing critical competencies. Focus on covering missing items in the Gap Detector and learning roadmap."}
                                    {score > 70 && score <= 90 && "Outstanding! Your profile details indicate you have baseline skills needed to secure an internship."}
                                    {score > 90 && "Congratulations! You possess industry-ready capabilities and a highly competitive profile."}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="glass-panel insights-card">
                        <h3>Profile Insights</h3>
                        <p className="section-desc">AI recommendations to improve your readiness score.</p>
                        
                        <ul className="insight-list">
                            {strengths.map((st, i) => (
                                <li key={`str-${i}`} className="insight-item strength">
                                    <span>✔️</span>
                                    <div>{st}</div>
                                </li>
                            ))}
                            {weaknesses.map((wk, i) => (
                                <li key={`wk-${i}`} className="insight-item weakness">
                                    <span>⚠️</span>
                                    <div>{wk}</div>
                                </li>
                            ))}
                        </ul>
                    </div>

                </div>

                {/* Right Panel: Skills Competency Tracks */}
                <div className="glass-panel skills-competency-card">
                    <h3>Technical Skill Index</h3>
                    <p className="section-desc">Student technical rankings. Upload a resume or finish assessment tests to raise scores.</p>
                    
                    <div className="skills-bars-list">
                        {['Python', 'Java', 'SQL', 'AI/ML', 'Web Development', 'Cyber Security'].map(skillName => {
                            const val = skills?.[skillName] || 0;
                            return (
                                <div key={skillName} className="skill-progress-bar-row">
                                    <div className="skill-meta">
                                        <span className="skill-name">{skillName}</span>
                                        <span className="skill-percent">{val}%</span>
                                    </div>
                                    <div className="progress-track">
                                        <div className="progress-fill" style={{ width: `${val}%` }}></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="quick-actions-box">
                        <h4>Need to raise scores?</h4>
                        <div className="actions-button-grid">
                            <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('resume')}>
                                📄 Upload Resume
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('assessments')}>
                                📝 Take Skill Test
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
