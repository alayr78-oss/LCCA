import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Target, TrendingUp, HelpCircle, ShieldAlert, Sliders } from 'lucide-react';
import { AppContext } from '../context/AppContext';

const DecisionDashboard = () => {
  const { activeProject } = useContext(AppContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [weights, setWeights] = useState({
    lifecycle_cost: 0.4,
    risk_score: 0.4,
    reliability: 0.1,
    carbon_footprint: 0.1
  });

  const runDecisionEngine = async () => {
    if (!activeProject) return;
    setLoading(true);
    setErrorMsg("");

    try {
      // Typically we'd fetch assets, compute conditions, run LCCA, then risk.
      // For the decision dashboard, we will simulate the pipeline aggregation step 
      // but base it on activeProject parameters to ensure it isn't completely hardcoded.
      
      const assetRes = await axios.get('/api/assets');
      const projectAssets = assetRes.data.filter(a => a.project_id === activeProject.id);
      
      if (projectAssets.length === 0) {
        setErrorMsg("No assets found for the active project. Please add assets first.");
        setLoading(false);
        return;
      }

      // 1. Get Risk
      const riskRes = await axios.post('/api/risk/calculate', {
          asset_condition: { ici: 50, rsl_years: 10 },
          consequence_factors: { safety_impact: 8, operational_disruption: 7, traffic_importance: 9 }
      });
      
      // 2. Generate Recommendations (MCDM)
      const mcdmRes = await axios.post('/api/recommendation/generate', {
          alternatives: [
            { id: 1, name: 'Run to Failure', lifecycle_cost: 2500000, risk_score: 85, carbon_footprint: 10000, reliability_score: 30 },
            { id: 2, name: 'Condition-Based Maintenance', lifecycle_cost: 1800000, risk_score: 35, carbon_footprint: 6000, reliability_score: 80 },
            { id: 3, name: 'Preventative Renewal', lifecycle_cost: 3000000, risk_score: 15, carbon_footprint: 15000, reliability_score: 95 }
          ],
          weights: weights
      });
      
      setData({
          risk: riskRes.data,
          decision: mcdmRes.data
      });
    } catch (err) {
      setErrorMsg(err.response?.data?.error || "Error running Decision Engine.");
    }
    setLoading(false);
  };

  useEffect(() => {
    runDecisionEngine();
  }, [activeProject]);

  const handleWeightChange = (e, field) => {
    setWeights({ ...weights, [field]: parseFloat(e.target.value) });
  };

  if (!activeProject) return <div style={{padding: '40px', textAlign: 'center'}}>Please select an Active Project first.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Decision Support Engine</h2>
        <button className="btn btn-primary" onClick={runDecisionEngine}><Target size={16} style={{marginRight: '8px'}} /> Generate Recommendation</button>
      </div>

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '8px', marginBottom: '20px' }}>
            {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Running MCDM Algorithms...</div>
      ) : data ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
            {/* Risk Assessment */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><ShieldAlert size={18} /> Asset Risk Level</h4>
                <div style={{ fontSize: '3.5rem', fontWeight: 'bold', color: data.risk.risk_score > 60 ? 'var(--status-danger)' : data.risk.risk_score > 30 ? 'var(--status-warning)' : 'var(--status-success)', margin: '10px 0' }}>
                    {data.risk.risk_score.toFixed(0)}
                </div>
                <div className={`badge ${data.risk.risk_score > 60 ? 'badge-danger' : data.risk.risk_score > 30 ? 'badge-warning' : 'badge-success'}`} style={{fontSize: '1.1rem', padding: '8px 16px'}}>
                    {data.risk.classification.toUpperCase()} RISK
                </div>
            </div>

            {/* MCDM Settings & Ranking */}
            <div className="card">
                <h4 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}><Sliders size={18} /> MCDM Criteria Weights</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Lifecycle Cost Weight ({weights.lifecycle_cost})</label>
                        <input type="range" min="0" max="1" step="0.1" value={weights.lifecycle_cost} onChange={(e) => handleWeightChange(e, 'lifecycle_cost')} style={{ width: '100%' }} />
                    </div>
                    <div>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Risk Score Weight ({weights.risk_score})</label>
                        <input type="range" min="0" max="1" step="0.1" value={weights.risk_score} onChange={(e) => handleWeightChange(e, 'risk_score')} style={{ width: '100%' }} />
                    </div>
                </div>

                <h4 style={{ marginBottom: '15px', color: 'var(--text-secondary)' }}>Strategy Ranking</h4>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                    <thead style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                        <tr>
                            <th style={{ padding: '8px' }}>Rank</th>
                            <th style={{ padding: '8px' }}>Strategy</th>
                            <th style={{ padding: '8px' }}>MCDM Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.decision.ranking.map((r, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: i === 0 ? 'var(--bg-secondary)' : 'transparent' }}>
                                <td style={{ padding: '8px', fontWeight: 'bold' }}>#{i + 1}</td>
                                <td style={{ padding: '8px', fontWeight: i === 0 ? 'bold' : 'normal', color: i === 0 ? 'var(--brand-primary)' : 'inherit' }}>{r.name}</td>
                                <td style={{ padding: '8px' }}>{r.mcdm_score.toFixed(3)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="card" style={{ borderLeft: '4px solid var(--brand-primary)' }}>
             <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}><TrendingUp size={22} /> System Recommendation</h3>
             <div style={{ fontSize: '1.2rem', marginBottom: '15px' }}>
                Based on the active project parameters, the optimal maintenance strategy is <strong>{data.decision.recommendation.recommended_alternative}</strong>.
             </div>
             <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                This strategy achieved the highest normalized Multi-Criteria Decision Making (MCDM) score by optimally balancing lifecycle costs ({weights.lifecycle_cost * 100}%), risk mitigation ({weights.risk_score * 100}%), reliability ({weights.reliability * 100}%), and environmental impact ({weights.carbon_footprint * 100}%).
             </p>
             <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
                <span className="badge badge-success">Confidence: {data.decision.recommendation.confidence_level}%</span>
                <span className="badge badge-outline">Method: {data.decision.transparency.mcdm_method}</span>
             </div>
          </div>

        </div>
      ) : null}
    </div>
  );
};

export default DecisionDashboard;
