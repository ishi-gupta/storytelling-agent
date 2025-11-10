import React from 'react';
import './JudgePanel.css';

function JudgePanel({ session, onSelectJudge }) {
  if (!session) {
    return <div className="judge-panel empty">Select a story to view judges</div>;
  }

  const judges = session.judges || {};
  const judgeNames = Object.keys(judges);

  if (judgeNames.length === 0) {
    return (
      <div className="judge-panel empty">
        <p>No judge evaluations yet</p>
      </div>
    );
  }

  const getJudgeScore = (judgeName, judgeData) => {
    // Try to extract a score from the judge data
    if (judgeData.goal) {
      return "GPA Judge";
    }
    if (judgeData.structure_analysis || judgeData.structure_analysis_simple) {
      return "Structure";
    }
    return "Evaluated";
  };

  return (
    <div className="judge-panel">
      <h2>Judges</h2>
      <div className="judge-cards">
        {judgeNames.map(judgeName => (
          <div
            key={judgeName}
            className="judge-card"
            onClick={() => onSelectJudge({ name: judgeName, data: judges[judgeName] })}
          >
            <div className="judge-name">{judgeName.toUpperCase()}</div>
            <div className="judge-score">{getJudgeScore(judgeName, judges[judgeName])}</div>
            <div className="judge-action">Click for details →</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default JudgePanel;

