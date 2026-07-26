import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FolderKanban, Database, FileBarChart, Settings, Moon, Sun, Activity, Layers, Target, CheckSquare, BookOpen } from 'lucide-react';
import ProjectManagement from './views/ProjectManagement';
import ComponentLibrary from './views/ComponentLibrary';
import ConditionAssessment from './views/ConditionAssessment';
import InspectionEntry from './views/InspectionEntry';
import LCCA from './views/LCCA';
import DecisionDashboard from './views/DecisionDashboard';
import Dashboard from './views/Dashboard';
import Validation from './views/Validation';
import ResearchMode from './views/ResearchMode';
import { AppProvider } from './context/AppContext';
import './index.css';

// --- Layout Components ---
const Sidebar = () => {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/projects', label: 'Projects', icon: <FolderKanban size={20} /> },
    { path: '/inspections', label: 'Asset & Inspections', icon: <Database size={20} /> },
    { path: '/condition', label: 'Condition & Risk', icon: <Activity size={20} /> },
    { path: '/components', label: 'Components', icon: <Layers size={20} /> },
    { path: '/decision', label: 'Decision Engine', icon: <Target size={20} /> },
    { path: '/validation', label: 'Validation Framework', icon: <CheckSquare size={20} /> },
    { path: '/research', label: 'Research Mode', icon: <BookOpen size={20} /> },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 style={{color: 'white', display: 'flex', alignItems: 'center', gap: '10px'}}>
          <Activity size={24} color="var(--brand-primary)"/> RAM-DSS
        </h2>
        <p style={{fontSize: '0.8rem', opacity: 0.7}}>Decision Support System</p>
      </div>
      <nav style={{padding: '20px 0'}}>
        {navItems.map((item) => (
          <Link key={item.path} to={item.path} className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}>
            {item.icon}
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
};

const App = () => {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  return (
    <AppProvider>
      <Router>
        <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <div className="top-bar">
            <div>
              <span className="badge badge-success">System Online</span>
            </div>
            <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <button 
                onClick={toggleTheme} 
                className="btn btn-outline" 
                style={{ padding: '6px', borderRadius: '50%' }}
              >
                {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
              </button>
              <button className="btn btn-outline" style={{ padding: '6px', borderRadius: '50%' }}>
                <Settings size={18} />
              </button>
            </div>
          </div>
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects" element={<ProjectManagement />} />
              <Route path="/lcca" element={<LCCA />} />
              <Route path="/components" element={<ComponentLibrary />} />
              <Route path="/condition" element={<ConditionAssessment />} />
              <Route path="/inspections" element={<InspectionEntry />} />
              <Route path="/decision" element={<DecisionDashboard />} />
              <Route path="/validation" element={<Validation />} />
              <Route path="/research" element={<ResearchMode />} />
              <Route path="*" element={<Dashboard />} />
            </Routes>
          </div>
        </div>
      </div>
      </Router>
    </AppProvider>
  );
};

export default App;
