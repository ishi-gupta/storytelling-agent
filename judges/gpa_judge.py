#!/usr/bin/env python3
"""
Simple GPA evaluation script in the same style as example_openai.py
- Reads a given session's generation_log.json and final_story.txt
- Runs three GPT-5 evaluations: Goal, Plan, Action
- Saves results to story_generation_logs/session_<id>/gpa_evaluation.json
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get project root (one level up from judges/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# === Configure here ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable (you can use a .env file)")

MODEL = "gpt-5"
SESSION_ID = "1"  # Numeric session ID (e.g., "1", "2", "3") or old format (e.g., "20251028_121006")
# =======================


def gpt5_respond(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.responses.create(
        model=MODEL,
        input=prompt.strip(),
        reasoning={"effort": "low"},
        text={"verbosity": "low"},
    )
    return resp.output_text


def load_session(session_id: str):
    """Load a session by ID (supports both numeric and old timestamp formats)"""
    sess_dir = os.path.join(PROJECT_ROOT, "story_generation_logs", f"session_{session_id}")
    log_path = os.path.join(sess_dir, "generation_log.json")
    story_path = os.path.join(sess_dir, "final_story.txt")
    with open(log_path, "r", encoding="utf-8") as f:
        log = json.load(f)
    with open(story_path, "r", encoding="utf-8") as f:
        story = f.read()
    return sess_dir, log, story


def extract_artifacts(log: dict):
    steps = log.get("steps", [])
    book_spec = ""
    enhanced_spec = ""
    enhanced_plan_text = ""
    scene_plan_text = ""
    for s in steps:
        data = s.get("data", {})
        if s.get("step") == "init_book_spec_success":
            book_spec = data.get("book_spec", book_spec)
        if s.get("step") == "enhance_book_spec_success":
            enhanced_spec = data.get("enhanced_spec", enhanced_spec)
        if s.get("step") == "enhance_plot_chapters_success":
            enhanced_plan = data.get("enhanced_plan", [])
            if enhanced_plan:
                enhanced_plan_text = json.dumps(enhanced_plan, ensure_ascii=False, indent=2)
        if s.get("step") == "split_chapters_into_scenes_success":
            scene_plan = data.get("scene_plan", [])
            if scene_plan:
                scene_plan_text = json.dumps(scene_plan, ensure_ascii=False, indent=2)
    return book_spec, enhanced_spec, enhanced_plan_text, scene_plan_text


def build_goal_prompt(topic: str, book_spec: str, enhanced_spec: str) -> str:
    return f"""
You are a story development judge. Evaluate the GOAL (initial setup).
Return JSON: {{core_question, theme, protagonist_stakes:[], strengths, weaknesses, score}}

Topic:
{topic}

BookSpec:
{book_spec}

EnhancedSpec:
{enhanced_spec}
"""


def build_plan_prompt(enhanced_plan: str, scene_plan: str) -> str:
    return f"""
You are a plot structure judge. Evaluate the PLAN (story spine and characters).
Return JSON: {{beats_covered:{{inciting,drive,midpoint,reversal,climax,aftermath}}, antagonist_motives_complete, character_map, structural_strengths, structural_issues, score}}

EnhancedPlan:
{enhanced_plan}

ScenePlan:
{scene_plan}
"""


def build_action_prompt(scene_plan: str, story_text: str) -> str:
    return f"""
You are a trajectory judge. Evaluate the ACTION (written scenes) for decision pressure, stakes escalation, and plot friction.
Return JSON: {{scene_function_pass_rate, stakes_clarity, friction, uncashed_setups:[], procedure_issues:[], motif_payoffs:{{}}, suggestions:[], score}}

ScenePlan:
{scene_plan}

Story (excerpt OK if long):
{story_text[:24000]}
"""


def main():
    print("🧪 GPA Evaluation (Goal / Plan / Action)")
    sess_dir, log, story = load_session(SESSION_ID)

    topic = log.get("topic") or next((s.get("data", {}).get("topic") for s in log.get("steps", []) if s.get("step") == "generate_story_start"), "")
    book_spec, enhanced_spec, enhanced_plan_text, scene_plan_text = extract_artifacts(log)

    goal_prompt = build_goal_prompt(topic, book_spec, enhanced_spec)
    plan_prompt = build_plan_prompt(enhanced_plan_text, scene_plan_text)
    action_prompt = build_action_prompt(scene_plan_text, story)

    print("- Evaluating Goal...")
    goal_json = gpt5_respond(goal_prompt)
    print("- Evaluating Plan...")
    plan_json = gpt5_respond(plan_prompt)
    print("- Evaluating Action...")
    action_json = gpt5_respond(action_prompt)

    result = {
        "session_id": SESSION_ID,
        "goal": goal_json,
        "plan": plan_json,
        "action": action_json,
    }

    out_path = os.path.join(sess_dir, "gpa_evaluation.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved GPA evaluation to: {out_path}")


if __name__ == "__main__":
    main()

