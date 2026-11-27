import React, { useState } from 'react';
import './ResumeAnalyzer.css';

export default function ResumeAnalyzer() {
    const [file, setFile] = useState(null);
    const [dragging, setDragging] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragging(true);
    };

    const handleDragLeave = () => {
        setDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.type === "application/pdf" || droppedFile.name.endsWith(".pdf")) {
                setFile(droppedFile);
                setError("");
            } else {
                setError("Please select a PDF document file.");
            }
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (selectedFile.type === "application/pdf" || selectedFile.name.endsWith(".pdf")) {
                setFile(selectedFile);
                setError("");
            } else {
                setError("Please select a PDF document file.");
            }
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("No file selected.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/resume/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': token || ''
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setResult(data.parsed_data);
            } else {
                setError(data.error || "Failed to process resume.");
            }
        } catch (err) {
            setError("Network connection issue. Make sure your Python Flask backend is running on port 5000.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="resume-analyzer-wrapper animated-card">
            <header className="page-header">
                <h1 className="page-title">Resume Analyzer</h1>
                <p className="page-subtitle">Upload your PDF resume. Our AI parser will scan formatting, skills, projects, and educational profiles.</p>
            </header>

            <div className="resume-layout-grid">
                
                {/* File Uploader Card */}
                <div className="glass-panel uploader-card">
                    <h3>Upload Resume PDF</h3>
                    <p className="section-desc">Submit your resume to auto-populate profile skills and calculate your initial scoring ranking.</p>

                    <form onSubmit={handleUpload}>
                        <div 
                            className={`drag-drop-zone ${dragging ? 'dragover' : ''} ${file ? 'has-file' : ''}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                        >
                            <div className="zone-icon">📁</div>
                            <div className="zone-instructions">
                                {file ? (
                                    <>
                                        <p className="filename-display">Selected: <strong>{file.name}</strong></p>
                                        <p className="filesize-display">({(file.size / 1024).toFixed(1)} KB)</p>
                                    </>
                                ) : (
                                    <>
                                        <p>Drag and drop your PDF resume here or</p>
                                        <label htmlFor="file-input-id" className="file-input-label">Browse Files</label>
                                    </>
                                )}
                            </div>
                            <input 
                                id="file-input-id" 
                                type="file" 
                                accept=".pdf"
                                onChange={handleFileChange}
                                className="raw-file-input"
                            />
                        </div>

                        {error && <div className="alert alert-error">{error}</div>}

                        <div className="uploader-actions">
                            {file && (
                                <button type="button" className="btn btn-secondary" onClick={() => setFile(null)} disabled={loading}>
                                    Clear
                                </button>
                            )}
                            <button type="submit" className="btn btn-primary" disabled={!file || loading}>
                                {loading ? "Analyzing Layout..." : "Submit for AI Parsing"}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Loading indicator */}
                {loading && (
                    <div className="glass-panel loading-status-panel">
                        <div className="scanner-line"></div>
                        <div className="spinner"></div>
                        <h4>Reading resume layout structures...</h4>
                        <p>Mapping technical skills, checking grammar keywords, and extracting projects database catalog.</p>
                    </div>
                )}

                {/* Analysis Report View */}
                {result && !loading && (
                    <div className="glass-panel analysis-results-panel">
                        <div className="results-header">
                            <div>
                                <h3>AI Parser Extraction Report</h3>
                                {result.score_explanation && (
                                    <p className="section-desc" style={{ marginTop: '0.35rem', fontSize: '0.85rem' }}>
                                        {result.score_explanation}
                                    </p>
                                )}
                            </div>
                            <div className="quality-score-badge">
                                <span>Resume Quality:</span>
                                <strong>{result.resume_quality}/100</strong>
                            </div>
                        </div>

                        <div className="extracted-fields-grid">
                            
                            <div className="extraction-block full-width">
                                <div className="block-title">🎓 Education Found</div>
                                {Array.isArray(result.education) && result.education.length > 0 && !result.education[0].startsWith("No ") && result.education[0] !== "Not found in resume" ? (
                                    <ul className="bullet-results-list">
                                        {result.education.map((edu, idx) => (
                                            <li key={idx}><span className="block-val">{edu}</span></li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="block-val" style={{ color: 'var(--text-muted)', fontWeight: 'normal' }}>
                                        {typeof result.education === 'string' && !result.education.startsWith("No ") ? result.education : "No education details found in resume"}
                                    </p>
                                )}
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">🛠️ Extracted Technical Skills</div>
                                <div className="skills-badge-wrap">
                                    {result.skills && result.skills.length > 0 && !result.skills[0].startsWith("No ") && result.skills[0] !== "Not found in resume" ? (
                                        result.skills.map(sk => (
                                            <span key={sk} className="skill-badge">{sk}</span>
                                        ))
                                    ) : (
                                        <span className="no-badge-text">No technical skills found in resume</span>
                                    )}
                                </div>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">📁 Identified Projects</div>
                                <ul className="bullet-results-list">
                                    {result.projects && result.projects.length > 0 && !result.projects[0].startsWith("No ") && result.projects[0] !== "Not found in resume" ? (
                                        result.projects.map((proj, idx) => (
                                            <li key={idx}>{proj}</li>
                                        ))
                                    ) : (
                                        <li style={{ color: 'var(--text-muted)' }}>No projects found in resume</li>
                                    )}
                                </ul>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">💼 Internship / Work Experience</div>
                                <ul className="bullet-results-list">
                                    {result.experience && result.experience.length > 0 && !result.experience[0].startsWith("No ") && result.experience[0] !== "Not found in resume" ? (
                                        result.experience.map((exp, idx) => (
                                            <li key={idx}>{exp}</li>
                                        ))
                                    ) : (
                                        <li style={{ color: 'var(--text-muted)' }}>No internship or work experience found in resume</li>
                                    )}
                                </ul>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">📜 Certifications Identified</div>
                                <ul className="bullet-results-list">
                                    {result.certifications && result.certifications.length > 0 && !result.certifications[0].startsWith("No ") && result.certifications[0] !== "Not found in resume" ? (
                                        result.certifications.map((cert, idx) => (
                                            <li key={idx}>{cert}</li>
                                        ))
                                    ) : (
                                        <li style={{ color: 'var(--text-muted)' }}>No certifications found in resume</li>
                                    )}
                                </ul>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">🏆 Achievements</div>
                                <ul className="bullet-results-list">
                                    {result.achievements && result.achievements.length > 0 && !result.achievements[0].startsWith("No ") && result.achievements[0] !== "Not found in resume" ? (
                                        result.achievements.map((ach, idx) => (
                                            <li key={idx}>{ach}</li>
                                        ))
                                    ) : (
                                        <li style={{ color: 'var(--text-muted)' }}>No achievements found in resume</li>
                                    )}
                                </ul>
                            </div>

                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
