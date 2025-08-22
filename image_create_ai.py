#!/usr/bin/env python3
"""
AI Image Generation Module
Handles AI-powered image generation using Together.ai API
"""

import os
import logging
import random
from PIL import Image
from api_client import api_client

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')
IMAGE_FILENAME_TEMPLATE = os.getenv('IMAGE_FILENAME_TEMPLATE', 'ASK-{image_number:02d}-{category}-{image_type}.jpg')

def generate_image_with_retry(prompt, category, image_number, max_retries=None, timeout=None, image_type="q"):
    """Generate Instagram story image using Together.ai API with retry logic"""

    # Get style for category using advanced style generator
    from research_csv_manager import get_questions_and_styles_from_log
    from style_data_manager import get_base_styles_for_category
    from style_ai_generator import get_ai_generated_style_suggestion, create_dynamic_style_combination
    from style_trend_analyzer import analyze_style_trends
    _, styles_by_category, _ = get_questions_and_styles_from_log()

    # Get the question for context-aware style selection
    questions_data, _, _ = get_questions_and_styles_from_log()
    question = None
    for q_data in questions_data.get(category, []):
        if isinstance(q_data, dict):
            question = q_data.get('question')
            break
        elif isinstance(q_data, str):
            question = q_data
            break

    # Get available styles
    available_styles = get_base_styles_for_category(category)
    if not available_styles:
        style = 'Modern'  # Fallback
    else:
        # If question is provided, try AI suggestions
        if question:
            ai_suggestions = get_ai_generated_style_suggestion(category, question)
            if ai_suggestions:
                selected_style = random.choice(ai_suggestions)
                # Create dynamic combination
                style = create_dynamic_style_combination(category, selected_style, question)
            else:
                # Fallback to random selection
                style = random.choice(available_styles)
        else:
            # Fallback to random selection
            style = random.choice(available_styles)
    log.info(f"Selected style for {category}: {style}")

    # Craft a detailed prompt optimized for FLUX.1 schnell
    formatted_prompt = (
        f"Professional architectural visualization, {style} architectural style. "
        f"Focus on {category} aspects. {prompt} "
        f"High-quality, photorealistic, detailed, professional photography, architectural visualisation"
    )

    # Use the consolidated API client
    image_url = api_client.call_image_api(
        prompt=formatted_prompt,
        negative_prompt="low quality, blurry, distorted, deformed, disfigured, bad proportions, watermark, signature, text",
        seed=random.randint(1, 999999999)
    )

    if not image_url:
        raise Exception(f"Failed to generate image URL for {category} image {image_number}")

    # Generate filename using template
    filename = f"{IMAGES_DIR}/{IMAGE_FILENAME_TEMPLATE.format(image_number=int(image_number), category=category, image_type=image_type)}"

    # Download and save image using the API client
    if api_client.download_image(image_url, filename):
        log.info(f"Generated {category} image {image_number}: {filename}")
        return filename, style
    else:
        raise Exception(f"Failed to download image for {category} image {image_number}")
