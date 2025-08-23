#!/usr/bin/env python3
"""
Image Layout Creator Module
Professional layout creation using PDF standards for image generation
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from image_typography_config import typography_config
from image_layout_config import layout_config
from image_text_processor import text_processor

# Setup logging
log = logging.getLogger(__name__)

class ImageLayoutCreator:
    """Professional layout creation using PDF standards"""
    
    def __init__(self):
        """Initialize layout creator"""
        self.typography = typography_config
        self.layout = layout_config
        self.text_processor = text_processor
        self._font_cache = {}
    
    def create_question_image(self, image_path: str, question_text: str, 
                            theme: str, image_number: str) -> Image.Image:
        """Create question image using PDF layout standards"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Process question text
            lines = self.text_processor.process_text_for_image(question_text, 'question')
            font_size = self.text_processor.calculate_adaptive_font_size(question_text, 'question')
            font_config = self.text_processor.get_font_config('question')
            font = self._get_font(font_size, font_config['weight'])
            
            # Calculate position
            text_y = self.layout.calculate_text_position(lines, font_size, font_config['line_spacing'], True)
            text_x = self.layout.get_text_area_bounds(True)['start_x']
            
            # Draw text
            self._draw_text_with_styling(draw, lines, font, text_x, text_y, font_config)
            self._add_footer(draw, theme, image_number)
            
            return img
        except Exception as e:
            log.error(f"Error creating question image: {e}")
            return Image.open(image_path)
    
    def create_answer_image(self, image_path: str, answer_text: str, 
                          theme: str, image_number: str) -> Image.Image:
        """Create answer image using PDF layout standards"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Process answer text
            lines = self.text_processor.process_text_for_image(answer_text, 'answer')
            font_size = self.text_processor.calculate_adaptive_font_size(answer_text, 'answer')
            font_config = self.text_processor.get_font_config('answer')
            font = self._get_font(font_size, font_config['weight'])
            
            # Calculate position
            text_y = self.layout.calculate_text_position(lines, font_size, font_config['line_spacing'], False)
            text_x = self.layout.get_text_area_bounds(False)['start_x']
            
            # Draw text
            self._draw_text_with_styling(draw, lines, font, text_x, text_y, font_config)
            self._add_footer(draw, theme, image_number)
            
            return img
        except Exception as e:
            log.error(f"Error creating answer image: {e}")
            return Image.open(image_path)
    
    def _get_font(self, font_size: int, font_weight: str = 'normal') -> ImageFont.FreeTypeFont:
        """Get font with caching"""
        cache_key = f"{font_size}_{font_weight}"
        if cache_key not in self._font_cache:
            try:
                self._font_cache[cache_key] = ImageFont.load_default()
            except Exception as e:
                log.error(f"Error loading font: {e}")
                self._font_cache[cache_key] = ImageFont.load_default()
        return self._font_cache[cache_key]
    
    def _draw_text_with_styling(self, draw: ImageDraw.Draw, lines: List[str], 
                               font: ImageFont.FreeTypeFont, x: int, y: int, 
                               font_config: Dict[str, any]):
        """Draw text with PDF styling"""
        try:
            text_color = self.typography.get_color_rgb(font_config['color'])
            line_height = int(font_config['size'] * font_config['line_spacing'] * 1.2)
            
            current_y = y
            for line in lines:
                # Draw shadow
                draw.text((x + 2, current_y + 2), line, font=font, fill=(0, 0, 0))
                # Draw main text
                draw.text((x, current_y), line, font=font, fill=text_color)
                current_y += line_height
        except Exception as e:
            log.error(f"Error drawing text: {e}")
    
    def _add_footer(self, draw: ImageDraw.Draw, theme: str, image_number: str):
        """Add PDF-style footer"""
        try:
            footer_bounds = self.layout.get_footer_bounds()
            footer_color = self.typography.get_color_rgb(self.layout.FOOTER_BACKGROUND_COLOR)
            
            # Draw footer background
            draw.rectangle([
                footer_bounds['start_x'], footer_bounds['start_y'],
                footer_bounds['end_x'], footer_bounds['end_y']
            ], fill=footer_color)
            
            # Draw footer text
            footer_config = self.text_processor.get_font_config('footer')
            footer_font = self._get_font(footer_config['size'], footer_config['weight'])
            footer_color = self.typography.get_color_rgb(footer_config['color'])
            
            # Brand
            brand_x, brand_y = self.layout.get_brand_position()
            draw.text((brand_x, brand_y), self.layout.BRAND_TEXT, font=footer_font, fill=footer_color)
            
            # Theme
            category_x, category_y = self.layout.get_category_position()
            draw.text((category_x, category_y), theme.upper(), font=footer_font, fill=footer_color)
            
            # Image number
            number_x, number_y = self.layout.get_image_number_position()
            draw.text((number_x, number_y), f"#{image_number}", font=footer_font, fill=footer_color)
            
        except Exception as e:
            log.error(f"Error adding footer: {e}")

# Global layout creator instance
layout_creator = ImageLayoutCreator()
