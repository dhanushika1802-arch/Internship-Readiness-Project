import React, { useState, useEffect } from 'react';
import './Assessments.css';

export default function Assessments() {
    const categories = ['Python', 'Java', 'SQL', 'AI/ML', 'Web Development'];
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    // Timer state
    const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
    const [quizActive, setQuizActive] = useState(false);

    useEffect(() => {
        let timer;
        if (quizActive && timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft(prev => prev - 1);
            }, 1000);
        } else if (timeLeft === 0 && quizActive) {
            handleSubmitQuiz();
        }
        return () => clearInterval(timer);
    }, [timeLeft, quizActive]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    };

    const handleStartTest = async (category) => {
        setLoading(true);
        setError("");
        setResult(null);
        setAnswers({});
        setCurrentIdx(0);
        setTimeLeft(300);

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/assessments/questions?category=${encodeURIComponent(category)}`);
            if (response.ok) {
                const data = await response.json();
                setQuestions(data);
                setSelectedCategory(category);
                setQuizActive(true);
            } else {
                setError("Failed to fetch assessment questions.");
            }
        } catch (err) {
            setError("Cannot reach backend. Make sure the server is online.");
        } finally {
            setLoading(false);
        }
    };

    const handleSelectOption = (qId, option) => {
        setAnswers(prev => ({
            ...prev,
            [qId]: option
        }));
    };

    const handleSubmitQuiz = async () => {
        setQuizActive(false);
        setSubmitting(true);
        setError("");

        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/assessments/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token || ''
                },
                body: JSON.stringify({
                    category: selectedCategory,
                    answers: answers
                })
            });

            if (response.ok) {
                const data = await response.json();
                setResult(data);
            } else {
                setError("Failed to submit assessment answers.");
            }
        } catch (err) {
            setError("Could not submit test due to backend connection error.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleBackToMenu = () => {
        setSelectedCategory(null);
        setQuestions([]);
        setResult(null);
        setQuizActive(false);
    };

    if (loading) {
        return (
            <div className="assessment-loading">
                <div className="spinner"></div>
                <p>Loading questions, prepare your console...</p>
            </div>
        );
    }

    if (submitting) {
        return (
            <div className="assessment-loading">
                <div className="spinner"></div>
                <p>Grading your assessment and updating profile scores...</p>
            </div>
        );
    }

    return (
        <div className="assessments-wrapper animated-card">
            <header className="page-header">
                <h1 className="page-title">Skill Assessment Room</h1>
                <p className="page-subtitle">Take 5-minute multiple choice tests to evaluate your level and raise your Internship Readiness ranking.</p>
            </header>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Menu View */}
            {!selectedCategory && !result && (
                <div className="categories-menu-grid">
                    {categories.map(cat => (
                        <div key={cat} className="category-test-card glass-panel">
                            <div className="test-badge">MCQ</div>
                            <h3>{cat} Assessment</h3>
                            <p className="test-meta">🕒 5 Minutes | 5 Questions</p>
                            <p className="test-desc">Tests syntax, data structures, execution logic, and best practices in {cat}.</p>
                            <button className="btn btn-primary start-test-btn" onClick={() => handleStartTest(cat)}>
                                Start Assessment
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Quiz Testing View */}
            {selectedCategory && quizActive && !result && questions.length > 0 && (
                <div className="quiz-active-container glass-panel">
                    
                    <div className="quiz-header">
                        <div className="quiz-title-box">
                            <h2>{selectedCategory} Test</h2>
                            <span className="question-counter">Question {currentIdx + 1} of {questions.length}</span>
                        </div>
                        <div className={`quiz-timer ${timeLeft < 60 ? 'timer-danger' : ''}`}>
                            ⏱️ {formatTime(timeLeft)}
                        </div>
                    </div>

                    <div className="question-display-block">
                        <p className="question-text">{questions[currentIdx].question}</p>
                        
                        <div className="options-grid">
                            {questions[currentIdx].options.map(opt => {
                                const qId = questions[currentIdx].id;
                                const isSelected = answers[qId] === opt;
                                return (
                                    <button
                                        key={opt}
                                        className={`option-btn ${isSelected ? 'selected' : ''}`}
                                        onClick={() => handleSelectOption(qId, opt)}
                                    >
                                        <span className="option-bullet">{isSelected ? '●' : '○'}</span>
                                        <span className="option-label">{opt}</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div className="quiz-navigation">
                        <button 
                            className="btn btn-secondary" 
                            onClick={() => setCurrentIdx(prev => Math.max(0, prev - 1))}
                            disabled={currentIdx === 0}
                        >
                            Previous
                        </button>
                        
                        {currentIdx < questions.length - 1 ? (
                            <button 
                                className="btn btn-primary" 
                                onClick={() => setCurrentIdx(prev => prev + 1)}
                                disabled={!answers[questions[currentIdx].id]}
                            >
                                Next
                            </button>
                        ) : (
                            <button 
                                className="btn btn-success submit-test-action"
                                onClick={handleSubmitQuiz}
                                disabled={Object.keys(answers).length < questions.length}
                            >
                                Finish & Grade
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Results Explanation View */}
            {result && (
                <div className="quiz-results-container glass-panel">
                    <div className="results-hero">
                        <div className="circular-score-badge">
                            <h2>{result.score}%</h2>
                            <p>Correct: {result.correct_count}/{result.total_count}</p>
                        </div>
                        <div className="results-grade-message">
                            <h3>{result.score >= 80 ? "Excellent Work!" : result.score >= 60 ? "Good Attempt!" : "Requires Revision"}</h3>
                            <p>Your assessment score has been logged. Your dashboard skills matrix and overall readiness ranking have been recalculated.</p>
                            <button className="btn btn-primary" onClick={handleBackToMenu}>Take Another Test</button>
                        </div>
                    </div>

                    <div className="results-explanations-list">
                        <h3>Detailed Question Review</h3>
                        {result.results.map((res, idx) => (
                            <div key={res.id} className={`explanation-card ${res.is_correct ? 'correct' : 'incorrect'}`}>
                                <div className="card-top">
                                    <span className="q-number">Question {idx + 1}</span>
                                    <span className={`correct-status-tag ${res.is_correct ? 'pass' : 'fail'}`}>
                                        {res.is_correct ? 'Correct' : 'Incorrect'}
                                    </span>
                                </div>
                                <p className="card-q-text">{res.question}</p>
                                <div className="selections-row">
                                    <p>Your choice: <strong>{res.your_choice || 'Unanswered'}</strong></p>
                                    {!res.is_correct && <p>Correct choice: <strong className="green-text">{res.correct_choice}</strong></p>}
                                </div>
                                <p className="explanation-paragraph"><strong>Explanation:</strong> {res.explanation}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
