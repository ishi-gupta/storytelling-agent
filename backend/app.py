#!/usr/bin/env python3
"""
Flask Backend for GOAT Story IDE
Provides live API endpoints for story generation and session management
"""

import os
import json
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import fcntl
import time
import subprocess
import sys
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow React (port 3000) to talk to Flask (port 5000)

# Get the base directory (where this file lives)
BASE_DIR = Path(__file__).parent.parent
SESSIONS_DIR = BASE_DIR / "story_generation_logs"
LOCK_FILE = BASE_DIR / ".session_lock"


def allocate_next_session_id():
    """
    Atomically allocate the next session ID using file locking
    This prevents race conditions when multiple requests try to generate stories simultaneously
    
    Returns:
        int: The next available session ID
    """
    # Ensure lock file exists
    LOCK_FILE.touch(exist_ok=True)
    
    # Open lock file and acquire exclusive lock
    with open(LOCK_FILE, 'r+') as lock_file:
        # fcntl.LOCK_EX = exclusive lock (blocks until available)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        
        try:
            # Now that we have the lock, safely determine next ID
            existing_sessions = [d.name for d in SESSIONS_DIR.iterdir() if d.is_dir()]
            session_numbers = [
                int(s.replace('session_', ''))
                for s in existing_sessions
                if s.replace('session_', '').isdigit()
            ]
            next_id = max(session_numbers) + 1 if session_numbers else 1
            
            # Create the session directory while we hold the lock
            session_name = f"session_{next_id}"
            session_dir = SESSIONS_DIR / session_name
            session_dir.mkdir(exist_ok=True)
            (session_dir / "plans").mkdir(exist_ok=True)
            (session_dir / "evaluations").mkdir(exist_ok=True)
            
            return next_id, session_dir
        finally:
            # Always release the lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def load_session(session_path):
    """
    Load a single session from disk
    This is the same logic as export_sessions.py, but as a function
    """
    session_id = session_path.name
    session_data = {
        "id": session_id,
        "seed": {},
        "plans": {},
        "judges": {},
        "story": ""
    }
    
    # Load seed.json
    seed_file = session_path / "seed.json"
    if seed_file.exists():
        with open(seed_file, 'r', encoding='utf-8') as f:
            session_data["seed"] = json.load(f)
    
    # Load plans
    plans_dir = session_path / "plans"
    if plans_dir.exists():
        plan_files = [
            "1_initial_book_spec.txt",
            "2_enhanced_book_spec.txt",
            "3_initial_plot.json",
            "4_enhanced_plot.json",
            "5_scene_plan.json"
        ]
        
        for filename in plan_files:
            plan_file = plans_dir / filename
            if plan_file.exists():
                if filename.endswith('.json'):
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        session_data["plans"][filename] = json.load(f)
                else:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        session_data["plans"][filename] = f.read()
    
    # Load evaluations (judges)
    eval_dir = session_path / "evaluations"
    if eval_dir.exists():
        judge_files = {
            "gpa_evaluation.json": "gpa",
            "structure_analysis.json": "structure",
            "structure_analysis_simple.json": "structure_simple",
            "character_analysis.json": "character",
            "plot_analysis.json": "plot",
            "writing_quality.json": "writing_quality"
        }
        
        for filename, key in judge_files.items():
            judge_file = eval_dir / filename
            if judge_file.exists():
                with open(judge_file, 'r', encoding='utf-8') as f:
                    session_data["judges"][key] = json.load(f)
    
    # Load final story
    story_file = session_path / "final_story.txt"
    if story_file.exists():
        with open(story_file, 'r', encoding='utf-8') as f:
            session_data["story"] = f.read()
    
    return session_data


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """
    GET /api/sessions
    Returns all story sessions from story_generation_logs/
    
    This endpoint replaces the need for export_sessions.py
    React can poll this every few seconds for live updates
    """
    try:
        sessions = []
        
        # Check if sessions directory exists
        if not SESSIONS_DIR.exists():
            return jsonify({"sessions": []})
        
        # Get all session directories and sort by number (ascending: 1, 2, 3...)
        session_dirs = sorted(
            [d for d in SESSIONS_DIR.iterdir() if d.is_dir()],
            key=lambda x: int(x.name.replace('session_', '')) if x.name.replace('session_', '').isdigit() else 999,
            reverse=False  # Ascending order (1, 2, 3...)
        )
        
        # Load each session
        for session_dir in session_dirs:
            try:
                session_data = load_session(session_dir)
                sessions.append(session_data)
            except Exception as e:
                print(f"Error loading session {session_dir.name}: {e}")
                continue
        
        return jsonify({"sessions": sessions})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    GET /api/health
    Simple health check to verify server is running
    """
    return jsonify({
        "status": "ok",
        "message": "GOAT Story Backend is running!",
        "sessions_dir": str(SESSIONS_DIR)
    })


@app.route('/api/generate/start', methods=['POST'])
def start_generation():
    """
    POST /api/generate/start
    Starts a new story generation
    
    Request body:
    {
        "topic": "a detective solving a mystery",
        "length": "short"
    }
    
    Returns:
    {
        "session_id": "10",
        "status": "started"
    }
    """
    try:
        data = request.json
        topic = data.get('topic', 'a detective solving a mystery')
        length = data.get('length', 'medium')
        
        # Atomically allocate next session ID (prevents race conditions)
        next_id, session_dir = allocate_next_session_id()
        
        # Create initial seed.json
        seed_data = {
            "topic": topic,
            "length_preset": length,
            "model": "gpt-5",
            "generated_at": datetime.now().isoformat(),
            "status": "generating",
            "version": "2.0"
        }
        
        with open(session_dir / "seed.json", 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
        # Generate ONLY Step 1 (initial book spec) for the wizard
        # Import the agent - use base StoryAgent since LoggingStoryAgent has path issues
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from goat_storytelling_agent.storytelling_agent import StoryAgent
        from story_presets import get_preset
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OPENAI_API_KEY not set"}), 500
        
        preset = get_preset(length)
        
        # Create agent instance - use base StoryAgent
        agent = StoryAgent(
            backend_uri=api_key,
            backend="openai",
            model="gpt-5",
            max_tokens=2000,
            story_preset=preset,
            extra_options={"temperature": 1.0, "top_p": 1.0}
        )
        
        # Manually set paths for saving
        agent.session_dir = str(session_dir)
        agent.plans_dir = str(session_dir / "plans")
        
        # Generate ONLY initial book spec (Step 1)
        # Don't run full story generation - wizard will handle the rest
        _, initial_spec = agent.init_book_spec(topic)
        
        # Save the plan manually
        plan_file = session_dir / "plans" / "1_initial_book_spec.txt"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(initial_spec)
        
        return jsonify({
            "session_id": str(next_id),
            "status": "generating",
            "message": f"Initial book spec generated for session {next_id}",
            "initial_spec": initial_spec
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/session/<session_id>/save-plan', methods=['POST'])
def save_plan_edit(session_id):
    """
    Save user edits to a plan file
    POST /api/session/session_15/save-plan or POST /api/session/15/save-plan
    Body: { "filename": "1_initial_book_spec.txt", "content": "..." }
    """
    try:
        data = request.json
        filename = data.get('filename')
        content = data.get('content')
        
        # Handle both "session_23" and "23" formats
        if not session_id.startswith('session_'):
            session_id = f"session_{session_id}"
        
        session_dir = SESSIONS_DIR / session_id
        plan_path = session_dir / "plans" / filename
        
        # Save the edited content
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "success": True,
            "message": f"Saved {filename}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/session/<session_id>/generate-next', methods=['POST'])
def generate_next_step(session_id):
    """
    Generate the next step in the story planning process
    POST /api/session/session_15/generate-next or POST /api/session/15/generate-next
    Body: { "current_step": 1 }
    
    Steps:
    1 → enhance book spec
    2 → create plot
    3 → enhance plot
    4 → create scene plan
    5 → generate full story
    """
    try:
        current_step = request.json.get('current_step')
        
        # Handle both "session_23" and "23" formats
        if not session_id.startswith('session_'):
            session_id = f"session_{session_id}"
        
        session_dir = SESSIONS_DIR / session_id
        
        # Load seed to get topic and length
        with open(session_dir / "seed.json", 'r') as f:
            seed = json.load(f)
        
        # Import the existing agent
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from generate_story import LoggingStoryAgent
        from story_presets import get_preset
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OPENAI_API_KEY not set"}), 500
        
        preset = get_preset(seed.get('length_preset', 'medium'))
        
        # Create agent instance - use base StoryAgent
        from goat_storytelling_agent.storytelling_agent import StoryAgent
        
        agent = StoryAgent(
            backend_uri=api_key,
            backend="openai",
            model="gpt-5",
            max_tokens=2000,
            story_preset=preset,
            extra_options={"temperature": 1.0, "top_p": 1.0}
        )
        
        result = None
        next_step = current_step + 1
        result_filename = None
        
        # Execute the appropriate generation step
        if current_step == 1:
            # Enhance book spec
            with open(session_dir / "plans" / "1_initial_book_spec.txt", 'r') as f:
                initial_spec = f.read()
            
            _, result = agent.enhance_book_spec(initial_spec)
            result_filename = "2_enhanced_book_spec.txt"
            
            # Save manually
            with open(session_dir / "plans" / result_filename, 'w', encoding='utf-8') as f:
                f.write(result)
        
        elif current_step == 2:
            # Create plot from enhanced spec
            with open(session_dir / "plans" / "2_enhanced_book_spec.txt", 'r') as f:
                enhanced_spec = f.read()
            
            _, result = agent.create_plot_chapters(enhanced_spec)
            result_filename = "3_initial_plot.json"
            
            # Save manually
            with open(session_dir / "plans" / result_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            result = json.dumps(result, indent=2)  # Convert to string for frontend
        
        elif current_step == 3:
            # Enhance plot
            with open(session_dir / "plans" / "2_enhanced_book_spec.txt", 'r') as f:
                book_spec = f.read()
            with open(session_dir / "plans" / "3_initial_plot.json", 'r') as f:
                initial_plot = json.load(f)
            
            _, result = agent.enhance_plot_chapters(book_spec, initial_plot)
            result_filename = "4_enhanced_plot.json"
            
            # Save manually
            with open(session_dir / "plans" / result_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            result = json.dumps(result, indent=2)
        
        elif current_step == 4:
            # Create scene plan
            with open(session_dir / "plans" / "4_enhanced_plot.json", 'r') as f:
                enhanced_plot = json.load(f)
            
            _, result = agent.split_chapters_into_scenes(enhanced_plot)
            result_filename = "5_scene_plan.json"
            
            # Save manually
            with open(session_dir / "plans" / result_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            result = json.dumps(result, indent=2)
        
        elif current_step == 5:
            # Generate full story (this will take a while)
            # For now, just trigger the existing generation
            return jsonify({
                "next_step": 6,
                "message": "Full story generation started",
                "generating": True
            })
        
        else:
            return jsonify({"error": "Invalid step number"}), 400
        
        return jsonify({
            "success": True,
            "next_step": next_step,
            "result": result,
            "filename": result_filename
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Get port from environment or default to 5001 (5000 is used by macOS AirPlay)
    port = int(os.getenv('PORT', 5001))
    
    print("=" * 60)
    print("🚀 GOAT Story Backend Server Starting...")
    print("=" * 60)
    print(f"📡 Running on: http://localhost:{port}")
    print(f"📂 Sessions directory: {SESSIONS_DIR}")
    print(f"💡 React should connect to: http://localhost:{port}/api/sessions")
    print("=" * 60)
    
    # Run Flask server
    app.run(
        host='0.0.0.0',  # Accept connections from anywhere (needed for React)
        port=port,
        debug=True  # Auto-reload when code changes
    )

