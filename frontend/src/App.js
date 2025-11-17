import React, { useState, useEffect } from 'react';
import './App.css';
import SessionList from './components/SessionList';
import StoryViewer from './components/StoryViewer';
import JudgePanel from './components/JudgePanel';
import JudgeModal from './components/JudgeModal';
import StoryPlanPanel from './components/StoryPlanPanel';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

function App() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [selectedJudge, setSelectedJudge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('story'); // 'story' or 'plans'

  useEffect(() => {
    // Load data from public/data.json
    fetch('/data.json')
      .then(res => res.json())
      .then(data => {
        setSessions(data.sessions);
        if (data.sessions.length > 0) {
          setSelectedSession(data.sessions[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading data:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="App loading">
        <h2>Loading stories...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>📊 Story Evaluation Dashboard</h1>
        <p>{sessions.length} stories generated</p>
      </header>
      
      <PanelGroup direction="horizontal" className="app-layout">
        <Panel defaultSize={20} minSize={15} maxSize={35}>
          <SessionList
            sessions={sessions}
            selectedSession={selectedSession}
            onSelectSession={setSelectedSession}
          />
        </Panel>
        
        <PanelResizeHandle className="resize-handle" />
        
        <Panel defaultSize={55} minSize={30}>
          <div className="main-content">
            <div className="view-toggle">
              <button 
                className={`toggle-btn ${viewMode === 'story' ? 'active' : ''}`}
                onClick={() => setViewMode('story')}
              >
                📖 Story
              </button>
              <button 
                className={`toggle-btn ${viewMode === 'plans' ? 'active' : ''}`}
                onClick={() => setViewMode('plans')}
              >
                📋 Plans
              </button>
            </div>
            
            {viewMode === 'story' ? (
              <StoryViewer session={selectedSession} />
            ) : (
              <StoryPlanPanel session={selectedSession} />
            )}
          </div>
        </Panel>
        
        <PanelResizeHandle className="resize-handle" />
        
        <Panel defaultSize={25} minSize={20} maxSize={40}>
          <JudgePanel
            session={selectedSession}
            onSelectJudge={setSelectedJudge}
          />
        </Panel>
      </PanelGroup>

      {selectedJudge && (
        <JudgeModal
          judge={selectedJudge}
          onClose={() => setSelectedJudge(null)}
        />
      )}
    </div>
  );
}

export default App;
