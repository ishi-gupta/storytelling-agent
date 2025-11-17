#!/usr/bin/env python3
"""
GOAT Storytelling Agent - Story Generation Script
Generates stories with comprehensive logging
"""

import json
import datetime
import os
import argparse
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv
from goat_storytelling_agent.storytelling_agent import StoryAgent
from story_presets import get_preset

def get_next_session_id(logs_dir: str) -> int:
    """Get the next available session ID (numeric, starting from 1)"""
    os.makedirs(logs_dir, exist_ok=True)
    
    # Find all existing session directories
    existing_sessions = []
    for item in os.listdir(logs_dir):
        if item.startswith("session_") and os.path.isdir(os.path.join(logs_dir, item)):
            try:
                # Extract numeric ID from "session_1", "session_2", etc.
                session_num = int(item.replace("session_", ""))
                existing_sessions.append(session_num)
            except ValueError:
                # Skip non-numeric session folders (old format)
                continue
    
    if not existing_sessions:
        return 1
    
    return max(existing_sessions) + 1

class LoggingStoryAgent(StoryAgent):
    """Enhanced StoryAgent with comprehensive logging"""
    
    def __init__(self, topic=None, length_preset='medium', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Store generation metadata
        self.topic = topic
        self.length_preset = length_preset
        self.generation_start_time = datetime.datetime.now()
        
        # Create logs directory
        self.logs_dir = "story_generation_logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Get next numeric session ID
        session_num = get_next_session_id(self.logs_dir)
        self.session_id = str(session_num)
        self.session_dir = os.path.join(self.logs_dir, f"session_{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Create plans and evaluations folders
        self.plans_dir = os.path.join(self.session_dir, "plans")
        self.evaluations_dir = os.path.join(self.session_dir, "evaluations")
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.evaluations_dir, exist_ok=True)
        
        # Create seed.json with initial metadata
        self.seed_data = {
            "version": "1.0",
            "session_id": self.session_id,
            "generated_at": self.generation_start_time.isoformat(),
            "topic": topic,
            "length_preset": length_preset,
            "model": kwargs.get('model', 'gpt-5'),
            "word_count": None,
            "scene_count": None,
            "generation_time_seconds": None
        }
        self.save_seed()
        
        # Initialize log data
        self.log_data = {
            "session_id": self.session_id,
            "timestamp": self.generation_start_time.isoformat(),
            "topic": topic,
            "steps": []
        }
        
        print(f"📁 Session: {self.session_id}")
        print(f"📂 Plans: {self.plans_dir}")
        print(f"📂 Evaluations: {self.evaluations_dir}")
    
    def save_seed(self):
        """Save seed.json with generation metadata"""
        seed_file = os.path.join(self.session_dir, "seed.json")
        with open(seed_file, "w", encoding='utf-8') as f:
            json.dump(self.seed_data, f, indent=2, ensure_ascii=False)
    
    def save_plan_artifact(self, filename: str, data: Any, as_json: bool = False):
        """Save a planning artifact to the plans/ folder"""
        filepath = os.path.join(self.plans_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if as_json:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                f.write(str(data))
        
        print(f"  💾 Saved: {filename}")
    
    def log_step(self, step_name: str, data: Any, status: str = "info"):
        """Log a step"""
        step_log = {
            "step": step_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": status,
            "data": data
        }
        self.log_data["steps"].append(step_log)
        
        # Save incremental log
        self.save_logs()
        
        print(f"📝 Logged step: {step_name} ({status})")
    
    def save_logs(self):
        """Save current log data to files"""
        # Save JSON log
        json_file = os.path.join(self.session_dir, "generation_log.json")
        with open(json_file, "w") as f:
            json.dump(self.log_data, f, indent=2)
        
        # Save human-readable log
        txt_file = os.path.join(self.session_dir, "generation_log.txt")
        with open(txt_file, "w") as f:
            f.write(f"GOAT Storytelling Agent - Session {self.session_id}\n")
            f.write(f"Generated: {self.log_data['timestamp']}\n")
            f.write(f"Topic: {self.log_data.get('topic', 'N/A')}\n")
            f.write("=" * 80 + "\n\n")
            
            for step in self.log_data["steps"]:
                f.write(f"\n[{step['timestamp']}] {step['step'].upper()} ({step['status']})\n")
                f.write("-" * 40 + "\n")
                
                # Write main data
                if isinstance(step['data'], str):
                    f.write(step['data'])
                elif isinstance(step['data'], dict):
                    f.write(json.dumps(step['data'], indent=2))
                else:
                    f.write(str(step['data']))
                
                f.write("\n\n")
    
    def write_a_scene_with_logging(self, scene, sc_num, ch_num, plan, 
                                    previous_scene=None):
        """Scene writing with logging"""
        print(f"\n📝 Generating scene {sc_num} of chapter {ch_num}...")
        
        # Generate scene using base StoryAgent
        messages, generated_scene = super(LoggingStoryAgent, self).write_a_scene(
            scene, sc_num, ch_num, plan, previous_scene)
        
        # Log the scene generation
        self.log_step(f"write_scene_{ch_num}_{sc_num}", {
            "final_scene": generated_scene,
            "scene_length": len(generated_scene)
        }, "success")
        
        return messages, generated_scene
    
    def generate_story_with_logging(self, topic):
        """Story generation with comprehensive logging"""
        self.log_data["topic"] = topic
        self.log_step("generate_story_start", {"topic": topic})
        
        try:
            print(f"\n🎭 Starting story generation for: '{topic}'")
            
            # Step 1: Book Specification
            print(f"\n📋 STEP 1: Creating book specification...")
            self.log_step("init_book_spec_start", {"topic": topic})
            _, book_spec = self.init_book_spec(topic)
            self.log_step("init_book_spec_success", {"book_spec": book_spec})
            self.save_plan_artifact("1_initial_book_spec.txt", book_spec)
            print(f"✅ Book spec completed")
            
            # Step 2: Enhanced Book Specification
            print(f"\n📋 STEP 2: Enhancing book specification...")
            self.log_step("enhance_book_spec_start", {"input_book_spec": book_spec})
            _, book_spec = self.enhance_book_spec(book_spec)
            self.log_step("enhance_book_spec_success", {"enhanced_spec": book_spec})
            self.save_plan_artifact("2_enhanced_book_spec.txt", book_spec)
            print(f"✅ Enhanced book spec completed")
            
            # Step 3: Chapter Planning
            print(f"\n📋 STEP 3: Creating plot chapters...")
            self.log_step("create_plot_chapters_start", {"book_spec": book_spec})
            _, plan = self.create_plot_chapters(book_spec)
            self.log_step("create_plot_chapters_success", {"plan": plan})
            self.save_plan_artifact("3_initial_plot.json", plan, as_json=True)
            print(f"✅ Plot chapters completed with {len(plan)} acts")
            
            # Step 4: Enhanced Chapter Planning
            print(f"\n📋 STEP 4: Enhancing plot chapters...")
            self.log_step("enhance_plot_chapters_start", {"plan": plan})
            _, plan = self.enhance_plot_chapters(book_spec, plan)
            self.log_step("enhance_plot_chapters_success", {"enhanced_plan": plan})
            self.save_plan_artifact("4_enhanced_plot.json", plan, as_json=True)
            print(f"✅ Enhanced plot chapters completed")
            
            # Step 5: Scene Breakdown
            print(f"\n📋 STEP 5: Splitting chapters into scenes...")
            self.log_step("split_chapters_into_scenes_start", {"plan": plan})
            _, plan = self.split_chapters_into_scenes(plan)
            self.log_step("split_chapters_into_scenes_success", {"scene_plan": plan})
            self.save_plan_artifact("5_scene_plan.json", plan, as_json=True)
            print(f"✅ Scene breakdown completed")
            
            # Step 6: Scene Text Generation
            print(f"\n📋 STEP 6: Generating scene text...")
            form_text = []
            total_scenes = 0
            
            for act_idx, act in enumerate(plan):
                print(f"\n🔍 Processing Act {act_idx + 1}...")
                if 'chapter_scenes' not in act:
                    print(f"⚠️  Act {act_idx + 1} missing 'chapter_scenes' key")
                    continue
                    
                chapter_scenes = act['chapter_scenes']
                
                for ch_num, chapter in chapter_scenes.items():
                    sc_num = 1
                    for scene_idx, scene in enumerate(chapter):
                        previous_scene = form_text[-1] if form_text else None
                        
                        try:
                            _, generated_scene = self.write_a_scene_with_logging(
                                scene, sc_num, ch_num, plan,
                                previous_scene=previous_scene
                            )
                            form_text.append(generated_scene)
                            total_scenes += 1
                            print(f"✅ Scene {sc_num} completed (length: {len(generated_scene)})")
                        except Exception as e:
                            print(f"❌ ERROR writing scene {sc_num}: {e}")
                            self.log_step(f"write_scene_{ch_num}_{sc_num}_error", {"error": str(e)}, "error")
                            form_text.append(f"[ERROR: Could not generate scene {sc_num}]")
                        sc_num += 1
            
            # Save final story
            story_file = os.path.join(self.session_dir, "final_story.txt")
            with open(story_file, "w") as f:
                for i, scene in enumerate(form_text, 1):
                    f.write(f"\n{'='*20} SCENE {i} {'='*20}\n")
                    f.write(scene)
                    f.write("\n\n")
            
            # Calculate final stats
            full_story_text = "\n\n".join(form_text)
            word_count = len(full_story_text.split())
            generation_time = (datetime.datetime.now() - self.generation_start_time).total_seconds()
            
            # Update seed.json with final stats
            self.seed_data["word_count"] = word_count
            self.seed_data["scene_count"] = total_scenes
            self.seed_data["generation_time_seconds"] = round(generation_time, 1)
            self.save_seed()
            
            # Final logging
            final_stats = {
                "num_scenes": total_scenes,
                "word_count": word_count,
                "total_length": len(full_story_text),
                "generation_time_seconds": generation_time,
                "story_file": story_file
            }
            
            self.log_step("generate_story_success", final_stats)
            
            print(f"\n🎉 STORY GENERATION COMPLETE!")
            print(f"📊 Generated {total_scenes} scenes, {word_count} words")
            print(f"⏱️  Generation time: {round(generation_time, 1)}s")
            
            return form_text
            
        except Exception as e:
            self.log_step("generate_story_error", {"error": str(e)}, "error")
            raise

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate stories with the GOAT Storytelling Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --length short --topic "a robot learning to love"
  %(prog)s --length medium  # Uses default topic
  %(prog)s --topic "time travel paradox"  # Uses default length (medium)
        """
    )
    parser.add_argument(
        '--length',
        choices=['short', 'medium', 'long'],
        default='medium',
        help='Story length preset: short (~5min/1000 words), medium (~10min/2000 words), long (~15min/3000 words)'
    )
    parser.add_argument(
        '--topic',
        type=str,
        default='a detective solving a mystery in a haunted mansion',
        help='Story topic/premise (default: "a detective solving a mystery in a haunted mansion")'
    )
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Load API key from environment variable
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY environment variable (you can use a .env file)")
    
    # Get the preset configuration
    preset = get_preset(args.length)
    
    # Create the story agent with logging
    writer = LoggingStoryAgent(
        topic=args.topic,
        length_preset=args.length,
        backend_uri=OPENAI_API_KEY,
        backend="openai",
        model="gpt-5",
        max_tokens=2000,
        story_preset=preset,  # Pass preset to base StoryAgent
        extra_options={
            # GPT-5 only supports default temperature (1.0) and top_p (1.0)
            "temperature": 1.0,
            "top_p": 1.0
        }
    )
    
    print("🎭 GOAT Storytelling Agent with OpenAI + Comprehensive Logging")
    print("=" * 80)
    print(f"📏 Length: {args.length.upper()} (~{preset['reading_time']}, target {preset['target_words']} words)")
    print(f"📝 Topic: {args.topic}")
    print("=" * 80)
    
    # Generate a complete story with full logging
    print("\n📚 Generating story...")
    topic = args.topic
    
    try:
        novel_scenes = writer.generate_story_with_logging(topic)
        print(f"\n✅ Generated {len(novel_scenes)} scenes!")
        print(f"📁 All logs saved to: {writer.session_dir}")
        
        # List what was saved
        print(f"\n📋 Files created:")
        for file in os.listdir(writer.session_dir):
            file_path = os.path.join(writer.session_dir, file)
            size = os.path.getsize(file_path)
            print(f"  📄 {file} ({size} bytes)")
        
    except Exception as e:
        print(f"❌ Error generating story: {e}")
        print(f"📁 Error logs saved to: {writer.session_dir}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
