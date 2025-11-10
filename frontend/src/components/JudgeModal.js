import React from 'react';
import './JudgeModal.css';

function JudgeModal({ judge, onClose }) {
  if (!judge) return null;

  // Extract and format the main text content from judge data
  const getFormattedContent = () => {
    // Structure judges - already formatted text
    if (judge.data.structure_analysis) {
      return { type: 'text', content: judge.data.structure_analysis };
    }
    if (judge.data.structure_analysis_simple) {
      return { type: 'text', content: judge.data.structure_analysis_simple };
    }
    
    // GPA judge - format the three sections nicely
    if (judge.data.goal || judge.data.plan || judge.data.action) {
      let formatted = '';
      
      const formatSection = (data) => {
        try {
          // Try to parse as JSON and pretty-print
          const parsed = typeof data === 'string' ? JSON.parse(data) : data;
          return JSON.stringify(parsed, null, 2);
        } catch (e) {
          // If not valid JSON, return as-is
          return typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        }
      };
      
      if (judge.data.goal) {
        formatted += '═══════════════════════════════════════\n';
        formatted += '📋 GOAL EVALUATION\n';
        formatted += '═══════════════════════════════════════\n\n';
        formatted += formatSection(judge.data.goal);
        formatted += '\n\n';
      }
      
      if (judge.data.plan) {
        formatted += '═══════════════════════════════════════\n';
        formatted += '🗺️  PLAN EVALUATION\n';
        formatted += '═══════════════════════════════════════\n\n';
        formatted += formatSection(judge.data.plan);
        formatted += '\n\n';
      }
      
      if (judge.data.action) {
        formatted += '═══════════════════════════════════════\n';
        formatted += '⚡ ACTION EVALUATION\n';
        formatted += '═══════════════════════════════════════\n\n';
        formatted += formatSection(judge.data.action);
      }
      
      return { type: 'text', content: formatted };
    }
    
    // Character analysis or other judges
    if (judge.data.analysis || judge.data.character_analysis) {
      const analysis = judge.data.analysis || judge.data.character_analysis;
      return { 
        type: 'text', 
        content: typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2)
      };
    }
    
    // Default: show formatted JSON
    return { type: 'json', content: JSON.stringify(judge.data, null, 2) };
  };

  const { type, content } = getFormattedContent();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{judge.name.toUpperCase()} Evaluation</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className={type === 'json' ? 'judge-output' : 'judge-output-formatted'}>
            {content}
          </div>
        </div>
      </div>
    </div>
  );
}

export default JudgeModal;

