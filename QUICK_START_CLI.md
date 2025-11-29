# Quick Start: CLI Wizard

## Why Start with CLI?

You're absolutely right - testing two things at once (backend + frontend) is hard. This CLI wizard lets you:

1. ✅ **Test core generation logic** without worrying about web servers
2. ✅ **Edit files manually** with your preferred text editor  
3. ✅ **See validation errors** immediately and fix them
4. ✅ **Understand the flow** before building the web UI

## Run It Now

```bash
# Make sure you're in the project directory
cd "/Users/ishita/Desktop/GOAT-AGENT /GOAT-Storytelling-Agent"

# Activate virtual environment
source venv/bin/activate

# Run the wizard
python interactive_wizard.py
```

## What Happens

### 1. Wizard Starts
```
============================================================
🎭 GOAT Story Generation Wizard (CLI)
============================================================

Let's create a story!

Story topic: [you type here]
```

### 2. Generate Step 1
```
============================================================
Step 1: Generating Initial Book Specification
============================================================

ℹ This defines the genre, characters, setting, and premise...
✓ Generated initial book spec

Preview:
------------------------------------------------------------
Genre: Mystery
Place: Haunted Mansion
Time: Present Day
...
------------------------------------------------------------

ℹ Please review and edit: story_generation_logs/session_18/plans/1_initial_book_spec.txt

Options:
  1. Press ENTER when you're done editing
  2. Type 'skip' to use as-is without opening
  3. Type 'quit' to exit

> 
```

### 3. You Edit the File

**In a separate terminal or editor:**
```bash
# Open the file
open story_generation_logs/session_18/plans/1_initial_book_spec.txt

# Edit it (add more character details, change setting, etc.)
# Save and close
```

**Back in wizard:**
```
> [Press ENTER]

✓ Book spec approved!
```

### 4. Repeat for Steps 2-5

Each step:
- Generates the next artifact
- Waits for you to review/edit
- Validates syntax
- Moves to next step

### 5. Final Story Generation

After Step 5:
```
============================================================
Step 6: Generating Full Story Text
============================================================

ℹ This will generate all 18 scenes. This may take a while...

Proceed with full story generation? (yes/no): yes

Generating scenes...

📖 Act 1
  Chapter 1:
    Scene 1... ✓ (1247 chars)
    Scene 2... ✓ (1156 chars)
  Chapter 2:
    Scene 1... ✓ (1389 chars)
...

✨ Story Generation Complete!
✓ Generated 18 scenes
✓ Total words: 2143
✓ Story saved to: story_generation_logs/session_18/final_story.txt
```

## Validation Examples

### Missing Field
```
✗ Missing required fields: Premise
ℹ Each field should be on its own line in format: 'Field: value'

> [Fix and press ENTER again]
```

### Bad JSON
```
✗ Invalid JSON syntax: Expecting ',' delimiter: line 12 column 5
ℹ Make sure your JSON is properly formatted with matching brackets and commas

> [Fix and press ENTER again]
```

## Files You'll Edit

```
story_generation_logs/session_18/plans/

1_initial_book_spec.txt      📝 Plain text (easy)
2_enhanced_book_spec.txt     📝 Plain text (easy)
3_initial_plot.json          ⚠️  JSON (careful with syntax)
4_enhanced_plot.json         ⚠️  JSON (careful with syntax)
5_scene_plan.json            ⚠️  JSON (careful with syntax)
```

## Tips for JSON Editing

1. **Use a proper editor**: VSCode, Sublime, or any editor with JSON syntax highlighting
2. **Common mistakes**:
   - Missing comma: `{"name": "John" "age": 30}` ❌
   - Extra comma: `{"name": "John", "age": 30,}` ❌
   - Unquoted keys: `{name: "John"}` ❌
3. **Validate online**: https://jsonlint.com/

## Workflow Diagram

```
You               File System              Wizard
─────────────────────────────────────────────────────

                                         [Generate Step 1]
                                               ↓
                  1_initial_book_spec.txt  
                       is created
                                               ↓
                                         [Show preview]
                                         [Wait for ENTER]
                                               
[Open file]
[Edit content]
[Save file]
[Close editor]
                                               
[Press ENTER] ──────────────────────────────→
                                               ↓
                                         [Validate file]
                                               ↓
                                         ✓ Valid!
                                               ↓
                                         [Generate Step 2]
                                               ↓
                                         ...repeat...
```

## What You're Testing

This CLI wizard helps you test:

1. ✅ **Generation quality**: Are the outputs good?
2. ✅ **Editability**: Can you improve them manually?
3. ✅ **Validation**: Do errors get caught properly?
4. ✅ **Flow**: Does step-by-step progression make sense?
5. ✅ **API integration**: Each step = one API call to GPT-5

## Next Steps

Once this works well:

1. **Backend already mirrors this** - `backend/app.py` has the same step-by-step logic
2. **Frontend just adds UI** - React wizard is same flow with buttons instead of CLI
3. **You can test separately**:
   - Test backend API with `curl` or Postman
   - Test frontend with mock data
   - Connect them when both work independently

## Comparison

### CLI Wizard (This)
- ✅ Simple to run
- ✅ Manual file editing
- ✅ Clear validation
- ✅ No web servers needed
- ❌ No fancy UI
- ❌ One user at a time

### Web Dashboard (frontend + backend)
- ✅ Beautiful UI
- ✅ In-browser editing
- ✅ Multiple sessions
- ✅ Live updates
- ❌ Two servers to run
- ❌ More complex debugging

## Troubleshooting

### "OPENAI_API_KEY not found"
```bash
# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

### "command not found: python"
```bash
# Activate virtual environment first
source venv/bin/activate
```

### "No module named 'openai'"
```bash
# Install dependencies
pip install -r requirements.txt
```

### Want to skip wizard and generate full story automatically?
```bash
python generate_story.py --length medium --topic "your topic"
```

This runs all 6 steps automatically without stopping for edits.

## Ready to Try?

```bash
source venv/bin/activate
python interactive_wizard.py
```

Have fun! 🎭

