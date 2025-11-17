"""
Story length presets for controlling generation parameters
"""

STORY_PRESETS = {
    'short': {
        'target_words': 1000,
        'reading_time': '5 minutes',
        'acts': 3,
        'chapters_instruction': 'Break the story into exactly 3 chapters: 1 chapter per act',
        'scenes_instruction': '2 scenes per chapter',
        'scene_length_instruction': 'Write a concise scene of 150-200 words'
    },
    'medium': {
        'target_words': 2000,
        'reading_time': '10 minutes',
        'acts': 3,
        'chapters_instruction': 'Break the story into 6-9 total chapters: 2-3 chapters per act',
        'scenes_instruction': '1-2 scenes per chapter',
        'scene_length_instruction': 'Write a scene of 200-300 words'
    },
    'long': {
        'target_words': 3000,
        'reading_time': '15 minutes',
        'acts': 3,
        'chapters_instruction': 'Break the story into 9-12 total chapters: 3-4 chapters per act',
        'scenes_instruction': '2-3 scenes per chapter',
        'scene_length_instruction': 'Write a detailed scene of 250-350 words'
    }
}

def get_preset(length='medium'):
    """
    Get a story preset by name
    
    Args:
        length: 'short', 'medium', or 'long' (default: 'medium')
    
    Returns:
        Dictionary with preset configuration
    """
    if length not in STORY_PRESETS:
        print(f"Warning: Unknown preset '{length}', defaulting to 'medium'")
        length = 'medium'
    
    return STORY_PRESETS[length]

