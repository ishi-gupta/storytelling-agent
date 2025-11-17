# Step-by-Step Interactive Story Generation Architecture

## Problem Statement

Currently, story generation is "fire and forget":
1. User clicks "New Story" 
2. Backend spawns `generate_story.py` as a subprocess
3. Story generates completely in background (5+ minutes)
4. No way to stop, pause, or edit intermediate stages
5. No live feedback except polling for completion

## Proposed Solution: Interactive IDE Mode

### User Experience Flow

```
Step 1: User enters topic + length
    ↓
Step 2: System generates INITIAL BOOK SPEC
    ↓
    [User sees spec in editable text box]
    [User can edit, then clicks "Next Step →"]
    ↓
Step 3: System generates ENHANCED BOOK SPEC (using edited spec)
    ↓
    [User sees enhanced spec, can edit]
    [User clicks "Next Step →"]
    ↓
Step 4: System generates INITIAL PLOT (3 acts, chapters)
    ↓
    [User sees plot outline, can edit]
    [User clicks "Next Step →"]
    ↓
Step 5: System generates ENHANCED PLOT
    ↓
    [User sees refined plot, can edit]
    [User clicks "Next Step →"]
    ↓
Step 6: System generates SCENE PLAN (breakdown of each chapter into scenes)
    ↓
    [User sees scene plan, can edit]
    [User clicks "Generate Full Story →"]
    ↓
Step 7: System writes all scenes sequentially
    ↓
    [Live progress: "Writing Scene 3/12..."]
    [User can STOP at any time]
    ↓
Done! Story saved to session folder
```

### Technical Architecture

#### Option A: Synchronous API (Simpler, but long requests)

**Backend Changes:**
```python
# New endpoints in app.py

@app.route('/api/generate/spec', methods=['POST'])
def generate_initial_spec():
    """
    Body: { "topic": "...", "length": "medium" }
    Returns: { "spec": "...", "session_id": "X" }
    """
    # Creates session, generates ONLY the initial spec
    # Returns result immediately (waits for LLM)
    # Timeout: ~30 seconds

@app.route('/api/generate/enhance-spec', methods=['POST'])
def enhance_spec():
    """
    Body: { "session_id": "X", "spec": "..." }
    Returns: { "enhanced_spec": "..." }
    """
    # Takes user-edited spec, enhances it
    # Returns result immediately
    # Timeout: ~30 seconds

@app.route('/api/generate/plot', methods=['POST'])
def generate_plot():
    """
    Body: { "session_id": "X", "book_spec": "..." }
    Returns: { "plot": {...} }  # JSON with 3 acts
    """
    # Generates plot based on (edited) spec
    # Timeout: ~45 seconds

# ... similar endpoints for enhance-plot, scene-plan, write-story
```

**Frontend Changes:**
```javascript
// NewStoryWizard.js (new component)
const [step, setStep] = useState(1);
const [sessionId, setSessionId] = useState(null);
const [spec, setSpec] = useState('');
const [loading, setLoading] = useState(false);

const handleStep1 = async () => {
  setLoading(true);
  const response = await fetch('/api/generate/spec', {
    method: 'POST',
    body: JSON.stringify({ topic, length })
  });
  const data = await response.json();
  setSessionId(data.session_id);
  setSpec(data.spec);
  setStep(2);
  setLoading(false);
};

// Similar handlers for each step...
```

**Pros:**
- ✅ Simple to implement
- ✅ User has full control
- ✅ Can edit at each stage

**Cons:**
- ❌ Long HTTP requests (30-60 seconds each)
- ❌ Timeout issues if LLM is slow
- ❌ Can't show real-time progress during scene writing

---

#### Option B: WebSocket Streaming (More complex, better UX)

