#!/usr/bin/env python3
"""
Image Typography Configuration Module
Adapts PDF typography rules for professional image generation
"""

import os
from typing import Dict, Tuple

class ImageTypographyConfig:
    """Typography configuration for images using PDF standards"""
    
    def __init__(self):
        """Initialize typography configuration"""
        # Load configuration from environment variables
        self._load_configuration()
    
    def _load_configuration(self):
        """Load typography configuration from environment variables"""
        # Font sizes (scaled 2x from PDF for image clarity at 1072x1792 resolution)
        self.FONT_SIZE_TITLE = int(os.getenv('IMAGE_FONT_SIZE_TITLE', '96'))        # 2x PDF size
        self.FONT_SIZE_SUBTITLE = int(os.getenv('IMAGE_FONT_SIZE_SUBTITLE', '48'))  # 2x PDF size
        self.FONT_SIZE_SECTION = int(os.getenv('IMAGE_FONT_SIZE_SECTION', '32'))    # 2x PDF size
        self.FONT_SIZE_ENTRY = int(os.getenv('IMAGE_FONT_SIZE_ENTRY', '28'))        # 2x PDF size
        self.FONT_SIZE_QUESTION = int(os.getenv('IMAGE_FONT_SIZE_QUESTION', '24'))  # 2x PDF size
        self.FONT_SIZE_DETAIL = int(os.getenv('IMAGE_FONT_SIZE_DETAIL', '20'))      # 2x PDF size
        self.FONT_SIZE_FOOTER = int(os.getenv('IMAGE_FONT_SIZE_FOOTER', '16'))      # 2x PDF size
        
        # Font families (adapted from PDF)
        self.FONT_FAMILY_PRIMARY = os.getenv('IMAGE_FONT_FAMILY_PRIMARY', 'Helvetica')
        self.FONT_FAMILY_SECONDARY = os.getenv('IMAGE_FONT_FAMILY_SECONDARY', 'Times-Roman')
        self.FONT_FAMILY_MONOSPACE = os.getenv('IMAGE_FONT_FAMILY_MONOSPACE', 'Courier')
        
        # Font weights
        self.FONT_WEIGHT_NORMAL = os.getenv('IMAGE_FONT_WEIGHT_NORMAL', 'normal')
        self.FONT_WEIGHT_BOLD = os.getenv('IMAGE_FONT_WEIGHT_BOLD', 'bold')
        self.FONT_WEIGHT_ITALIC = os.getenv('IMAGE_FONT_WEIGHT_ITALIC', 'italic')
        
        # Colors (adapted from PDF for image overlays)
        self.COLOR_PRIMARY = os.getenv('IMAGE_COLOR_PRIMARY', '#FFFFFF')           # White for dark overlays
        self.COLOR_SECONDARY = os.getenv('IMAGE_COLOR_SECONDARY', '#F0F0F0')       # Light gray
        self.COLOR_ACCENT = os.getenv('IMAGE_COLOR_ACCENT', '#E74C3C')             # Red accent
        self.COLOR_THEME_HEADER = os.getenv('IMAGE_COLOR_THEME_HEADER', '#8E44AD')  # Purple
        self.COLOR_BRAND = os.getenv('IMAGE_COLOR_BRAND', '#34495E')               # Brand blue
        self.COLOR_FOOTER_TEXT = os.getenv('IMAGE_COLOR_FOOTER_TEXT', '#FFFFFF')   # White footer text
        self.COLOR_FOOTER_BG = os.getenv('IMAGE_COLOR_FOOTER_BG', '#2C3E50')       # Dark footer background
        
        # Line spacing (adapted from PDF)
        self.LINE_SPACING_SINGLE = float(os.getenv('IMAGE_LINE_SPACING_SINGLE', '1.0'))
        self.LINE_SPACING_ONE_HALF = float(os.getenv('IMAGE_LINE_SPACING_ONE_HALF', '1.5'))
        self.LINE_SPACING_DOUBLE = float(os.getenv('IMAGE_LINE_SPACING_DOUBLE', '2.0'))
        self.LINE_SPACING_TRIPLE = float(os.getenv('IMAGE_LINE_SPACING_TRIPLE', '3.0'))
        
        # Character spacing
        self.CHAR_SPACING_NORMAL = float(os.getenv('IMAGE_CHAR_SPACING_NORMAL', '0.0'))
        self.CHAR_SPACING_WIDE = float(os.getenv('IMAGE_CHAR_SPACING_WIDE', '2.0'))
        self.CHAR_SPACING_TIGHT = float(os.getenv('IMAGE_CHAR_SPACING_TIGHT', '-1.0'))
    
    def get_font_config(self, font_type: str = 'question') -> Dict[str, any]:
        """
        Get font configuration for specific text type
        
        Args:
            font_type: Type of text ('title', 'subtitle', 'section', 'entry', 'question', 'detail', 'footer')
            
        Returns:
            Dictionary with font configuration
        """
        configs = {
            'title': {
                'size': self.FONT_SIZE_TITLE,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_BOLD,
                'color': self.COLOR_PRIMARY,
                'line_spacing': self.LINE_SPACING_DOUBLE,
                'char_spacing': self.CHAR_SPACING_WIDE
            },
            'subtitle': {
                'size': self.FONT_SIZE_SUBTITLE,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_BOLD,
                'color': self.COLOR_SECONDARY,
                'line_spacing': self.LINE_SPACING_ONE_HALF,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'section': {
                'size': self.FONT_SIZE_SECTION,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_BOLD,
                'color': self.COLOR_THEME_HEADER,
                'line_spacing': self.LINE_SPACING_ONE_HALF,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'entry': {
                'size': self.FONT_SIZE_ENTRY,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_NORMAL,
                'color': self.COLOR_PRIMARY,
                'line_spacing': self.LINE_SPACING_SINGLE,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'question': {
                'size': self.FONT_SIZE_QUESTION,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_BOLD,
                'color': self.COLOR_PRIMARY,
                'line_spacing': self.LINE_SPACING_ONE_HALF,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'answer': {
                'size': self.FONT_SIZE_ENTRY,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_NORMAL,
                'color': self.COLOR_PRIMARY,
                'line_spacing': self.LINE_SPACING_SINGLE,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'detail': {
                'size': self.FONT_SIZE_DETAIL,
                'family': self.FONT_FAMILY_SECONDARY,
                'weight': self.FONT_WEIGHT_NORMAL,
                'color': self.COLOR_SECONDARY,
                'line_spacing': self.LINE_SPACING_SINGLE,
                'char_spacing': self.CHAR_SPACING_NORMAL
            },
            'footer': {
                'size': self.FONT_SIZE_FOOTER,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_NORMAL,
                'color': self.COLOR_FOOTER_TEXT,
                'line_spacing': self.LINE_SPACING_SINGLE,
                'char_spacing': self.CHAR_SPACING_NORMAL
            }
        }
        
        return configs.get(font_type, configs['question'])
    
    def calculate_adaptive_font_size(self, text: str, base_font_type: str = 'question') -> int:
        """
        Calculate adaptive font size based on text length (PDF-style scaling)
        
        Args:
            text: Text content
            base_font_type: Base font type for scaling
            
        Returns:
            Adaptive font size
        """
        base_config = self.get_font_config(base_font_type)
        base_size = base_config['size']
        text_length = len(text)
        
        # Apply PDF-style scaling logic
        if text_length > 300:
            return int(base_size * 0.7)  # Much smaller for very long text
        elif text_length > 200:
            return int(base_size * 0.8)  # Smaller for long text
        elif text_length > 100:
            return int(base_size * 0.9)  # Slightly smaller for medium text
        elif text_length < 30:
            return int(base_size * 1.2)  # Larger for short text
        elif text_length < 50:
            return int(base_size * 1.1)  # Slightly larger for short text
        else:
            return base_size  # Default size for medium text
    
    def get_color_rgb(self, color_hex: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple
        
        Args:
            color_hex: Hex color string (e.g., '#FFFFFF')
            
        Returns:
            RGB tuple (r, g, b)
        """
        color_hex = color_hex.lstrip('#')
        return tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    def get_color_rgba(self, color_hex: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
        """
        Convert hex color to RGBA tuple
        
        Args:
            color_hex: Hex color string (e.g., '#FFFFFF')
            alpha: Alpha value (0.0 to 1.0)
            
        Returns:
            RGBA tuple (r, g, b, a)
        """
        rgb = self.get_color_rgb(color_hex)
        return rgb + (int(255 * alpha),)

# Global typography configuration instance
typography_config = ImageTypographyConfig()
