#!/usr/bin/env python3
"""
Simple CPU Image Generator
Creates AI-like images using basic image processing and patterns
Works without complex diffusers dependencies
"""

import os
import logging
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pathlib import Path
from typing import Tuple, Optional

# Setup logging
log = logging.getLogger(__name__)

def create_ai_style_image(prompt: str, theme: str, image_number: int, image_type: str) -> Tuple[str, str]:
    """
    Create an AI-style image using basic image processing
    
    Args:
        prompt (str): The prompt for the image
        theme (str): Theme name
        image_number (int): Image number
        image_type (str): Image type (q/a)
        
    Returns:
        Tuple[str, str]: (filepath, style)
    """
    try:
        # Get configuration
        width = int(os.getenv("IMAGE_WIDTH", "1072"))
        height = int(os.getenv("IMAGE_HEIGHT", "1792"))
        
        # Create base image with theme-based colors
        colors = get_theme_colors(theme)
        base_color = random.choice(colors)
        
        # Create gradient background
        image = create_gradient_background(width, height, base_color)
        
        # Add geometric patterns
        add_geometric_patterns(image, theme)
        
        # Add texture and effects
        add_texture_effects(image, prompt)
        
        # Add theme-specific elements
        add_theme_elements(image, theme, prompt)
        
        # Apply final enhancements
        enhance_image(image)
        
        # Generate filename
        images_dir = os.getenv("IMAGES_DIR", "images")
        filename_template = os.getenv("IMAGE_FILENAME_TEMPLATE", "ASK-{image_number:02d}-{theme}-{image_type}.jpg")
        
        # Sanitize theme for filename
        safe_theme = "".join(c for c in theme if c.isalnum() or c in ('-', '_')).rstrip()
        if not safe_theme:
            safe_theme = "unknown_theme"
        
        filename = filename_template.format(
            image_number=int(image_number), 
            theme=safe_theme, 
            image_type=image_type
        )
        
        # Save image
        file_path = Path(images_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        image.save(str(file_path), quality=95, optimize=True)
        log.info(f"Created AI-style image: {file_path}")
        
        return str(file_path), "AI-Style"
        
    except Exception as e:
        log.error(f"Failed to create AI-style image: {e}")
        raise

def get_theme_colors(theme: str) -> list:
    """Get color palette based on theme"""
    color_palettes = {
        'design_research': ['#2C3E50', '#34495E', '#3498DB', '#2980B9', '#1ABC9C'],
        'technology_innovation': ['#8E44AD', '#9B59B6', '#3498DB', '#2980B9', '#2C3E50'],
        'sustainability_science': ['#27AE60', '#2ECC71', '#16A085', '#1ABC9C', '#2E8B57'],
        'engineering_systems': ['#E67E22', '#D35400', '#F39C12', '#E74C3C', '#C0392B'],
        'environmental_design': ['#27AE60', '#2ECC71', '#16A085', '#1ABC9C', '#2E8B57'],
        'urban_planning': ['#34495E', '#2C3E50', '#7F8C8D', '#95A5A6', '#BDC3C7'],
        'spatial_design': ['#9B59B6', '#8E44AD', '#3498DB', '#2980B9', '#2C3E50'],
        'digital_technology': ['#8E44AD', '#9B59B6', '#3498DB', '#2980B9', '#2C3E50']
    }
    
    return color_palettes.get(theme.lower(), ['#2C3E50', '#34495E', '#3498DB', '#2980B9'])

def create_gradient_background(width: int, height: int, base_color: str) -> Image.Image:
    """Create a gradient background"""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create gradient effect
    for y in range(height):
        # Calculate gradient intensity
        intensity = int(255 * (1 - y / height) * 0.7)
        
        # Parse base color
        r, g, b = int(base_color[1:3], 16), int(base_color[3:5], 16), int(base_color[5:7], 16)
        
        # Apply gradient
        color = (
            max(0, min(255, r + intensity)),
            max(0, min(255, g + intensity)),
            max(0, min(255, b + intensity))
        )
        
        draw.line([(0, y), (width, y)], fill=color)
    
    return image

def add_geometric_patterns(image: Image.Image, theme: str):
    """Add geometric patterns to the image"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Add different patterns based on theme
    if 'technology' in theme.lower():
        # Circuit-like patterns
        for i in range(0, width, 50):
            for j in range(0, height, 50):
                if random.random() < 0.3:
                    draw.rectangle([i, j, i+20, j+20], outline='#FFFFFF', width=1)
                    if random.random() < 0.5:
                        draw.line([i+10, j, i+10, j+20], fill='#FFFFFF', width=1)
                        draw.line([i, j+10, i+20, j+10], fill='#FFFFFF', width=1)
    
    elif 'sustainability' in theme.lower() or 'environmental' in theme.lower():
        # Organic patterns
        for i in range(0, width, 30):
            for j in range(0, height, 30):
                if random.random() < 0.4:
                    radius = random.randint(5, 15)
                    draw.ellipse([i, j, i+radius*2, j+radius*2], outline='#FFFFFF', width=1)
    
    else:
        # Abstract patterns
        for i in range(0, width, 40):
            for j in range(0, height, 40):
                if random.random() < 0.2:
                    points = [
                        (i, j),
                        (i+30, j),
                        (i+15, j+30)
                    ]
                    draw.polygon(points, outline='#FFFFFF', width=1)

def add_texture_effects(image: Image.Image, prompt: str):
    """Add texture and visual effects"""
    # Add noise texture
    noise_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    noise_draw = ImageDraw.Draw(noise_layer)
    
    for x in range(0, image.size[0], 2):
        for y in range(0, image.size[1], 2):
            if random.random() < 0.1:
                alpha = random.randint(10, 50)
                noise_draw.point((x, y), fill=(255, 255, 255, alpha))
    
    # Blend noise layer
    image = Image.alpha_composite(image.convert('RGBA'), noise_layer)
    
    # Add slight blur for texture
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return image

def add_theme_elements(image: Image.Image, theme: str, prompt: str):
    """Add theme-specific visual elements"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Add floating elements based on theme
    if 'design' in theme.lower():
        # Design elements
        for i in range(5):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            size = random.randint(20, 60)
            draw.rectangle([x, y, x+size, y+size], outline='#FFFFFF', width=2)
    
    elif 'technology' in theme.lower():
        # Tech elements
        for i in range(8):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            radius = random.randint(10, 25)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='#FFFFFF', width=1)
    
    elif 'sustainability' in theme.lower():
        # Nature elements
        for i in range(6):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            points = [
                (x, y-15),
                (x-10, y+15),
                (x+10, y+15)
            ]
            draw.polygon(points, outline='#FFFFFF', width=1)

def enhance_image(image: Image.Image):
    """Apply final enhancements"""
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    # Enhance brightness slightly
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)
    
    # Add slight saturation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.1)

def generate_image_with_retry(prompt: str, theme: str, image_number: int, image_type: str) -> Tuple[str, str]:
    """
    Generate image with retry logic
    
    Args:
        prompt (str): Image prompt
        theme (str): Theme name
        image_number (int): Image number
        image_type (str): Image type
        
    Returns:
        Tuple[str, str]: (filepath, style)
    """
    try:
        return create_ai_style_image(prompt, theme, image_number, image_type)
    except Exception as e:
        log.error(f"Failed to generate AI-style image: {e}")
        raise
