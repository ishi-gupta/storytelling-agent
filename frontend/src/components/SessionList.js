import React from 'react';
import './SessionList.css';

function SessionList({ sessions, selectedSession, onSelectSession }) {
  return (
    <div className="session-list">
      <h2>Stories</h2>
      <div className="session-items">
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${selectedSession?.id === session.id ? 'selected' : ''}`}
            onClick={() => onSelectSession(session)}
          >
            <div className="session-id">
              Session {session.id}
              {session.seed?.length_preset && (
                <span className={`length-badge ${session.seed.length_preset}`}>
                  {session.seed.length_preset}
                </span>
              )}
            </div>
            <div className="session-title">{session.title}</div>
            <div className="session-meta">
              {Object.keys(session.judges).length} judges · {Object.keys(session.plans || {}).length} plans
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SessionList;

