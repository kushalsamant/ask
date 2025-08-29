#!/usr/bin/env python3
"""
Image Typography Configuration Module - Optimized Version 2.0
Enhanced typography configuration with improved performance and error handling

This module provides functionality to:
- Configure typography settings for professional image generation
- Load configuration from environment variables with validation
- Calculate adaptive font sizes based on text length
- Convert color formats (hex to RGB/RGBA)
- Provide font configurations for different text types
- Handle various font families, weights, and spacing options
- Support PDF-style typography rules for image clarity

Optimizations:
- Enhanced error handling and input validation
- Performance monitoring and statistics
- Better environment variable handling
- Improved color conversion accuracy
- Thread-safe operations
- Memory-efficient configuration management
- Enhanced font size calculation algorithms

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized)
"""

import os
import logging
import time
from typing import Dict, Tuple, Any, Optional
from functools import wraps, lru_cache
from threading import Lock

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_font_configs': 0,
    'total_font_calculations': 0,
    'total_color_conversions': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'total_time': 0.0,
    'last_reset': time.time()
}
_performance_lock = Lock()

def performance_monitor(func):
    """Decorator to monitor function performance with thread safety"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            with _performance_lock:
                _performance_stats['total_time'] += duration
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            with _performance_lock:
                _performance_stats['total_time'] += duration
            
            raise
    
    return wrapper

def validate_input_parameters(font_type: str = 'question') -> Tuple[bool, str]:
    """
    Validate input parameters for typography operations
    
    Args:
        font_type: Type of font to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not font_type or not isinstance(font_type, str):
        return False, "Font type must be a non-empty string"
    
    valid_font_types = ['title', 'subtitle', 'section', 'entry', 'question', 'answer', 'detail', 'footer']
    if font_type not in valid_font_types:
        return False, f"Font type must be one of: {valid_font_types}"
    
    return True, ""

def safe_int_conversion(value: str, default: int) -> int:
    """
    Safely convert string to integer with fallback
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        int: Converted value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        log.warning(f"Invalid integer value '{value}', using default {default}")
        return default

def safe_float_conversion(value: str, default: float) -> float:
    """
    Safely convert string to float with fallback
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        float: Converted value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        log.warning(f"Invalid float value '{value}', using default {default}")
        return default

