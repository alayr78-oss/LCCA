import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Activity, Zap, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { AppContext } from '../context/AppContext';

const ConditionAssessment = () => {
  const { activeProject } = useContext(AppContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const fetchCondition = async () => {
    if (!activeProject) return;
    setLoading(true);
    setErrorMsg("");
    try {
      const assetRes = await axios.get('/api/assets');
      const projectAssets = assetRes.data.filter(a => a.project_id === activeProject.id);
      
      if (projectAssets.length === 0) {
        setErrorMsg("No assets found for the active project. Please add assets first.");
        setLoading(false);
        return;
      }

      const components = projectAssets.map(a => ({
        name: `Asset ${a.id}`,
        cci: 60, // Simplified for now
        importance: 1 / projectAssets.length
      }));

      const res = await axios.post('/api/engine/condition', {
        components: components,
        deterioration_rate: 2.5,
        model_type: 'Linear',
        critical_threshold: 40
      });
      setData(res.data);
    } catch (err) {
      setErrorMsg(err.response?.data?.error || "Error calculating condition.");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCondition();
  }, [activeProject]);

  if (!activeProject) return <div style={{padding: '40px', textAlign: 'center'}}>Please select an Active Project first.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Condition Assessment & Remaining Life</h2>
        <button className="btn btn-primary" onClick={fetchCondition}><Zap size={16} style={{marginRight: '8px'}} /> Recalculate</button>
      </div>

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '8px', marginBottom: '20px' }}>
            {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Calculating Deterioration Models...</div>
      ) : data ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>Infrastructure Condition Index (ICI)</h4>
                <div style={{ fontSize: '3rem', fontWeight: 'bold', color: data.ici_result.ici > 70 ? 'var(--status-success)' : 'var(--status-warning)', margin: '10px 0' }}>
                    {data.ici_result.ici.toFixed(1)} <span style={{fontSize: '1rem', color: 'var(--text-muted)'}}>/ 100</span>
                </div>
            </div>

            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>Remaining Service Life (RSL)</h4>
                <div style={{ fontSize: '3rem', fontWeight: 'bold', color: 'var(--brand-primary)', margin: '10px 0' }}>
                    {data.rsl_result.rsl_years.toFixed(1)} <span style={{fontSize: '1rem', color: 'var(--text-muted)'}}>Years</span>
                </div>
                <p style={{fontSize: '0.85rem', color: 'var(--status-danger)'}}>Reaches critical threshold ({data.rsl_result.threshold}) in {new Date().getFullYear() + Math.floor(data.rsl_result.rsl_years)}</p>
            </div>
          </div>

          <div className="card">
            <h4 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={18} /> Deterioration Prediction Curve
            </h4>
            <div style={{ height: '300px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.rsl_result.predicted_curve} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="year" tickFormatter={(tick) => `Year ${tick}`} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <ReferenceLine y={data.rsl_result.threshold} label="Safety Threshold" stroke="var(--status-danger)" strokeDasharray="3 3" />
                        <Line type="monotone" dataKey="condition" stroke="var(--brand-primary)" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
             <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}><Info size={18} /> Engine Transparency Log</h4>
             <ul style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                <li><strong>ICI Model:</strong> {data.transparency.formula_ici}</li>
                <li><strong>RSL Model ({data.transparency.model_selected}):</strong> {data.transparency.formula_rsl}</li>
             </ul>
          </div>

        </div>
      ) : null}
    </div>
  );
};

export default ConditionAssessment;
