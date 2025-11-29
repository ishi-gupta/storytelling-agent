#!/usr/bin/env python3
"""
Interactive Story Wizard - CLI Version
Generates story one step at a time with user approval
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from generate_story import LoggingStoryAgent
from story_presets import get_preset

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def validate_book_spec(file_path):
    """Validate that book spec has all required fields"""
    required_fields = ['Genre', 'Place', 'Time', 'Theme', 'Tone', 'Point of View', 'Characters', 'Premise']
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_fields = []
    for field in required_fields:
        # Check if field exists with colon
        if f"{field}:" not in content:
            missing_fields.append(field)
    
    if missing_fields:
        print_error(f"Missing required fields: {', '.join(missing_fields)}")
        print_info("Each field should be on its own line in format: 'Field: value'")
        return False
    
    return True


def validate_json_plan(file_path):
    """Validate that a JSON plan file is valid JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic structure check for plot files
        if isinstance(data, list):
            if len(data) != 3:
                print_error(f"Plot should have exactly 3 acts, found {len(data)}")
                return False
        
        return True
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON syntax: {e}")
        print_info("Make sure your JSON is properly formatted with matching brackets and commas")
        return False


def wait_for_user_edit(file_path, step_name):
    """Wait for user to edit and approve a file"""
    print_info(f"Please review and edit: {file_path}")
    print(f"\n{Colors.BOLD}Options:{Colors.ENDC}")
    print(f"  1. Press ENTER when you're done editing")
    print(f"  2. Type 'skip' to use as-is without opening")
    print(f"  3. Type 'quit' to exit")
    
    choice = input(f"\n{Colors.BOLD}> {Colors.ENDC}").strip().lower()
    
    if choice == 'quit':
        print_info("Exiting wizard...")
        sys.exit(0)
    elif choice == 'skip':
        print_info("Using generated content as-is")
        return True
    
    # Wait for user to confirm they're done editing
    return True


