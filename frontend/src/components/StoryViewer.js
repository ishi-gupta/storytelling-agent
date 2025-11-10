import React from 'react';
import './StoryViewer.css';

function StoryViewer({ session }) {
  if (!session) {
    return (
      <div className="story-viewer empty">
        <p>Select a story to view</p>
      </div>
    );
  }

  return (
    <div className="story-viewer">
      <div className="story-header">
        <h2>{session.title}</h2>
        <div className="story-meta">Session {session.id}</div>
      </div>
      <div className="story-content">
        {session.story ? (
          <pre className="story-text">{session.story}</pre>
        ) : (
          <p className="no-story">No story text available</p>
        )}
      </div>
    </div>
  );
}

export default StoryViewer;

