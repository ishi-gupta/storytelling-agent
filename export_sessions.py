#!/usr/bin/env python3
"""
Export all story sessions and judge evaluations to a single JSON file
for the frontend viewer
"""

import os
import json
from pathlib import Path

def export_sessions():
    """Export all sessions to frontend/public/data.json"""
    
    project_root = Path(__file__).parent
    logs_dir = project_root / "story_generation_logs"
    output_file = project_root / "frontend" / "public" / "data.json"
    
    sessions = []
    
    # Scan all session directories
    if logs_dir.exists():
        for session_dir in sorted(logs_dir.iterdir()):
            if not session_dir.is_dir() or not session_dir.name.startswith("session_"):
                continue
            
            session_id = session_dir.name.replace("session_", "")
            session_data = {
                "id": session_id,
                "title": "Untitled Story",
                "story": "",
                "seed": {},
                "plans": {},
                "judges": {}
            }
            
            # Load seed.json if exists (new format)
            seed_path = session_dir / "seed.json"
            if seed_path.exists():
                try:
                    with open(seed_path, 'r', encoding='utf-8') as f:
                        session_data["seed"] = json.load(f)
                        session_data["title"] = session_data["seed"].get("topic", "Untitled Story")
                except Exception as e:
                    print(f"Warning: Could not read seed for {session_id}: {e}")
            
            # Load story text
            story_path = session_dir / "final_story.txt"
            if story_path.exists():
                try:
                    with open(story_path, 'r', encoding='utf-8') as f:
                        session_data["story"] = f.read()
                except Exception as e:
                    print(f"Warning: Could not read story for {session_id}: {e}")
            
            # Load plans from plans/ folder (new format)
            plans_dir = session_dir / "plans"
            if plans_dir.exists():
                plan_files = {
                    "initial_book_spec": "1_initial_book_spec.txt",
                    "enhanced_book_spec": "2_enhanced_book_spec.txt",
                    "initial_plot": "3_initial_plot.json",
                    "enhanced_plot": "4_enhanced_plot.json",
                    "scene_plan": "5_scene_plan.json"
                }
                
                for key, filename in plan_files.items():
                    plan_path = plans_dir / filename
                    if plan_path.exists():
                        try:
                            with open(plan_path, 'r', encoding='utf-8') as f:
                                if filename.endswith('.json'):
                                    session_data["plans"][key] = json.load(f)
                                else:
                                    session_data["plans"][key] = f.read()
                        except Exception as e:
                            print(f"Warning: Could not read {filename} for {session_id}: {e}")
            
            # Fallback: extract plans from generation_log.json if plans/ doesn't exist
            if not session_data["plans"]:
                gen_log_path = session_dir / "generation_log.json"
                if gen_log_path.exists():
                    try:
                        with open(gen_log_path, 'r', encoding='utf-8') as f:
                            gen_log = json.load(f)
                            
                            # Get title from topic
                            topic = gen_log.get("topic", "")
                            if not topic:
                                for step in gen_log.get("steps", []):
                                    if step.get("step") == "generate_story_start":
                                        topic = step.get("data", {}).get("topic", "")
                                        break
                            if topic and not session_data["seed"]:
                                session_data["title"] = topic
                            
                            # Extract plan data from steps (old format)
                            for step in gen_log.get("steps", []):
                                step_name = step.get("step", "")
                                data = step.get("data", {})
                                
                                if step_name == "enhance_book_spec_success":
                                    session_data["plans"]["enhanced_book_spec"] = data.get("enhanced_spec", "")
                                elif step_name == "enhance_plot_chapters_success":
                                    session_data["plans"]["enhanced_plot"] = data.get("enhanced_plan", [])
                                elif step_name == "split_chapters_into_scenes_success":
                                    session_data["plans"]["scene_plan"] = data.get("scene_plan", [])
                    except Exception as e:
                        print(f"Warning: Could not read generation log for {session_id}: {e}")
            
            # Load judge evaluations from evaluations/ folder (new format)
            evaluations_dir = session_dir / "evaluations"
            if evaluations_dir.exists():
                for eval_file in evaluations_dir.glob("*.json"):
                    judge_name = eval_file.stem
                    try:
                        with open(eval_file, 'r', encoding='utf-8') as f:
                            session_data["judges"][judge_name] = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not read {judge_name} for {session_id}: {e}")
            
            # Fallback: load judges from root (old format)
            if not session_data["judges"]:
                judge_files = {
                    "gpa": "gpa_evaluation.json",
                    "structure": "structure_analysis.json",
                    "structure_simple": "structure_analysis_simple.json",
                    "character": "character_analysis.json"
                }
                
                for judge_name, filename in judge_files.items():
                    judge_path = session_dir / filename
                    if judge_path.exists():
                        try:
                            with open(judge_path, 'r', encoding='utf-8') as f:
                                session_data["judges"][judge_name] = json.load(f)
                        except Exception as e:
                            print(f"Warning: Could not read {judge_name} for {session_id}: {e}")
            
            sessions.append(session_data)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON
    output = {
        "sessions": sessions,
        "total": len(sessions)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(sessions)} sessions to {output_file}")
    for session in sessions:
        judges_count = len(session["judges"])
        plans_count = len(session["plans"])
        has_seed = "✓" if session["seed"] else "✗"
        print(f"  - {session['id']}: {session['title'][:50]}... (seed:{has_seed} plans:{plans_count} judges:{judges_count})")

if __name__ == "__main__":
    export_sessions()
