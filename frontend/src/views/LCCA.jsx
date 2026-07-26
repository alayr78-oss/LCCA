import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { FileBarChart, DollarSign, ArrowRight, Settings } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { AppContext } from '../context/AppContext';

const LCCA = () => {
  const { activeProject } = useContext(AppContext);
  const [lccaData, setLccaData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const runAnalysis = async () => {
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
        initial_cost: 1500000 / projectAssets.length, 
        routine_maintenance_annual: 50000 / projectAssets.length, 
        rsl_years: 15, 
        replacement_cost: 1000000 / projectAssets.length
      }));

      // Base Analysis
      const baseRes = await axios.post('/api/lcca/calculate', {
        components: components,
        analysis_period: activeProject.analysis_period_years || 50,
        discount_rate: activeProject.discount_rate || 0.08,
        country_profile: { labour_cost_factor: 1.0, material_cost_factor: 1.0, inflation_rate: 0.02 },
        track_length_km: activeProject.track_length_km || 1
      });
      setLccaData(baseRes.data);

      // Scenario Comparison
      const compRes = await axios.post('/api/lcca/scenario_compare', {
        scenarios: [
          {
            name: "Current Strategy",
            components: components,
            analysis_period: activeProject.analysis_period_years || 50,
            discount_rate: activeProject.discount_rate || 0.08,
            country_profile: { labour_cost_factor: 1.0, material_cost_factor: 1.0, inflation_rate: 0.02 },
            track_length_km: activeProject.track_length_km || 1
          },
          {
            name: "Preventative Strategy",
            components: components.map(c => ({...c, routine_maintenance_annual: c.routine_maintenance_annual * 1.5, rsl_years: c.rsl_years + 5})),
            analysis_period: activeProject.analysis_period_years || 50,
            discount_rate: activeProject.discount_rate || 0.08,
            country_profile: { labour_cost_factor: 1.0, material_cost_factor: 1.0, inflation_rate: 0.02 },
            track_length_km: activeProject.track_length_km || 1
          }
        ]
      });
      setComparisonData(compRes.data.comparison);
      
    } catch (err) {
      setErrorMsg(err.response?.data?.error || "Error running LCCA.");
    }
    setLoading(false);
  };

  useEffect(() => {
    runAnalysis();
  }, [activeProject]);

  if (!activeProject) return <div style={{padding: '40px', textAlign: 'center'}}>Please select an Active Project first.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Lifecycle Cost Analysis (LCCA)</h2>
        <button className="btn btn-primary" onClick={runAnalysis}><FileBarChart size={16} style={{marginRight: '8px'}} /> Run Analysis</button>
      </div>

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '8px', marginBottom: '20px' }}>
            {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Calculating Lifecycle Costs...</div>
      ) : lccaData ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>Total NPV</h4>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--brand-primary)', margin: '10px 0' }}>${(lccaData.total_npv / 1000000).toFixed(2)}M</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>Equivalent Annual Cost</h4>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0' }}>${(lccaData.total_eac / 1000).toFixed(1)}k</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>Cost per km</h4>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0' }}>${(lccaData.cost_per_km / 1000).toFixed(1)}k</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Cost Breakdown */}
            <div className="card">
              <h4 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}><DollarSign size={18} /> Component Cost Breakdown (NPV)</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                  <tr>
                    <th style={{ padding: '8px' }}>Asset</th>
                    <th style={{ padding: '8px' }}>Initial Cost</th>
                    <th style={{ padding: '8px' }}>Maintenance NPV</th>
                    <th style={{ padding: '8px' }}>Replacement NPV</th>
                    <th style={{ padding: '8px' }}>Total NPV</th>
                  </tr>
                </thead>
                <tbody>
                  {lccaData.component_breakdown.map((c, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '8px', fontWeight: 500 }}>{c.component}</td>
                      <td style={{ padding: '8px' }}>${(c.initial_cost / 1000).toFixed(1)}k</td>
                      <td style={{ padding: '8px' }}>${(c.routine_maintenance_npv / 1000).toFixed(1)}k</td>
                      <td style={{ padding: '8px' }}>${(c.replacement_npv / 1000).toFixed(1)}k</td>
                      <td style={{ padding: '8px', fontWeight: 'bold' }}>${(c.total_npv / 1000).toFixed(1)}k</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Scenario Comparison Chart */}
            {comparisonData && (
              <div className="card">
                <h4 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}><ArrowRight size={18} /> Strategy Scenario Comparison (NPV)</h4>
                <div style={{ height: '300px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="scenario_name" />
                      <YAxis tickFormatter={(val) => `$${(val/1000000).toFixed(1)}M`} />
                      <RechartsTooltip formatter={(value) => `$${(value/1000000).toFixed(2)}M`} />
                      <Bar dataKey="total_npv" fill="var(--brand-primary)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
};

export default LCCA;
