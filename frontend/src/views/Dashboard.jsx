import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Activity, Database, FileBarChart, Target, FileText, Download } from 'lucide-react';
import { AppContext } from '../context/AppContext';

const Dashboard = () => {
  const { activeProject } = useContext(AppContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const fetchUnifiedData = async () => {
    if (!activeProject) return;
    setLoading(true);
    setErrorMsg("");
    
    try {
      // 1. Fetch Assets for Active Project
      const assetRes = await axios.get('/api/assets');
      const projectAssets = assetRes.data.filter(a => a.project_id === activeProject.id);
      
      if (projectAssets.length === 0) {
        setErrorMsg("No assets found for the active project. Please add assets in the Inspection tab.");
        setLoading(false);
        return;
      }

      // Map assets to component payload format
      const components = projectAssets.map((a, idx) => ({
        name: `Asset ${a.id} (Chainage ${a.location_start_km}-${a.location_end_km})`,
        cci: 60, // Ideally pulled from inspection table, simplifying for now
        importance: 1 / projectAssets.length,
        initial_cost: 1500000, 
        routine_maintenance_annual: 50000, 
        rsl_years: 15, 
        replacement_cost: 1000000
      }));
      
      const conditionRes = await axios.post('/api/engine/condition', {
        components: components,
        deterioration_rate: 2.5
      });
      
      const lccaRes = await axios.post('/api/lcca/calculate', {
        components: components,
        analysis_period: activeProject.analysis_period_years || 50,
        discount_rate: activeProject.discount_rate || 0.08,
        country_profile: { labour_cost_factor: 1.0, material_cost_factor: 1.0, inflation_rate: 0.02 }
      });
      
      const riskRes = await axios.post('/api/risk/calculate', {
        asset_condition: conditionRes.data.rsl_result,
        consequence_factors: { safety_impact: 8, operational_disruption: 7, traffic_importance: 9 }
      });
      
      const mcdmRes = await axios.post('/api/recommendation/generate', {
        alternatives: [
            { id: 1, name: 'Condition-Based Maintenance', lifecycle_cost: lccaRes.data.total_npv, risk_score: riskRes.data.risk_score, carbon_footprint: 5000, reliability_score: 85 }
        ],
        weights: { lifecycle_cost: 0.3, risk_score: 0.3, reliability: 0.2, carbon_footprint: 0.2 }
      });

      setData({
        ici: conditionRes.data.ici_result.ici,
        rsl: conditionRes.data.rsl_result.rsl_years,
        lcca: lccaRes.data.total_npv,
        eac: lccaRes.data.total_eac,
        riskLevel: riskRes.data.classification,
        recommendation: mcdmRes.data.recommendation.recommended_alternative,
        confidence: mcdmRes.data.recommendation.confidence_level
      });
    } catch (err) {
      setErrorMsg(err.response?.data?.error || "Error executing calculation pipeline.");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUnifiedData();
  }, [activeProject]);

  const handleExport = async (format) => {
    if (!data) return;
    
    try {
        const response = await axios.post('/api/export/report', {
            format: format,
            report_data: {
                project_name: activeProject.name,
                total_lcca: data.lcca,
                risk_score: data.riskLevel,
                carbon_footprint: 5000,
                recommended_strategy: data.recommendation,
                ici: data.ici,
                rsl: data.rsl
            }
        }, { responseType: 'blob' });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `ram_dss_report.${format === 'excel' ? 'xlsx' : format}`);
        document.body.appendChild(link);
        link.click();
    } catch (err) {
        alert("Export failed.");
    }
  };

  if (!activeProject) return <div style={{padding: '40px', textAlign: 'center'}}>Please select an Active Project in Project Management first.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Dashboard for Project: {activeProject.name}</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-outline" onClick={() => handleExport('csv')} disabled={!data}>
                <Download size={16} style={{marginRight: '8px'}}/> CSV
            </button>
            <button className="btn btn-outline" onClick={() => handleExport('excel')} disabled={!data}>
                <FileText size={16} style={{marginRight: '8px'}}/> Excel
            </button>
            <button className="btn btn-primary" onClick={() => handleExport('pdf')} disabled={!data}>
                <FileText size={16} style={{marginRight: '8px'}}/> Export PDF Report
            </button>
        </div>
      </div>

      {errorMsg && (
        <div style={{ padding: '15px', backgroundColor: 'var(--status-danger)', color: 'white', borderRadius: '8px', marginBottom: '20px' }}>
            {errorMsg}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Aggregating Project Data via Backend APIs...</div>
      ) : data ? (
        <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                <div className="card">
                    <h4 style={{color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px'}}><Activity size={18}/> Infrastructure Condition (ICI)</h4>
                    <h2 style={{marginTop: '10px', color: data.ici > 70 ? 'var(--status-success)' : 'var(--status-warning)'}}>{data.ici.toFixed(1)} / 100</h2>
                    <p style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>{data.rsl.toFixed(1)} Years Remaining Life</p>
                </div>
                
                <div className="card">
                    <h4 style={{color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px'}}><FileBarChart size={18}/> Total Lifecycle Cost (NPV)</h4>
                    <h2 style={{marginTop: '10px', color: 'var(--brand-primary)'}}>${(data.lcca / 1000000).toFixed(2)}M</h2>
                    <p style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>${(data.eac / 1000).toFixed(1)}k / Year EAC</p>
                </div>

                <div className="card">
                    <h4 style={{color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px'}}><Target size={18}/> Overall Risk Level</h4>
                    <h2 style={{marginTop: '10px', color: 'var(--status-danger)'}}>{data.riskLevel}</h2>
                </div>
            </div>
            
            <div className="card" style={{ backgroundColor: 'var(--brand-primary)', color: 'white', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <h3 style={{ opacity: 0.9 }}>AI Recommended Strategy</h3>
                <h1 style={{ margin: '10px 0' }}>{data.recommendation}</h1>
                <p style={{ opacity: 0.9 }}>Confidence Score: {data.confidence}%</p>
            </div>
        </>
      ) : null}
    </div>
  );
};

export default Dashboard;
