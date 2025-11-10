#!/usr/bin/env python3
"""
Story Structure Judge (Simple)
Creates concise narrative essence analysis
Focuses on core plot and key elements only
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


STRUCTURE_ANALYSIS_PROMPT = """Analyze this story and extract the essential narrative.

## THE CORE PLOT (2-3 sentences max)
Describe the story in its simplest form: Who does what, and what do they discover/achieve/lose? 
Strip away all detail - just the bare essence.

Example: "A detective investigates a murder and discovers the victim's brother did it for inheritance money."
Example: "A woman goes on a road trip to find herself and decides to leave her marriage."
Example: "An investigator examines hauntings at an estate and proves they're artificially created by con artists."

## MAIN CHARACTERS (3-5 people max)
- **Name**: One sentence about their role

## KEY EVENTS (5-8 beats)
The skeleton of what happens, in order.

## STORY TYPE
One sentence: What genre/type is this and what's the main question?

## ISSUES (if any)
Anything confusing or unresolved? (Skip if none)

Focus on ESSENCE, not detail. What would you tell someone in an elevator?

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
    """Run simple structural analysis on the story"""
    print("📐 Analyzing story essence...")
    prompt = STRUCTURE_ANALYSIS_PROMPT.format(story=story)
    result = gpt5_respond(prompt)
    return result


def main():
    print(f"📐 Simple Structure Judge")
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
        "structure_analysis_simple": structure_analysis
    }
    
    output_path = os.path.join(sess_dir, "structure_analysis_simple.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also save human-readable version
    readable_path = os.path.join(sess_dir, "structure_analysis_simple.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SIMPLE STRUCTURE ANALYSIS\n")
        f.write(f"Session: {SESSION_ID}\n")
        f.write("=" * 80 + "\n\n")
        f.write(structure_analysis)
    
    print(f"\n✅ Simple structure analysis complete!")
    print(f"📄 Saved to: {output_path}")
    print(f"📄 Readable version: {readable_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print(structure_analysis)
    print("=" * 80)


if __name__ == "__main__":
    main()


