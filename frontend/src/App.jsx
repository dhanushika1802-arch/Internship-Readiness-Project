import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatbotDrawer from './components/ChatbotDrawer';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import Assessments from './pages/Assessments';
import GapDetector from './pages/GapDetector';
import RoadmapView from './pages/RoadmapView';
import Profile from './pages/Profile';
import './styles/global.css';

export default function App() {
    const [user, setUser] = useState(null);
    const [activeTab, setActiveTab] = useState('dashboard');
    const [targetRole, setTargetRole] = useState('Software Developer');
    const [initialized, setInitialized] = useState(false);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        const storedRole = localStorage.getItem('targetRole');
        if (storedUser && token) {
            const parsedUser = JSON.parse(storedUser);
            setUser(parsedUser);
            if (parsedUser.target_role) {
                setTargetRole(parsedUser.target_role);
            } else if (storedRole) {
                setTargetRole(storedRole);
            }
        } else if (storedRole) {
            setTargetRole(storedRole);
        }
        setInitialized(true);
    }, []);

    const handleLoginSuccess = (userData) => {
        setUser(userData);
        if (userData && userData.target_role) {
            setTargetRole(userData.target_role);
            localStorage.setItem('targetRole', userData.target_role);
        }
        setActiveTab('dashboard');
    };

    const handleTargetRoleChange = async (newRole) => {
        setTargetRole(newRole);
        localStorage.setItem('targetRole', newRole);
        
        const token = localStorage.getItem('token');
        if (token) {
            try {
                await fetch(`${import.meta.env.VITE_API_URL}/api/user/target-role`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token
                    },
                    body: JSON.stringify({ target_role: newRole })
                });
                if (user) {
                    const updatedUser = { ...user, target_role: newRole };
                    setUser(updatedUser);
                    localStorage.setItem('user', JSON.stringify(updatedUser));
                }
            } catch (err) {
                console.error("Failed to persist target role to backend:", err);
            }
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
    };

    if (!initialized) {
        return (
            <div style={{
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#F8FAFC',
                color: '#0F172A',
                fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif",
                fontWeight: 600
            }}>
                <p>Initializing Career Workspace...</p>
            </div>
        );
    }

    if (!user) {
        return <LoginRegister onLoginSuccess={handleLoginSuccess} />;
    }

    return (
        <div className="app-container">
            {/* Sidebar Navigation */}
            <Sidebar 
                activeTab={activeTab} 
                setActiveTab={setActiveTab} 
                user={user} 
                onLogout={handleLogout}
                targetRole={targetRole}
                setTargetRole={handleTargetRoleChange}
            />

            {/* Main Section */}
            <main className="main-content">
                {activeTab === 'dashboard' && (
                    <Dashboard 
                        targetRole={targetRole} 
                        setActiveTab={setActiveTab} 
                    />
                )}
                {activeTab === 'resume' && (
                    <ResumeAnalyzer />
                )}
                {activeTab === 'assessments' && (
                    <Assessments />
                )}
                {activeTab === 'gaps' && (
                    <GapDetector 
                        targetRole={targetRole} 
                        setActiveTab={setActiveTab} 
                    />
                )}
                {activeTab === 'roadmap' && (
                    <RoadmapView 
                        targetRole={targetRole} 
                    />
                )}
                {activeTab === 'profile' && (
                    <Profile 
                        user={user} 
                        setUser={setUser} 
                    />
                )}
            </main>

            {/* Floating Chatbot Coach */}
            <ChatbotDrawer targetRole={targetRole} />
        </div>
    );
}