def interactive_wizard():
    """Run the interactive story generation wizard"""
    
    print_header("🎭 GOAT Story Generation Wizard (CLI)")
    
    # Get user input
    print(f"{Colors.BOLD}Let's create a story!{Colors.ENDC}\n")
    
    topic = input(f"{Colors.BOLD}Story topic:{Colors.ENDC} ").strip()
    if not topic:
        topic = "a detective solving a mystery in a haunted mansion"
        print_info(f"Using default topic: {topic}")
    
    print(f"\n{Colors.BOLD}Story length:{Colors.ENDC}")
    print("  1. Short (~5 min, 1000 words)")
    print("  2. Medium (~10 min, 2000 words)")
    print("  3. Long (~15 min, 3000 words)")
    
    length_choice = input(f"{Colors.BOLD}Choose (1/2/3):{Colors.ENDC} ").strip()
    length_map = {'1': 'short', '2': 'medium', '3': 'long'}
    length = length_map.get(length_choice, 'medium')
    
    print_info(f"Selected: {length}")
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print_error("OPENAI_API_KEY not found in environment")
        print_info("Please set OPENAI_API_KEY in your .env file")
        sys.exit(1)
    
    # Get preset
    preset = get_preset(length)
    
    # Create agent
    print_header("Step 0: Initializing Agent")
    agent = LoggingStoryAgent(
        topic=topic,
        length_preset=length,
        backend_uri=api_key,
        backend="openai",
        model="gpt-5",
        max_tokens=2000,
        story_preset=preset,
        extra_options={"temperature": 1.0, "top_p": 1.0}
    )
    
    print_success(f"Created session: {agent.session_id}")
    print_info(f"Session folder: {agent.session_dir}")
    
    # Step 1: Initial Book Spec
    print_header("Step 1: Generating Initial Book Specification")
    print_info("This defines the genre, characters, setting, and premise...")
    
    _, book_spec = agent.init_book_spec(topic)
    spec_file = os.path.join(agent.plans_dir, "1_initial_book_spec.txt")
    agent.save_plan_artifact("1_initial_book_spec.txt", book_spec, as_json=False)
    
    print_success("Generated initial book spec")
    print(f"\n{Colors.BOLD}Preview:{Colors.ENDC}")
    print("-" * 60)
    print(book_spec[:300] + "..." if len(book_spec) > 300 else book_spec)
    print("-" * 60)
    
    # Wait for user approval
    if not wait_for_user_edit(spec_file, "Initial Book Spec"):
        return
    
    # Validate after edit
    while not validate_book_spec(spec_file):
        print_error("Please fix the errors and try again")
        wait_for_user_edit(spec_file, "Initial Book Spec")
    
    # Reload potentially edited content
    with open(spec_file, 'r', encoding='utf-8') as f:
        book_spec = f.read()
    
    print_success("Book spec approved!")
    
    # Step 2: Enhanced Book Spec
    print_header("Step 2: Enhancing Book Specification")
    print_info("Making the specification more detailed...")
    
    _, book_spec = agent.enhance_book_spec(book_spec)
    enhanced_spec_file = os.path.join(agent.plans_dir, "2_enhanced_book_spec.txt")
    agent.save_plan_artifact("2_enhanced_book_spec.txt", book_spec, as_json=False)
    
    print_success("Generated enhanced book spec")
    
    if not wait_for_user_edit(enhanced_spec_file, "Enhanced Book Spec"):
        return
    
    while not validate_book_spec(enhanced_spec_file):
        print_error("Please fix the errors and try again")
        wait_for_user_edit(enhanced_spec_file, "Enhanced Book Spec")
    
    with open(enhanced_spec_file, 'r', encoding='utf-8') as f:
        book_spec = f.read()
    
    print_success("Enhanced spec approved!")
    
    # Step 3: Initial Plot
    print_header("Step 3: Creating Plot Chapters")
    print_info("Breaking story into acts and chapters...")
    
    _, plan = agent.create_plot_chapters(book_spec)
    plot_file = os.path.join(agent.plans_dir, "3_initial_plot.json")
    agent.save_plan_artifact("3_initial_plot.json", plan, as_json=True)
    
    print_success("Generated initial plot")
    print_info(f"Created {len(plan)} acts")
    
    if not wait_for_user_edit(plot_file, "Initial Plot"):
        return
    
    while not validate_json_plan(plot_file):
        print_error("Please fix the JSON syntax and try again")
        wait_for_user_edit(plot_file, "Initial Plot")
    
    with open(plot_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print_success("Plot approved!")
    
    # Step 4: Enhanced Plot
    print_header("Step 4: Enhancing Plot Chapters")
    print_info("Refining chapter structure and story values...")
    
    _, plan = agent.enhance_plot_chapters(book_spec, plan)
    enhanced_plot_file = os.path.join(agent.plans_dir, "4_enhanced_plot.json")
    agent.save_plan_artifact("4_enhanced_plot.json", plan, as_json=True)
    
    print_success("Generated enhanced plot")
    
    if not wait_for_user_edit(enhanced_plot_file, "Enhanced Plot"):
        return
    
    while not validate_json_plan(enhanced_plot_file):
        print_error("Please fix the JSON syntax and try again")
        wait_for_user_edit(enhanced_plot_file, "Enhanced Plot")
    
    with open(enhanced_plot_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print_success("Enhanced plot approved!")
    
    # Step 5: Scene Plan
    print_header("Step 5: Creating Scene Plan")
    print_info("Breaking chapters into detailed scenes...")
    
    _, plan = agent.split_chapters_into_scenes(plan)
    scene_plan_file = os.path.join(agent.plans_dir, "5_scene_plan.json")
    agent.save_plan_artifact("5_scene_plan.json", plan, as_json=True)
    
    print_success("Generated scene plan")
    
    # Count scenes
    total_scenes = 0
    for act in plan:
        if 'chapter_scenes' in act:
            for ch_num, scenes in act['chapter_scenes'].items():
                total_scenes += len(scenes)
    
    print_info(f"Created {total_scenes} scenes total")
    
    if not wait_for_user_edit(scene_plan_file, "Scene Plan"):
        return
    
    while not validate_json_plan(scene_plan_file):
        print_error("Please fix the JSON syntax and try again")
        wait_for_user_edit(scene_plan_file, "Scene Plan")
    
    with open(scene_plan_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print_success("Scene plan approved!")
    
    # Step 6: Generate Full Story
    print_header("Step 6: Generating Full Story Text")
    print_info(f"This will generate all {total_scenes} scenes. This may take a while...")
    
    proceed = input(f"\n{Colors.BOLD}Proceed with full story generation? (yes/no):{Colors.ENDC} ").strip().lower()
    
    if proceed != 'yes':
        print_info("Story generation cancelled. All plans are saved and ready for later.")
        print_info(f"Session folder: {agent.session_dir}")
        return
    
    print("\n" + Colors.BOLD + "Generating scenes..." + Colors.ENDC)
    
    form_text = []
    scene_count = 0
    
    for act_idx, act in enumerate(plan):
        print(f"\n{Colors.BOLD}📖 Act {act_idx + 1}{Colors.ENDC}")
        
        if 'chapter_scenes' not in act:
            print_error(f"Act {act_idx + 1} missing 'chapter_scenes'")
            continue
        
        chapter_scenes = act['chapter_scenes']
        
        for ch_num, chapter in chapter_scenes.items():
            print(f"  Chapter {ch_num}:")
            sc_num = 1
            
            for scene_idx, scene in enumerate(chapter):
                previous_scene = form_text[-1] if form_text else None
                
                try:
                    print(f"    Scene {sc_num}... ", end='', flush=True)
                    _, generated_scene = agent.write_a_scene(
                        scene, sc_num, ch_num, plan,
                        previous_scene=previous_scene
                    )
                    form_text.append(generated_scene)
                    scene_count += 1
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} ({len(generated_scene)} chars)")
                except Exception as e:
                    print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
                    form_text.append(f"[ERROR: Could not generate scene {sc_num}]")
                
                sc_num += 1
    
    # Save final story
    story_file = os.path.join(agent.session_dir, "final_story.txt")
    with open(story_file, "w", encoding='utf-8') as f:
        for i, scene in enumerate(form_text, 1):
            f.write(f"\n{'='*20} SCENE {i} {'='*20}\n")
            f.write(scene)
            f.write("\n\n")
    
    # Calculate stats
    full_story_text = "\n\n".join(form_text)
    word_count = len(full_story_text.split())
    
    # Success!
    print_header("✨ Story Generation Complete!")
    print_success(f"Generated {scene_count} scenes")
    print_success(f"Total words: {word_count}")
    print_success(f"Story saved to: {story_file}")
    print_info(f"All files in: {agent.session_dir}")
    
    # Offer to open story
    open_now = input(f"\n{Colors.BOLD}Open the story now? (yes/no):{Colors.ENDC} ").strip().lower()
    if open_now == 'yes':
        # Try to open with default text editor
        if sys.platform == 'darwin':  # macOS
            os.system(f'open "{story_file}"')
        elif sys.platform == 'linux':
            os.system(f'xdg-open "{story_file}"')
        elif sys.platform == 'win32':
            os.system(f'start "" "{story_file}"')


if __name__ == "__main__":
    try:
        interactive_wizard()
    except KeyboardInterrupt:
        print("\n\n" + Colors.WARNING + "⚠ Interrupted by user" + Colors.ENDC)
        print_info("Your progress has been saved in the session folder")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

