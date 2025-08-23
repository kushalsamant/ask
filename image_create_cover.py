#!/usr/bin/env python3
"""
Cover Image Generator Module
Creates professional cover images for volumes and themes
"""

import os
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from image_create_ai import generate_image_with_retry

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))
IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))

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
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate cover prompt - clean, minimalist architectural design
        prompt = "Professional architectural research cover design. Modern, clean, minimalist design with architectural elements, professional typography, suitable for research publication. No text elements, just visual design."
        
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
            return image_path
        else:
            log.error(f"Failed to generate cover image for {cover_type}")
            return None
            
    except Exception as e:
        log.error(f"Error generating cover image: {e}")
        return None

def add_cover_brand_overlay(image_path, volume_number=None):
    """
    Add only brand information overlay to cover image
    
    Args:
        image_path (str): Path to image
        volume_number (int): Volume number for brand text
    """
    try:
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
            brand_text = f"ASK: Daily Architectural Research - VOL - {volume_number:02d}"
        else:
            brand_text = "ASK: Daily Architectural Research"
        
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
        
        log.info(f"Added brand overlay to cover image: {image_path}")
        
    except Exception as e:
        log.error(f"Error adding brand overlay to cover image: {e}")

def create_volume_cover(volume_number, qa_pairs, output_dir="images"):
    """
    Create a volume cover image with only brand information
    
    Args:
        volume_number (int): Volume number
        qa_pairs (list): Q&A pairs for this volume
        output_dir (str): Output directory
    
    Returns:
        str: Path to cover image
    """
    try:
        return generate_cover_image('volume', volume_number, output_dir)
        
    except Exception as e:
        log.error(f"Error creating volume cover: {e}")
        return None

def create_category_cover(theme, qa_pairs, output_dir="images"):
    """
    Create a theme cover image with only brand information
    
    Args:
        theme (str): Theme name
        qa_pairs (list): Q&A pairs for this theme
        output_dir (str): Output directory
    
    Returns:
        str: Path to cover image
    """
    try:
        return generate_cover_image('theme', None, output_dir)
        
    except Exception as e:
        log.error(f"Error creating theme cover: {e}")
        return None

def create_compilation_cover(compilation_type, qa_pairs, output_dir="images"):
    """
    Create a compilation cover image with only brand information
    
    Args:
        compilation_type (str): Type of compilation
        qa_pairs (list): Q&A pairs for this compilation
        output_dir (str): Output directory
    
    Returns:
        str: Path to cover image
    """
    try:
        return generate_cover_image('compilation', None, output_dir)
        
    except Exception as e:
        log.error(f"Error creating compilation cover: {e}")
        return None
