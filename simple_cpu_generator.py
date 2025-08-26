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
    """Add architectural patterns to the image"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Add architectural elements based on theme
    if 'technology' in theme.lower():
        # Modern architectural elements - glass facades, steel structures
        for i in range(0, width, 80):
            for j in range(0, height, 80):
                if random.random() < 0.4:
                    # Glass facade panels
                    panel_width = random.randint(30, 60)
                    panel_height = random.randint(40, 80)
                    draw.rectangle([i, j, i+panel_width, j+panel_height], outline='#FFFFFF', width=2)
                    # Add horizontal lines for glass panels
                    for k in range(j+10, j+panel_height, 15):
                        draw.line([i, k, i+panel_width, k], fill='#FFFFFF', width=1)
    
    elif 'sustainability' in theme.lower() or 'environmental' in theme.lower():
        # Green building elements - solar panels, green roofs, natural materials
        for i in range(0, width, 60):
            for j in range(0, height, 60):
                if random.random() < 0.5:
                    # Solar panel arrays
                    panel_size = random.randint(20, 40)
                    draw.rectangle([i, j, i+panel_size, j+panel_size], outline='#FFFFFF', width=2)
                    # Add grid pattern for solar cells
                    for k in range(i+5, i+panel_size, 8):
                        for l in range(j+5, j+panel_size, 8):
                            draw.rectangle([k, l, k+6, l+6], outline='#FFFFFF', width=1)
    
    elif 'urban' in theme.lower() or 'planning' in theme.lower():
        # Urban planning elements - buildings, streets, infrastructure
        for i in range(0, width, 70):
            for j in range(0, height, 70):
                if random.random() < 0.6:
                    # Building blocks
                    building_width = random.randint(25, 50)
                    building_height = random.randint(30, 70)
                    draw.rectangle([i, j, i+building_width, j+building_height], outline='#FFFFFF', width=2)
                    # Add windows
                    for k in range(i+5, i+building_width-5, 8):
                        for l in range(j+5, j+building_height-5, 12):
                            draw.rectangle([k, l, k+6, l+8], outline='#FFFFFF', width=1)
    
    elif 'spatial' in theme.lower() or 'design' in theme.lower():
        # Spatial design elements - interior spaces, furniture, circulation
        for i in range(0, width, 50):
            for j in range(0, height, 50):
                if random.random() < 0.4:
                    # Room layouts
                    room_width = random.randint(30, 60)
                    room_height = random.randint(25, 50)
                    draw.rectangle([i, j, i+room_width, j+room_height], outline='#FFFFFF', width=2)
                    # Add furniture elements
                    if random.random() < 0.7:
                        furniture_x = i + random.randint(5, room_width-15)
                        furniture_y = j + random.randint(5, room_height-10)
                        draw.rectangle([furniture_x, furniture_y, furniture_x+12, furniture_y+8], outline='#FFFFFF', width=1)
    
    else:
        # General architectural elements - columns, arches, facades
        for i in range(0, width, 60):
            for j in range(0, height, 60):
                if random.random() < 0.3:
                    # Architectural columns
                    column_width = random.randint(15, 25)
                    column_height = random.randint(40, 80)
                    draw.rectangle([i, j, i+column_width, j+column_height], outline='#FFFFFF', width=2)
                    # Add column details
                    draw.rectangle([i-2, j+column_height-5, i+column_width+2, j+column_height], outline='#FFFFFF', width=1)

def add_texture_effects(image: Image.Image, prompt: str):
    """Add architectural texture and visual effects"""
    # Add architectural texture
    texture_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture_layer)
    
    # Add subtle architectural details
    for x in range(0, image.size[0], 3):
        for y in range(0, image.size[1], 3):
            if random.random() < 0.05:
                alpha = random.randint(5, 25)
                texture_draw.point((x, y), fill=(255, 255, 255, alpha))
    
    # Add architectural grid lines
    for x in range(0, image.size[0], 50):
        if random.random() < 0.3:
            alpha = random.randint(10, 30)
            texture_draw.line([(x, 0), (x, image.size[1])], fill=(255, 255, 255, alpha), width=1)
    
    for y in range(0, image.size[1], 50):
        if random.random() < 0.3:
            alpha = random.randint(10, 30)
            texture_draw.line([(0, y), (image.size[0], y)], fill=(255, 255, 255, alpha), width=1)
    
    # Blend texture layer
    image = Image.alpha_composite(image.convert('RGBA'), texture_layer)
    
    # Add slight blur for architectural depth
    image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
    
    return image

def add_theme_elements(image: Image.Image, theme: str, prompt: str):
    """Add architectural theme-specific visual elements"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Add architectural elements based on theme
    if 'design' in theme.lower():
        # Design elements - furniture, lighting, materials
        for i in range(4):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            if random.random() < 0.5:
                # Furniture pieces
                size = random.randint(25, 45)
                draw.rectangle([x, y, x+size, y+size], outline='#FFFFFF', width=2)
                # Add furniture details
                draw.line([x+5, y+size//2, x+size-5, y+size//2], fill='#FFFFFF', width=1)
            else:
                # Lighting fixtures
                radius = random.randint(8, 15)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='#FFFFFF', width=2)
                draw.line([x, y+radius, x, y+radius+20], fill='#FFFFFF', width=1)
    
    elif 'technology' in theme.lower():
        # Tech elements - smart building systems, digital interfaces
        for i in range(6):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            if random.random() < 0.6:
                # Digital displays
                size = random.randint(20, 35)
                draw.rectangle([x, y, x+size, y+size//2], outline='#FFFFFF', width=2)
                # Add digital grid
                for k in range(x+3, x+size-3, 4):
                    for l in range(y+3, y+size//2-3, 3):
                        draw.point((k, l), fill='#FFFFFF')
            else:
                # Smart sensors
                radius = random.randint(5, 12)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='#FFFFFF', width=1)
                draw.line([x-radius-5, y, x+radius+5, y], fill='#FFFFFF', width=1)
    
    elif 'sustainability' in theme.lower():
        # Sustainability elements - green roofs, solar panels, natural materials
        for i in range(5):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            if random.random() < 0.7:
                # Green roof sections
                size = random.randint(30, 50)
                draw.rectangle([x, y, x+size, y+size//2], outline='#FFFFFF', width=2)
                # Add vegetation pattern
                for k in range(x+5, x+size-5, 6):
                    for l in range(y+5, y+size//2-5, 6):
                        draw.ellipse([k-2, l-2, k+2, l+2], outline='#FFFFFF', width=1)
            else:
                # Solar panels
                size = random.randint(25, 40)
                draw.rectangle([x, y, x+size, y+size], outline='#FFFFFF', width=2)
                # Add solar cell grid
                for k in range(x+3, x+size-3, 5):
                    for l in range(y+3, y+size-3, 5):
                        draw.rectangle([k, l, k+3, l+3], outline='#FFFFFF', width=1)
    
    elif 'urban' in theme.lower() or 'planning' in theme.lower():
        # Urban elements - buildings, streets, public spaces
        for i in range(7):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            if random.random() < 0.8:
                # Building facades
                building_width = random.randint(20, 40)
                building_height = random.randint(25, 60)
                draw.rectangle([x, y, x+building_width, y+building_height], outline='#FFFFFF', width=2)
                # Add windows and doors
                for k in range(x+3, x+building_width-3, 6):
                    for l in range(y+3, y+building_height-3, 8):
                        draw.rectangle([k, l, k+4, l+6], outline='#FFFFFF', width=1)
            else:
                # Street elements
                street_width = random.randint(15, 30)
                draw.rectangle([x, y, x+street_width, y+8], outline='#FFFFFF', width=2)
                # Add street markings
                draw.line([x+street_width//2, y, x+street_width//2, y+8], fill='#FFFFFF', width=1)
    
    else:
        # General architectural elements - structural components
        for i in range(5):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            if random.random() < 0.6:
                # Structural beams
                beam_width = random.randint(20, 35)
                beam_height = random.randint(8, 15)
                draw.rectangle([x, y, x+beam_width, y+beam_height], outline='#FFFFFF', width=2)
                # Add beam details
                draw.line([x+beam_width//2, y, x+beam_width//2, y+beam_height], fill='#FFFFFF', width=1)
            else:
                # Architectural details
                size = random.randint(15, 25)
                draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], outline='#FFFFFF', width=1)
                draw.line([x-size//2, y, x+size//2, y], fill='#FFFFFF', width=1)

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

def generate_architectural_prompt(theme: str, prompt: str) -> str:
    """
    Generate photorealistic architectural prompts based on theme
    
    Args:
        theme (str): Theme name
        prompt (str): Original prompt
        
    Returns:
        str: Enhanced architectural prompt
    """
    architectural_prompts = {
        'design_research': [
            "photorealistic architectural rendering, modern research facility, glass facade, sustainable design, natural lighting, professional photography, 8k resolution, architectural photography",
            "photorealistic architectural visualization, contemporary design studio, minimalist interior, clean lines, natural materials, professional architectural photography, high detail",
            "photorealistic architectural model, innovative research building, geometric forms, sustainable materials, natural environment, professional photography, architectural detail"
        ],
        'technology_innovation': [
            "photorealistic architectural rendering, futuristic tech building, smart glass, LED lighting, digital infrastructure, professional photography, 8k resolution, modern architecture",
            "photorealistic architectural visualization, innovation center, cutting-edge design, technological integration, sustainable technology, professional photography, high detail",
            "photorealistic architectural model, smart building, IoT integration, renewable energy, modern facade, professional photography, architectural innovation"
        ],
        'sustainability_science': [
            "photorealistic architectural rendering, green building, living walls, solar panels, sustainable materials, natural environment, professional photography, 8k resolution",
            "photorealistic architectural visualization, eco-friendly building, passive design, renewable energy, natural ventilation, professional photography, high detail",
            "photorealistic architectural model, sustainable architecture, green roof, rainwater harvesting, natural lighting, professional photography, environmental design"
        ],
        'engineering_systems': [
            "photorealistic architectural rendering, industrial facility, structural engineering, mechanical systems, technical infrastructure, professional photography, 8k resolution",
            "photorealistic architectural visualization, engineering complex, structural elements, technical design, functional architecture, professional photography, high detail",
            "photorealistic architectural model, engineering building, structural innovation, technical systems, industrial design, professional photography, engineering architecture"
        ],
        'environmental_design': [
            "photorealistic architectural rendering, environmental building, natural integration, landscape architecture, sustainable design, professional photography, 8k resolution",
            "photorealistic architectural visualization, eco-architecture, natural materials, environmental harmony, sustainable landscape, professional photography, high detail",
            "photorealistic architectural model, environmental design, natural systems, sustainable architecture, landscape integration, professional photography, environmental architecture"
        ],
        'urban_planning': [
            "photorealistic architectural rendering, urban development, city planning, mixed-use building, urban infrastructure, professional photography, 8k resolution",
            "photorealistic architectural visualization, urban architecture, cityscape, modern urban design, sustainable urban planning, professional photography, high detail",
            "photorealistic architectural model, urban building, city integration, modern urbanism, sustainable development, professional photography, urban architecture"
        ],
        'spatial_design': [
            "photorealistic architectural rendering, spatial architecture, interior design, spatial planning, modern interior, professional photography, 8k resolution",
            "photorealistic architectural visualization, spatial design, interior architecture, space planning, modern spatial concepts, professional photography, high detail",
            "photorealistic architectural model, spatial building, interior innovation, modern space design, architectural interiors, professional photography, spatial architecture"
        ],
        'digital_technology': [
            "photorealistic architectural rendering, digital building, smart architecture, technological integration, modern digital design, professional photography, 8k resolution",
            "photorealistic architectural visualization, digital architecture, smart systems, technological innovation, modern digital space, professional photography, high detail",
            "photorealistic architectural model, digital building, smart technology, modern digital architecture, technological design, professional photography, digital architecture"
        ]
    }
    
    # Get theme-specific prompts
    theme_prompts = architectural_prompts.get(theme.lower(), architectural_prompts['design_research'])
    
    # Select a random architectural prompt
    base_prompt = random.choice(theme_prompts)
    
    # Combine with original prompt
    enhanced_prompt = f"{prompt}, {base_prompt}"
    
    return enhanced_prompt

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
