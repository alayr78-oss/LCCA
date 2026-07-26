import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { CheckCircle, AlertTriangle, BarChart, Settings, CheckSquare, Database } from 'lucide-react';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { AppContext } from '../context/AppContext';

const Validation = () => {
  const { activeProject } = useContext(AppContext);
  const [valData, setValData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const runValidation = async () => {
    if (!activeProject) {
        setErrorMsg("Please select an active project to run validation.");
        return;
    }
    setLoading(true);
    setErrorMsg('');

    try {
      // Fetch assets and inspections
      const assetRes = await axios.get('/api/assets');
      const inspRes = await axios.get('/api/inspections');
      
      const projectAssets = assetRes.data.filter(a => a.project_id === activeProject.id);
      if (projectAssets.length === 0) {
          setErrorMsg("No assets found. Cannot run validation. Please seed data or add assets.");
          setLoading(false);
          return;
      }

      // We will validate against the first asset
      const testAsset = projectAssets[0];
      const assetInspections = inspRes.data.filter(i => i.asset_id === testAsset.id);
      
      if (assetInspections.length < 2) {
          setErrorMsg("Not enough inspection records found for Asset " + testAsset.id + ". Validation requires at least 2 historical condition records.");
          setLoading(false);
          return;
      }

      // Map inspections to observed data
      const observed_data = assetInspections.map((insp, idx) => ({
          year: idx + 1, // Simplified timeline for validation
          condition_rating: insp.condition_rating
      }));

      const res = await axios.post('/api/validation/run', {
        component: { name: `Asset ${testAsset.id}`, initial_cost: 200000, routine_maintenance_annual: 10000 },
        analysis_period: activeProject.analysis_period_years || 50,
        discount_rate: activeProject.discount_rate || 0.08,
        inflation_rate: 0.02,
        base_scenario: {
            country_profile: { discount_rate: activeProject.discount_rate || 0.08, inflation_rate: 0.02, material_cost_factor: 1.0, labour_cost_factor: 1.0 },
            components: [{ name: `Asset ${testAsset.id}`, initial_cost: 200000, routine_maintenance_annual: 10000 }],
            analysis_period: activeProject.analysis_period_years || 50
        },
        ranges: {
            'discount_rate': [0.05, 0.08, 0.11],
            'material_cost_factor': [0.8, 1.0, 1.2]
        },
        predicted_curve: [100, 95, 90, 85, 80],
        observed_data: observed_data
      });
      setValData(res.data);
    } catch (err) {
      setErrorMsg(err.response?.data?.error || "Validation failed.");
    }
    setLoading(false);
  };

  const seedDemoData = async () => {
    setLoading(true);
    try {
        const pRes = await axios.post('/api/projects', { name: 'Demo Validation Project', track_length_km: 10, railway_type: 'Mainline', discount_rate: 0.08, analysis_period_years: 50 });
        const aRes = await axios.post('/api/assets', { project_id: pRes.data.id, install_year: 2020, location_start_km: 0, location_end_km: 1 });
        await axios.post('/api/inspections', { asset_id: aRes.data.id, inspection_date: '2021-01-01', inspector: 'System', condition_rating: 94, defect_severity: 'None' });
        await axios.post('/api/inspections', { asset_id: aRes.data.id, inspection_date: '2023-01-01', inspector: 'System', condition_rating: 86, defect_severity: 'Minor' });
        alert("Demo Database Data Seeded. Please select 'Demo Validation Project' in Project Management.");
    } catch (err) {
        alert("Error seeding data.");
    }
    setLoading(false);
  }

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Research Validation Framework</h2>
        <div style={{display: 'flex', gap: '10px'}}>
            <button className="btn btn-outline" onClick={seedDemoData}>
            <Database size={16} style={{marginRight: '8px'}} /> Seed DB Demo Data
            </button>
            <button className="btn btn-primary" onClick={runValidation}>
            <CheckSquare size={16} style={{marginRight: '8px'}} /> Run Validation Suite
            </button>
        </div>
      </div>

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: 'var(--status-warning)', color: 'white', borderRadius: '8px', marginBottom: '20px' }}>
            {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Running Validation Models...</div>
      ) : valData ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
            
            {/* 1. Mathematical Validation */}
            <div className="card">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                    <CheckCircle size={18} /> Mathematical Validation (LCCA Engine vs Manual Formula)
                </h4>
                <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', padding: '20px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>RAM-DSS NPV Result</div>
                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>${Math.round(valData.mathematical_validation.ram_dss_npv).toLocaleString()}</div>
                    </div>
                    <div style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>vs</div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Algebraic Manual Result</div>
                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>${Math.round(valData.mathematical_validation.manual_npv).toLocaleString()}</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Difference (%)</div>
                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: valData.mathematical_validation.difference_percentage < 0.1 ? 'var(--status-success)' : 'var(--status-danger)' }}>
                            {valData.mathematical_validation.difference_percentage}%
                        </div>
                    </div>
                    <div>
                        {valData.mathematical_validation.accuracy_result === 'Pass' ? 
                            <span className="badge badge-success">PASS</span> : <span className="badge badge-danger">FAIL</span>
                        }
                    </div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                {/* 2. Model Validation */}
                <div className="card">
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                        <AlertTriangle size={18} /> Condition Model Validation (Predicted vs Observed)
                    </h4>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '15px' }}>
                        Comparing theoretical deterioration curves against historical DB inspection data.
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div style={{ padding: '15px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Root Mean Square Error (RMSE)</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--brand-primary)' }}>{valData.model_validation.rmse}</div>
                        </div>
                        <div style={{ padding: '15px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Mean Absolute Error (MAE)</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--brand-primary)' }}>{valData.model_validation.mae}</div>
                        </div>
                    </div>
                    <div style={{ marginTop: '15px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        DB Data Points Validated: {valData.model_validation.data_points_validated}
                    </div>
                </div>

                {/* 3. Sensitivity Validation (Tornado Chart Data) */}
                <div className="card">
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                        <BarChart size={18} /> Sensitivity Analysis (Impact on NPV)
                    </h4>
                    <div style={{ height: '200px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <RechartsBarChart layout="vertical" data={valData.sensitivity_validation} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" tickFormatter={(val) => `$${val/1000000}M`} />
                                <YAxis dataKey="parameter" type="category" width={120} style={{fontSize: '0.8rem'}} />
                                <RechartsTooltip formatter={(value, name) => [`$${value.toLocaleString()}`, "NPV Impact Swing"]} />
                                <Bar dataKey="impact_swing" fill="var(--brand-primary)" />
                            </RechartsBarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
      ) : null}
    </div>
  );
};

export default Validation;
