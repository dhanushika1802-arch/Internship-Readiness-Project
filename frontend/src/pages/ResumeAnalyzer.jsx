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
                            <h3>AI Parser Extraction Report</h3>
                            <div className="quality-score-badge">
                                <span>Resume Quality:</span>
                                <strong>{result.resume_quality}/100</strong>
                            </div>
                        </div>

                        <div className="extracted-fields-grid">
                            
                            <div className="extraction-block">
                                <div className="block-title">🎓 Education Found</div>
                                <p className="block-val">{result.education}</p>
                            </div>

                            <div className="extraction-block">
                                <div className="block-title">🛠️ Extracted Skills</div>
                                <div className="skills-badge-wrap">
                                    {result.skills.length > 0 ? (
                                        result.skills.map(sk => (
                                            <span key={sk} className="skill-badge">{sk}</span>
                                        ))
                                    ) : (
                                        <span className="no-badge-text">No matching skills identified (check keyword formatting).</span>
                                    )}
                                </div>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">📂 Identified Projects & Experience Items</div>
                                <ul className="bullet-results-list">
                                    {result.projects.map((proj, idx) => (
                                        <li key={idx}>{proj}</li>
                                    ))}
                                </ul>
                            </div>

                            <div className="extraction-block full-width">
                                <div className="block-title">🏅 Certifications Identified</div>
                                <ul className="bullet-results-list">
                                    {result.certifications.map((cert, idx) => (
                                        <li key={idx}>{cert}</li>
                                    ))}
                                </ul>
                            </div>

                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
