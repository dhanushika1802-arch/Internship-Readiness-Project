import React from 'react';
import {
    LayoutDashboard,
    FileText,
    ClipboardCheck,
    Search,
    Map,
    User,
    LogOut,
    Zap,
    ChevronDown
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ activeTab, setActiveTab, user, onLogout, targetRole, setTargetRole }) {
    const roles = [
        "Data Analyst",
        "Data Scientist",
        "AI Engineer",
        "Software Developer",
        "Full Stack Developer",
        "Cyber Security Analyst"
    ];

    const navItems = [
        { id: 'dashboard',   label: 'Dashboard',        Icon: LayoutDashboard },
        { id: 'resume',      label: 'Resume Analyzer',  Icon: FileText         },
        { id: 'assessments', label: 'Skill Assessments', Icon: ClipboardCheck  },
        { id: 'gaps',        label: 'Gap Detector',     Icon: Search           },
        { id: 'roadmap',     label: 'Learning Roadmap', Icon: Map              },
        { id: 'profile',     label: 'Profile',          Icon: User             },
    ];

    const initials = user?.name ? user.name.charAt(0).toUpperCase() : 'S';

    return (
        <aside className="sidebar">

            {/* ── Brand ─────────────────────────────────── */}
            <div className="sidebar-brand">
                <div className="brand-logo">
                    <Zap size={18} strokeWidth={2.5} />
                </div>
                <div className="brand-text">
                    <h2>ReadyUp AI</h2>
                    <p>Internship Readiness</p>
                </div>
            </div>

            {/* ── User card ─────────────────────────────── */}
            <div className="sidebar-profile">
                <div className="avatar">{initials}</div>
                <div className="profile-info">
                    <h4>{user?.name || 'Guest Student'}</h4>
                    <p>{user?.degree || 'Computer Science'}</p>
                </div>
            </div>

            {/* ── Target Role ───────────────────────────── */}
            <div className="role-selector-container">
                <label className="role-label">Target Role</label>
                <div className="role-select-wrapper">
                    <select
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        className="role-select"
                    >
                        {roles.map(r => (
                            <option key={r} value={r}>{r}</option>
                        ))}
                    </select>
                    <ChevronDown size={14} className="role-chevron" />
                </div>
            </div>

            {/* ── Nav section label ─────────────────────── */}
            <p className="nav-section-label">Navigation</p>

            {/* ── Navigation ────────────────────────────── */}
            <nav className="sidebar-nav">
                {navItems.map(({ id, label, Icon }) => (
                    <button
                        key={id}
                        onClick={() => setActiveTab(id)}
                        className={`nav-link ${activeTab === id ? 'active' : ''}`}
                        aria-current={activeTab === id ? 'page' : undefined}
                    >
                        <span className="nav-icon">
                            <Icon size={18} strokeWidth={activeTab === id ? 2.5 : 1.75} />
                        </span>
                        <span className="nav-label">{label}</span>
                        {activeTab === id && <span className="nav-indicator" />}
                    </button>
                ))}
            </nav>

            {/* ── Footer / Logout ───────────────────────── */}
            <div className="sidebar-footer">
                <button onClick={onLogout} className="logout-btn">
                    <LogOut size={16} strokeWidth={2} />
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
}
