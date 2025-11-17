import React, { useState } from 'react';
import './SessionList.css';
import NewStoryModal from './NewStoryModal';

function SessionList({ sessions, selectedSession, onSelectSession }) {
  const [showNewStoryModal, setShowNewStoryModal] = useState(false);

  // Extract just the number from session ID (handles both "5" and "session_5")
  const getSessionNumber = (id) => {
    return id.replace('session_', '');
  };

  return (
    <div className="session-list">
      <h2>Stories</h2>
      
      <button 
        className="new-story-btn"
        onClick={() => setShowNewStoryModal(true)}
      >
        + New Story
      </button>

      <div className="session-items">
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${selectedSession?.id === session.id ? 'selected' : ''}`}
            onClick={() => onSelectSession(session)}
          >
            <div className="session-id">
              {getSessionNumber(session.id)}
              {session.seed?.length_preset && (
                <span className={`length-badge ${session.seed.length_preset}`}>
                  {session.seed.length_preset}
                </span>
              )}
            </div>
            <div className="session-meta">
              {Object.keys(session.judges).length} judges · {Object.keys(session.plans || {}).length} plans
            </div>
          </div>
        ))}
      </div>

      {showNewStoryModal && (
        <NewStoryModal
          onClose={() => setShowNewStoryModal(false)}
          onSubmit={() => {
            // Modal will close itself, just refresh will happen via polling
          }}
        />
      )}
    </div>
  );
}

export default SessionList;

