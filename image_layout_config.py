#!/usr/bin/env python3
"""
Image Layout Configuration Module
Adapts PDF layout rules for professional image generation
"""

import os
from typing import Dict, Tuple

class ImageLayoutConfig:
    """Layout configuration for images using PDF standards"""
    
    def __init__(self):
        """Initialize layout configuration"""
        # Load configuration from environment variables
        self._load_configuration()
    
    def _load_configuration(self):
        """Load layout configuration from environment variables"""
        # Image dimensions (1072x1792 - Instagram story format)
        self.IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))
        self.IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))
        
        # Margins (scaled 2x from PDF 72pt to pixels for image clarity)
        self.MARGIN_LEFT = int(os.getenv('IMAGE_MARGIN_LEFT', '144'))      # 2x PDF margin
        self.MARGIN_RIGHT = int(os.getenv('IMAGE_MARGIN_RIGHT', '144'))
        self.MARGIN_TOP = int(os.getenv('IMAGE_MARGIN_TOP', '144'))
        self.MARGIN_BOTTOM = int(os.getenv('IMAGE_MARGIN_BOTTOM', '144'))
        
        # Text area positioning (adapted from PDF bottom-up approach)
        self.TEXT_AREA_START_Y = int(os.getenv('IMAGE_TEXT_AREA_START_Y', '80'))    # From top
        self.TEXT_AREA_END_Y = int(os.getenv('IMAGE_TEXT_AREA_END_Y', '400'))       # Above footer
        self.TEXT_AREA_START_X = self.MARGIN_LEFT
        self.TEXT_AREA_END_X = self.IMAGE_WIDTH - self.MARGIN_RIGHT
        
        # Footer configuration (adapted from PDF)
        self.FOOTER_HEIGHT = int(os.getenv('IMAGE_FOOTER_HEIGHT', '160'))           # 2x PDF footer height
        self.FOOTER_START_Y = self.IMAGE_HEIGHT - self.FOOTER_HEIGHT
        self.FOOTER_PADDING = int(os.getenv('IMAGE_FOOTER_PADDING', '20'))
        self.FOOTER_BACKGROUND_COLOR = os.getenv('IMAGE_FOOTER_BG_COLOR', '#2C3E50')
        self.FOOTER_BACKGROUND_ALPHA = float(os.getenv('IMAGE_FOOTER_BG_ALPHA', '0.9'))
        
        # Brand positioning (adapted from PDF)
        self.BRAND_Y_OFFSET = int(os.getenv('IMAGE_BRAND_Y_OFFSET', '200'))         # From bottom
        self.BRAND_X_OFFSET = int(os.getenv('IMAGE_BRAND_X_OFFSET', '144'))         # From left
        self.BRAND_TEXT = os.getenv('IMAGE_BRAND_TEXT', 'ASK')
        
        # Category and image number positioning
        self.CATEGORY_Y_OFFSET = int(os.getenv('IMAGE_CATEGORY_Y_OFFSET', '120'))   # From bottom
        self.IMAGE_NUMBER_Y_OFFSET = int(os.getenv('IMAGE_NUMBER_Y_OFFSET', '80'))  # From bottom
        self.IMAGE_NUMBER_X_OFFSET = int(os.getenv('IMAGE_NUMBER_X_OFFSET', '800')) # From right
        
        # Gradient overlay configuration
        self.GRADIENT_START_Y = int(os.getenv('IMAGE_GRADIENT_START_Y', '0'))
        self.GRADIENT_END_Y = int(os.getenv('IMAGE_GRADIENT_END_Y', '600'))
        self.GRADIENT_START_COLOR = os.getenv('IMAGE_GRADIENT_START_COLOR', '#000000')
        self.GRADIENT_END_COLOR = os.getenv('IMAGE_GRADIENT_END_COLOR', '#000000')
        self.GRADIENT_START_ALPHA = float(os.getenv('IMAGE_GRADIENT_START_ALPHA', '0.8'))
        self.GRADIENT_END_ALPHA = float(os.getenv('IMAGE_GRADIENT_END_ALPHA', '0.0'))
        
        # Text positioning offsets
        self.TEXT_OFFSET_X = int(os.getenv('IMAGE_TEXT_OFFSET_X', '0'))
        self.TEXT_OFFSET_Y = int(os.getenv('IMAGE_TEXT_OFFSET_Y', '0'))
        
        # Question vs Answer positioning differences
        self.QUESTION_OFFSET_Y = int(os.getenv('IMAGE_QUESTION_OFFSET_Y', '100'))   # Questions higher
        self.ANSWER_OFFSET_Y = int(os.getenv('IMAGE_ANSWER_OFFSET_Y', '50'))        # Answers lower
        
        # Text wrapping configuration (adapted from PDF)
        self.TEXT_WRAP_WIDTH_QUESTION = int(os.getenv('IMAGE_TEXT_WRAP_WIDTH_QUESTION', '50'))
        self.TEXT_WRAP_WIDTH_ANSWER = int(os.getenv('IMAGE_TEXT_WRAP_WIDTH_ANSWER', '60'))
        self.TEXT_WRAP_WIDTH_TITLE = int(os.getenv('IMAGE_TEXT_WRAP_WIDTH_TITLE', '40'))
        
        # Line spacing multipliers
        self.LINE_SPACING_MULTIPLIER = float(os.getenv('IMAGE_LINE_SPACING_MULTIPLIER', '1.2'))
        self.PARAGRAPH_SPACING = int(os.getenv('IMAGE_PARAGRAPH_SPACING', '20'))
    
    def get_text_area_bounds(self, is_question: bool = True) -> Dict[str, int]:
        """
        Get text area bounds for question or answer
        
        Args:
            is_question: True for question, False for answer
            
        Returns:
            Dictionary with text area bounds
        """
        if is_question:
            start_y = self.TEXT_AREA_START_Y + self.QUESTION_OFFSET_Y
        else:
            start_y = self.TEXT_AREA_START_Y + self.ANSWER_OFFSET_Y
        
        return {
            'start_x': self.TEXT_AREA_START_X + self.TEXT_OFFSET_X,
            'end_x': self.TEXT_AREA_END_X + self.TEXT_OFFSET_X,
            'start_y': start_y + self.TEXT_OFFSET_Y,
            'end_y': self.TEXT_AREA_END_Y + self.TEXT_OFFSET_Y
        }
    
    def get_footer_bounds(self) -> Dict[str, int]:
        """
        Get footer area bounds
        
        Returns:
            Dictionary with footer bounds
        """
        return {
            'start_x': 0,
            'end_x': self.IMAGE_WIDTH,
            'start_y': self.FOOTER_START_Y,
            'end_y': self.IMAGE_HEIGHT
        }
    
    def get_brand_position(self) -> Tuple[int, int]:
        """
        Get brand text position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        x = self.BRAND_X_OFFSET
        y = self.IMAGE_HEIGHT - self.BRAND_Y_OFFSET
        return (x, y)
    
    def get_category_position(self) -> Tuple[int, int]:
        """
        Get category text position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        x = self.BRAND_X_OFFSET
        y = self.IMAGE_HEIGHT - self.CATEGORY_Y_OFFSET
        return (x, y)
    
    def get_image_number_position(self) -> Tuple[int, int]:
        """
        Get image number position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        x = self.IMAGE_WIDTH - self.IMAGE_NUMBER_X_OFFSET
        y = self.IMAGE_HEIGHT - self.IMAGE_NUMBER_Y_OFFSET
        return (x, y)
    
    def get_gradient_bounds(self) -> Dict[str, int]:
        """
        Get gradient overlay bounds
        
        Returns:
            Dictionary with gradient bounds
        """
        return {
            'start_x': 0,
            'end_x': self.IMAGE_WIDTH,
            'start_y': self.GRADIENT_START_Y,
            'end_y': self.GRADIENT_END_Y
        }
    
    def calculate_text_position(self, lines: list, font_size: int, line_spacing: float, 
                               is_question: bool = True) -> int:
        """
        Calculate optimal text Y position using PDF-style bottom-up approach
        
        Args:
            lines: List of text lines
            font_size: Font size in pixels
            line_spacing: Line spacing multiplier
            is_question: True for question, False for answer
            
        Returns:
            Y position for text placement
        """
        # Get text area bounds
        bounds = self.get_text_area_bounds(is_question)
        
        # Calculate total text height
        line_height = int(font_size * line_spacing * self.LINE_SPACING_MULTIPLIER)
        total_text_height = len(lines) * line_height
        
        # Position text from bottom of text area (PDF-style)
        text_y = bounds['end_y'] - total_text_height
        
        # Ensure text doesn't go above text area start
        if text_y < bounds['start_y']:
            text_y = bounds['start_y']
        
        return text_y
    
    def get_text_wrap_width(self, text_type: str = 'question') -> int:
        """
        Get text wrap width for specific text type
        
        Args:
            text_type: Type of text ('question', 'answer', 'title')
            
        Returns:
            Wrap width in characters
        """
        wrap_widths = {
            'question': self.TEXT_WRAP_WIDTH_QUESTION,
            'answer': self.TEXT_WRAP_WIDTH_ANSWER,
            'title': self.TEXT_WRAP_WIDTH_TITLE
        }
        
        return wrap_widths.get(text_type, self.TEXT_WRAP_WIDTH_QUESTION)
    
    def get_margins(self) -> Dict[str, int]:
        """
        Get margin configuration
        
        Returns:
            Dictionary with margin values
        """
        return {
            'left': self.MARGIN_LEFT,
            'right': self.MARGIN_RIGHT,
            'top': self.MARGIN_TOP,
            'bottom': self.MARGIN_BOTTOM
        }
    
    def get_image_dimensions(self) -> Tuple[int, int]:
        """
        Get image dimensions
        
        Returns:
            Tuple of (width, height)
        """
        return (self.IMAGE_WIDTH, self.IMAGE_HEIGHT)

# Global layout configuration instance
layout_config = ImageLayoutConfig()
