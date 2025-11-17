import React, { useState } from 'react';
import './StoryPlanPanel.css';

function StoryPlanPanel({ session }) {
  const [activeTab, setActiveTab] = useState('seed');

  if (!session) {
    return <div className="plan-panel empty">Select a story to view plans</div>;
  }

  const plans = session.plans || {};
  const seed = session.seed || {};
  
  const hasPlans = Object.keys(plans).length > 0 || Object.keys(seed).length > 0;

  if (!hasPlans) {
    return (
      <div className="plan-panel empty">
        <p>No planning data available</p>
      </div>
    );
  }

  // Render seed metadata
  const renderSeed = () => {
    if (!seed || Object.keys(seed).length === 0) {
      return <p className="empty-text">No seed data available</p>;
    }
    
    return (
      <div className="seed-container">
        <div className="seed-section">
          <h3 className="seed-section-title">📋 Generation Info</h3>
          <div className="seed-grid">
            <div className="seed-item">
              <span className="seed-label">Topic</span>
              <span className="seed-value">{seed.topic || 'Unknown'}</span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Length Preset</span>
              <span className="seed-value">{seed.length_preset || 'Unknown'}</span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Model</span>
              <span className="seed-value">{seed.model || 'Unknown'}</span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Generated</span>
              <span className="seed-value">
                {seed.generated_at ? new Date(seed.generated_at).toLocaleString() : 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        <div className="seed-section">
          <h3 className="seed-section-title">📊 Statistics</h3>
          <div className="seed-grid">
            <div className="seed-item">
              <span className="seed-label">Word Count</span>
              <span className="seed-value">{seed.word_count?.toLocaleString() || 'Unknown'}</span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Scene Count</span>
              <span className="seed-value">{seed.scene_count || 'Unknown'}</span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Generation Time</span>
              <span className="seed-value">
                {seed.generation_time_seconds ? `${seed.generation_time_seconds}s` : 'Unknown'}
              </span>
            </div>
            <div className="seed-item">
              <span className="seed-label">Version</span>
              <span className="seed-value">{seed.version || '1.0'}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render plot data nicely
  const renderPlot = (plotData) => {
    if (!plotData) return <p className="empty-text">No data available</p>;
    
    if (typeof plotData === 'string') {
      return <pre className="plan-text">{plotData}</pre>;
    }

    // If it's structured JSON with acts/chapters
    if (plotData.acts || Array.isArray(plotData)) {
      return (
        <div className="plot-structured">
          <pre className="plan-json">{JSON.stringify(plotData, null, 2)}</pre>
        </div>
      );
    }

    return <pre className="plan-json">{JSON.stringify(plotData, null, 2)}</pre>;
  };

  return (
    <div className="plan-panel">
      <h2>Story Plans</h2>
      
      <div className="plan-tabs">
        {seed && Object.keys(seed).length > 0 && (
          <button 
            className={`plan-tab ${activeTab === 'seed' ? 'active' : ''}`}
            onClick={() => setActiveTab('seed')}
          >
            📊 Metadata
          </button>
        )}
        {plans.initial_book_spec && (
          <button 
            className={`plan-tab ${activeTab === 'initial_spec' ? 'active' : ''}`}
            onClick={() => setActiveTab('initial_spec')}
          >
            1️⃣ Initial Spec
          </button>
        )}
        {plans.enhanced_book_spec && (
          <button 
            className={`plan-tab ${activeTab === 'enhanced_spec' ? 'active' : ''}`}
            onClick={() => setActiveTab('enhanced_spec')}
          >
            2️⃣ Enhanced Spec
          </button>
        )}
        {plans.initial_plot && (
          <button 
            className={`plan-tab ${activeTab === 'initial_plot' ? 'active' : ''}`}
            onClick={() => setActiveTab('initial_plot')}
          >
            3️⃣ Initial Plot
          </button>
        )}
        {plans.enhanced_plot && (
          <button 
            className={`plan-tab ${activeTab === 'enhanced_plot' ? 'active' : ''}`}
            onClick={() => setActiveTab('enhanced_plot')}
          >
            4️⃣ Enhanced Plot
          </button>
        )}
        {plans.scene_plan && (
          <button 
            className={`plan-tab ${activeTab === 'scene_plan' ? 'active' : ''}`}
            onClick={() => setActiveTab('scene_plan')}
          >
            5️⃣ Scene Plan
          </button>
        )}
      </div>

      <div className="plan-content">
        {activeTab === 'seed' && renderSeed()}
        
        {activeTab === 'initial_spec' && (
          <div className="spec-container">
            <pre className="plan-text">
              {plans.initial_book_spec || 'No initial book spec available'}
            </pre>
          </div>
        )}
        
        {activeTab === 'enhanced_spec' && (
          <div className="spec-container">
            <pre className="plan-text">
              {plans.enhanced_book_spec || 'No enhanced book spec available'}
            </pre>
          </div>
        )}
        
        {activeTab === 'initial_plot' && renderPlot(plans.initial_plot)}
        
        {activeTab === 'enhanced_plot' && renderPlot(plans.enhanced_plot)}
        
        {activeTab === 'scene_plan' && renderPlot(plans.scene_plan)}
      </div>
    </div>
  );
}

export default StoryPlanPanel;
