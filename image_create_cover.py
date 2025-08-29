#!/usr/bin/env python3
"""
Cover Image Generator Module
Creates professional cover images for volumes and themes
"""

import os
import logging
import time
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from image_create_ai import generate_image_with_retry

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))
IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))

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

def validate_input_parameters(cover_type: str, volume_number: Optional[int] = None, output_dir: str = "images") -> Tuple[bool, str]:
    """Enhanced input validation"""
    try:
        if not cover_type or not isinstance(cover_type, str):
            return False, "Invalid cover type"
        if cover_type not in ["volume", "theme", "compilation"]:
            return False, f"Invalid cover type: {cover_type}"
        if volume_number is not None and not isinstance(volume_number, int):
            return False, "Invalid volume number"
        if not output_dir or not isinstance(output_dir, str):
            return False, "Invalid output directory"
        return True, "All parameters valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_environment():
    """Validate environment configuration"""
    try:
        required_vars = ['IMAGE_WIDTH', 'IMAGE_HEIGHT', 'IMAGE_QUALITY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        return True, "Environment configuration valid"
    except Exception as e:
        return False, f"Environment validation error: {str(e)}"

def generate_cover_image(cover_type, volume_number=None, output_dir="images"):
    """
    Generate a professional cover image with only brand information
    
    Args:
        cover_type (str): Type of cover ('volume', 'theme', 'compilation')
        volume_number (int): Volume number for brand text
        output_dir (str): Output directory
    
    Returns:
        str: Path to generated cover image
    """
    # Start performance monitoring
    performance_monitor.start_timer()
    
    try:
        # Input validation
        is_valid, validation_message = validate_input_parameters(cover_type, volume_number, output_dir)
        if not is_valid:
            log.error(f"Input validation failed: {validation_message}")
            performance_monitor.record_failure()
            return None
        
        # Environment validation
        is_valid, validation_message = validate_environment()
        if not is_valid:
            log.error(f"Environment validation failed: {validation_message}")
            performance_monitor.record_failure()
            return None
        
        log.info(f"Starting enhanced cover generation for {cover_type}...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate cover prompt - clean, minimalist research design
        prompt = "Professional research cover design. Modern, clean, minimalist design with research elements, professional typography, suitable for research publication. No text elements, just visual design."
        
        # Generate base image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ASK_COVER_{cover_type.upper()}_{timestamp}.jpg"
        image_path = os.path.join(output_dir, filename)
        
        # Generate image using AI
        generated_path, _ = generate_image_with_retry(
            prompt=prompt,
            theme="cover",
            image_number="cover",
            image_type="cover"
        )
        
        if generated_path and os.path.exists(generated_path):
            # Rename to our desired filename
            os.rename(generated_path, image_path)
            
            # Add only brand text overlay
            add_cover_brand_overlay(image_path, volume_number)
            
            log.info(f"Generated cover image: {image_path}")
            # Record success and end timer
            performance_monitor.end_timer()
            performance_monitor.record_success()
            
            return image_path
        else:
            log.error(f"Failed to generate cover image for {cover_type}")
            return None
            
    except Exception as e:
        log.error(f"Error in enhanced cover generation: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return None

def add_cover_brand_overlay(image_path, volume_number=None):
    """
    Add only brand information overlay to cover image
    
    Args:
        image_path (str): Path to image
        volume_number (int): Volume number for brand text
    """
    # Start performance monitoring
    performance_monitor.start_timer()
    
    try:
        # Validate input
        if not image_path or not os.path.exists(image_path):
            log.error(f"Invalid image path: {image_path}")
            performance_monitor.record_failure()
            return
        
        log.info(f"Starting enhanced brand overlay for {image_path}...")
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Font settings - use brand text size for consistency
        font_file = os.getenv('FONT_FILE_PATH', 'fonts/arial.ttf')
        brand_font_size = int(os.getenv('BRAND_FONT_SIZE', '36'))
        
        try:
            brand_font = ImageFont.truetype(font_file, brand_font_size)
        except:
            brand_font = ImageFont.load_default()
        
        # Create subtle overlay for readability
        overlay = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
        for i in range(IMAGE_HEIGHT):
            # Create gradient from top to bottom
            alpha = int(120 - (i * 40 / IMAGE_HEIGHT))
            alpha = max(60, min(120, alpha))
            line_overlay = Image.new('RGBA', (IMAGE_WIDTH, 1), (0, 0, 0, alpha))
            overlay.paste(line_overlay, (0, i))
        
        img.paste(overlay, (0, 0), overlay)
        
        # Brand text color
        brand_color = (255, 255, 255)  # White for visibility
        
        # Create brand text with volume number
        if volume_number:
            brand_text = f"ASK: Daily Research - VOL - {volume_number:02d}"
        else:
            brand_text = "ASK: Daily Research"
        
        # Calculate brand text position (bottom center)
        brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_width = brand_bbox[2] - brand_bbox[0]
        brand_height = brand_bbox[3] - brand_bbox[1]
        
        # Position at bottom center with 1-inch margin
        margin_pixels = int(1 * 96)  # 1 inch = 96 pixels
        brand_x = (IMAGE_WIDTH - brand_width) / 2
        brand_y = IMAGE_HEIGHT - margin_pixels - brand_height
        
        # Draw brand text
        draw.text((brand_x, brand_y), brand_text, font=brand_font, fill=brand_color)
        
        # Save the enhanced image
        img.save(image_path, quality=IMAGE_QUALITY, optimize=True)
        
        # Record success and end timer
        performance_monitor.end_timer()
        performance_monitor.record_success()
        
        log.info(f"Added brand overlay to cover image: {image_path}")
        
    except Exception as e:
        log.error(f"Error in enhanced brand overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()

def create_cover(cover_type, volume_number=None, qa_pairs=None, output_dir="images"):
    """
    Create a cover image with only brand information
    
    Args:
        cover_type (str): Type of cover ('volume', 'theme', 'compilation')
        volume_number (int): Volume number (for volume covers)
        qa_pairs (list): Q&A pairs (unused, kept for compatibility)
        output_dir (str): Output directory
    
    Returns:
        str: Path to cover image
    """
    try:
        return generate_cover_image(cover_type, volume_number, output_dir)
        
    except Exception as e:
        log.error(f"Error creating {cover_type} cover: {e}")
        return None

# Backward compatibility functions
def create_volume_cover(volume_number, qa_pairs, output_dir="images"):
    """Create a volume cover image (backward compatibility)"""
    return create_cover('volume', volume_number, qa_pairs, output_dir)

def create_category_cover(theme, qa_pairs, output_dir="images"):
    """Create a theme cover image (backward compatibility)"""
    return create_cover('theme', None, qa_pairs, output_dir)

def create_compilation_cover(compilation_type, qa_pairs, output_dir="images"):
    """Create a compilation cover image (backward compatibility)"""
    return create_cover('compilation', None, qa_pairs, output_dir)

def get_performance_stats():
    """Get performance statistics"""
    return performance_monitor.get_stats()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    log.info("Performance statistics reset")

def get_cover_generation_history():
    """Get recent cover generation history"""
    stats = performance_monitor.get_stats()
    return {
        'total_generated': stats['successful_operations'],
        'total_failed': stats['failed_operations'],
        'success_rate': stats['success_rate'],
        'total_time': stats['total_time']
    }

def validate_cover_quality(image_path: str) -> Tuple[bool, str]:
    """Validate generated cover quality"""
    try:
        if not os.path.exists(image_path):
            return False, f"Cover file does not exist: {image_path}"
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            return False, f"Cover file is empty: {image_path}"
        
        if file_size < 1024:  # Less than 1KB
            return False, f"Cover file too small: {file_size} bytes"
        
        if file_size > 10 * 1024 * 1024:  # More than 10MB
            return False, f"Cover file too large: {file_size} bytes"
        
        return True, "Cover quality valid"
    except Exception as e:
        return False, f"Cover quality validation error: {str(e)}"

def get_cover_templates():
    """Get available cover templates"""
    return {
        'volume': {
            'prompt': 'Professional research cover design. Modern, clean, minimalist design with research elements, professional typography, suitable for research publication. No text elements, just visual design.',
            'brand_text': 'ASK: Daily Research - VOL - {volume_number:02d}'
        },
        'theme': {
            'prompt': 'Professional research cover design. Modern, clean, minimalist design with research elements, professional typography, suitable for research publication. No text elements, just visual design.',
            'brand_text': 'ASK: Daily Research'
        },
        'compilation': {
            'prompt': 'Professional research cover design. Modern, clean, minimalist design with research elements, professional typography, suitable for research publication. No text elements, just visual design.',
            'brand_text': 'ASK: Daily Research'
        }
    }
