import React, { useState, useEffect } from 'react';
import './App.css';
import SessionList from './components/SessionList';
import StoryViewer from './components/StoryViewer';
import JudgePanel from './components/JudgePanel';
import JudgeModal from './components/JudgeModal';
import StoryPlanPanel from './components/StoryPlanPanel';
import StoryWizard from './components/StoryWizard';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

function App() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [selectedJudge, setSelectedJudge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('story'); // 'story' or 'plans'

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/sessions');
      const data = await response.json();
      setSessions(data.sessions);
      
      // Auto-select first session if none selected
      if (data.sessions.length > 0 && !selectedSession) {
        setSelectedSession(data.sessions[0]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading sessions from Flask:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchSessions();

    // Poll for updates every 3 seconds (live updates!)
    const pollInterval = setInterval(fetchSessions, 3000);

    // Cleanup interval when component unmounts
    return () => clearInterval(pollInterval);
  }, [selectedSession]);

  const handleNewStory = async (sessionId) => {
    // Wait a moment for the session to be created
    setTimeout(async () => {
      await fetchSessions();
      // Find and select the new session
      const newSession = sessions.find(s => s.id === `session_${sessionId}`);
      if (newSession) {
        setSelectedSession(newSession);
      }
      // Auto-switch to Plans view
      setViewMode('plans');
    }, 1000);
  };

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
            onNewStory={handleNewStory}
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
              // Show wizard if session is in progress, otherwise show plans
              selectedSession?.seed?.status === 'generating' ? (
                <StoryWizard 
                  session={selectedSession}
                  onComplete={() => {
                    // Refresh sessions when wizard completes
                    fetch('http://localhost:5001/api/sessions')
                      .then(res => res.json())
                      .then(data => setSessions(data.sessions));
                  }}
                />
              ) : (
                <StoryPlanPanel session={selectedSession} />
              )
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
