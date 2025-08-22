#!/usr/bin/env python3
"""
Image Text Processor Module
Enhanced text processing using PDF formatting rules for images
"""

import textwrap
import re
import logging
from typing import List, Dict, Tuple, Optional
from image_typography_config import typography_config
from image_layout_config import layout_config

# Setup logging
log = logging.getLogger(__name__)

class ImageTextProcessor:
    """Enhanced text processing using PDF standards"""
    
    def __init__(self):
        """Initialize text processor"""
        self.typography = typography_config
        self.layout = layout_config
    
    def process_text_for_image(self, text: str, text_type: str = 'question', 
                              max_lines: Optional[int] = None) -> List[str]:
        """
        Process text for image display using PDF formatting rules
        
        Args:
            text: Text content to process
            text_type: Type of text ('question', 'answer', 'title')
            max_lines: Maximum number of lines (None for unlimited)
            
        Returns:
            List of processed text lines
        """
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Get wrap width for text type
            wrap_width = self.layout.get_text_wrap_width(text_type)
            
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
            
            return processed_lines
            
        except Exception as e:
            log.error(f"Error processing text for image: {e}")
            # Return original text as fallback
            return [text[:50] + "..." if len(text) > 50 else text]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\.,!?;:()\-]', '', text)
        
        # Normalize quotes and apostrophes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text
    
    def _apply_image_line_processing(self, lines: List[str], text_type: str) -> List[str]:
        """
        Apply PDF-style line processing
        
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
        Format individual line using PDF standards
        
        Args:
            line: Text line
            text_type: Type of text
            is_first_line: Whether this is the first line
            
        Returns:
            Formatted line
        """
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
        
        # Ensure proper capitalization
        if line and not line[0].isupper():
            line = line[0].upper() + line[1:]
        
        return line
    
    def calculate_adaptive_font_size(self, text: str, text_type: str = 'question') -> int:
        """
        Calculate adaptive font size using PDF scaling logic
        
        Args:
            text: Text content
            text_type: Type of text
            
        Returns:
            Adaptive font size
        """
        return self.typography.calculate_adaptive_font_size(text, text_type)
    
    def get_font_config(self, text_type: str = 'question') -> Dict[str, any]:
        """
        Get font configuration for text type
        
        Args:
            text_type: Type of text
            
        Returns:
            Font configuration dictionary
        """
        return self.typography.get_font_config(text_type)
    
    def calculate_text_dimensions(self, lines: List[str], font_size: int, 
                                 line_spacing: float) -> Tuple[int, int]:
        """
        Calculate text dimensions for layout positioning
        
        Args:
            lines: List of text lines
            font_size: Font size in pixels
            line_spacing: Line spacing multiplier
            
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            # Estimate line height
            line_height = int(font_size * line_spacing * self.layout.LINE_SPACING_MULTIPLIER)
            
            # Calculate total height
            total_height = len(lines) * line_height
            
            # Estimate width (use longest line)
            max_width = 0
            for line in lines:
                # Rough estimate: 0.6 * font_size per character
                estimated_width = len(line) * int(font_size * 0.6)
                max_width = max(max_width, estimated_width)
            
            return (max_width, total_height)
            
        except Exception as e:
            log.error(f"Error calculating text dimensions: {e}")
            return (400, 200)  # Fallback dimensions
    
    def split_long_text(self, text: str, text_type: str = 'question', 
                       max_chars_per_line: Optional[int] = None) -> List[str]:
        """
        Split long text into manageable chunks using PDF logic
        
        Args:
            text: Long text content
            text_type: Type of text
            max_chars_per_line: Maximum characters per line
            
        Returns:
            List of text chunks
        """
        if not max_chars_per_line:
            max_chars_per_line = self.layout.get_text_wrap_width(text_type)
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
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
        
        return chunks
    
    def add_text_emphasis(self, text: str, emphasis_type: str = 'bold') -> str:
        """
        Add text emphasis using PDF-style formatting
        
        Args:
            text: Text content
            emphasis_type: Type of emphasis ('bold', 'italic', 'underline')
            
        Returns:
            Text with emphasis markers
        """
        # For now, return text as-is since PIL handles emphasis through font selection
        # In a more advanced implementation, this could add markdown-style formatting
        return text
    
    def create_text_summary(self, text: str, max_length: int = 100) -> str:
        """
        Create text summary using PDF truncation logic
        
        Args:
            text: Full text content
            max_length: Maximum length for summary
            
        Returns:
            Text summary
        """
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

# Global text processor instance
text_processor = ImageTextProcessor()
