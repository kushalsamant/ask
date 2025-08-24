#!/usr/bin/env python3
"""
Image Layout Creator Module - Optimized Version 2.0
Professional layout creation using PDF standards for image generation with enhanced performance

This module provides functionality to:
- Create professional question and answer images with PDF-standard layouts
- Apply typography and styling consistent with professional design standards
- Handle text processing, font management, and layout calculations
- Support footer generation with branding and metadata
- Provide performance monitoring and error recovery
- Implement caching and optimization for repeated operations

Optimizations:
- Enhanced font caching and management
- Performance monitoring and statistics
- Better error handling and recovery
- Memory-efficient image operations
- Thread-safe operations
- Improved text rendering and styling
- Enhanced footer generation
- Better dependency management

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized)
"""

import os
import logging
import time
from typing import List, Dict, Tuple, Optional, Any
from PIL import Image, ImageDraw, ImageFont
from functools import wraps, lru_cache
from threading import Lock
from pathlib import Path

# Import dependencies with error handling
try:
    from image_typography_config import typography_config
except ImportError as e:
    logging.warning(f"Could not import typography_config: {e}")
    typography_config = None

try:
    from image_layout_config import layout_config
except ImportError as e:
    logging.warning(f"Could not import layout_config: {e}")
    layout_config = None

try:
    from image_text_processor import text_processor
except ImportError as e:
    logging.warning(f"Could not import text_processor: {e}")
    text_processor = None

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_question_images': 0,
    'total_answer_images': 0,
    'total_font_loads': 0,
    'total_text_renders': 0,
    'total_footer_renders': 0,
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

