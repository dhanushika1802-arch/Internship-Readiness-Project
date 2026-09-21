import React, { useState, useEffect } from 'react';
import './RoadmapView.css';

export default function RoadmapView({ targetRole }) {
    const [roadmap, setRoadmap] = useState([]);
    const [suggestions, setSuggestions] = useState(null);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [downloading, setDownloading] = useState(false);
    const [error, setError] = useState("");

    const fetchRoadmapData = async () => {
        setLoading(true);
        setError("");
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            // 1. Fetch Roadmap & Suggestions
            const responseRoadmap = await fetch(`${import.meta.env.VITE_API_URL}/api/roadmap?target_role=${encodeURIComponent(targetRole)}`, {
                headers: { 'Authorization': token }
            });

            // 2. Fetch Projects
            const responseProjects = await fetch(`${import.meta.env.VITE_API_URL}/api/projects/recommended?target_role=${encodeURIComponent(targetRole)}`, {
                headers: { 'Authorization': token }
            });

            if (responseRoadmap.ok && responseProjects.ok) {
                const dataRoadmap = await responseRoadmap.json();
                const dataProjects = await responseProjects.json();

                setRoadmap(dataRoadmap.roadmap);
                setSuggestions(dataRoadmap.suggestions);
                setProjects(dataProjects);
            } else {
                setError("Failed to load customized roadmap data.");
            }
        } catch (err) {
            setError("Cannot reach backend server. Please verify Flask configuration.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRoadmapData();
    }, [targetRole]);

    const handleToggleTask = async (id, currentStatus) => {
        const token = localStorage.getItem('token');
        const newStatus = currentStatus === 1 ? 0 : 1;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/roadmap/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token || ''
                },
                body: JSON.stringify({ id, completed: newStatus })
            });

            if (response.ok) {
                // Update local state
                setRoadmap(prev => prev.map(item => {
                    if (item.id === id) {
                        return { ...item, completed: newStatus };
                    }
                    return item;
                }));
            }
        } catch (err) {
            console.error("Error updating roadmap task status", err);
        }
    };

    const handleDownloadReport = async () => {
        setDownloading(true);
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/report/download?target_role=${encodeURIComponent(targetRole)}`, {
                headers: { 'Authorization': token || '' }
            });

            if (response.ok) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = `Internship_Readiness_Report_${targetRole.replace(/\s+/g, '_')}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                alert("Failed to build PDF report. Streaming fallback.");
            }
        } catch (error) {
            alert("Error downloading report. Check backend console log.");
        } finally {
            setDownloading(false);
        }
    };

    if (loading) {
        return (
            <div className="roadmap-loading">
                <div className="spinner"></div>
                <p>Generating personalized learning nodes...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="roadmap-error glass-panel">
                <h3>⚠️ Roadmap Error</h3>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={fetchRoadmapData}>Retry Sync</button>
            </div>
        );
    }

    // Calculate completion percentage locally
    const totalTasks = roadmap.length;
    const completedTasks = roadmap.filter(item => item.completed === 1).length;
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    return (
        <div className="roadmap-view-wrapper animated-card">
            
            <header className="roadmap-header-row">
                <div>
                    <h1 className="page-title">Learning Roadmap</h1>
                    <p className="page-subtitle">Your personalized {targetRole} study plan. Check off items as you complete them.</p>
                </div>
                <button 
                    onClick={handleDownloadReport} 
                    className="btn btn-primary download-report-btn" 
                    disabled={downloading}
                >
                    {downloading ? "Building Report..." : "📥 Download PDF Report"}
                </button>
            </header>

            {/* Progress Bar Widget */}
            <div className="glass-panel roadmap-progress-card">
                <div className="progress-card-meta">
                    <h3>Roadmap Progress</h3>
                    <span className="progress-card-percentage">{completionRate}% Complete</span>
                </div>
                <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${completionRate}%` }}></div>
                </div>
                <p className="progress-tasks-fraction">Completed {completedTasks} out of {totalTasks} weekly checkpoints</p>
            </div>

            <div className="roadmap-grid-layout">
                
                {/* Left Side: 6-Week Tasks Checklist */}
                <div className="glass-panel roadmap-weeks-card">
                    <h3>Weekly Learning Schedule</h3>
                    <p className="section-desc">Mark each week's milestones as complete once you finish studying recommended resources and building code.</p>

                    <div className="weeks-list">
                        {roadmap.map((item) => (
                            <div key={item.id} className={`week-row ${item.completed === 1 ? 'task-complete' : ''}`}>
                                <div className="week-checkbox-col">
                                    <input 
                                        type="checkbox" 
                                        checked={item.completed === 1}
                                        onChange={() => handleToggleTask(item.id, item.completed)}
                                        className="week-check-box"
                                        id={`check-${item.id}`}
                                    />
                                </div>
                                <label className="week-content-col" htmlFor={`check-${item.id}`}>
                                    <span className="week-number-tag">Week {item.week}</span>
                                    <p className="week-task-text">{item.task}</p>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Side: Courses, Certs, & Projects */}
                <div className="right-recommendations-col">
                    
                    {/* Catalog Projects */}
                    <div className="glass-panel projects-recommendation-card">
                        <h3>Recommended Projects</h3>
                        <p className="section-desc">Hands-on systems selected based on your missing skill gaps and difficulty levels.</p>

                        <div className="recommended-projects-list">
                            {projects.map((proj) => (
                                <div key={proj.id} className="recommended-project-item">
                                    <div className="project-top-row">
                                        <h4>{proj.title}</h4>
                                        <span className={`diff-badge ${proj.difficulty.toLowerCase()}`}>
                                            {proj.difficulty}
                                        </span>
                                    </div>
                                    <p className="project-desc">{proj.description}</p>
                                    <div className="project-meta-bottom">
                                        <span>Focus: <strong>{proj.category}</strong></span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Courses & Certs */}
                    <div className="glass-panel materials-card">
                        <h3>Courses & Certifications</h3>
                        <p className="section-desc">Study guides and credentials matching your profile goals.</p>

                        <div className="materials-sections">
                            <div className="materials-sub">
                                <h5>Online Classes</h5>
                                <ul>
                                    {suggestions?.courses?.map((course, idx) => (
                                        <li key={idx}>🔗 {course}</li>
                                    ))}
                                </ul>
                            </div>
                            
                            <div className="materials-sub">
                                <h5>Certificates</h5>
                                <ul>
                                    {suggestions?.certifications?.map((cert, idx) => (
                                        <li key={idx}>🎓 {cert}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
}
