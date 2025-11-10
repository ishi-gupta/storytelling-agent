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

  const formatJSON = (data) => {
    if (!data) return 'No data available';
    return JSON.stringify(data, null, 2);
  };

  const formatSeed = () => {
    if (!seed || Object.keys(seed).length === 0) return 'No seed data available';
    
    return `📋 GENERATION METADATA
${'═'.repeat(50)}

Topic: ${seed.topic || 'Unknown'}
Length Preset: ${seed.length_preset || 'Unknown'}
Model: ${seed.model || 'Unknown'}
Generated: ${seed.generated_at ? new Date(seed.generated_at).toLocaleString() : 'Unknown'}

📊 STATS
${'═'.repeat(50)}

Word Count: ${seed.word_count || 'Unknown'}
Scene Count: ${seed.scene_count || 'Unknown'}
Generation Time: ${seed.generation_time_seconds ? `${seed.generation_time_seconds}s` : 'Unknown'}

Version: ${seed.version || '1.0'}`;
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
            Seed
          </button>
        )}
        {plans.initial_book_spec && (
          <button 
            className={`plan-tab ${activeTab === 'initial_spec' ? 'active' : ''}`}
            onClick={() => setActiveTab('initial_spec')}
          >
            1. Initial Spec
          </button>
        )}
        {plans.enhanced_book_spec && (
          <button 
            className={`plan-tab ${activeTab === 'enhanced_spec' ? 'active' : ''}`}
            onClick={() => setActiveTab('enhanced_spec')}
          >
            2. Enhanced Spec
          </button>
        )}
        {plans.initial_plot && (
          <button 
            className={`plan-tab ${activeTab === 'initial_plot' ? 'active' : ''}`}
            onClick={() => setActiveTab('initial_plot')}
          >
            3. Initial Plot
          </button>
        )}
        {plans.enhanced_plot && (
          <button 
            className={`plan-tab ${activeTab === 'enhanced_plot' ? 'active' : ''}`}
            onClick={() => setActiveTab('enhanced_plot')}
          >
            4. Enhanced Plot
          </button>
        )}
        {plans.scene_plan && (
          <button 
            className={`plan-tab ${activeTab === 'scene_plan' ? 'active' : ''}`}
            onClick={() => setActiveTab('scene_plan')}
          >
            5. Scene Plan
          </button>
        )}
      </div>

      <div className="plan-content">
        {activeTab === 'seed' && (
          <pre className="plan-text">
            {formatSeed()}
          </pre>
        )}
        
        {activeTab === 'initial_spec' && (
          <pre className="plan-text">
            {plans.initial_book_spec || 'No initial book spec available'}
          </pre>
        )}
        
        {activeTab === 'enhanced_spec' && (
          <pre className="plan-text">
            {plans.enhanced_book_spec || 'No enhanced book spec available'}
          </pre>
        )}
        
        {activeTab === 'initial_plot' && (
          <pre className="plan-text">
            {formatJSON(plans.initial_plot)}
          </pre>
        )}
        
        {activeTab === 'enhanced_plot' && (
          <pre className="plan-text">
            {formatJSON(plans.enhanced_plot)}
          </pre>
        )}
        
        {activeTab === 'scene_plan' && (
          <pre className="plan-text">
            {formatJSON(plans.scene_plan)}
          </pre>
        )}
      </div>
    </div>
  );
}

export default StoryPlanPanel;

