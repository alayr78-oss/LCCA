import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { AppContext } from '../context/AppContext';

const ProjectManagement = () => {
  const { activeProject, setActiveProject } = useContext(AppContext);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorDetails, setErrorDetails] = useState({ message: '', field: '' });
  
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
    setErrorDetails({ message: '', field: '' });
    setIsSubmitting(true);
    
    // Ensure numbers are properly formatted
    const payload = {
        ...formData,
        track_length_km: formData.track_length_km ? parseFloat(formData.track_length_km) : null,
        discount_rate: formData.discount_rate ? parseFloat(formData.discount_rate) : null,
        analysis_period_years: formData.analysis_period_years ? parseInt(formData.analysis_period_years, 10) : null
    };

    try {
      await axios.post('/api/projects', payload);
      setShowModal(false);
      setFormData({ name: '', track_length_km: '', railway_type: '', discount_rate: 0.08, analysis_period_years: 50 });
      fetchProjects();
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorDetails({
            message: err.response.data.error,
            field: err.response.data.field || ''
        });
      } else {
        setErrorDetails({ message: "An unexpected network or server error occurred.", field: '' });
      }
    }
    setIsSubmitting(false);
  };

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Project Management</h2>
        <button className="btn btn-primary" onClick={() => { setShowModal(true); setErrorDetails({message:'', field:''}); }}>
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
            
            {errorDetails.message && (
                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={16} />
                    <span>{errorDetails.message}</span>
                </div>
            )}

            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Project Name</label>
                <input type="text" required style={{ width: '100%', padding: '8px', border: errorDetails.field === 'name' ? '2px solid var(--status-danger)' : '1px solid var(--border-color)' }} value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Track Length (km)</label>
                <input type="number" step="0.1" required style={{ width: '100%', padding: '8px', border: errorDetails.field === 'track_length_km' ? '2px solid var(--status-danger)' : '1px solid var(--border-color)' }} value={formData.track_length_km} onChange={e => setFormData({...formData, track_length_km: e.target.value})} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Analysis Period (Years)</label>
                <input type="number" required style={{ width: '100%', padding: '8px', border: errorDetails.field === 'analysis_period_years' ? '2px solid var(--status-danger)' : '1px solid var(--border-color)' }} value={formData.analysis_period_years} onChange={e => setFormData({...formData, analysis_period_years: e.target.value})} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Discount Rate</label>
                <input type="number" step="0.01" required style={{ width: '100%', padding: '8px', border: errorDetails.field === 'discount_rate' ? '2px solid var(--status-danger)' : '1px solid var(--border-color)' }} value={formData.discount_rate} onChange={e => setFormData({...formData, discount_rate: e.target.value})} />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {isSubmitting && <Loader size={16} className="spin" />}
                    Save Project
                </button>
                <button type="button" className="btn btn-outline" disabled={isSubmitting} onClick={() => setShowModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectManagement;