class ImageTypographyConfig:
    """Enhanced typography configuration for images using PDF standards"""
    
    def __init__(self):
        """Initialize typography configuration with enhanced error handling"""
        # Performance monitoring
        self._initialization_time = time.time()
        self._last_operation_time = None
        
        # Load configuration from environment variables
        self._load_configuration()
        
        log.info("ImageTypographyConfig initialized successfully")
    
    def _load_configuration(self):
        """Load typography configuration from environment variables with validation"""
        try:
            # Font sizes (scaled 2x from PDF for image clarity at 1072x1792 resolution)
            self.FONT_SIZE_TITLE = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_TITLE', '96'), 96)
            self.FONT_SIZE_SUBTITLE = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_SUBTITLE', '48'), 48)
            self.FONT_SIZE_SECTION = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_SECTION', '32'), 32)
            self.FONT_SIZE_ENTRY = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_ENTRY', '28'), 28)
            self.FONT_SIZE_QUESTION = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_QUESTION', '24'), 24)
            self.FONT_SIZE_DETAIL = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_DETAIL', '20'), 20)
            self.FONT_SIZE_FOOTER = safe_int_conversion(
                os.getenv('IMAGE_FONT_SIZE_FOOTER', '16'), 16)
            
            # Font families (adapted from PDF)
            self.FONT_FAMILY_PRIMARY = os.getenv('IMAGE_FONT_FAMILY_PRIMARY', 'Helvetica')
            self.FONT_FAMILY_SECONDARY = os.getenv('IMAGE_FONT_FAMILY_SECONDARY', 'Times-Roman')
            self.FONT_FAMILY_MONOSPACE = os.getenv('IMAGE_FONT_FAMILY_MONOSPACE', 'Courier')
            
            # Font weights
            self.FONT_WEIGHT_NORMAL = os.getenv('IMAGE_FONT_WEIGHT_NORMAL', 'normal')
            self.FONT_WEIGHT_BOLD = os.getenv('IMAGE_FONT_WEIGHT_BOLD', 'bold')
            self.FONT_WEIGHT_ITALIC = os.getenv('IMAGE_FONT_WEIGHT_ITALIC', 'italic')
            
            # Colors (adapted from PDF for image overlays)
            self.COLOR_PRIMARY = os.getenv('IMAGE_COLOR_PRIMARY', '#FFFFFF')
            self.COLOR_SECONDARY = os.getenv('IMAGE_COLOR_SECONDARY', '#F0F0F0')
            self.COLOR_ACCENT = os.getenv('IMAGE_COLOR_ACCENT', '#E74C3C')
            self.COLOR_THEME_HEADER = os.getenv('IMAGE_COLOR_THEME_HEADER', '#8E44AD')
            self.COLOR_BRAND = os.getenv('IMAGE_COLOR_BRAND', '#34495E')
            self.COLOR_FOOTER_TEXT = os.getenv('IMAGE_COLOR_FOOTER_TEXT', '#FFFFFF')
            self.COLOR_FOOTER_BG = os.getenv('IMAGE_COLOR_FOOTER_BG', '#2C3E50')
            
            # Line spacing (adapted from PDF)
            self.LINE_SPACING_SINGLE = safe_float_conversion(
                os.getenv('IMAGE_LINE_SPACING_SINGLE', '1.0'), 1.0)
            self.LINE_SPACING_ONE_HALF = safe_float_conversion(
                os.getenv('IMAGE_LINE_SPACING_ONE_HALF', '1.5'), 1.5)
            self.LINE_SPACING_DOUBLE = safe_float_conversion(
                os.getenv('IMAGE_LINE_SPACING_DOUBLE', '2.0'), 2.0)
            self.LINE_SPACING_TRIPLE = safe_float_conversion(
                os.getenv('IMAGE_LINE_SPACING_TRIPLE', '3.0'), 3.0)
            
            # Character spacing
            self.CHAR_SPACING_NORMAL = safe_float_conversion(
                os.getenv('IMAGE_CHAR_SPACING_NORMAL', '0.0'), 0.0)
            self.CHAR_SPACING_WIDE = safe_float_conversion(
                os.getenv('IMAGE_CHAR_SPACING_WIDE', '2.0'), 2.0)
            self.CHAR_SPACING_TIGHT = safe_float_conversion(
                os.getenv('IMAGE_CHAR_SPACING_TIGHT', '-1.0'), -1.0)
            
            # Validate configuration
            self._validate_configuration()
            
        except Exception as e:
            log.error(f"Error loading configuration: {e}")
            self._load_default_configuration()
    
    def _validate_configuration(self):
        """Validate loaded configuration values"""
        # Validate font sizes are positive
        font_sizes = [
            self.FONT_SIZE_TITLE, self.FONT_SIZE_SUBTITLE, self.FONT_SIZE_SECTION,
            self.FONT_SIZE_ENTRY, self.FONT_SIZE_QUESTION, self.FONT_SIZE_DETAIL,
            self.FONT_SIZE_FOOTER
        ]
        
        for size in font_sizes:
            if size <= 0:
                raise ValueError(f"Font size must be positive, got {size}")
        
        # Validate font size hierarchy
        if not (self.FONT_SIZE_TITLE > self.FONT_SIZE_SUBTITLE > self.FONT_SIZE_SECTION > 
                self.FONT_SIZE_ENTRY > self.FONT_SIZE_QUESTION > self.FONT_SIZE_DETAIL > 
                self.FONT_SIZE_FOOTER):
            log.warning("Font size hierarchy may not be optimal")
        
        # Validate colors are valid hex strings
        colors = [
            self.COLOR_PRIMARY, self.COLOR_SECONDARY, self.COLOR_ACCENT,
            self.COLOR_THEME_HEADER, self.COLOR_BRAND, self.COLOR_FOOTER_TEXT,
            self.COLOR_FOOTER_BG
        ]
        
        for color in colors:
            if not self._is_valid_hex_color(color):
                log.warning(f"Invalid hex color format: {color}")
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """
        Check if color string is a valid hex color
        
        Args:
            color: Color string to validate
            
        Returns:
            bool: True if valid hex color
        """
        if not color or not isinstance(color, str):
            return False
        
        if not color.startswith('#'):
            return False
        
        if len(color) != 7:  # #RRGGBB format
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def _load_default_configuration(self):
        """Load default configuration when environment loading fails"""
        log.info("Loading default configuration")
        
        # Default font sizes
        self.FONT_SIZE_TITLE = 96
        self.FONT_SIZE_SUBTITLE = 48
        self.FONT_SIZE_SECTION = 32
        self.FONT_SIZE_ENTRY = 28
        self.FONT_SIZE_QUESTION = 24
        self.FONT_SIZE_DETAIL = 20
        self.FONT_SIZE_FOOTER = 16
        
        # Default font families
        self.FONT_FAMILY_PRIMARY = 'Helvetica'
        self.FONT_FAMILY_SECONDARY = 'Times-Roman'
        self.FONT_FAMILY_MONOSPACE = 'Courier'
        
        # Default font weights
        self.FONT_WEIGHT_NORMAL = 'normal'
        self.FONT_WEIGHT_BOLD = 'bold'
        self.FONT_WEIGHT_ITALIC = 'italic'
        
        # Default colors
        self.COLOR_PRIMARY = '#FFFFFF'
        self.COLOR_SECONDARY = '#F0F0F0'
        self.COLOR_ACCENT = '#E74C3C'
        self.COLOR_THEME_HEADER = '#8E44AD'
        self.COLOR_BRAND = '#34495E'
        self.COLOR_FOOTER_TEXT = '#FFFFFF'
        self.COLOR_FOOTER_BG = '#2C3E50'
        
        # Default line spacing
        self.LINE_SPACING_SINGLE = 1.0
        self.LINE_SPACING_ONE_HALF = 1.5
        self.LINE_SPACING_DOUBLE = 2.0
        self.LINE_SPACING_TRIPLE = 3.0
        
        # Default character spacing
        self.CHAR_SPACING_NORMAL = 0.0
        self.CHAR_SPACING_WIDE = 2.0
        self.CHAR_SPACING_TIGHT = -1.0
    
    @performance_monitor
    @lru_cache(maxsize=128)
    def get_font_config(self, font_type: str = 'question') -> Dict[str, Any]:
        """
        Get font configuration for specific text type with caching
        
        Args:
            font_type: Type of text ('title', 'subtitle', 'section', 'entry', 'question', 'answer', 'detail', 'footer')
            
        Returns:
            Dictionary with font configuration
        """
        try:
            # Validate input
            is_valid, error_msg = validate_input_parameters(font_type)
            if not is_valid:
                log.error(f"Invalid font type: {error_msg}")
                font_type = 'question'  # Use default
            
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
            
            result = configs.get(font_type, configs['question'])
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_font_configs'] += 1
            
            self._last_operation_time = time.time()
            return result
            
        except Exception as e:
            log.error(f"Error getting font config: {e}")
            # Return basic fallback configuration
            return {
                'size': self.FONT_SIZE_QUESTION,
                'family': self.FONT_FAMILY_PRIMARY,
                'weight': self.FONT_WEIGHT_NORMAL,
                'color': self.COLOR_PRIMARY,
                'line_spacing': self.LINE_SPACING_SINGLE,
                'char_spacing': self.CHAR_SPACING_NORMAL
            }
    
    @performance_monitor
    def calculate_adaptive_font_size(self, text: str, base_font_type: str = 'question') -> int:
        """
        Calculate adaptive font size based on text length with enhanced algorithm
        
        Args:
            text: Text content
            base_font_type: Base font type for scaling
            
        Returns:
            Adaptive font size
        """
        try:
            # Validate inputs
            if not text or not isinstance(text, str):
                log.warning("Invalid text input, using base font size")
                base_config = self.get_font_config(base_font_type)
                return base_config['size']
            
            base_config = self.get_font_config(base_font_type)
            base_size = base_config['size']
            text_length = len(text)
            
            # Enhanced PDF-style scaling logic with better precision
            if text_length > 300:
                return max(int(base_size * 0.7), 8)  # Much smaller for very long text
            elif text_length > 200:
                return max(int(base_size * 0.8), 10)  # Smaller for long text
            elif text_length > 100:
                return max(int(base_size * 0.9), 12)  # Slightly smaller for medium text
            elif text_length < 30:
                return min(int(base_size * 1.2), 72)  # Larger for short text
            elif text_length < 50:
                return min(int(base_size * 1.1), 60)  # Slightly larger for short text
            else:
                return base_size  # Default size for medium text
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_font_calculations'] += 1
                
        except Exception as e:
            log.error(f"Error calculating adaptive font size: {e}")
            # Return safe fallback
            return 24
    
    @performance_monitor
    def get_color_rgb(self, color_hex: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple with enhanced validation
        
        Args:
            color_hex: Hex color string (e.g., '#FFFFFF')
            
        Returns:
            RGB tuple (r, g, b)
        """
        try:
            if not color_hex or not isinstance(color_hex, str):
                log.warning("Invalid color input, using default white")
                return (255, 255, 255)
            
            # Remove hash if present
            color_hex = color_hex.lstrip('#')
            
            # Validate hex string
            if len(color_hex) != 6:
                log.warning(f"Invalid hex color length: {color_hex}")
                return (255, 255, 255)
            
            # Convert to RGB
            rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            # Validate RGB values
            for component in rgb:
                if not (0 <= component <= 255):
                    log.warning(f"Invalid RGB component: {component}")
                    return (255, 255, 255)
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_color_conversions'] += 1
            
            return rgb
            
        except Exception as e:
            log.error(f"Error converting color to RGB: {e}")
            return (255, 255, 255)  # Default to white
    
    @performance_monitor
    def get_color_rgba(self, color_hex: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
        """
        Convert hex color to RGBA tuple with enhanced precision
        
        Args:
            color_hex: Hex color string (e.g., '#FFFFFF')
            alpha: Alpha value (0.0 to 1.0)
            
        Returns:
            RGBA tuple (r, g, b, a)
        """
        try:
            # Validate alpha value
            if not isinstance(alpha, (int, float)) or not (0.0 <= alpha <= 1.0):
                log.warning(f"Invalid alpha value: {alpha}, using 1.0")
                alpha = 1.0
            
            # Get RGB values
            rgb = self.get_color_rgb(color_hex)
            
            # Calculate alpha with proper rounding
            alpha_value = int(round(255 * alpha))
            
            # Ensure alpha is within bounds
            alpha_value = max(0, min(255, alpha_value))
            
            return rgb + (alpha_value,)
            
        except Exception as e:
            log.error(f"Error converting color to RGBA: {e}")
            return (255, 255, 255, 255)  # Default to white with full opacity
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for the typography configuration
        
        Returns:
            dict: Performance statistics
        """
        with _performance_lock:
            total_operations = (_performance_stats['total_font_configs'] + 
                              _performance_stats['total_font_calculations'] + 
                              _performance_stats['total_color_conversions'])
            
            return {
                'total_font_configs': _performance_stats['total_font_configs'],
                'total_font_calculations': _performance_stats['total_font_calculations'],
                'total_color_conversions': _performance_stats['total_color_conversions'],
                'cache_hits': _performance_stats['cache_hits'],
                'cache_misses': _performance_stats['cache_misses'],
                'cache_hit_ratio': _performance_stats['cache_hits'] / max(_performance_stats['cache_hits'] + _performance_stats['cache_misses'], 1),
                'total_time': _performance_stats['total_time'],
                'average_time_per_operation': _performance_stats['total_time'] / max(total_operations, 1),
                'initialization_time': self._initialization_time,
                'last_operation_time': self._last_operation_time,
                'module_version': '2.0',
                'optimization_date': '2025-08-24'
            }
    
    def reset_performance_stats(self):
        """Reset performance statistics with thread safety"""
        global _performance_stats
        with _performance_lock:
            _performance_stats = {
                'total_font_configs': 0,
                'total_font_calculations': 0,
                'total_color_conversions': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_time': 0.0,
                'last_reset': time.time()
            }
        log.info("Performance statistics reset")
    
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate the environment configuration
        
        Returns:
            dict: Environment validation results
        """
        validation_results = {
            'font_sizes': {
                'title': self.FONT_SIZE_TITLE,
                'subtitle': self.FONT_SIZE_SUBTITLE,
                'section': self.FONT_SIZE_SECTION,
                'entry': self.FONT_SIZE_ENTRY,
                'question': self.FONT_SIZE_QUESTION,
                'detail': self.FONT_SIZE_DETAIL,
                'footer': self.FONT_SIZE_FOOTER
            },
            'font_families': {
                'primary': self.FONT_FAMILY_PRIMARY,
                'secondary': self.FONT_FAMILY_SECONDARY,
                'monospace': self.FONT_FAMILY_MONOSPACE
            },
            'colors': {
                'primary': self.COLOR_PRIMARY,
                'secondary': self.COLOR_SECONDARY,
                'accent': self.COLOR_ACCENT,
                'theme_header': self.COLOR_THEME_HEADER,
                'brand': self.COLOR_BRAND,
                'footer_text': self.COLOR_FOOTER_TEXT,
                'footer_bg': self.COLOR_FOOTER_BG
            },
            'line_spacing': {
                'single': self.LINE_SPACING_SINGLE,
                'one_half': self.LINE_SPACING_ONE_HALF,
                'double': self.LINE_SPACING_DOUBLE,
                'triple': self.LINE_SPACING_TRIPLE
            },
            'performance': {
                'initialization_time': self._initialization_time,
                'last_operation_time': self._last_operation_time,
                'total_operations': _performance_stats['total_font_configs'] + _performance_stats['total_font_calculations']
            }
        }
        
        return validation_results

# Global typography configuration instance
typography_config = ImageTypographyConfig()

# Convenience functions with performance monitoring
@performance_monitor
def get_font_config(font_type: str = 'question') -> Dict[str, Any]:
    """Get font configuration with performance monitoring"""
    return typography_config.get_font_config(font_type)

@performance_monitor
def calculate_adaptive_font_size(text: str, base_font_type: str = 'question') -> int:
    """Calculate adaptive font size with performance monitoring"""
    return typography_config.calculate_adaptive_font_size(text, base_font_type)

@performance_monitor
def get_color_rgb(color_hex: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB with performance monitoring"""
    return typography_config.get_color_rgb(color_hex)

@performance_monitor
def get_color_rgba(color_hex: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA with performance monitoring"""
    return typography_config.get_color_rgba(color_hex, alpha)

def get_performance_statistics() -> Dict[str, Any]:
    """Get performance statistics"""
    return typography_config.get_performance_statistics()

def reset_performance_stats():
    """Reset performance statistics"""
    typography_config.reset_performance_stats()

def validate_environment() -> Dict[str, Any]:
    """Validate environment"""
    return typography_config.validate_environment()

# Export main functions
__all__ = [
    'ImageTypographyConfig',
    'get_font_config',
    'calculate_adaptive_font_size',
    'get_color_rgb',
    'get_color_rgba',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
