import React, { useState, useEffect } from 'react';
import './GapDetector.css';

export default function GapDetector({ targetRole, setActiveTab }) {
    const [gapData, setGapData] = useState(null);
    const [userSkills, setUserSkills] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchGapData = async () => {
        setLoading(true);
        setError("");
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            // 1. Fetch Gaps with real role comparison
            const responseGap = await fetch(`${import.meta.env.VITE_API_URL}/api/gap-analysis?target_role=${encodeURIComponent(targetRole)}`, {
                headers: { 'Authorization': token }
            });

            // 2. Fetch User Stats (to get actual scores of skills)
            const responseStats = await fetch(`${import.meta.env.VITE_API_URL}/api/dashboard/stats?target_role=${encodeURIComponent(targetRole)}`, {
                headers: { 'Authorization': token }
            });

            if (responseGap.ok && responseStats.ok) {
                const dataGap = await responseGap.json();
                const dataStats = await responseStats.json();
                
                setGapData(dataGap);
                setUserSkills(dataStats.skills || {});
            } else {
                setError("Failed to fetch gap analysis data.");
            }
        } catch (err) {
            setError("Could not establish connection to Python API.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGapData();
    }, [targetRole]);

    if (loading) {
        return (
            <div className="gap-loading">
                <div className="spinner"></div>
                <p>Auditing real skill mappings...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="gap-error glass-panel">
                <h3>⚠️ Analysis Error</h3>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={fetchGapData}>Retry Audit</button>
            </div>
        );
    }

    // Condition 1: Resume has not been analyzed yet
    if (gapData && gapData.has_analyzed_resume === false) {
        return (
            <div className="gap-detector-wrapper animated-card">
                <header className="page-header">
                    <h1 className="page-title">Skill Gap Detector</h1>
                    <p className="page-subtitle">Verify how your current technical profile aligns with the standard industry requirements for a <strong>{targetRole}</strong> role.</p>
                </header>

                <div className="glass-panel gap-empty-notice-card">
                    <div className="empty-notice-icon">📄</div>
                    <h3>Analyze your resume first to view your skill gap.</h3>
                    <p>
                        Your skill gap analysis is generated from real technical evidence in your resume. 
                        Upload your resume in the Resume Analyzer to detect your active skills and compare them against <strong>{targetRole}</strong> requirements.
                    </p>
                    <button className="btn btn-primary" onClick={() => setActiveTab('resume')}>
                        📄 Go to Resume Analyzer
                    </button>
                </div>
            </div>
        );
    }

    // Condition 2: Resume analyzed, but no technical skills detected from text
    if (gapData && gapData.has_skills === false) {
        return (
            <div className="gap-detector-wrapper animated-card">
                <header className="page-header">
                    <h1 className="page-title">Skill Gap Detector</h1>
                    <p className="page-subtitle">Verify how your current technical profile aligns with the standard industry requirements for a <strong>{targetRole}</strong> role.</p>
                </header>

                <div className="glass-panel gap-empty-notice-card">
                    <div className="empty-notice-icon">🔍</div>
                    <h3>No technical skills detected yet. Upload and analyze your resume.</h3>
                    <p>
                        We could not detect core programming or technical skills from your uploaded document. 
                        Ensure your resume lists technical competencies (such as Python, Java, SQL, Web, or Security) or take an assessment quiz to validate your skills.
                    </p>
                    <div className="empty-notice-actions">
                        <button className="btn btn-primary" onClick={() => setActiveTab('resume')}>
                            📄 Upload Resume in Analyzer
                        </button>
                        <button className="btn btn-secondary" onClick={() => setActiveTab('assessments')}>
                            📝 Take Skill Assessment
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const { match_percentage = 0, matched_skills = [], missing_skills = [], required_skills = [], targets = {} } = gapData || {};

    return (
        <div className="gap-detector-wrapper animated-card">
            <header className="page-header">
                <h1 className="page-title">Skill Gap Detector</h1>
                <p className="page-subtitle">Verify how your current technical profile aligns with the standard industry requirements for a <strong>{targetRole}</strong> role.</p>
            </header>

            <div className="gap-layout-grid">
                
                {/* Left Card: Match Rate & Gaps list */}
                <div className="glass-panel gap-status-card">
                    <div className="match-percentage-badge">
                        <div className="percentage-circle">
                            <h2>{match_percentage}%</h2>
                            <p>Skill Match</p>
                        </div>
                    </div>

                    <div className="gap-summary-lists">
                        <div className="summary-section">
                            <h4>Matched Skills ({matched_skills.length})</h4>
                            <div className="matched-tags-list">
                                {matched_skills.length > 0 ? (
                                    matched_skills.map(sk => (
                                        <div key={sk} className="matched-tag">
                                            <span className="tag-check">✔</span> {sk}
                                        </div>
                                    ))
                                ) : (
                                    <p className="no-tags-msg">No required skills matched yet for {targetRole}.</p>
                                )}
                            </div>
                        </div>

                        <div className="summary-section">
                            <h4>Missing Core Skills ({missing_skills.length})</h4>
                            <div className="missing-tags-list">
                                {missing_skills.length > 0 ? (
                                    missing_skills.map(sk => (
                                        <div key={sk} className="missing-tag">
                                            <span className="tag-warn">✕</span> {sk}
                                        </div>
                                    ))
                                ) : (
                                    <div className="fully-matched-alert">
                                        ✨ <strong>Congratulations!</strong> You have no missing core skills for this role! You are internship-ready.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Card: Detail Comparison Bars */}
                <div className="glass-panel comparison-chart-card">
                    <h3>Skill Competency vs Target Threshold</h3>
                    <p className="section-desc">
                        Direct comparison of your real resume & assessment competency against industry benchmarks for <strong>{targetRole}</strong>.
                    </p>

                    <div className="comparison-bars-list">
                        {required_skills.map(skName => {
                            const userVal = userSkills[skName] || 0;
                            const targetVal = targets[skName] || 75;
                            
                            return (
                                <div key={skName} className="comparison-row">
                                    <div className="comparison-meta">
                                        <span className="comp-skill-name">{skName}</span>
                                        <div className="comp-score-labels">
                                            <span className="label-user">
                                                Current: <strong>{userVal > 0 ? `${userVal}%` : 'Not Demonstrated (0%)'}</strong>
                                            </span>
                                            <span className="label-target">Target: <strong>{targetVal}%</strong></span>
                                        </div>
                                    </div>
                                    <div className="dual-progress-track">
                                        {/* User Fill */}
                                        <div 
                                            className={`user-fill ${userVal >= targetVal ? 'satisfies' : 'lacks'}`} 
                                            style={{ width: `${userVal}%` }}
                                        ></div>
                                        {/* Target Marker */}
                                        <div className="target-marker" style={{ left: `${targetVal}%` }}>
                                            <span className="marker-tip"></span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {missing_skills.length > 0 && (
                        <div className="gap-remediation-box">
                            <h4>How to bridge the gaps?</h4>
                            <p>We recommend starting with the online assessment tests to validate your capability, or follow your personalized weekly roadmap for targeted modules.</p>
                            <div className="remediation-actions">
                                <button className="btn btn-primary btn-sm" onClick={() => setActiveTab('assessments')}>
                                    📝 Go to Assessment Room
                                </button>
                                <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('roadmap')}>
                                    🗺️ View Learning Roadmap
                                </button>
                            </div>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
