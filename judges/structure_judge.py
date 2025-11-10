#!/usr/bin/env python3
"""
Story Structure Judge
Analyzes story coherence, completeness, and narrative structure
Creates a structured summary for human review
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
SESSION_ID = "20251028_121006"  # Numeric session ID (e.g., "1", "2", "3") or old format
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


STRUCTURE_ANALYSIS_PROMPT = """Analyze the provided story and create a structured summary. Your goal is to help someone who has NOT read the story understand what happens, who the characters are, and how the story works.

## 1. WHAT HAPPENS (Plot Summary)
Write 3-5 paragraphs summarizing the complete story from beginning to end. Include:
- Where and when the story takes place
- What happens in chronological order
- How the story begins, develops, and ends
- Any major twists, revelations, or turning points

## 2. WHO'S IN IT (Characters)
List each significant character with:
- **Name** - Role (protagonist/antagonist/supporting)
- Brief description of who they are and what they want
- How they relate to the main conflict
- What happens to them by the end

## 3. THE SPINE (Major Plot Beats)
List 8-12 key events in numbered order that form the story's skeleton. One sentence each.

## 4. THE CORE (Story Essence)
Answer these questions in 2-3 sentences total:
- What type of story is this? (mystery, romance, adventure, horror, drama, etc.)
- What is the main question or tension that drives the story?
- What makes this story interesting or distinct?

## 5. DOES IT WORK? (Coherence Check)
Answer briefly:
- Is the plot complete and resolved?
- Are character motivations clear?
- Are there confusing parts, plot holes, or loose ends?
- Does the ending address what the story set up?

---

STORY TO ANALYZE:

{story}
"""


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


def analyze_structure(story: str) -> str:
    """Run structural analysis on the story"""
    print("📐 Analyzing story structure...")
    prompt = STRUCTURE_ANALYSIS_PROMPT.format(story=story)
    result = gpt5_respond(prompt)
    return result


def main():
    print(f"📐 Story Structure Judge")
    print(f"Session ID: {SESSION_ID}")
    print(f"Model: {MODEL}\n")
    
    # Load session data
    sess_dir, log, story = load_session(SESSION_ID)
    print(f"✅ Loaded session from: {sess_dir}")
    print(f"📖 Story length: {len(story)} characters\n")
    
    # Run structure analysis
    structure_analysis = analyze_structure(story)
    
    # Save results
    output = {
        "session_id": SESSION_ID,
        "model": MODEL,
        "story_length": len(story),
        "structure_analysis": structure_analysis
    }
    
    output_path = os.path.join(sess_dir, "structure_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also save human-readable version
    readable_path = os.path.join(sess_dir, "structure_analysis.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("STORY STRUCTURE ANALYSIS\n")
        f.write(f"Session: {SESSION_ID}\n")
        f.write("=" * 80 + "\n\n")
        f.write(structure_analysis)
    
    print(f"\n✅ Structure analysis complete!")
    print(f"📄 Saved to: {output_path}")
    print(f"📄 Readable version: {readable_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print(structure_analysis)
    print("=" * 80)


if __name__ == "__main__":
    main()

