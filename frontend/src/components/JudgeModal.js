import React from 'react';
import './JudgeModal.css';

function JudgeModal({ judge, onClose }) {
  if (!judge) return null;

  // Format analysis content with proper structure
  const renderContent = () => {
    const data = judge.data;

    // Structure judges (simple & detailed) - already well formatted
    if (data.structure_analysis || data.structure_analysis_simple) {
      const content = data.structure_analysis || data.structure_analysis_simple;
      return (
        <div className="judge-formatted">
          <pre className="judge-text">{content}</pre>
        </div>
      );
    }

    // GPA Judge - show three sections with nice headers
    if (data.goal || data.plan || data.action) {
      return (
        <div className="judge-formatted">
          {data.goal && (
            <div className="judge-section">
              <h3 className="section-title">📋 Goal Evaluation</h3>
              <div className="section-content">
                <pre className="judge-json">{JSON.stringify(data.goal, null, 2)}</pre>
              </div>
            </div>
          )}
          
          {data.plan && (
            <div className="judge-section">
              <h3 className="section-title">🗺️ Plan Evaluation</h3>
              <div className="section-content">
                <pre className="judge-json">{JSON.stringify(data.plan, null, 2)}</pre>
              </div>
            </div>
          )}
          
          {data.action && (
            <div className="judge-section">
              <h3 className="section-title">⚡ Action Evaluation</h3>
              <div className="section-content">
                <pre className="judge-json">{JSON.stringify(data.action, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      );
    }

    // Character Analysis
    if (data.character_analysis) {
      return (
        <div className="judge-formatted">
          <pre className="judge-text">{data.character_analysis}</pre>
        </div>
      );
    }

    // Plot Analysis
    if (data.plot_analysis) {
      return (
        <div className="judge-formatted">
          <pre className="judge-text">{data.plot_analysis}</pre>
        </div>
      );
    }

    // Writing Quality
    if (data.writing_analysis || data.overall_assessment) {
      return (
        <div className="judge-formatted">
          {data.overall_assessment && (
            <div className="judge-section">
              <h3 className="section-title">📊 Overall Assessment</h3>
              <div className="section-content">
                <pre className="judge-json">{JSON.stringify(data.overall_assessment, null, 2)}</pre>
              </div>
            </div>
          )}
          
          {data.scene_analyses && (
            <div className="judge-section">
              <h3 className="section-title">📝 Scene Analyses</h3>
              <div className="section-content">
                {data.scene_analyses.map((scene, idx) => (
                  <div key={idx} className="scene-analysis">
                    <h4 className="scene-title">Scene {scene.scene_number || idx + 1}</h4>
                    <pre className="judge-json">{JSON.stringify(scene, null, 2)}</pre>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {data.writing_analysis && (
            <div className="judge-section">
              <pre className="judge-text">{data.writing_analysis}</pre>
            </div>
          )}
        </div>
      );
    }

    // Generic analysis field
    if (data.analysis) {
      return (
        <div className="judge-formatted">
          <pre className="judge-text">{typeof data.analysis === 'string' ? data.analysis : JSON.stringify(data.analysis, null, 2)}</pre>
        </div>
      );
    }

    // Fallback: show raw JSON
    return (
      <div className="judge-formatted">
        <pre className="judge-json">{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{judge.name} Evaluation</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default JudgeModal;
