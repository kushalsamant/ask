#!/usr/bin/env python3
"""
Image Text Processor Module - Optimized Version 2.0
Enhanced text processing using PDF formatting rules for images with improved performance

This module provides functionality to:
- Process text for image display using PDF formatting rules
- Clean and normalize text content with enhanced character handling
- Calculate adaptive font sizes and text dimensions
- Apply PDF-style line processing and formatting
- Split long text into manageable chunks
- Create text summaries with intelligent truncation
- Support text emphasis and styling
- Handle various text types (questions, answers, titles)
- Provide performance monitoring and error recovery

Optimizations:
- Enhanced text cleaning and normalization
- Performance monitoring and statistics
- Better error handling and recovery
- Memory-efficient text processing
- Thread-safe operations
- Improved regex patterns and text wrapping
- Enhanced character encoding support
- Better dependency management

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized)
"""

import textwrap
import re
import logging
import time
from typing import List, Dict, Tuple, Optional, Any
from functools import wraps, lru_cache
from threading import Lock

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

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_text_processes': 0,
    'total_text_cleans': 0,
    'total_font_calculations': 0,
    'total_dimension_calculations': 0,
    'total_text_splits': 0,
    'total_summaries': 0,
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

def validate_input_parameters(text: str, text_type: str = 'question') -> Tuple[bool, str]:
    """
    Validate input parameters for text processing operations
    
    Args:
        text: Text content to validate
        text_type: Type of text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not isinstance(text, str):
        return False, "Text must be a non-empty string"
    
    if not text_type or not isinstance(text_type, str):
        return False, "Text type must be a non-empty string"
    
    valid_text_types = ['question', 'answer', 'title', 'footer']
    if text_type not in valid_text_types:
        return False, f"Text type must be one of: {valid_text_types}"
    
    # Check for potentially harmful characters
    invalid_chars = ['<', '>', '"', "'", '\\', '/', '|', ':', '*', '?']
    if any(char in text for char in invalid_chars):
        return False, "Text contains invalid characters"
    
    return True, ""

class ImageTextProcessor:
    """Enhanced text processing using PDF standards with improved performance"""
    
    def __init__(self):
        """Initialize text processor with enhanced error handling"""
        self.typography = typography_config
        self.layout = layout_config
        
        # Performance monitoring
        self._initialization_time = time.time()
        self._last_operation_time = None
        
        # Pre-compile regex patterns for better performance
        self._whitespace_pattern = re.compile(r'\s+')
        self._special_chars_pattern = re.compile(r'[^\w\s\.,!?;:()\-]')
        self._sentence_split_pattern = re.compile(r'[.!?]+')
        
        # Default configurations
        self._default_wrap_width = 50
        self._default_font_size = 24
        self._default_line_spacing = 1.2
        self._default_line_spacing_multiplier = 1.2
        
        log.info("ImageTextProcessor initialized successfully")
    
    @performance_monitor
    def process_text_for_image(self, text: str, text_type: str = 'question', 
                              max_lines: Optional[int] = None) -> List[str]:
        """
        Process text for image display using PDF formatting rules with enhanced error handling
        
        Args:
            text: Text content to process
            text_type: Type of text ('question', 'answer', 'title', 'footer')
            max_lines: Maximum number of lines (None for unlimited)
            
        Returns:
            List of processed text lines
        """
        try:
            # Validate inputs
            is_valid, error_msg = validate_input_parameters(text, text_type)
            if not is_valid:
                log.error(f"Invalid parameters for text processing: {error_msg}")
                return self._get_fallback_text(text)
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Get wrap width for text type
            wrap_width = self._get_text_wrap_width_safely(text_type)
            
            # Apply text wrapping using PDF logic
            lines = textwrap.wrap(cleaned_text, width=wrap_width, 
                                 break_long_words=True, break_on_hyphens=True)
            
            # Apply line limits if specified
            if max_lines and len(lines) > max_lines:
                lines = lines[:max_lines]
                if lines:
                    # Add ellipsis to indicate truncation
                    last_line = lines[-1]
                    if len(last_line) > wrap_width - 3:
                        lines[-1] = last_line[:wrap_width-3] + "..."
                    else:
                        lines[-1] = last_line + "..."
            
            # Apply PDF-style line processing
            processed_lines = self._apply_image_line_processing(lines, text_type)
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_text_processes'] += 1
            
            self._last_operation_time = time.time()
            return processed_lines
            
        except Exception as e:
            log.error(f"Error processing text for image: {e}")
            return self._get_fallback_text(text)
    
    def _get_fallback_text(self, text: str) -> List[str]:
        """
        Get fallback text when processing fails
        
        Args:
            text: Original text
            
        Returns:
            List[str]: Fallback text lines
        """
        if not text:
            return [""]
        
        # Simple fallback: truncate to 50 characters
        truncated = text[:50] + "..." if len(text) > 50 else text
        return [truncated]
    
    @performance_monitor
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content with enhanced character handling
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        try:
            # Remove extra whitespace using pre-compiled pattern
            text = self._whitespace_pattern.sub(' ', text.strip())
            
            # Remove special characters that might cause issues
            text = self._special_chars_pattern.sub('', text)
            
            # Normalize quotes and apostrophes
            text = text.replace('"', '"').replace('"', '"')
            text = text.replace(''', "'").replace(''', "'")
            
            # Normalize dashes and hyphens
            text = text.replace('—', '-').replace('–', '-')
            
            # Normalize ellipsis
            text = text.replace('…', '...')
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_text_cleans'] += 1
            
            return text
            
        except Exception as e:
            log.warning(f"Error cleaning text, using fallback: {e}")
            return text.strip() if text else ""
    
    def _get_text_wrap_width_safely(self, text_type: str) -> int:
        """
        Get text wrap width safely with fallback
        
        Args:
            text_type: Type of text
            
        Returns:
            int: Wrap width
        """
        try:
            if self.layout and hasattr(self.layout, 'get_text_wrap_width'):
                return self.layout.get_text_wrap_width(text_type)
            else:
                return self._default_wrap_width
        except Exception as e:
            log.warning(f"Error getting text wrap width, using default: {e}")
            return self._default_wrap_width
    
    def _apply_image_line_processing(self, lines: List[str], text_type: str) -> List[str]:
        """
        Apply PDF-style line processing with enhanced formatting
        
        Args:
            lines: List of text lines
            text_type: Type of text
            
        Returns:
            Processed lines
        """
        processed_lines = []
        
        for i, line in enumerate(lines):
            # Apply PDF-style line formatting
            processed_line = self._format_line(line, text_type, i == 0)
            processed_lines.append(processed_line)
        
        return processed_lines
    
    def _format_line(self, line: str, text_type: str, is_first_line: bool) -> str:
        """
        Format individual line using PDF standards with enhanced logic
        
        Args:
            line: Text line
            text_type: Type of text
            is_first_line: Whether this is the first line
            
        Returns:
            Formatted line
        """
        try:
            # Apply text type specific formatting
            if text_type == 'question' and is_first_line:
                # Questions start with capital letter and end with question mark
                line = line.strip()
                if not line.endswith('?'):
                    line = line.rstrip('.') + '?'
            
            elif text_type == 'answer':
                # Answers start with capital letter and end with period
                line = line.strip()
                if not line.endswith(('.', '!', '?')):
                    line = line + '.'
            
            elif text_type == 'title':
                # Titles are properly capitalized
                line = line.strip()
                if line:
                    line = line.title()
            
            elif text_type == 'footer':
                # Footer text is uppercase
                line = line.strip().upper()
            
            # Ensure proper capitalization for all types
            if line and not line[0].isupper():
                line = line[0].upper() + line[1:]
            
            return line
            
        except Exception as e:
            log.warning(f"Error formatting line, using original: {e}")
            return line
    
    @performance_monitor
    def calculate_adaptive_font_size(self, text: str, text_type: str = 'question') -> int:
        """
        Calculate adaptive font size using PDF scaling logic with fallback
        
        Args:
            text: Text content
            text_type: Type of text
            
        Returns:
            Adaptive font size
        """
        try:
            if self.typography and hasattr(self.typography, 'calculate_adaptive_font_size'):
                result = self.typography.calculate_adaptive_font_size(text, text_type)
                
                # Update performance stats
                with _performance_lock:
                    _performance_stats['total_font_calculations'] += 1
                
                return result
            else:
                # Fallback font size calculation
                return self._calculate_fallback_font_size(text, text_type)
                
        except Exception as e:
            log.warning(f"Error calculating font size, using fallback: {e}")
            return self._calculate_fallback_font_size(text, text_type)
    
    def _calculate_fallback_font_size(self, text: str, text_type: str) -> int:
        """
        Calculate fallback font size when typography config is unavailable
        
        Args:
            text: Text content
            text_type: Type of text
            
        Returns:
            int: Font size
        """
        base_size = self._default_font_size
        
        # Adjust based on text type
        if text_type == 'title':
            base_size = 32
        elif text_type == 'question':
            base_size = 28
        elif text_type == 'answer':
            base_size = 24
        elif text_type == 'footer':
            base_size = 12
        
        # Adjust based on text length
        if len(text) > 100:
            base_size = max(base_size - 4, 12)
        elif len(text) < 20:
            base_size = min(base_size + 4, 48)
        
        return base_size
    
    def get_font_config(self, text_type: str = 'question') -> Dict[str, Any]:
        """
        Get font configuration for text type with fallback
        
        Args:
            text_type: Type of text
            
        Returns:
            Font configuration dictionary
        """
        try:
            if self.typography and hasattr(self.typography, 'get_font_config'):
                return self.typography.get_font_config(text_type)
            else:
                return self._get_default_font_config(text_type)
                
        except Exception as e:
            log.warning(f"Error getting font config, using default: {e}")
            return self._get_default_font_config(text_type)
    
    def _get_default_font_config(self, text_type: str) -> Dict[str, Any]:
        """
        Get default font configuration
        
        Args:
            text_type: Type of text
            
        Returns:
            Dict[str, Any]: Default font configuration
        """
        base_config = {
            'weight': 'normal',
            'color': 'white',
            'size': self._default_font_size,
            'line_spacing': self._default_line_spacing
        }
        
        # Adjust based on text type
        if text_type == 'title':
            base_config['size'] = 32
            base_config['weight'] = 'bold'
        elif text_type == 'question':
            base_config['size'] = 28
        elif text_type == 'answer':
            base_config['size'] = 24
        elif text_type == 'footer':
            base_config['size'] = 12
        
        return base_config
    
    @performance_monitor
    def calculate_text_dimensions(self, lines: List[str], font_size: int, 
                                 line_spacing: float) -> Tuple[int, int]:
        """
        Calculate text dimensions for layout positioning with enhanced accuracy
        
        Args:
            lines: List of text lines
            font_size: Font size in pixels
            line_spacing: Line spacing multiplier
            
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            # Get line spacing multiplier
            line_spacing_multiplier = self._get_line_spacing_multiplier_safely()
            
            # Estimate line height
            line_height = int(font_size * line_spacing * line_spacing_multiplier)
            
            # Calculate total height
            total_height = len(lines) * line_height
            
            # Estimate width (use longest line)
            max_width = 0
            for line in lines:
                # Enhanced width estimation: 0.6 * font_size per character
                estimated_width = len(line) * int(font_size * 0.6)
                max_width = max(max_width, estimated_width)
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_dimension_calculations'] += 1
            
            return (max_width, total_height)
            
        except Exception as e:
            log.error(f"Error calculating text dimensions: {e}")
            return (400, 200)  # Fallback dimensions
    
    def _get_line_spacing_multiplier_safely(self) -> float:
        """
        Get line spacing multiplier safely with fallback
        
        Returns:
            float: Line spacing multiplier
        """
        try:
            if self.layout and hasattr(self.layout, 'LINE_SPACING_MULTIPLIER'):
                return self.layout.LINE_SPACING_MULTIPLIER
            else:
                return self._default_line_spacing_multiplier
        except Exception as e:
            log.warning(f"Error getting line spacing multiplier, using default: {e}")
            return self._default_line_spacing_multiplier
    
    @performance_monitor
    def split_long_text(self, text: str, text_type: str = 'question', 
                       max_chars_per_line: Optional[int] = None) -> List[str]:
        """
        Split long text into manageable chunks using PDF logic with enhanced splitting
        
        Args:
            text: Long text content
            text_type: Type of text
            max_chars_per_line: Maximum characters per line
            
        Returns:
            List of text chunks
        """
        try:
            if not max_chars_per_line:
                max_chars_per_line = self._get_text_wrap_width_safely(text_type)
            
            # Split by sentences first using pre-compiled pattern
            sentences = self._sentence_split_pattern.split(text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Add punctuation back
                sentence += '.'
                
                # Check if adding this sentence would exceed limit
                if len(current_chunk + sentence) <= max_chars_per_line:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            
            # Add remaining chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_text_splits'] += 1
            
            return chunks
            
        except Exception as e:
            log.error(f"Error splitting long text: {e}")
            return [text] if text else []
    
    def add_text_emphasis(self, text: str, emphasis_type: str = 'bold') -> str:
        """
        Add text emphasis using PDF-style formatting with enhanced support
        
        Args:
            text: Text content
            emphasis_type: Type of emphasis ('bold', 'italic', 'underline')
            
        Returns:
            Text with emphasis markers
        """
        try:
            # Enhanced emphasis handling
            if emphasis_type == 'bold':
                return f"**{text}**"
            elif emphasis_type == 'italic':
                return f"*{text}*"
            elif emphasis_type == 'underline':
                return f"__{text}__"
            else:
                return text
                
        except Exception as e:
            log.warning(f"Error adding text emphasis, returning original: {e}")
            return text
    
    @performance_monitor
    def create_text_summary(self, text: str, max_length: int = 100) -> str:
        """
        Create text summary using PDF truncation logic with enhanced intelligence
        
        Args:
            text: Full text content
            max_length: Maximum length for summary
            
        Returns:
            Text summary
        """
        try:
            if len(text) <= max_length:
                return text
            
            # Find the last complete sentence within the limit
            truncated = text[:max_length]
            last_period = truncated.rfind('.')
            last_exclamation = truncated.rfind('!')
            last_question = truncated.rfind('?')
            
            end_pos = max(last_period, last_exclamation, last_question)
            
            if end_pos > max_length * 0.7:  # Only use if it's not too early
                return truncated[:end_pos + 1]
            else:
                return truncated.rstrip() + "..."
            
            # Update performance stats
            with _performance_lock:
                _performance_stats['total_summaries'] += 1
                
        except Exception as e:
            log.error(f"Error creating text summary: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for the text processor
        
        Returns:
            dict: Performance statistics
        """
        with _performance_lock:
            total_operations = (_performance_stats['total_text_processes'] + 
                              _performance_stats['total_text_cleans'] + 
                              _performance_stats['total_font_calculations'] + 
                              _performance_stats['total_dimension_calculations'])
            
            return {
                'total_text_processes': _performance_stats['total_text_processes'],
                'total_text_cleans': _performance_stats['total_text_cleans'],
                'total_font_calculations': _performance_stats['total_font_calculations'],
                'total_dimension_calculations': _performance_stats['total_dimension_calculations'],
                'total_text_splits': _performance_stats['total_text_splits'],
                'total_summaries': _performance_stats['total_summaries'],
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
                'total_text_processes': 0,
                'total_text_cleans': 0,
                'total_font_calculations': 0,
                'total_dimension_calculations': 0,
                'total_text_splits': 0,
                'total_summaries': 0,
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
                'layout_config': self.layout is not None
            },
            'regex_patterns': {
                'whitespace_pattern': self._whitespace_pattern is not None,
                'special_chars_pattern': self._special_chars_pattern is not None,
                'sentence_split_pattern': self._sentence_split_pattern is not None
            },
            'performance': {
                'initialization_time': self._initialization_time,
                'last_operation_time': self._last_operation_time,
                'total_operations': _performance_stats['total_text_processes'] + _performance_stats['total_text_cleans']
            }
        }
        
        return validation_results

# Global text processor instance
text_processor = ImageTextProcessor()

# Convenience functions with performance monitoring
@performance_monitor
def process_text_for_image(text: str, text_type: str = 'question', max_lines: Optional[int] = None) -> List[str]:
    """Process text for image display with performance monitoring"""
    return text_processor.process_text_for_image(text, text_type, max_lines)

@performance_monitor
def calculate_adaptive_font_size(text: str, text_type: str = 'question') -> int:
    """Calculate adaptive font size with performance monitoring"""
    return text_processor.calculate_adaptive_font_size(text, text_type)

def get_font_config(text_type: str = 'question') -> Dict[str, Any]:
    """Get font configuration"""
    return text_processor.get_font_config(text_type)

@performance_monitor
def calculate_text_dimensions(lines: List[str], font_size: int, line_spacing: float) -> Tuple[int, int]:
    """Calculate text dimensions with performance monitoring"""
    return text_processor.calculate_text_dimensions(lines, font_size, line_spacing)

@performance_monitor
def split_long_text(text: str, text_type: str = 'question', max_chars_per_line: Optional[int] = None) -> List[str]:
    """Split long text with performance monitoring"""
    return text_processor.split_long_text(text, text_type, max_chars_per_line)

def add_text_emphasis(text: str, emphasis_type: str = 'bold') -> str:
    """Add text emphasis"""
    return text_processor.add_text_emphasis(text, emphasis_type)

@performance_monitor
def create_text_summary(text: str, max_length: int = 100) -> str:
    """Create text summary with performance monitoring"""
    return text_processor.create_text_summary(text, max_length)

def get_performance_statistics() -> Dict[str, Any]:
    """Get performance statistics"""
    return text_processor.get_performance_statistics()

def reset_performance_stats():
    """Reset performance statistics"""
    text_processor.reset_performance_stats()

def validate_environment() -> Dict[str, Any]:
    """Validate environment"""
    return text_processor.validate_environment()

# Export main functions
__all__ = [
    'ImageTextProcessor',
    'process_text_for_image',
    'calculate_adaptive_font_size',
    'get_font_config',
    'calculate_text_dimensions',
    'split_long_text',
    'add_text_emphasis',
    'create_text_summary',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
