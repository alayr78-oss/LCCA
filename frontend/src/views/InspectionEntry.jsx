import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Database, Plus, CheckSquare, AlertCircle } from 'lucide-react';
import { AppContext } from '../context/AppContext';

const InspectionEntry = () => {
  const { activeProject, activeAsset, setActiveAsset } = useContext(AppContext);
  const [assets, setAssets] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);

  const [assetForm, setAssetForm] = useState({
    component_id: 1, location_start_km: 0, location_end_km: 1, install_year: 2020
  });

  const [inspectionForm, setInspectionForm] = useState({
    inspection_date: new Date().toISOString().split('T')[0],
    inspector: '', condition_rating: 100, defect_severity: 'None'
  });

  useEffect(() => {
    if (activeProject) fetchAssets();
    else setLoading(false);
  }, [activeProject]);

  useEffect(() => {
    if (activeAsset) fetchInspections();
  }, [activeAsset]);

  const fetchAssets = async () => {
    try {
      const res = await axios.get('/api/assets');
      const filtered = res.data.filter(a => a.project_id === activeProject.id);
      setAssets(filtered);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const fetchInspections = async () => {
    try {
      const res = await axios.get('/api/inspections');
      setInspections(res.data.filter(i => i.asset_id === activeAsset.id));
    } catch (err) { console.error(err); }
  };

  const [errorDetails, setErrorDetails] = useState({ message: '' });

  const handleCreateAsset = async (e) => {
    e.preventDefault();
    setErrorDetails({ message: '' });
    
    // Ensure numbers are properly formatted
    const payload = {
        ...assetForm,
        project_id: activeProject.id,
        location_start_km: assetForm.location_start_km ? parseFloat(assetForm.location_start_km) : null,
        location_end_km: assetForm.location_end_km ? parseFloat(assetForm.location_end_km) : null,
        install_year: assetForm.install_year ? parseInt(assetForm.install_year, 10) : null
    };

    try {
      await axios.post('/api/assets', payload);
      fetchAssets();
      setAssetForm({ component_id: 1, location_start_km: 0, location_end_km: 1, install_year: 2020 });
    } catch (err) { 
        setErrorDetails({ message: err.response?.data?.error || "An unexpected error occurred while creating the asset." }); 
    }
  };

  const handleCreateInspection = async (e) => {
    e.preventDefault();
    setErrorDetails({ message: '' });
    
    const payload = {
        ...inspectionForm,
        asset_id: activeAsset.id,
        condition_rating: inspectionForm.condition_rating ? parseFloat(inspectionForm.condition_rating) : null
    };

    try {
      await axios.post('/api/inspections', payload);
      fetchInspections();
    } catch (err) { 
        setErrorDetails({ message: err.response?.data?.error || "An unexpected error occurred while logging the inspection." }); 
    }
  };

  if (!activeProject) return <div style={{padding: '40px', textAlign: 'center'}}>Please select an Active Project in Project Management first.</div>;

  return (
    <div className="fade-in">
      <h2>Asset & Inspection Management</h2>
      <p style={{color: 'var(--text-secondary)'}}>Managing assets for Project: <strong>{activeProject.name}</strong></p>

      {errorDetails.message && (
        <div style={{ marginTop: '15px', padding: '10px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{errorDetails.message}</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        {/* Assets Panel */}
        <div className="card">
          <h4><Database size={18} style={{marginRight: '8px'}} /> Project Assets</h4>
          <form onSubmit={handleCreateAsset} style={{ display: 'flex', gap: '10px', marginTop: '15px', marginBottom: '20px' }}>
            <input type="number" step="0.1" placeholder="Start km" style={{width: '80px'}} value={assetForm.location_start_km} onChange={e => setAssetForm({...assetForm, location_start_km: e.target.value})} />
            <input type="number" step="0.1" placeholder="End km" style={{width: '80px'}} value={assetForm.location_end_km} onChange={e => setAssetForm({...assetForm, location_end_km: e.target.value})} />
            <input type="number" placeholder="Install Year" style={{width: '100px'}} value={assetForm.install_year} onChange={e => setAssetForm({...assetForm, install_year: e.target.value})} />
            <button type="submit" className="btn btn-primary"><Plus size={16}/></button>
          </form>

          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{padding: '8px'}}>ID</th>
                <th style={{padding: '8px'}}>Chainage</th>
                <th style={{padding: '8px'}}>Year</th>
                <th style={{padding: '8px'}}>Action</th>
              </tr>
            </thead>
            <tbody>
              {assets.map(a => (
                <tr key={a.id} style={{ backgroundColor: activeAsset?.id === a.id ? 'var(--bg-tertiary)' : 'transparent', borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{padding: '8px'}}>{a.id}</td>
                  <td style={{padding: '8px'}}>{a.location_start_km} - {a.location_end_km} km</td>
                  <td style={{padding: '8px'}}>{a.install_year}</td>
                  <td style={{padding: '8px'}}>
                    <button className="btn btn-outline" style={{padding: '4px 8px'}} onClick={() => setActiveAsset(a)}>Select</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Inspections Panel */}
        {activeAsset ? (
          <div className="card" style={{borderLeft: '4px solid var(--brand-primary)'}}>
            <h4><CheckSquare size={18} style={{marginRight: '8px'}} /> Inspections for Asset {activeAsset.id}</h4>
            <form onSubmit={handleCreateInspection} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px', marginBottom: '20px' }}>
                <input type="date" required onChange={e => setInspectionForm({...inspectionForm, inspection_date: e.target.value})} />
                <input type="text" placeholder="Inspector Name" required onChange={e => setInspectionForm({...inspectionForm, inspector: e.target.value})} />
                <input type="number" placeholder="Condition (0-100)" required max="100" min="0" onChange={e => setInspectionForm({...inspectionForm, condition_rating: e.target.value})} />
                <select onChange={e => setInspectionForm({...inspectionForm, defect_severity: e.target.value})}>
                    <option value="None">No Defects</option>
                    <option value="Minor">Minor</option>
                    <option value="Severe">Severe</option>
                    <option value="Critical">Critical</option>
                </select>
                <button type="submit" className="btn btn-primary" style={{gridColumn: 'span 2'}}>Log Inspection</button>
            </form>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{padding: '8px'}}>Date</th>
                  <th style={{padding: '8px'}}>Inspector</th>
                  <th style={{padding: '8px'}}>Condition</th>
                  <th style={{padding: '8px'}}>Severity</th>
                </tr>
              </thead>
              <tbody>
                {inspections.map(i => (
                  <tr key={i.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{padding: '8px'}}>{i.inspection_date}</td>
                    <td style={{padding: '8px'}}>{i.inspector}</td>
                    <td style={{padding: '8px'}}>{i.condition_rating}</td>
                    <td style={{padding: '8px'}}>{i.defect_severity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)'}}>
            Select an asset to manage inspections.
          </div>
        )}
      </div>
    </div>
  );
};

export default InspectionEntry;
