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
        plan_files = {
            "1_initial_book_spec.txt": "initial_book_spec",
            "2_enhanced_book_spec.txt": "enhanced_book_spec",
            "3_initial_plot.json": "initial_plot",
            "4_enhanced_plot.json": "enhanced_plot",
            "5_scene_plan.json": "scene_plan"
        }
        
        for filename, key in plan_files.items():
            plan_file = plans_dir / filename
            if plan_file.exists():
                if filename.endswith('.json'):
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        session_data["plans"][key] = json.load(f)
                else:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        session_data["plans"][key] = f.read()
    
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
        
        # Start story generation in background (non-blocking)
        # Get the path to the generate_story.py script
        script_path = BASE_DIR / "generate_story.py"
        python_path = sys.executable
        
        # Run in background without blocking, pass session ID to avoid race condition
        subprocess.Popen(
            [python_path, str(script_path), '--length', length, '--topic', topic, '--session-id', str(next_id)],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return jsonify({
            "session_id": str(next_id),
            "status": "started",
            "message": f"Story generation started for session {next_id}"
        })
    
    except Exception as e:
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

