# Story Wizard - Step-by-Step Story Creation

## What's New?

You can now create stories interactively! Instead of waiting 10 minutes for a full story, you go through each planning step, edit as you want, and decide when to continue.

## How to Use:

### 1. Start a New Story
1. Click **"+ New Story"** button in the sidebar
2. Enter your topic (e.g., "A detective solving a mystery")
3. Choose length (short/medium/long)
4. Click **"Generate Story"**

### 2. The Wizard Opens Automatically
- The modal closes
- Dashboard switches to **"Plans"** view
- You see the **Story Wizard** with Step 1

### 3. Edit → Save → Next
**For each step:**
1. **Read** the generated content in the textarea
2. **Edit** anything you want to change
3. Click **"💾 Save Changes"** to save your edits
4. Click **"→ Next: [Step Name]"** to generate the next step

**The 5 steps are:**
1. **Initial Book Spec** - Genre, setting, characters, premise
2. **Enhanced Book Spec** - More detailed version
3. **Initial Plot** - 3-act structure with chapters
4. **Enhanced Plot** - Refined plot structure
5. **Scene Plan** - Breakdown of each chapter into scenes

### 4. Generate Full Story
- After Step 5 (Scene Plan), click **"🚀 Generate Full Story"**
- This will start the full scene-by-scene generation
- Story will appear in the **"Story"** view when complete

## Key Features:

✅ **Edit at Every Step** - Change anything before moving forward
✅ **Save Your Edits** - Backend updates files immediately  
✅ **No More Waiting Blind** - See what's being generated  
✅ **Progress Bar** - Visual progress through 5 steps  
✅ **Consent-Based** - YOU decide when to continue  

## Backend Endpoints:

- `POST /api/session/<id>/save-plan` - Save user edits
- `POST /api/session/<id>/generate-next` - Generate next step

## Notes:

- Sessions with `status: 'generating'` show the wizard
- Completed sessions show read-only plans
- You must save changes before clicking "Next"
- The wizard uses the existing story agent (no rewrite needed!)

## Troubleshooting:

**"Next button disabled?"**
- Make sure you saved your changes first

**"Nothing happens when I click Next?"**
- Check the browser console (F12) for errors
- Make sure Flask backend is running on port 5001

**"Story takes forever at Step 5?"**
- Step 5 generates the full story (all scenes)
- This can take 5-10 minutes depending on length
- Check `story_generation_logs/session_X/generation_log.txt` for progress


