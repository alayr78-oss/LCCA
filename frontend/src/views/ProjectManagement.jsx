import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, CheckCircle } from 'lucide-react';
import { AppContext } from '../context/AppContext';

const ProjectManagement = () => {
  const { activeProject, setActiveProject } = useContext(AppContext);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '', track_length_km: '', railway_type: '', discount_rate: 0.08, analysis_period_years: 50
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get('/api/projects');
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/projects', formData);
      setShowModal(false);
      fetchProjects();
    } catch (err) {
      alert("Error creating project");
    }
  };

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Project Management</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} style={{marginRight: '8px'}} /> New Project
        </button>
      </div>
      
      {activeProject && (
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '8px', borderLeft: '4px solid var(--brand-primary)' }}>
          <strong>Active Project:</strong> {activeProject.name} (ID: {activeProject.id}) - All dashboards will analyze this project.
        </div>
      )}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead style={{ backgroundColor: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)' }}>
            <tr>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>ID</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Project Name</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Length (km)</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Discount Rate</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="5" style={{ padding: '20px', textAlign: 'center' }}>Loading...</td></tr>
            ) : projects.length === 0 ? (
              <tr><td colSpan="5" style={{ padding: '20px', textAlign: 'center' }}>No projects found.</td></tr>
            ) : (
              projects.map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: activeProject?.id === p.id ? 'var(--bg-tertiary)' : 'transparent' }}>
                  <td style={{ padding: '12px 16px' }}>{p.id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 500, color: 'var(--brand-primary)' }}>{p.name}</td>
                  <td style={{ padding: '12px 16px' }}>{p.track_length_km}</td>
                  <td style={{ padding: '12px 16px' }}>{p.discount_rate}</td>
                  <td style={{ padding: '12px 16px', display: 'flex', gap: '10px' }}>
                    <button className="btn btn-outline" style={{ padding: '4px 8px' }} onClick={() => setActiveProject(p)}>
                      <CheckCircle size={14} style={{marginRight: '4px'}} /> Select
                    </button>
                    <button className="btn btn-outline" style={{ padding: '4px 8px', color: 'var(--status-danger)' }}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div className="card" style={{ width: '400px' }}>
            <h3>Create Project</h3>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Project Name</label>
                <input type="text" required style={{ width: '100%', padding: '8px' }} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Track Length (km)</label>
                <input type="number" required style={{ width: '100%', padding: '8px' }} onChange={e => setFormData({...formData, track_length_km: parseFloat(e.target.value)})} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Discount Rate</label>
                <input type="number" step="0.01" required value={formData.discount_rate} style={{ width: '100%', padding: '8px' }} onChange={e => setFormData({...formData, discount_rate: parseFloat(e.target.value)})} />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <button type="submit" className="btn btn-primary">Save Project</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectManagement;
