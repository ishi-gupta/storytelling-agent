"""
Story length presets for controlling generation parameters
"""

STORY_PRESETS = {
    'short': {
        'target_words': 1000,
        'reading_time': '5 minutes',
        'acts': 3,
        'chapters_instruction': 'Come up with a plot for a bestseller-grade {form} in 3 acts with 2-3 chapters total',
        'scenes_instruction': 'Break each chapter in Act {act_num} into 1 scene',
        'scene_length_instruction': 'Write a concise scene for a {form} (aim for 150-200 words)'
    },
    'medium': {
        'target_words': 2000,
        'reading_time': '10 minutes',
        'acts': 3,
        'chapters_instruction': 'Come up with a plot for a bestseller-grade {form} in 3 acts with 6-9 chapters total',
        'scenes_instruction': 'Break each chapter in Act {act_num} into 1-2 scenes (number depends on how packed a chapter is)',
        'scene_length_instruction': 'Write a scene for a {form} (aim for 200-300 words)'
    },
    'long': {
        'target_words': 3000,
        'reading_time': '15 minutes',
        'acts': 3,
        'chapters_instruction': 'Come up with a plot for a bestseller-grade {form} in 3 acts with 9-12 chapters total',
        'scenes_instruction': 'Break each chapter in Act {act_num} into 2-3 scenes (number depends on how packed a chapter is)',
        'scene_length_instruction': 'Write a detailed scene for a {form} (aim for 250-350 words)'
    }
}

def get_preset(length='medium'):
    """Get a story preset by name"""
    return STORY_PRESETS.get(length, STORY_PRESETS['medium'])

