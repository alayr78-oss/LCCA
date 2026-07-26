import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2 } from 'lucide-react';

const ComponentLibrary = () => {
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      const res = await axios.get('/api/components');
      setComponents(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching components", err);
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Component Library</h2>
        <button className="btn btn-primary"><Plus size={16} style={{marginRight: '8px'}} /> Add Component</button>
      </div>
      
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead style={{ backgroundColor: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)' }}>
            <tr>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>ID</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Component Name</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Description</th>
              <th style={{ padding: '12px 16px', fontWeight: 600 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4" style={{ padding: '20px', textAlign: 'center' }}>Loading...</td></tr>
            ) : components.length === 0 ? (
              <tr><td colSpan="4" style={{ padding: '20px', textAlign: 'center' }}>No components found.</td></tr>
            ) : (
              components.map(c => (
                <tr key={c.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px 16px' }}>{c.id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 500, color: 'var(--brand-primary)' }}>{c.name}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>{c.description || "N/A"}</td>
                  <td style={{ padding: '12px 16px', display: 'flex', gap: '10px' }}>
                    <button className="btn btn-outline" style={{ padding: '4px 8px' }}><Edit2 size={14} /></button>
                    <button className="btn btn-outline" style={{ padding: '4px 8px', color: 'var(--status-danger)' }}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComponentLibrary;
