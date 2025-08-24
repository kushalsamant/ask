#!/usr/bin/env python3
"""
AI Image Generation Module
Handles AI-powered image generation using Together.ai API
"""

import os
import time
from typing import Optional, Tuple, List, Dict, Any

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {'total_operations': 0, 'successful_operations': 0, 'failed_operations': 0, 'total_time': 0.0}
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics['total_time'] += duration
            self.metrics['total_operations'] += 1
    
    def record_success(self):
        self.metrics['successful_operations'] += 1
    
    def record_failure(self):
        self.metrics['failed_operations'] += 1
    
    def get_stats(self):
        stats = self.metrics.copy()
        stats['success_rate'] = (self.metrics['successful_operations'] / max(self.metrics['total_operations'], 1)) * 100
        return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()

def validate_input_parameters(prompt: str, theme: str, image_number: Any, image_type: str = "q") -> Tuple[bool, str]:
    """Enhanced input validation"""
    try:
        if not prompt or not isinstance(prompt, str):
            return False, "Invalid prompt"
        if len(prompt.strip()) == 0:
            return False, "Empty prompt"
        if not theme or not isinstance(theme, str):
            return False, "Invalid theme"
        if image_number is None:
            return False, "Invalid image number"
        if not isinstance(image_type, str) or image_type not in ["q", "a", "cover", "toc"]:
            return False, "Invalid image type"
        return True, "All parameters valid"
    except Exception as e:
        log.error(f"Error in enhanced image generation: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        raise
        return False, f"Validation error: {str(e)}"

def validate_environment():
    """Validate environment configuration"""
    try:
        required_vars = ['IMAGES_DIR', 'IMAGE_FILENAME_TEMPLATE']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        # Validate API key
        if not os.getenv('TOGETHER_API_KEY'):
            return False, "Missing TOGETHER_API_KEY"
        
        return True, "Environment configuration valid"
    except Exception as e:
        log.error(f"Error in enhanced image generation: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        raise
        return False, f"Environment validation error: {str(e)}"
import logging
import random
from PIL import Image
from api_client import api_client

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')
IMAGE_FILENAME_TEMPLATE = os.getenv('IMAGE_FILENAME_TEMPLATE', 'ASK-{image_number:02d}-{theme}-{image_type}.jpg')

def generate_image_with_retry(prompt, theme, image_number, max_retries=None, timeout=None, image_type="q"):
    """Generate Instagram story image using Together.ai API with retry logic"""
    # Start performance monitoring
    performance_monitor.start_timer()
    
    try:
        # Input validation
        is_valid, validation_message = validate_input_parameters(prompt, theme, image_number, image_type)
        if not is_valid:
            log.error(f"Input validation failed: {validation_message}")
            performance_monitor.record_failure()
            raise ValueError(validation_message)
        
        # Environment validation
        is_valid, validation_message = validate_environment()
        if not is_valid:
            log.error(f"Environment validation failed: {validation_message}")
            performance_monitor.record_failure()
            raise ValueError(validation_message)
        
        log.info(f"Starting enhanced image generation for {theme} image {image_number}...")

        # Get style for theme using advanced style generator
        from research_csv_manager import get_questions_and_styles_from_log
        from style_data_manager import get_base_styles_for_category
        from style_ai_generator import get_ai_generated_style_suggestion, create_dynamic_style_combination
        from style_trend_analyzer import analyze_style_trends
        _, styles_by_category, _ = get_questions_and_styles_from_log()

        # Get the question for context-aware style selection
        questions_data, _, _ = get_questions_and_styles_from_log()
        question = None
        for q_data in questions_data.get(theme, []):
            if isinstance(q_data, dict):
                question = q_data.get('question')
                break
            elif isinstance(q_data, str):
                question = q_data
                break

        # Get available styles
        available_styles = get_base_styles_for_category(theme)
        if not available_styles:
            style = 'Modern'  # Fallback
        else:
            # If question is provided, try AI suggestions
            if question:
                ai_suggestions = get_ai_generated_style_suggestion(theme, question)
                if ai_suggestions:
                    selected_style = random.choice(ai_suggestions)
                    # Create dynamic combination
                    style = create_dynamic_style_combination(theme, selected_style, question)
                else:
                    # Fallback to random selection
                    style = random.choice(available_styles)
            else:
                # Fallback to random selection
                style = random.choice(available_styles)
        log.info(f"Selected style for {theme}: {style}")

        # Craft a detailed prompt optimized for FLUX.1 schnell
        formatted_prompt = (
            f"Professional architectural visualization, {style} architectural style. "
            f"Focus on {theme} aspects. {prompt} "
            f"High-quality, photorealistic, detailed, professional photography, architectural visualisation"
        )

        # Use the consolidated API client
        image_url = api_client.call_image_api(
            prompt=formatted_prompt,
            negative_prompt="low quality, blurry, distorted, deformed, disfigured, bad proportions, watermark, signature, text",
            seed=random.randint(1, 999999999)
        )

        if not image_url:
            raise Exception(f"Failed to generate image URL for {theme} image {image_number}")

        # Generate filename using template
        filename = f"{IMAGES_DIR}/{IMAGE_FILENAME_TEMPLATE.format(image_number=int(image_number), theme=theme, image_type=image_type)}"

        # Download and save image using the API client
        if api_client.download_image(image_url, filename):
            log.info(f"Generated {theme} image {image_number}: {filename}")
            # Record success and end timer
            performance_monitor.end_timer()
            performance_monitor.record_success()
            
            return filename, style
        else:
            raise Exception(f"Failed to download image for {theme} image {image_number}")
    
    except Exception as e:
        log.error(f"Error in enhanced image generation: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        raise


def get_performance_stats():
    """Get performance statistics"""
    return performance_monitor.get_stats()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    log.info("Performance statistics reset")

def get_generation_history():
    """Get recent image generation history"""
    stats = performance_monitor.get_stats()
    return {
        'total_generated': stats['successful_operations'],
        'total_failed': stats['failed_operations'],
        'success_rate': stats['success_rate'],
        'total_time': stats['total_time']
    }

def validate_image_quality(image_path: str) -> Tuple[bool, str]:
    """Validate generated image quality"""
    try:
        if not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            return False, f"Image file is empty: {image_path}"
        
        if file_size < 1024:  # Less than 1KB
            return False, f"Image file too small: {file_size} bytes"
        
        if file_size > 10 * 1024 * 1024:  # More than 10MB
            return False, f"Image file too large: {file_size} bytes"
        
        return True, "Image quality valid"
    except Exception as e:
        return False, f"Image quality validation error: {str(e)}"