**Backend Changes:**
```python
# Add Flask-SocketIO
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('generate_spec')
def handle_generate_spec(data):
    """
    Client sends: { "topic": "...", "length": "medium" }
    Server emits: 
      - 'progress': { "step": "Generating spec...", "percent": 10 }
      - 'spec_ready': { "spec": "...", "session_id": "X" }
    """
    session_id = allocate_next_session_id()
    emit('progress', {'step': 'Generating initial spec...', 'percent': 10})
    
    spec = story_agent.generate_initial_spec(data['topic'])
    
    emit('spec_ready', {'spec': spec, 'session_id': session_id})

@socketio.on('generate_plot')
def handle_generate_plot(data):
    """
    Client sends: { "session_id": "X", "book_spec": "..." }
    Server streams progress, then emits 'plot_ready'
    """
    emit('progress', {'step': 'Creating plot structure...', 'percent': 40})
    # ... generate plot ...
    emit('plot_ready', {'plot': plot})

@socketio.on('write_story')
def handle_write_story(data):
    """
    Client sends: { "session_id": "X", "scene_plan": {...} }
    Server emits progress for EACH scene:
      - 'scene_progress': { "current": 3, "total": 12, "text": "..." }
      - 'story_complete': { "session_id": "X" }
    """
    total_scenes = count_scenes(data['scene_plan'])
    for i, scene in enumerate(data['scene_plan']):
        emit('progress', {
            'step': f'Writing scene {i+1}/{total_scenes}...',
            'percent': int((i+1) / total_scenes * 100)
        })
        scene_text = story_agent.write_scene(scene)
        emit('scene_progress', {
            'current': i+1,
            'total': total_scenes,
            'text': scene_text
        })
    emit('story_complete', {'session_id': data['session_id']})
```

**Frontend Changes:**
```javascript
// Use socket.io-client
import io from 'socket.io-client';

const socket = io('http://localhost:5001');

socket.on('progress', (data) => {
  setProgress(data.percent);
  setStatusMessage(data.step);
});

socket.on('spec_ready', (data) => {
  setSessionId(data.session_id);
  setSpec(data.spec);
  setStep(2);
});

socket.on('scene_progress', (data) => {
  setStoryText(prev => prev + '\n\n' + data.text);
  setProgress(Math.round(data.current / data.total * 100));
});
```

**Pros:**
- ✅ Real-time progress updates
- ✅ Can show scene-by-scene generation
- ✅ User can STOP mid-generation
- ✅ No timeout issues
- ✅ Better UX (feels more "live")

**Cons:**
- ❌ More complex to implement
- ❌ Requires WebSocket library (Flask-SocketIO)
- ❌ Harder to debug

---

### Recommended Approach

**Phase 1 (Quick Demo):** Option A - Synchronous API
- Implement 6 endpoints (spec, enhance-spec, plot, enhance-plot, scene-plan, write-story)
- Create wizard-style React component
- Each step is a separate API call
- User edits in text boxes between steps
- **Time to implement:** 2-3 hours

**Phase 2 (Polish):** Add WebSocket streaming for final story writing
- Keep steps 1-5 as synchronous APIs (they're fast enough)
- Only use WebSocket for step 6 (writing scenes)
- Shows live progress: "Writing Scene 5/12..."
- User can click "Stop" to cancel generation
- **Time to implement:** 1-2 hours additional

---

### Data Flow Example

```
User Input: "A detective solving a mystery" (medium length)
    ↓
POST /api/generate/spec
    ← Response: { session_id: "14", spec: "Title: The Missing Manuscript..." }
    ↓
User edits spec: "Title: The Vanishing Violin..."
    ↓
POST /api/generate/enhance-spec { session_id: "14", spec: "Title: The Vanishing Violin..." }
    ← Response: { enhanced_spec: "Enhanced version with more detail..." }
    ↓
User clicks "Next Step" (doesn't edit)
    ↓
POST /api/generate/plot { session_id: "14", book_spec: "..." }
    ← Response: { plot: { acts: [...] } }
    ↓
User edits plot JSON: Adds a subplot
    ↓
POST /api/generate/enhance-plot { session_id: "14", plot: {...} }
    ← Response: { enhanced_plot: {...} }
    ↓
... continue through all steps ...
    ↓
Final story saved to session_14/final_story.txt
```

---

### Files to Create/Modify

**Backend:**
- `backend/app.py` - Add 6 new endpoints
- `backend/story_generator_api.py` (NEW) - Wrapper around `storytelling_agent.py` for API use

**Frontend:**
- `frontend/src/components/StoryWizard.js` (NEW) - Multi-step form
- `frontend/src/components/StoryWizard.css` (NEW)
- `frontend/src/App.js` - Add route to wizard
- `frontend/src/components/SessionList.js` - Update "New Story" button to open wizard

---

### Next Steps

1. ✅ **Fix race condition** (DONE - implemented file locking)
2. Choose approach (A or B)
3. Implement backend endpoints
4. Build frontend wizard component
5. Test step-by-step generation
6. Add "Stop" button if using WebSockets

