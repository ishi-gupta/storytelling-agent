#!/usr/bin/env python3
"""
Plot Sophistication Judge

Evaluates plot structure, context management, and cliché usage.

1. Plot Sophistication:
   - Is the plot structure interesting and well-constructed?
   - Are there unexpected but logical developments?
   - Is the mystery/structure flat or predictable?

2. Context Management:
   - Are interesting details from earlier used in interesting ways later?
   - Are setups paid off effectively (Chekov's guns)?
   - Is there thematic coherence throughout?

3. Clichés & Templates:
   - How does the writing use clichés? Does it use them in an interesting way?
   - Could benefit from story templates and instructions to neatly deviate from them
   - Are there fresh takes on familiar tropes?
   - Is the structure too formulaic or does it have unique elements?
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
SESSION_ID = "9"  # Numeric session ID (e.g., "1", "2", "3") or old format
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


PLOT_ANALYSIS_PROMPT = """Analyze the plot structure and sophistication of this story.

## 1. PLOT STRUCTURE (Score 1-10 for each)
- **Originality**: Is the plot fresh and interesting, or predictable and formulaic?
- **Logical coherence**: Do events flow naturally from causes? Are there plot holes?
- **Complexity**: Is the plot appropriately layered, or too simple/convoluted?
- **Pacing**: Does the story move at the right speed? Are there draggy or rushed sections?
- **Satisfying resolution**: Does the ending pay off the setup? Are loose ends addressed?

## 2. CONTEXT MANAGEMENT & CALLBACKS
- **Setups and payoffs**: List any Chekov's guns (details introduced early that matter later)
  - What was set up and how was it paid off?
  - Were there missed opportunities for callbacks?
- **Thematic coherence**: Do themes introduced early carry through consistently?
- **Detail tracking**: Are interesting early details leveraged effectively later?
- **Score (1-10)**: How well does the story manage and reward its own context?

## 3. CLICHÉS & FRESHNESS
- **Clichés identified**: List any obvious clichés or tired tropes used
- **Execution**: When clichés are used, are they subverted or freshly executed?
- **Template adherence**: Does the story follow a predictable template (e.g., hero's journey, romance beats)?
- **Unique elements**: What makes this plot stand out from similar stories?
- **Overall freshness score (1-10)**: How original is the plot?

## 4. SURPRISING BUT LOGICAL DEVELOPMENTS
- Are there plot twists or turns that surprise the reader?
- When surprises occur, are they properly foreshadowed?
- Do developments feel earned or arbitrary?

## 5. OVERALL PLOT ASSESSMENT
- **Sophistication score (1-10)**: How sophisticated is the plot construction?
- **Strengths**: What works well in the plot?
- **Weaknesses**: What could be improved?
- **Recommendations**: Specific suggestions for plot enhancement

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
    print(f"📖 Running Plot Judge on session_{SESSION_ID}...")
    sess_dir, story = load_story(SESSION_ID)
    
    prompt = PLOT_ANALYSIS_PROMPT.format(story=story)
    print("📝 Analyzing plot structure...")
    plot_analysis = gpt5_respond(prompt)
    
    output = {
        "session_id": SESSION_ID,
        "model": MODEL,
        "story_length": len(story),
        "plot_analysis": plot_analysis
    }
    
    # Save to evaluations/ folder
    eval_dir = os.path.join(sess_dir, "evaluations")
    os.makedirs(eval_dir, exist_ok=True)
    
    output_path = os.path.join(eval_dir, "plot_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also save human-readable version
    readable_path = os.path.join(eval_dir, "plot_analysis.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PLOT SOPHISTICATION ANALYSIS\n")
        f.write(f"Session: {SESSION_ID}\n")
        f.write("=" * 80 + "\n\n")
        f.write(plot_analysis)
    
    print(f"✅ Saved plot analysis to: {output_path}")
    print(f"✅ Saved readable version to: {readable_path}")


if __name__ == "__main__":
    main()
