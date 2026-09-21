import React, { useState } from 'react';
import './LoginRegister.css';

export default function LoginRegister({ onLoginSuccess }) {
    const [isLogin, setIsLogin] = useState(true);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [degree, setDegree] = useState("Computer Science");
    const [year, setYear] = useState(2);
    
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");
        setLoading(true);

        const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
        const payload = isLogin 
            ? { email, password } 
            : { name, email, password, degree, year: parseInt(year) };

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                if (isLogin) {
                    setSuccess("Login successful!");
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    setTimeout(() => {
                        onLoginSuccess(data.user);
                    }, 500);
                } else {
                    setSuccess("Registration successful! Please login.");
                    setIsLogin(true);
                    setName("");
                    setPassword("");
                }
            } else {
                setError(data.error || "An error occurred. Please try again.");
            }
        } catch (err) {
            setError("Cannot connect to authorization server. Please ensure Flask is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page-wrapper">
            <div className="auth-background-shapes">
                <div className="shape circle-1"></div>
                <div className="shape circle-2"></div>
            </div>

            <div className="auth-card glass-panel animated-card">
                <div className="auth-header">
                    <h2>{isLogin ? "Welcome Back" : "Create Account"}</h2>
                    <p>{isLogin ? "Sign in to monitor your internship readiness" : "Fill details to start your custom learning path"}</p>
                </div>

                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    {!isLogin && (
                        <div className="input-group">
                            <label className="input-label">Full Name</label>
                            <input 
                                type="text" 
                                required 
                                value={name} 
                                onChange={(e) => setName(e.target.value)}
                                className="input-field"
                                placeholder="John Doe"
                            />
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label">Email Address</label>
                        <input 
                            type="email" 
                            required 
                            value={email} 
                            onChange={(e) => setEmail(e.target.value)}
                            className="input-field"
                            placeholder="john@example.com"
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <input 
                            type="password" 
                            required 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                            placeholder="••••••••"
                        />
                    </div>

                    {!isLogin && (
                        <div className="form-row">
                            <div className="input-group half-width">
                                <label className="input-label">Degree Major</label>
                                <input 
                                    type="text" 
                                    required 
                                    value={degree} 
                                    onChange={(e) => setDegree(e.target.value)}
                                    className="input-field"
                                    placeholder="e.g. Computer Science"
                                />
                            </div>

                            <div className="input-group half-width">
                                <label className="input-label">Year of Study</label>
                                <select 
                                    value={year} 
                                    onChange={(e) => setYear(e.target.value)}
                                    className="input-field"
                                >
                                    <option value={1}>Year 1</option>
                                    <option value={2}>Year 2</option>
                                    <option value={3}>Year 3</option>
                                    <option value={4}>Year 4</option>
                                </select>
                            </div>
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary auth-submit-btn" disabled={loading}>
                        {loading ? "Processing..." : isLogin ? "Sign In" : "Register"}
                    </button>
                </form>

                <div className="auth-toggle-prompt">
                    <p>
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <button onClick={() => { setIsLogin(!isLogin); setError(""); setSuccess(""); }} className="toggle-btn-link">
                            {isLogin ? "Sign Up" : "Log In"}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
