import React, { useState, useEffect } from 'react';
import './Profile.css';

export default function Profile({ user, setUser }) {
    const [name, setName] = useState("");
    const [degree, setDegree] = useState("");
    const [year, setYear] = useState(2);
    const [email, setEmail] = useState("");
    
    const [loading, setLoading] = useState(false);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const fetchProfile = async () => {
        setLoading(true);
        setError("");
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user/profile`, {
                headers: { 'Authorization': token }
            });

            if (response.ok) {
                const data = await response.json();
                setName(data.name || "");
                setDegree(data.degree || "");
                setYear(data.year || 2);
                setEmail(data.email || "");
            } else {
                setError("Failed to fetch user profile details.");
            }
        } catch (err) {
            setError("Cannot reach backend profile service.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProfile();
    }, []);

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        setUpdating(true);
        setError("");
        setSuccess("");
        
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token
                },
                body: JSON.stringify({
                    name: name,
                    degree: degree,
                    year: parseInt(year)
                })
            });

            if (response.ok) {
                setSuccess("Profile settings saved successfully!");
                // Update parent context and local storage
                const updatedUser = { ...user, name, degree, year: parseInt(year) };
                setUser(updatedUser);
                localStorage.setItem('user', JSON.stringify(updatedUser));
                
                // Automatically hide toast after 4 seconds
                setTimeout(() => {
                    setSuccess("");
                }, 4000);
            } else {
                setError("Failed to update profile changes.");
            }
        } catch (err) {
            setError("Database network error. Please check backend connection.");
        } finally {
            setUpdating(false);
        }
    };

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="spinner"></div>
                <p>Retrieving student configurations...</p>
            </div>
        );
    }

    return (
        <div className="profile-page-wrapper animated-card">
            <header className="page-header">
                <h1 className="page-title">Profile Settings</h1>
                <p className="page-subtitle">Manage your student credentials and enrollment information.</p>
            </header>

            {/* Success Toast */}
            {success && (
                <div className="profile-toast success">
                    <span className="toast-icon">✓</span>
                    <span className="toast-text">{success}</span>
                </div>
            )}

            {/* Error Toast */}
            {error && (
                <div className="profile-toast error">
                    <span className="toast-icon">⚠</span>
                    <span className="toast-text">{error}</span>
                </div>
            )}

            <div className="profile-card">
                {/* Profile Avatar Header Row */}
                <div className="profile-header-row">
                    <div className="profile-avatar-wrapper">
                        <div className="profile-avatar">
                            {name ? name.charAt(0).toUpperCase() : 'S'}
                        </div>
                        <div className="avatar-badge" title="Student Account">
                            ✓
                        </div>
                    </div>
                    <div className="profile-header-info">
                        <h2 className="profile-name-heading">{name || 'Student'}</h2>
                        <p className="profile-email-text">{email}</p>
                        <div className="profile-status-tag">
                            {degree || 'Computer Science'} • Year {year}
                        </div>
                    </div>
                </div>

                <hr className="profile-divider" />

                {/* Profile Form */}
                <form onSubmit={handleSaveProfile} className="profile-form">
                    {/* Section 1: Personal Information */}
                    <div className="profile-section">
                        <div className="section-title-box">
                            <h3 className="section-title">Personal Information</h3>
                            <p className="section-subtitle">Basic details associated with your student account.</p>
                        </div>

                        <div className="form-fields-grid">
                            <div className="form-field-group">
                                <label className="field-label" htmlFor="full-name-input">
                                    Full Name <span className="required-star">*</span>
                                </label>
                                <input 
                                    id="full-name-input"
                                    type="text" 
                                    value={name} 
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                    placeholder="Enter your full name"
                                    className="form-control" 
                                />
                            </div>

                            <div className="form-field-group">
                                <label className="field-label" htmlFor="email-input">
                                    Email Address <span className="readonly-badge">Read-only</span>
                                </label>
                                <input 
                                    id="email-input"
                                    type="email" 
                                    value={email} 
                                    disabled
                                    className="form-control readonly-control" 
                                />
                                <span className="field-hint">Email cannot be changed after registration.</span>
                            </div>
                        </div>
                    </div>

                    <hr className="profile-divider" />

                    {/* Section 2: Academic Information */}
                    <div className="profile-section">
                        <div className="section-title-box">
                            <h3 className="section-title">Academic Information</h3>
                            <p className="section-subtitle">University degree and cohort level for internship readiness matching.</p>
                        </div>

                        <div className="form-fields-grid">
                            <div className="form-field-group">
                                <label className="field-label" htmlFor="degree-input">
                                    Degree Major <span className="required-star">*</span>
                                </label>
                                <input 
                                    id="degree-input"
                                    type="text" 
                                    value={degree} 
                                    onChange={(e) => setDegree(e.target.value)}
                                    required
                                    placeholder="e.g. Computer Science & Engineering"
                                    className="form-control" 
                                />
                            </div>

                            <div className="form-field-group">
                                <label className="field-label" htmlFor="year-select">
                                    Year of Study <span className="required-star">*</span>
                                </label>
                                <select 
                                    id="year-select"
                                    value={year} 
                                    onChange={(e) => setYear(e.target.value)}
                                    className="form-control"
                                >
                                    <option value={1}>Year 1</option>
                                    <option value={2}>Year 2</option>
                                    <option value={3}>Year 3</option>
                                    <option value={4}>Year 4</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Form Footer Actions */}
                    <div className="profile-form-footer">
                        <button 
                            type="submit" 
                            className="btn-save-profile" 
                            disabled={updating}
                        >
                            {updating ? (
                                <>
                                    <span className="btn-spinner"></span>
                                    <span>Saving Changes...</span>
                                </>
                            ) : (
                                "Save Profile Details"
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
