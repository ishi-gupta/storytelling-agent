#!/usr/bin/env python3
"""
Writing Quality Judge

Evaluates if each scene stands alone as a good piece of writing.
Assesses prose quality, sentence structure, clarity, show vs tell balance,
dialogue quality, and pacing/rhythm at the scene level.
"""

import os
import json
import re
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
SESSION_ID = "9"  # Numeric session ID (e.g., "1", "2", "3") or old format
SAMPLE_SCENES = 5  # Analyze first N scenes (set to 0 for all scenes)
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


WRITING_QUALITY_PROMPT = """Evaluate the writing quality of this scene as a standalone piece of prose. Rate each dimension on a 1-10 scale.

## 1. PROSE QUALITY (1-10)
- Sentence variety and rhythm
- Word choice and vocabulary
- Flow and readability
- Descriptive language effectiveness

## 2. CLARITY (1-10)
- Is it clear what's happening?
- Are descriptions vivid but not confusing?
- Can the reader easily follow the action?

## 3. SHOW VS TELL (1-10)
- Does it show emotions through actions/dialogue rather than stating them?
- Are there vivid sensory details?
- Does it avoid excessive exposition?

## 4. DIALOGUE QUALITY (1-10, or N/A if no dialogue)
- Does dialogue sound natural and distinct per character?
- Does it advance the story or reveal character?
- Is there appropriate balance of dialogue vs narrative?

## 5. PACING & RHYTHM (1-10)
- Does the scene move at an appropriate pace?
- Are there effective variations in sentence length for rhythm?
- Does it hold attention or drag?

## 6. TECHNICAL CRAFT (1-10)
- Grammatical correctness
- Paragraph structure
- Consistency of tense and POV

## 7. OVERALL ASSESSMENT
- **Scene quality score (average of above)**: 
- **Strengths**: What works well in this scene?
- **Weaknesses**: What could be improved?
- **Specific feedback**: 1-2 concrete suggestions for improvement

Be concise but specific in your feedback.

---

SCENE TO ANALYZE:

{scene}
"""


def split_scenes(story: str):
    """Split story into scenes based on scene markers"""
    # Look for scene markers like "SCENE 1", "Scene 1:", etc.
    scene_pattern = r'={10,}\s*SCENE\s+\d+\s*={10,}'
    scenes = re.split(scene_pattern, story)
    
    # Clean up empty scenes
    scenes = [s.strip() for s in scenes if s.strip()]
    
    return scenes


def load_story(session_id: str):
    """Load a session's story"""
    sess_dir = os.path.join(PROJECT_ROOT, "story_generation_logs", f"session_{session_id}")
    story_path = os.path.join(sess_dir, "final_story.txt")
    with open(story_path, "r", encoding="utf-8") as f:
        story = f.read()
    return sess_dir, story


def main():
    print(f"✍️  Running Writing Quality Judge on session_{SESSION_ID}...")
    sess_dir, story = load_story(SESSION_ID)
    
    # Split story into scenes
    scenes = split_scenes(story)
    print(f"📝 Found {len(scenes)} scenes")
    
    # Determine which scenes to analyze
    if SAMPLE_SCENES > 0 and len(scenes) > SAMPLE_SCENES:
        scenes_to_analyze = scenes[:SAMPLE_SCENES]
        print(f"📊 Analyzing first {SAMPLE_SCENES} scenes")
    else:
        scenes_to_analyze = scenes
        print(f"📊 Analyzing all {len(scenes)} scenes")
    
    # Analyze each scene
    scene_evaluations = []
    for i, scene in enumerate(scenes_to_analyze, 1):
        print(f"  Analyzing scene {i}/{len(scenes_to_analyze)}...")
        prompt = WRITING_QUALITY_PROMPT.format(scene=scene)
        evaluation = gpt5_respond(prompt)
        
        scene_evaluations.append({
            "scene_number": i,
            "scene_length": len(scene),
            "evaluation": evaluation
        })
    
    output = {
        "session_id": SESSION_ID,
        "model": MODEL,
        "total_scenes": len(scenes),
        "scenes_analyzed": len(scenes_to_analyze),
        "story_length": len(story),
        "scene_evaluations": scene_evaluations
    }
    
    # Save to evaluations/ folder
    eval_dir = os.path.join(sess_dir, "evaluations")
    os.makedirs(eval_dir, exist_ok=True)
    
    output_path = os.path.join(eval_dir, "writing_quality.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also save human-readable version
    readable_path = os.path.join(eval_dir, "writing_quality.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("WRITING QUALITY ANALYSIS\n")
        f.write(f"Session: {SESSION_ID}\n")
        f.write(f"Total scenes: {len(scenes)} | Analyzed: {len(scenes_to_analyze)}\n")
        f.write("=" * 80 + "\n\n")
        
        for scene_eval in scene_evaluations:
            f.write(f"\n{'='*80}\n")
            f.write(f"SCENE {scene_eval['scene_number']}\n")
            f.write(f"Length: {scene_eval['scene_length']} characters\n")
            f.write(f"{'='*80}\n\n")
            f.write(scene_eval['evaluation'])
            f.write("\n\n")
    
    print(f"✅ Saved writing quality analysis to: {output_path}")
    print(f"✅ Saved readable version to: {readable_path}")


if __name__ == "__main__":
    main()
