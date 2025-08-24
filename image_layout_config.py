#!/usr/bin/env python3
"""
Image Layout Configuration Module
Adapts PDF layout rules for professional image generation
"""

import os
import time
import logging
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass, field

# Configure logging
log = logging.getLogger(__name__)

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {
            'total_calculations': 0,
            'successful_calculations': 0,
            'failed_calculations': 0,
            'total_time': 0.0,
            'bounds_calculations': 0.0,
            'position_calculations': 0.0,
            'text_calculations': 0.0
        }
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics['total_time'] += duration
            self.metrics['total_calculations'] += 1
    
    def record_success(self):
        self.metrics['successful_calculations'] += 1
    
    def record_failure(self):
        self.metrics['failed_calculations'] += 1
    
    def record_operation_time(self, operation_type: str, duration: float):
        if operation_type in self.metrics:
            self.metrics[operation_type] += duration
    
    def get_stats(self):
        stats = self.metrics.copy()
        stats['success_rate'] = (self.metrics['successful_calculations'] / max(self.metrics['total_calculations'], 1)) * 100
        return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()

def validate_environment_variables() -> Tuple[bool, str]:
    """Validate environment variable configuration"""
    try:
        required_vars = [
            'IMAGE_WIDTH', 'IMAGE_HEIGHT', 'IMAGE_MARGIN_LEFT', 'IMAGE_MARGIN_RIGHT',
            'IMAGE_MARGIN_TOP', 'IMAGE_MARGIN_BOTTOM', 'IMAGE_TEXT_AREA_START_Y',
            'IMAGE_TEXT_AREA_END_Y', 'IMAGE_FOOTER_HEIGHT', 'IMAGE_BRAND_TEXT'
        ]
        
        missing_vars = []
        invalid_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            else:
                # Validate numeric values
                if var in ['IMAGE_WIDTH', 'IMAGE_HEIGHT', 'IMAGE_MARGIN_LEFT', 'IMAGE_MARGIN_RIGHT',
                          'IMAGE_MARGIN_TOP', 'IMAGE_MARGIN_BOTTOM', 'IMAGE_TEXT_AREA_START_Y',
                          'IMAGE_TEXT_AREA_END_Y', 'IMAGE_FOOTER_HEIGHT']:
                    try:
                        int_val = int(value)
                        if int_val <= 0:
                            invalid_vars.append(f"{var}: {value} (must be positive)")
                    except ValueError:
                        invalid_vars.append(f"{var}: {value} (must be integer)")
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        if invalid_vars:
            return False, f"Invalid environment variables: {invalid_vars}"
        
        return True, "Environment variables valid"
    except Exception as e:
        return False, f"Environment validation error: {str(e)}"

def validate_configuration_values(config) -> Tuple[bool, str]:
    """Validate configuration values"""
    try:
        # Check image dimensions
        if config.IMAGE_WIDTH <= 0 or config.IMAGE_HEIGHT <= 0:
            return False, "Image dimensions must be positive"
        
        # Check margins
        if config.MARGIN_LEFT < 0 or config.MARGIN_RIGHT < 0:
            return False, "Margins must be non-negative"
        
        if config.MARGIN_LEFT + config.MARGIN_RIGHT >= config.IMAGE_WIDTH:
            return False, "Left + right margins must be less than image width"
        
        if config.MARGIN_TOP + config.MARGIN_BOTTOM >= config.IMAGE_HEIGHT:
            return False, "Top + bottom margins must be less than image height"
        
        # Check text area bounds
        if config.TEXT_AREA_START_Y >= config.TEXT_AREA_END_Y:
            return False, "Text area start Y must be less than end Y"
        
        if config.TEXT_AREA_END_Y >= config.IMAGE_HEIGHT:
            return False, "Text area end Y must be less than image height"
        
        # Check footer bounds
        if config.FOOTER_START_Y < 0 or config.FOOTER_START_Y >= config.IMAGE_HEIGHT:
            return False, "Footer start Y must be within image bounds"
        
        return True, "Configuration values valid"
    except Exception as e:
        return False, f"Configuration validation error: {str(e)}"

