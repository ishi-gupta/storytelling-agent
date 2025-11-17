#!/usr/bin/env python3
"""
Character & Motivation Judge

Evaluates character depth, consistency, and psychological realism.
Every good story is driven by good characters.

1. Character Consistency:
   - Are character motivations clear throughout the story?
   - Do characters act consistently with their incentives?

2. Human Psychology:
   - Do characters act reasonably given human psychology?
   - Are their reactions and decisions believable?

3. Character Design:
   - Are characters interesting and nuanced?
   - Do they have depth (like tragic heroes, complex motivations)?
   - Are they more than just plot functions?

4. Motivation & Drive:
   - Do characters have clear wants, fears, and stakes?
   - Are their motivations driving the story forward?
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
SESSION_ID = "4"  # Numeric session ID (e.g., "1", "2", "3") or old format
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


CHARACTER_ANALYSIS_PROMPT = """Analyze the characters in this story. Evaluate character depth, consistency, and psychological realism.

## 1. MAIN CHARACTERS
List each major character with:
- Name and role in the story
- Core motivation (what they want/need)
- Internal conflict (what holds them back)
- Character arc (how they change from beginning to end)
- Consistency score (1-10): Are their actions consistent with their established personality and motivations?

## 2. CHARACTER PSYCHOLOGY
For each main character, assess:
- Psychological realism (1-10): Do they act like real people would?
- Believability of reactions and decisions
- Depth beyond plot function
- Emotional authenticity

## 3. RELATIONSHIPS & DYNAMICS
- How do character relationships evolve?
- Are interactions believable and engaging?
- Do characters challenge/change each other?

## 4. CHARACTER DESIGN QUALITY
Overall assessment:
- Are characters interesting and nuanced? (Yes/No + explanation)
- Do they have clear wants, fears, and stakes? (Yes/No + explanation)
- Are they more than plot devices? (Yes/No + explanation)
- Do their motivations drive the story forward? (Yes/No + explanation)

## 5. STRENGTHS & WEAKNESSES
- What works well with the character design?
- What could be improved?
- Any flat or inconsistent characterization?

---

STORY TO ANALYZE:

{story}
"""


def load_story(session_id: str):
    """Load a session's story"""
    sess_dir = os.path.join(PROJECT_ROOT, "story_generation_logs", f"session_{session_id}")
    story_path = os.path.join(sess_dir, "final_story.txt")
    with open(story_path, "r", encoding="utf-8") as f:
        story = f.read()
    return sess_dir, story


def main():
    print(f"🎭 Running Character Judge on session_{SESSION_ID}...")
    sess_dir, story = load_story(SESSION_ID)
    
    prompt = CHARACTER_ANALYSIS_PROMPT.format(story=story)
    print("📝 Analyzing characters...")
    character_analysis = gpt5_respond(prompt)
    
    output = {
        "session_id": SESSION_ID,
        "model": MODEL,
        "story_length": len(story),
        "character_analysis": character_analysis
    }
    
    # Save to evaluations/ folder
    eval_dir = os.path.join(sess_dir, "evaluations")
    os.makedirs(eval_dir, exist_ok=True)
    
    output_path = os.path.join(eval_dir, "character_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also save human-readable version
    readable_path = os.path.join(eval_dir, "character_analysis.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("CHARACTER & MOTIVATION ANALYSIS\n")
        f.write(f"Session: {SESSION_ID}\n")
        f.write("=" * 80 + "\n\n")
        f.write(character_analysis)
    
    print(f"✅ Saved character analysis to: {output_path}")
    print(f"✅ Saved readable version to: {readable_path}")


if __name__ == "__main__":
    main()
