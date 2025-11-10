#!/usr/bin/env python3
"""
Log Viewer for GOAT Storytelling Agent
"""

import json
import os
import sys
from datetime import datetime

def list_sessions():
    """List all available sessions (numeric sessions first, then old timestamp sessions)"""
    logs_dir = "story_generation_logs"
    if not os.path.exists(logs_dir):
        print("No logs directory found.")
        return []
    
    numeric_sessions = []
    old_sessions = []
    
    for item in os.listdir(logs_dir):
        if item.startswith("session_"):
            session_path = os.path.join(logs_dir, item)
            if os.path.isdir(session_path):
                # Try to extract numeric ID
                try:
                    session_num = int(item.replace("session_", ""))
                    numeric_sessions.append((session_num, item))
                except ValueError:
                    # Old timestamp format
                    old_sessions.append(item)
    
    # Sort numeric sessions by number (highest first)
    numeric_sessions.sort(key=lambda x: x[0], reverse=True)
    # Sort old sessions (most recent first by name)
    old_sessions.sort(reverse=True)
    
    # Combine: numeric first, then old format
    sessions = [item for _, item in numeric_sessions] + old_sessions
    return sessions

def show_session_summary(session_id):
    """Show summary of a session"""
    session_dir = os.path.join("story_generation_logs", session_id)
    json_file = os.path.join(session_dir, "generation_log.json")
    
    if not os.path.exists(json_file):
        print(f"Log file not found for session {session_id}")
        return
    
    with open(json_file, "r") as f:
        log_data = json.load(f)
    
    print(f"\n📊 SESSION SUMMARY: {session_id}")
    print("=" * 60)
    print(f"📅 Generated: {log_data['timestamp']}")
    print(f"📝 Topic: {log_data.get('topic', 'N/A')}")
    print(f"📈 Total Steps: {len(log_data['steps'])}")
    
    # Count step types
    step_counts = {}
    error_count = 0
    for step in log_data['steps']:
        step_name = step['step']
        step_counts[step_name] = step_counts.get(step_name, 0) + 1
        if step['status'] == 'error':
            error_count += 1
    
    print(f"\n📋 Step Breakdown:")
    for step_name, count in step_counts.items():
        print(f"  {step_name}: {count}")
    
    if error_count > 0:
        print(f"\n❌ Errors: {error_count}")
    
    # Show final result if available
    final_step = None
    for step in reversed(log_data['steps']):
        if step['step'] == 'generate_story_success':
            final_step = step
            break
    
    if final_step:
        data = final_step['data']
        print(f"\n✅ Final Result:")
        print(f"  📚 Scenes Generated: {data.get('num_scenes', 'N/A')}")
        print(f"  📏 Total Length: {data.get('total_length', 'N/A')} characters")
        print(f"  📄 Story File: {data.get('story_file', 'N/A')}")

def show_step_details(session_id, step_name=None):
    """Show detailed step information"""
    session_dir = os.path.join("story_generation_logs", session_id)
    json_file = os.path.join(session_dir, "generation_log.json")
    
    with open(json_file, "r") as f:
        log_data = json.load(f)
    
    print(f"\n🔍 DETAILED LOG: {session_id}")
    print("=" * 60)
    
    for step in log_data['steps']:
        if step_name and step_name not in step['step']:
            continue
            
        print(f"\n[{step['timestamp']}] {step['step'].upper()} ({step['status']})")
        print("-" * 40)
        
        data = step['data']
        if isinstance(data, dict):
            # Pretty print specific data types
            if 'book_spec' in data:
                print("Book Specification:")
                print(data['book_spec'])
            elif 'plan' in data:
                print("Plan Structure:")
                print(json.dumps(data['plan'], indent=2))
            elif 'generated_scene' in data:
                print(f"Generated Scene (length: {data.get('scene_length', 'N/A')}):")
                print(data['generated_scene'][:500] + "..." if len(data['generated_scene']) > 500 else data['generated_scene'])
            elif 'error' in data:
                print(f"ERROR: {data['error']}")
            else:
                print(json.dumps(data, indent=2))
        else:
            print(str(data))

def main():
    if len(sys.argv) < 2:
        print("GOAT Storytelling Agent - Log Viewer")
        print("=" * 40)
        print("\nUsage:")
        print("  python log_viewer.py list                    # List all sessions")
        print("  python log_viewer.py summary <session_id>    # Show session summary")
        print("  python log_viewer.py details <session_id>   # Show detailed logs")
        print("  python log_viewer.py details <session_id> <step_name>  # Show specific step")
        print("\nExamples:")
        print("  python log_viewer.py list")
        print("  python log_viewer.py summary session_1")
        print("  python log_viewer.py details session_1")
        print("  python log_viewer.py details session_1 book_spec")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        sessions = list_sessions()
        if sessions:
            print("📁 Available Sessions:")
            for session in sessions:
                print(f"  {session}")
        else:
            print("No sessions found.")
    
    elif command == "summary":
        if len(sys.argv) < 3:
            print("Please provide a session ID")
            return
        session_id = sys.argv[2]
        show_session_summary(session_id)
    
    elif command == "details":
        if len(sys.argv) < 3:
            print("Please provide a session ID")
            return
        session_id = sys.argv[2]
        step_name = sys.argv[3] if len(sys.argv) > 3 else None
        show_step_details(session_id, step_name)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