class ImageLayoutConfig:
    """Layout configuration for images using PDF standards"""
    
    def __init__(self):
        # Start performance monitoring
        performance_monitor.start_timer()
        
        try:
            # Validate environment variables
            is_valid, validation_message = validate_environment_variables()
            if not is_valid:
                log.error(f"Environment validation failed: {validation_message}")
                performance_monitor.record_failure()
                raise ValueError(validation_message)
            
            log.info("Starting enhanced image layout configuration initialization...")
            
            self._load_configuration()
            
            # Validate configuration values
            is_valid, validation_message = validate_configuration_values(self)
            if not is_valid:
                log.error(f"Configuration validation failed: {validation_message}")
                performance_monitor.record_failure()
                raise ValueError(validation_message)
            
            # Record success and end timer
            performance_monitor.end_timer()
            performance_monitor.record_success()
            
            log.info("Enhanced image layout configuration initialization completed")
            
        except Exception as e:
            log.error(f"Error in enhanced image layout configuration initialization: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
    
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
        
        # Theme and image number positioning
        self.CATEGORY_Y_OFFSET = int(os.getenv('IMAGE_THEME_Y_OFFSET', '120'))   # From bottom
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
        Get theme text position
        
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
        # Start performance monitoring
        start_time = time.time()
        
        try:
            # Input validation
            if not isinstance(lines, list):
                raise ValueError("Lines must be a list")
            
            if not isinstance(font_size, int) or font_size <= 0:
                raise ValueError("Font size must be a positive integer")
            
            if not isinstance(line_spacing, (int, float)) or line_spacing <= 0:
                raise ValueError("Line spacing must be a positive number")
            
            if not isinstance(is_question, bool):
                raise ValueError("is_question must be a boolean")
            
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
            
            # Record operation time
            duration = time.time() - start_time
            performance_monitor.record_operation_time('text_calculations', duration)
            performance_monitor.record_success()
            
            return text_y
            
        except Exception as e:
            log.error(f"Error in text position calculation: {e}")
            performance_monitor.record_failure()
            raise
    
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


def get_performance_stats():
    """Get performance statistics"""
    return performance_monitor.get_stats()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    log.info("Performance statistics reset")

def get_layout_analysis():
    """Get layout analysis and recommendations"""
    try:
        config = ImageLayoutConfig()
        stats = performance_monitor.get_stats()
        
        # Analyze layout efficiency
        text_area_width = config.TEXT_AREA_END_X - config.TEXT_AREA_START_X
        text_area_height = config.TEXT_AREA_END_Y - config.TEXT_AREA_START_Y
        text_area_ratio = text_area_width / text_area_height if text_area_height > 0 else 0
        
        # Calculate margin efficiency
        total_margins = config.MARGIN_LEFT + config.MARGIN_RIGHT + config.MARGIN_TOP + config.MARGIN_BOTTOM
        image_area = config.IMAGE_WIDTH * config.IMAGE_HEIGHT
        margin_efficiency = (image_area - total_margins * (config.IMAGE_WIDTH + config.IMAGE_HEIGHT)) / image_area
        
        return {
            'text_area_efficiency': text_area_ratio,
            'margin_efficiency': margin_efficiency,
            'performance_metrics': stats,
            'recommendations': [
                'Monitor text positioning performance',
                'Optimize margin calculations for different screen sizes',
                'Consider dynamic text area adjustments',
                'Implement layout caching for repeated calculations',
                'Add support for responsive design patterns'
            ]
        }
    except Exception as e:
        log.error(f"Error in layout analysis: {e}")
        return {'error': str(e)}

def validate_text_positioning(lines: List[str], font_size: int, line_spacing: float, 
                            is_question: bool = True) -> Tuple[bool, str]:
    """Validate text positioning parameters"""
    try:
        if not lines or len(lines) == 0:
            return False, "Lines list cannot be empty"
        
        if font_size <= 0:
            return False, "Font size must be positive"
        
        if line_spacing <= 0:
            return False, "Line spacing must be positive"
        
        if not isinstance(is_question, bool):
            return False, "is_question must be boolean"
        
        return True, "Text positioning parameters valid"
    except Exception as e:
        return False, f"Text positioning validation error: {str(e)}"

def get_configuration_summary():
    """Get configuration summary"""
    try:
        config = ImageLayoutConfig()
        return {
            'image_dimensions': f"{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}",
            'margins': {
                'left': config.MARGIN_LEFT,
                'right': config.MARGIN_RIGHT,
                'top': config.MARGIN_TOP,
                'bottom': config.MARGIN_BOTTOM
            },
            'text_area': {
                'start_y': config.TEXT_AREA_START_Y,
                'end_y': config.TEXT_AREA_END_Y,
                'width': config.TEXT_AREA_END_X - config.TEXT_AREA_START_X
            },
            'footer': {
                'height': config.FOOTER_HEIGHT,
                'start_y': config.FOOTER_START_Y
            },
            'brand': {
                'text': config.BRAND_TEXT,
                'position': config.get_brand_position()
            },
            'text_wrapping': {
                'question': config.TEXT_WRAP_WIDTH_QUESTION,
                'answer': config.TEXT_WRAP_WIDTH_ANSWER,
                'title': config.TEXT_WRAP_WIDTH_TITLE
            }
        }
    except Exception as e:
        log.error(f"Error getting configuration summary: {e}")
        return {'error': str(e)}

def optimize_layout_for_content(content_length: int, font_size: int, 
                              is_question: bool = True) -> Dict[str, Any]:
    """Optimize layout parameters for specific content"""
    try:
        config = ImageLayoutConfig()
        
        # Calculate optimal text area based on content
        estimated_lines = max(1, content_length // 50)  # Rough estimate
        line_height = int(font_size * config.LINE_SPACING_MULTIPLIER)
        estimated_height = estimated_lines * line_height
        
        # Adjust text area if needed
        current_text_height = config.TEXT_AREA_END_Y - config.TEXT_AREA_START_Y
        if estimated_height > current_text_height:
            # Suggest increasing text area
            suggested_end_y = min(config.IMAGE_HEIGHT - config.FOOTER_HEIGHT - 50,
                                config.TEXT_AREA_START_Y + estimated_height + 100)
            
            return {
                'current_text_height': current_text_height,
                'estimated_content_height': estimated_height,
                'suggested_text_area_end_y': suggested_end_y,
                'adjustment_needed': True,
                'recommendation': f"Increase text area end Y to {suggested_end_y}"
            }
        else:
            return {
                'current_text_height': current_text_height,
                'estimated_content_height': estimated_height,
                'adjustment_needed': False,
                'recommendation': "Current text area is sufficient"
            }
    except Exception as e:
        log.error(f"Error optimizing layout: {e}")
        return {'error': str(e)}

def get_system_health():
    """Get system health status"""
    try:
        stats = performance_monitor.get_stats()
        env_valid = validate_environment_variables()[0]
        
        health_score = 0
        issues = []
        
        # Check success rate
        if stats['success_rate'] >= 90:
            health_score += 30
        elif stats['success_rate'] >= 70:
            health_score += 20
            issues.append("Low success rate")
        else:
            issues.append("Very low success rate")
        
        # Check environment
        if env_valid:
            health_score += 20
        else:
            issues.append("Environment configuration issues")
        
        # Check performance
        if stats['total_time'] > 0:
            avg_time = stats['total_time'] / stats['total_calculations']
            if avg_time < 0.001:  # Very fast
                health_score += 25
            elif avg_time < 0.01:  # Fast
                health_score += 15
                issues.append("Slow performance")
            else:
                issues.append("Very slow performance")
        
        # Check error rate
        error_rate = stats['failed_calculations'] / max(stats['total_calculations'], 1)
        if error_rate < 0.1:
            health_score += 25
        elif error_rate < 0.3:
            health_score += 15
            issues.append("High error rate")
        else:
            issues.append("Very high error rate")
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
            'issues': issues,
            'recommendations': [
                'Monitor calculation success rates',
                'Optimize layout calculation performance',
                'Check environment configuration',
                'Implement error recovery mechanisms',
                'Add performance monitoring'
            ]
        }
    except Exception as e:
        return {
            'health_score': 0,
            'status': 'error',
            'issues': [f"Health check failed: {str(e)}"],
            'recommendations': ['Check system configuration and logs']
        }
