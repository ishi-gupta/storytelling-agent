# Interactive Story Wizard (CLI)

A simple command-line tool for step-by-step story generation with manual editing and validation.

## Quick Start

```bash
python interactive_wizard.py
```

## How It Works

### 1. Initial Setup
- Enter your story topic (e.g., "a detective in a haunted mansion")
- Choose length: short/medium/long
- Creates a new session folder

### 2. Step-by-Step Generation

The wizard generates 5 planning steps, one at a time:

#### **Step 1: Initial Book Spec**
- Generates: `plans/1_initial_book_spec.txt`
- Contains: Genre, Place, Time, Theme, Tone, POV, Characters, Premise
- **You edit**: Open the file in your text editor, make changes, save
- **Validation**: Checks all 8 fields are present

#### **Step 2: Enhanced Book Spec**
- Generates: `plans/2_enhanced_book_spec.txt`
- Contains: More detailed version of Step 1
- **You edit**: Same process
- **Validation**: Same field checks

#### **Step 3: Initial Plot**
- Generates: `plans/3_initial_plot.json`
- Contains: 3-act structure with chapters
- **You edit**: Edit the JSON (careful with syntax!)
- **Validation**: Checks valid JSON and 3 acts

#### **Step 4: Enhanced Plot**
- Generates: `plans/4_enhanced_plot.json`
- Contains: Refined plot with story value alternation
- **You edit**: Edit the JSON
- **Validation**: JSON syntax check

#### **Step 5: Scene Plan**
- Generates: `plans/5_scene_plan.json`
- Contains: Detailed scene breakdown for each chapter
- **You edit**: Edit the JSON
- **Validation**: JSON syntax check

### 3. Final Story Generation
- Asks for confirmation
- Generates all scene text (may take 5-15 minutes)
- Saves to: `final_story.txt`

## User Flow

```
Generate Step 1
     ↓
Preview in terminal
     ↓
Press ENTER
     ↓
[You open plans/1_initial_book_spec.txt in your editor]
[You make edits]
[You save and close]
     ↓
Press ENTER again
     ↓
Validation check
     ↓
  ✓ Valid? → Continue to Step 2
  ✗ Error? → Fix and retry
```

## Options At Each Step

When you see the prompt:
- **Press ENTER** - Continue (assumes you'll edit the file if needed)
- **Type 'skip'** - Use generated content as-is without editing
- **Type 'quit'** - Exit the wizard (progress is saved)

## Validation Errors

### Book Spec Errors
```
✗ Missing required fields: Characters, Premise
ℹ Each field should be on its own line in format: 'Field: value'
```

**Fix**: Make sure your text file has all 8 fields with colons:
```
Genre: Mystery
Place: Haunted Mansion
Time: Present Day
Theme: Courage and redemption
Tone: Dark and suspenseful
Point of View: Third person limited
Characters: Detective John Smith, Ghost of Mary, Caretaker Bob
Premise: A detective must solve a 100-year-old murder...
```

### JSON Errors
```
✗ Invalid JSON syntax: Expecting ',' delimiter: line 12 column 5
```

**Fix**: Common JSON mistakes:
- Missing commas between items
- Extra comma at end of list
- Unmatched brackets `{` `}` or `[` `]`
- Unquoted strings
- Use a JSON validator or editor with syntax highlighting

```
✗ Plot should have exactly 3 acts, found 2
```

**Fix**: Make sure your plot JSON has 3 act objects in the array

## Example Session

```bash
$ python interactive_wizard.py

============================================================
🎭 GOAT Story Generation Wizard (CLI)
============================================================

Let's create a story!

Story topic: a robot learning to love

Story length:
  1. Short (~5 min, 1000 words)
  2. Medium (~10 min, 2000 words)
  3. Long (~15 min, 3000 words)
Choose (1/2/3): 2

ℹ Selected: medium

============================================================
Step 0: Initializing Agent
============================================================

✓ Created session: 18
ℹ Session folder: story_generation_logs/session_18

============================================================
Step 1: Generating Initial Book Specification
============================================================

ℹ This defines the genre, characters, setting, and premise...
✓ Generated initial book spec

Preview:
------------------------------------------------------------
Genre: Science Fiction Romance
Place: Neo-Tokyo, 2087
Time: Near future
Theme: What it means to be human, love transcending biology
...
------------------------------------------------------------

ℹ Please review and edit: story_generation_logs/session_18/plans/1_initial_book_spec.txt

Options:
  1. Press ENTER when you're done editing
  2. Type 'skip' to use as-is without opening
  3. Type 'quit' to exit

> [Press ENTER]

[You open the file, edit Characters to add more detail, save]

> [Press ENTER again]

✓ Book spec approved!

[... continues through all steps ...]
```

## Benefits of CLI Version

1. **Simple**: No web server, no JavaScript, just Python
2. **Manual Control**: Edit files with your favorite editor
3. **Clear Validation**: Immediate feedback on syntax errors
4. **Incremental**: Generate and review one step at a time
5. **Saved Progress**: All files saved to disk, can resume later
6. **Transparent**: See exactly what files are created and where

## Files Created

```
story_generation_logs/session_18/
├── plans/
│   ├── 1_initial_book_spec.txt      ← Edit these
│   ├── 2_enhanced_book_spec.txt     ← as you go
│   ├── 3_initial_plot.json          ← through the
│   ├── 4_enhanced_plot.json         ← wizard
│   └── 5_scene_plan.json            ← steps
├── seed.json                        ← Metadata
└── final_story.txt                  ← Final output
```

## Tips

1. **Keep a text editor open** - You'll be editing 5 files
2. **Use a JSON validator** - For the 3 JSON files (steps 3-5)
3. **Make small edits** - Don't completely rewrite, AI regenerates from your changes
4. **Save often** - Files are validated only when you press ENTER
5. **Review previews** - Terminal shows you a preview before you edit

## Next Steps

Once you're comfortable with the CLI:
- The backend API (`backend/app.py`) mirrors this flow
- The frontend (`frontend/`) is just a fancy UI for the same process
- You can test generation logic here, then wire up the UI later

## Troubleshooting

**Wizard crashes mid-generation?**
- Your progress is saved in `story_generation_logs/session_N/`
- Check `plans/` folder to see which steps completed
- You can manually run the agent from that point (see `generate_story.py`)

**Want to skip wizard and generate full story?**
- Use: `python generate_story.py --length medium --topic "your topic"`
- This runs all steps automatically without editing

**Want to resume a session?**
- Currently not supported in wizard
- But you can manually edit files in existing session folder
- Then run evaluation judges on it

