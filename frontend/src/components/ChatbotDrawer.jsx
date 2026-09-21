import React, { useState, useRef, useEffect } from 'react';
import './ChatbotDrawer.css';

export default function ChatbotDrawer({ targetRole }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { sender: 'bot', text: "Hi! I'm your AI Career Coach. Ask me anything about skill gaps, project ideas, resume updates, or how to get internship-ready!" }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        setInput("");
        setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
        setIsLoading(true);

        const token = localStorage.getItem('token') || '';

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chat?target_role=${encodeURIComponent(targetRole)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token
                },
                body: JSON.stringify({ query: userMsg })
            });

            if (response.ok) {
                const data = await response.json();
                setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
            } else {
                setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I'm having trouble connecting to the career server. Please ensure the backend is running." }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { sender: 'bot', text: "Network error. Please check your connection and try again." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Floating Toggle Button */}
            <button className="chat-toggle-btn" onClick={() => setIsOpen(!isOpen)}>
                <span>💬</span>
                <span className="toggle-text">AI Career Coach</span>
            </button>

            {/* Chat Drawer */}
            <div className={`chat-drawer ${isOpen ? 'open' : ''}`}>
                <div className="chat-header">
                    <div className="chat-header-title">
                        <h3>AI Career Coach</h3>
                        <p>Guidance for {targetRole}</p>
                    </div>
                    <button className="chat-close-btn" onClick={() => setIsOpen(false)}>✕</button>
                </div>

                <div className="chat-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message-wrapper ${msg.sender}`}>
                            <div className="message-bubble">
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message-wrapper bot">
                            <div className="message-bubble typing">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSend} className="chat-input-form">
                    <input
                        type="text"
                        placeholder="Ask about resume tips, projects, skills..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="chat-input"
                    />
                    <button type="submit" className="chat-send-btn" disabled={isLoading}>
                        ➜
                    </button>
                </form>
            </div>
        </>
    );
}