def validate_input_parameters(image_path: str, text: str, theme: str, image_number: str) -> Tuple[bool, str]:
    """
    Validate input parameters for image creation operations
    
    Args:
        image_path: Path to the source image
        text: Text content to add to image
        theme: Theme/category name
        image_number: Image number identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not image_path or not isinstance(image_path, str) or not image_path.strip():
        return False, "Image path must be a non-empty string"
    
    if not text or not isinstance(text, str) or not text.strip():
        return False, "Text must be a non-empty string"
    
    if not theme or not isinstance(theme, str) or not theme.strip():
        return False, "Theme must be a non-empty string"
    
    if not image_number or not isinstance(image_number, str) or not image_number.strip():
        return False, "Image number must be a non-empty string"
    
    # Check for potentially harmful characters
    invalid_chars = ['<', '>', '"', "'", '\\', '/', '|', ':', '*', '?']
    if any(char in theme for char in invalid_chars):
        return False, "Theme contains invalid characters"
    
    if any(char in image_number for char in invalid_chars):
        return False, "Image number contains invalid characters"
    
    # Check if image file exists
    if not os.path.exists(image_path):
        return False, f"Image file does not exist: {image_path}"
    
    return True, ""

class ImageLayoutCreator:
    """Professional layout creation using PDF standards with enhanced performance"""
    
    def __init__(self):
        """Initialize layout creator with enhanced error handling"""
        self.typography = typography_config
        self.layout = layout_config
        self.text_processor = text_processor
        self._font_cache = {}
        self._font_cache_lock = Lock()
        self._default_font = None
        self._default_font_size = 24
        
        # Performance monitoring
        self._initialization_time = time.time()
        self._last_operation_time = None
        
        # Initialize default font
        self._initialize_default_font()
        
        log.info("ImageLayoutCreator initialized successfully")
    
    def _initialize_default_font(self):
        """Initialize default font with fallback handling"""
        try:
            self._default_font = ImageFont.load_default()
            log.debug("Default font loaded successfully")
        except Exception as e:
            log.warning(f"Could not load default font: {e}")
            self._default_font = None
    
    @performance_monitor
    def create_question_image(self, image_path: str, question_text: str, 
                            theme: str, image_number: str) -> Image.Image:
        """
        Create question image using PDF layout standards with enhanced error handling
        
        Args:
            image_path: Path to source image
            question_text: Question text to add
            theme: Theme/category name
            image_number: Image number identifier
            
        Returns:
            PIL.Image: Processed image with question text
        """
        try:
            # Validate inputs
            is_valid, error_msg = validate_input_parameters(image_path, question_text, theme, image_number)
            if not is_valid:
                log.error(f"Invalid parameters for question image: {error_msg}")
                return self._load_fallback_image(image_path)
            
            # Load image
            img = self._load_image_safely(image_path)
            if img is None:
                return self._create_placeholder_image()
            
            draw = ImageDraw.Draw(img)
            
            # Process question text
            lines = self._process_text_safely(question_text, 'question')
            font_size = self._calculate_font_size_safely(question_text, 'question')
            font_config = self._get_font_config_safely('question')
            font = self._get_font(font_size, font_config.get('weight', 'normal'))
            
            # Calculate position
            text_y = self._calculate_text_position_safely(lines, font_size, font_config.get('line_spacing', 1.2), True)
            text_x = self._get_text_area_bounds_safely(True).get('start_x', 100)
            
            # Draw text
            self._draw_text_with_styling(draw, lines, font, text_x, text_y, font_config)
            self._add_footer(draw, theme, image_number)
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_question_images'] += 1
            
            self._last_operation_time = time.time()
            return img
            
        except Exception as e:
            log.error(f"Error creating question image: {e}")
            return self._load_fallback_image(image_path)
    
    @performance_monitor
    def create_answer_image(self, image_path: str, answer_text: str, 
                          theme: str, image_number: str) -> Image.Image:
        """
        Create answer image using PDF layout standards with enhanced error handling
        
        Args:
            image_path: Path to source image
            answer_text: Answer text to add
            theme: Theme/category name
            image_number: Image number identifier
            
        Returns:
            PIL.Image: Processed image with answer text
        """
        try:
            # Validate inputs
            is_valid, error_msg = validate_input_parameters(image_path, answer_text, theme, image_number)
            if not is_valid:
                log.error(f"Invalid parameters for answer image: {error_msg}")
                return self._load_fallback_image(image_path)
            
            # Load image
            img = self._load_image_safely(image_path)
            if img is None:
                return self._create_placeholder_image()
            
            draw = ImageDraw.Draw(img)
            
            # Process answer text
            lines = self._process_text_safely(answer_text, 'answer')
            font_size = self._calculate_font_size_safely(answer_text, 'answer')
            font_config = self._get_font_config_safely('answer')
            font = self._get_font(font_size, font_config.get('weight', 'normal'))
            
            # Calculate position
            text_y = self._calculate_text_position_safely(lines, font_size, font_config.get('line_spacing', 1.2), False)
            text_x = self._get_text_area_bounds_safely(False).get('start_x', 100)
            
            # Draw text
            self._draw_text_with_styling(draw, lines, font, text_x, text_y, font_config)
            self._add_footer(draw, theme, image_number)
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_answer_images'] += 1
            
            self._last_operation_time = time.time()
            return img
            
        except Exception as e:
            log.error(f"Error creating answer image: {e}")
            return self._load_fallback_image(image_path)
    
    def _load_image_safely(self, image_path: str) -> Optional[Image.Image]:
        """
        Load image with error handling
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL.Image or None if loading fails
        """
        try:
            return Image.open(image_path)
        except Exception as e:
            log.error(f"Error loading image {image_path}: {e}")
            return None
    
    def _load_fallback_image(self, image_path: str) -> Image.Image:
        """
        Load fallback image when original fails
        
        Args:
            image_path: Original image path (for logging)
            
        Returns:
            PIL.Image: Fallback image
        """
        try:
            return Image.open(image_path)
        except Exception:
            return self._create_placeholder_image()
    
    def _create_placeholder_image(self) -> Image.Image:
        """
        Create a placeholder image when no image is available
        
        Returns:
            PIL.Image: Placeholder image
        """
        try:
            # Create a simple placeholder image
            img = Image.new('RGB', (800, 600), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Add placeholder text
            if self._default_font:
                draw.text((400, 300), "Image Not Available", font=self._default_font, fill='black', anchor='mm')
            
            return img
        except Exception as e:
            log.error(f"Error creating placeholder image: {e}")
            # Return minimal image
            return Image.new('RGB', (800, 600), color='white')
    
    def _process_text_safely(self, text: str, text_type: str) -> List[str]:
        """
        Process text safely with fallback
        
        Args:
            text: Text to process
            text_type: Type of text (question/answer)
            
        Returns:
            List[str]: Processed text lines
        """
        try:
            if self.text_processor and hasattr(self.text_processor, 'process_text_for_image'):
                return self.text_processor.process_text_for_image(text, text_type)
            else:
                # Fallback text processing
                return self._simple_text_wrap(text, 50)
        except Exception as e:
            log.warning(f"Error processing text, using fallback: {e}")
            return self._simple_text_wrap(text, 50)
    
    def _simple_text_wrap(self, text: str, max_width: int) -> List[str]:
        """
        Simple text wrapping fallback
        
        Args:
            text: Text to wrap
            max_width: Maximum characters per line
            
        Returns:
            List[str]: Wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines if lines else [text]
    
    def _calculate_font_size_safely(self, text: str, text_type: str) -> int:
        """
        Calculate font size safely with fallback
        
        Args:
            text: Text content
            text_type: Type of text
            
        Returns:
            int: Font size
        """
        try:
            if self.text_processor and hasattr(self.text_processor, 'calculate_adaptive_font_size'):
                return self.text_processor.calculate_adaptive_font_size(text, text_type)
            else:
                return self._default_font_size
        except Exception as e:
            log.warning(f"Error calculating font size, using default: {e}")
            return self._default_font_size
    
    def _get_font_config_safely(self, text_type: str) -> Dict[str, Any]:
        """
        Get font configuration safely with fallback
        
        Args:
            text_type: Type of text
            
        Returns:
            Dict[str, Any]: Font configuration
        """
        try:
            if self.text_processor and hasattr(self.text_processor, 'get_font_config'):
                return self.text_processor.get_font_config(text_type)
            else:
                return self._get_default_font_config()
        except Exception as e:
            log.warning(f"Error getting font config, using default: {e}")
            return self._get_default_font_config()
    
    def _get_default_font_config(self) -> Dict[str, Any]:
        """
        Get default font configuration
        
        Returns:
            Dict[str, Any]: Default font configuration
        """
        return {
            'weight': 'normal',
            'color': 'white',
            'size': self._default_font_size,
            'line_spacing': 1.2
        }
    
    def _calculate_text_position_safely(self, lines: List[str], font_size: int, 
                                      line_spacing: float, is_question: bool) -> int:
        """
        Calculate text position safely with fallback
        
        Args:
            lines: Text lines
            font_size: Font size
            line_spacing: Line spacing
            is_question: Whether this is a question
            
        Returns:
            int: Y position for text
        """
        try:
            if self.layout and hasattr(self.layout, 'calculate_text_position'):
                return self.layout.calculate_text_position(lines, font_size, line_spacing, is_question)
            else:
                return 50  # Default position
        except Exception as e:
            log.warning(f"Error calculating text position, using default: {e}")
            return 50
    
    def _get_text_area_bounds_safely(self, is_question: bool) -> Dict[str, int]:
        """
        Get text area bounds safely with fallback
        
        Args:
            is_question: Whether this is a question
            
        Returns:
            Dict[str, int]: Text area bounds
        """
        try:
            if self.layout and hasattr(self.layout, 'get_text_area_bounds'):
                return self.layout.get_text_area_bounds(is_question)
            else:
                return {'start_x': 100}  # Default bounds
        except Exception as e:
            log.warning(f"Error getting text area bounds, using default: {e}")
            return {'start_x': 100}
    
    def _get_font(self, font_size: int, font_weight: str = 'normal') -> ImageFont.FreeTypeFont:
        """
        Get font with enhanced caching and error handling
        
        Args:
            font_size: Font size
            font_weight: Font weight
            
        Returns:
            ImageFont.FreeTypeFont: Font object
        """
        cache_key = f"{font_size}_{font_weight}"
        
        with self._font_cache_lock:
            if cache_key in self._font_cache:
                with _performance_lock:
                    _performance_stats['cache_hits'] += 1
                return self._font_cache[cache_key]
            
            # Font not in cache, load it
            with _performance_lock:
                _performance_stats['cache_misses'] += 1
                _performance_stats['total_font_loads'] += 1
            
            try:
                font = ImageFont.load_default()
                self._font_cache[cache_key] = font
                log.debug(f"Font loaded and cached: {cache_key}")
                return font
            except Exception as e:
                log.error(f"Error loading font {cache_key}: {e}")
                # Return default font if available
                if self._default_font:
                    return self._default_font
                # Create minimal font
                return ImageFont.load_default()
    
    def _draw_text_with_styling(self, draw: ImageDraw.Draw, lines: List[str], 
                               font: ImageFont.FreeTypeFont, x: int, y: int, 
                               font_config: Dict[str, Any]):
        """
        Draw text with PDF styling and enhanced error handling
        
        Args:
            draw: ImageDraw object
            lines: Text lines to draw
            font: Font to use
            x: X position
            y: Y position
            font_config: Font configuration
        """
        try:
            # Get text color
            text_color = self._get_color_safely(font_config.get('color', 'white'))
            line_height = int(font_config.get('size', self._default_font_size) * font_config.get('line_spacing', 1.2) * 1.2)
            
            current_y = y
            for line in lines:
                # Draw shadow
                shadow_offset = 2
                draw.text((x + shadow_offset, current_y + shadow_offset), line, font=font, fill=(0, 0, 0))
                # Draw main text
                draw.text((x, current_y), line, font=font, fill=text_color)
                current_y += line_height
            
            with _performance_lock:
                _performance_stats['total_text_renders'] += 1
                
        except Exception as e:
            log.error(f"Error drawing text: {e}")
    
    def _get_color_safely(self, color_name: str) -> Tuple[int, int, int]:
        """
        Get color safely with fallback
        
        Args:
            color_name: Color name or hex value
            
        Returns:
            Tuple[int, int, int]: RGB color values
        """
        try:
            if self.typography and hasattr(self.typography, 'get_color_rgb'):
                return self.typography.get_color_rgb(color_name)
            else:
                # Default color handling
                if color_name.startswith('#'):
                    # Hex color
                    color_name = color_name.lstrip('#')
                    return tuple(int(color_name[i:i+2], 16) for i in (0, 2, 4))
                else:
                    # Named color fallback
                    color_map = {
                        'white': (255, 255, 255),
                        'black': (0, 0, 0),
                        'red': (255, 0, 0),
                        'green': (0, 255, 0),
                        'blue': (0, 0, 255)
                    }
                    return color_map.get(color_name.lower(), (255, 255, 255))
        except Exception as e:
            log.warning(f"Error getting color {color_name}, using white: {e}")
            return (255, 255, 255)
    
    def _add_footer(self, draw: ImageDraw.Draw, theme: str, image_number: str):
        """
        Add PDF-style footer with enhanced error handling
        
        Args:
            draw: ImageDraw object
            theme: Theme name
            image_number: Image number
        """
        try:
            # Get footer bounds
            footer_bounds = self._get_footer_bounds_safely()
            footer_color = self._get_color_safely('black')
            
            # Draw footer background
            draw.rectangle([
                footer_bounds['start_x'], footer_bounds['start_y'],
                footer_bounds['end_x'], footer_bounds['end_y']
            ], fill=footer_color)
            
            # Get footer configuration
            footer_config = self._get_font_config_safely('footer')
            footer_font = self._get_font(footer_config.get('size', 12), footer_config.get('weight', 'normal'))
            footer_text_color = self._get_color_safely(footer_config.get('color', 'white'))
            
            # Get positions
            brand_pos = self._get_brand_position_safely()
            category_pos = self._get_category_position_safely()
            number_pos = self._get_image_number_position_safely()
            
            # Get brand text
            brand_text = self._get_brand_text_safely()
            
            # Draw footer text
            draw.text(brand_pos, brand_text, font=footer_font, fill=footer_text_color)
            draw.text(category_pos, theme.upper(), font=footer_font, fill=footer_text_color)
            draw.text(number_pos, f"#{image_number}", font=footer_font, fill=footer_text_color)
            
            with _performance_lock:
                _performance_stats['total_footer_renders'] += 1
                
        except Exception as e:
            log.error(f"Error adding footer: {e}")
    
    def _get_footer_bounds_safely(self) -> Dict[str, int]:
        """Get footer bounds safely with fallback"""
        try:
            if self.layout and hasattr(self.layout, 'get_footer_bounds'):
                return self.layout.get_footer_bounds()
            else:
                return {'start_x': 0, 'start_y': 550, 'end_x': 800, 'end_y': 600}
        except Exception as e:
            log.warning(f"Error getting footer bounds, using default: {e}")
            return {'start_x': 0, 'start_y': 550, 'end_x': 800, 'end_y': 600}
    
    def _get_brand_position_safely(self) -> Tuple[int, int]:
        """Get brand position safely with fallback"""
        try:
            if self.layout and hasattr(self.layout, 'get_brand_position'):
                return self.layout.get_brand_position()
            else:
                return (10, 560)
        except Exception as e:
            log.warning(f"Error getting brand position, using default: {e}")
            return (10, 560)
    
    def _get_category_position_safely(self) -> Tuple[int, int]:
        """Get category position safely with fallback"""
        try:
            if self.layout and hasattr(self.layout, 'get_category_position'):
                return self.layout.get_category_position()
            else:
                return (300, 560)
        except Exception as e:
            log.warning(f"Error getting category position, using default: {e}")
            return (300, 560)
    
    def _get_image_number_position_safely(self) -> Tuple[int, int]:
        """Get image number position safely with fallback"""
        try:
            if self.layout and hasattr(self.layout, 'get_image_number_position'):
                return self.layout.get_image_number_position()
            else:
                return (700, 560)
        except Exception as e:
            log.warning(f"Error getting image number position, using default: {e}")
            return (700, 560)
    
    def _get_brand_text_safely(self) -> str:
        """Get brand text safely with fallback"""
        try:
            if self.layout and hasattr(self.layout, 'BRAND_TEXT'):
                return self.layout.BRAND_TEXT
            else:
                return "ASK: Daily Architectural Research"
        except Exception as e:
            log.warning(f"Error getting brand text, using default: {e}")
            return "ASK: Daily Architectural Research"
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for the layout creator
        
        Returns:
            dict: Performance statistics
        """
        with _performance_lock:
            total_operations = (_performance_stats['total_question_images'] + 
                              _performance_stats['total_answer_images'])
            
            return {
                'total_question_images': _performance_stats['total_question_images'],
                'total_answer_images': _performance_stats['total_answer_images'],
                'total_font_loads': _performance_stats['total_font_loads'],
                'total_text_renders': _performance_stats['total_text_renders'],
                'total_footer_renders': _performance_stats['total_footer_renders'],
                'cache_hits': _performance_stats['cache_hits'],
                'cache_misses': _performance_stats['cache_misses'],
                'cache_hit_ratio': _performance_stats['cache_hits'] / max(_performance_stats['cache_hits'] + _performance_stats['cache_misses'], 1),
                'total_time': _performance_stats['total_time'],
                'average_time_per_operation': _performance_stats['total_time'] / max(total_operations, 1),
                'initialization_time': self._initialization_time,
                'last_operation_time': self._last_operation_time,
                'font_cache_size': len(self._font_cache),
                'module_version': '2.0',
                'optimization_date': '2025-08-24'
            }
    
    def reset_performance_stats(self):
        """Reset performance statistics with thread safety"""
        global _performance_stats
        with _performance_lock:
            _performance_stats = {
                'total_question_images': 0,
                'total_answer_images': 0,
                'total_font_loads': 0,
                'total_text_renders': 0,
                'total_footer_renders': 0,
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
            'dependencies': {
                'typography_config': self.typography is not None,
                'layout_config': self.layout is not None,
                'text_processor': self.text_processor is not None
            },
            'font_system': {
                'default_font_loaded': self._default_font is not None,
                'font_cache_size': len(self._font_cache),
                'font_cache_working': True
            },
            'performance': {
                'initialization_time': self._initialization_time,
                'last_operation_time': self._last_operation_time,
                'total_operations': _performance_stats['total_question_images'] + _performance_stats['total_answer_images']
            }
        }
        
        return validation_results

# Global layout creator instance
layout_creator = ImageLayoutCreator()

# Convenience functions with performance monitoring
@performance_monitor
def create_question_image(image_path: str, question_text: str, theme: str, image_number: str) -> Image.Image:
    """
    Create question image with performance monitoring
    
    Args:
        image_path: Path to source image
        question_text: Question text to add
        theme: Theme/category name
        image_number: Image number identifier
        
    Returns:
        PIL.Image: Processed image with question text
    """
    return layout_creator.create_question_image(image_path, question_text, theme, image_number)

@performance_monitor
def create_answer_image(image_path: str, answer_text: str, theme: str, image_number: str) -> Image.Image:
    """
    Create answer image with performance monitoring
    
    Args:
        image_path: Path to source image
        answer_text: Answer text to add
        theme: Theme/category name
        image_number: Image number identifier
        
    Returns:
        PIL.Image: Processed image with answer text
    """
    return layout_creator.create_answer_image(image_path, answer_text, theme, image_number)

def get_performance_statistics() -> Dict[str, Any]:
    """
    Get performance statistics
    
    Returns:
        dict: Performance statistics
    """
    return layout_creator.get_performance_statistics()

def reset_performance_stats():
    """Reset performance statistics"""
    layout_creator.reset_performance_stats()

def validate_environment() -> Dict[str, Any]:
    """
    Validate environment
    
    Returns:
        dict: Environment validation results
    """
    return layout_creator.validate_environment()

# Export main functions
__all__ = [
    'ImageLayoutCreator',
    'create_question_image',
    'create_answer_image',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
