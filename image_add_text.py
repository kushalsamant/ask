#!/usr/bin/env python3
"""
Text Overlay Module
Professional text overlay using PDF layout standards
"""

import os
import time
from typing import Optional, Tuple, List, Dict, Any

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {'total_operations': 0, 'successful_operations': 0, 'failed_operations': 0, 'total_time': 0.0}
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics['total_time'] += duration
            self.metrics['total_operations'] += 1
    
    def record_success(self):
        self.metrics['successful_operations'] += 1
    
    def record_failure(self):
        self.metrics['failed_operations'] += 1
    
    def get_stats(self):
        stats = self.metrics.copy()
        stats['success_rate'] = (self.metrics['successful_operations'] / max(self.metrics['total_operations'], 1)) * 100
        return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()

def validate_input_parameters(image_path: str, prompt: str, image_number: Any, is_question: bool = True) -> Tuple[bool, str]:
    """Enhanced input validation"""
    try:
        if not image_path or not isinstance(image_path, str):
            return False, "Invalid image path"
        if not prompt or not isinstance(prompt, str):
            return False, "Invalid prompt"
        if len(prompt.strip()) == 0:
            return False, "Empty prompt"
        if image_number is None:
            return False, "Invalid image number"
        if not isinstance(is_question, bool):
            return False, "Invalid is_question parameter"
        return True, "All parameters valid"
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        return False, f"Validation error: {str(e)}"

def validate_image_file(image_path: str) -> Tuple[bool, str]:
    """Validate image file exists and is accessible"""
    try:
        if not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
        if not os.path.isfile(image_path):
            return False, f"Path is not a file: {image_path}"
        if not os.access(image_path, os.R_OK):
            return False, f"Image file is not readable: {image_path}"
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            return False, f"Image file is empty: {image_path}"
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return False, f"Image file too large: {file_size} bytes"
        return True, "Image file valid"
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        return False, f"Image validation error: {str(e)}"

def create_font_with_fallback(font_file: str, font_size: int):
    """Create font with enhanced fallback mechanism"""
    try:
        if os.path.exists(font_file):
            return ImageFont.truetype(font_file, font_size)
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.warning(f"Failed to load font {font_file}: {e}")
    
    try:
        system_fonts = ['arial.ttf', 'Arial.ttf', 'times.ttf', 'Times.ttf', 'calibri.ttf', 'Calibri.ttf']
        for system_font in system_fonts:
            try:
                return ImageFont.truetype(system_font, font_size)
            except:
                continue
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.warning(f"Failed to load system fonts: {e}")
    
    log.warning("Using default font as fallback")
    return ImageFont.load_default()
import logging
import re
import shutil
from PIL import Image, ImageDraw, ImageFont
from image_layout_creator import layout_creator
from image_text_processor import text_processor
from image_create_ai import generate_image_with_retry

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))
IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))

def add_text_overlay(image_path, prompt, image_number, is_question=True):
    """Add professional text overlay using PDF formatting standards"""
    log.info(f"Starting text overlay for {image_path} with prompt: {prompt[:50]}...")
    
    # For answers, check if we need multiple images
    if not is_question and len(prompt) > 500:  # If answer is long, use multi-image approach
        log.info(f"Long answer detected ({len(prompt)} chars), using multi-image approach")
        return _add_text_overlay_multi_image(image_path, prompt, image_number, is_question)
    else:
        # Force fallback method for now to ensure text appears
        log.info("Using fallback text overlay method to ensure text visibility")
        return _add_text_overlay_fallback(image_path, prompt, image_number, is_question)

def _add_text_overlay_fallback(image_path, prompt, image_number, is_question=True):
    """Fallback text overlay method (original implementation)"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Font settings - all text sizes equal to brand text size
        font_file = os.getenv('FONT_FILE_PATH', 'fonts/arial.ttf')
        brand_font_size = int(os.getenv('BRAND_FONT_SIZE', '36'))
        
        # All text sizes equal to brand text size
        main_font_size = brand_font_size
        number_font_size = brand_font_size

        # Create fonts with enhanced fallback
        main_font = create_font_with_fallback(font_file, main_font_size)
        brand_font = create_font_with_fallback(font_file, brand_font_size)
        number_font = create_font_with_fallback(font_file, number_font_size)

        # Create overlay - fill the whole image
        overlay_height = IMAGE_HEIGHT  # Full image height
        overlay_y = 0  # Start from top

        # Gradient overlay covering entire image
        overlay = Image.new('RGBA', (IMAGE_WIDTH, overlay_height), (0, 0, 0, 0))
        for i in range(overlay_height):
            # Create gradient from top to bottom
            alpha = int(150 - (i * 50 / overlay_height))  # Lighter gradient for full image
            alpha = max(80, min(150, alpha))  # Keep alpha between 80-150 for readability
            line_overlay = Image.new('RGBA', (IMAGE_WIDTH, 1), (0, 0, 0, alpha))
            overlay.paste(line_overlay, (0, i))

        img.paste(overlay, (0, overlay_y), overlay)

        # Add full overlay for readability
        full_overlay = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
        for i in range(IMAGE_HEIGHT):
            # Create gradient from top to bottom for full image readability
            alpha = int(120 - (i * 40 / IMAGE_HEIGHT))  # Lighter gradient for full image
            alpha = max(60, min(120, alpha))  # Keep alpha between 60-120 for readability
            line_overlay = Image.new('RGBA', (IMAGE_WIDTH, 1), (0, 0, 0, alpha))
            full_overlay.paste(line_overlay, (0, i))

        img.paste(full_overlay, (0, 0), full_overlay)

        # Prepare prompt text - consistent wrapping for questions and answers
        max_chars_per_line = int(os.getenv('MAX_CHARS_PER_LINE', '35'))

        words = prompt.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)

        # Colors
        text_color = (240, 240, 240)  # Light gray
        brand_color = (52, 73, 94)    # Dark blue-gray

        # Calculate 1-inch margins (assuming 96 DPI for screen)
        # 1 inch = 96 pixels
        margin_inches = 1
        margin_pixels = int(margin_inches * 96)
        
        # Define safe areas within 1-inch margins
        left_margin = margin_pixels
        right_margin = IMAGE_WIDTH - margin_pixels
        top_margin = margin_pixels
        bottom_margin = IMAGE_HEIGHT - margin_pixels
        
        # Define brand positioning within 1-inch margins
        brand_y = bottom_margin - 100  # 100px from bottom margin

        # Calculate brand text height for proper spacing
        brand_text = "ASK: Daily Architectural Research"
        brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_text_height = brand_bbox[3] - brand_bbox[1]
        
        # Draw divider 2x brand text size above brand text
        divider_y = brand_y - (brand_text_height * 2)  # 2x brand text size above brand text
        divider_start_x = left_margin  # Start from left margin
        divider_end_x = right_margin  # End at right margin (full width)
        divider_color = (255, 255, 255)  # White divider
        draw.line([(divider_start_x, divider_y), (divider_end_x, divider_y)], fill=divider_color, width=2)

        # Calculate positions for left-aligned text, bottom to top arrangement
        # Question text starts 2x brand text size above divider
        spacing = brand_text_height * 2
        text_start_y = divider_y - spacing  # Start 2x brand text size above the divider
        line_height = main_font_size + 10
        
        # Draw text lines from bottom to top
        for i, line in enumerate(lines):
            # Calculate position from bottom up
            text_y = text_start_y - (len(lines) - 1 - i) * line_height
            
            # Don't go too high up - stay within 1-inch top margin
            if text_y < top_margin + 50:  # 50px buffer from top margin
                break
                
            # Left align text within 1-inch margin
            text_x = left_margin
                
            # Get text dimensions
            bbox = draw.textbbox((0, 0), line, font=main_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Check if text fits within right margin
            if text_x + text_width > right_margin:
                break  # Stop if text would exceed right margin
            
            # Draw text with shadow
            shadow_offset = 2
            draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=main_font, fill=(0, 0, 0, 100))
            draw.text((text_x, text_y), line, font=main_font, fill=text_color)

        # Draw full brand text on LEFT with "ASK" in italics and bold
        brand_x = left_margin  # Left aligned within 1-inch margin
        
        # Split text to handle "ASK" in italics/bold
        ask_part = "ASK"
        rest_part = ": Daily Architectural Research"
        
        # Draw "ASK" in bold/italics (if font supports it)
        try:
            bold_font = ImageFont.truetype(font_file, brand_font_size)
        except:
            bold_font = brand_font
        
        draw.text((brand_x, brand_y), ask_part, font=bold_font, fill=(255, 255, 255))
        
        # Get width of "ASK" to position the rest
        ask_bbox = draw.textbbox((0, 0), ask_part, font=bold_font)
        ask_width = ask_bbox[2] - ask_bbox[0]
        
        # Draw the rest of the text
        draw.text((brand_x + ask_width, brand_y), rest_part, font=brand_font, fill=(255, 255, 255))

        # Theme text removed - no longer displaying theme on images

        # Draw image number on TOP RIGHT, right-aligned and bold within 1-inch margins
        # Handle image numbers that might contain dashes (e.g., "01-2")
        try:
            # Try to convert to int for formatting
            number_display = f"ASK {int(image_number):02d}"
        except ValueError:
            # If it contains dashes or other characters, use as-is
            number_display = f"ASK {image_number}"
        
        number_bbox = draw.textbbox((0, 0), number_display, font=number_font)
        number_width = number_bbox[2] - number_bbox[0]
        number_x = right_margin - number_width  # Right-aligned within 1-inch margin
        number_y = top_margin  # Top within 1-inch margin
        draw.text((number_x, number_y), number_display, font=number_font, fill=(255, 255, 255))

        # Save the enhanced image
        img.save(image_path, quality=IMAGE_QUALITY, optimize=True)
        
        log.info(f"Added fallback text overlay to image: {image_path}")
        # Record success and end timer
        performance_monitor.end_timer()
        performance_monitor.record_success()
        
        return image_path
        
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.error(f"Error adding fallback text overlay to {image_path}: {e}")
        # Record success and end timer
        performance_monitor.end_timer()
        performance_monitor.record_success()
        
        return image_path

def _add_text_overlay_multi_image(image_path, prompt, image_number, is_question=True):
    """Handle long answers by creating multiple images"""
    try:
        # Split text into manageable chunks
        text_chunks = _split_text_into_chunks(prompt)
        
        if len(text_chunks) == 1:
            # If only one chunk, use regular fallback
            return _add_text_overlay_fallback(image_path, prompt, image_number, is_question)
        
        # Create multiple images for the chunks
        image_paths = []
        base_image_number = int(image_number) if isinstance(image_number, str) and image_number.isdigit() else int(str(image_number).split('-')[0])
        
        for i, chunk in enumerate(text_chunks):
            # Use sequential integer numbering for display (ASK 01, ASK 02, etc.)
            display_image_number = base_image_number + i
            
            if i == 0:
                # Use the original image for the first chunk
                current_image_path = image_path
                current_image_number = str(display_image_number)
            else:
                # Create new image for additional chunks
                current_image_number = str(display_image_number)
                current_image_path = _create_new_image_for_chunk(chunk, current_image_number, image_path)
            
            # Add text overlay to this chunk
            result_path = _add_text_overlay_fallback(current_image_path, chunk, current_image_number, is_question)
            image_paths.append(result_path)
            
            log.info(f"Created image {i+1}/{len(text_chunks)}: {os.path.basename(result_path)}")
        
        # Return all image paths for multi-image support
        log.info(f"Created {len(image_paths)} images for long answer")
        # Record success and end timer
        performance_monitor.end_timer()
        performance_monitor.record_success()
        
        return image_paths if image_paths else [image_path]
        
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.error(f"Error in multi-image text overlay: {e}")
        # Fallback to single image
        return _add_text_overlay_fallback(image_path, prompt, image_number, is_question)

def _split_text_into_chunks(text, max_chars_per_chunk=800):
    """Split text into chunks that fit on images"""
    try:
        # Split by sentences first
        sentences = _split_into_sentences(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit
            if len(current_chunk) + len(sentence) > max_chars_per_chunk and current_chunk:
                # Add ellipsis to indicate text continues, ensuring it doesn't break words
                chunk_with_ellipsis = _add_ellipsis_safely(current_chunk.strip())
                chunks.append(chunk_with_ellipsis)
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk (no ellipsis for the final chunk)
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
        
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.error(f"Error splitting text into chunks: {e}")
        # Fallback: split by character count with ellipsis
        chunks = []
        for i in range(0, len(text), max_chars_per_chunk):
            chunk = text[i:i+max_chars_per_chunk]
            if i + max_chars_per_chunk < len(text):  # Not the last chunk
                chunk = _add_ellipsis_safely(chunk)
            chunks.append(chunk)
        return chunks

def _add_ellipsis_safely(text):
    """Add ellipsis to text without breaking words"""
    if not text:
        return "..."
    
    # If the text already ends with a complete word, just add ellipsis
    if text.endswith(' ') or text.endswith('.') or text.endswith('!') or text.endswith('?'):
        return text.strip() + "..."
    
    # Find the last complete word boundary
    words = text.split()
    if len(words) <= 1:
        # If there's only one word or no words, just add ellipsis
        return text.strip() + "..."
    
    # Remove the last word to avoid breaking it
    text_without_last_word = ' '.join(words[:-1])
    
    # Add ellipsis after the complete words
    return text_without_last_word.strip() + "..."

def _split_into_sentences(text):
    """Split text into sentences"""
    # Split by sentence endings (.!?) followed by space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def _create_new_image_for_chunk(chunk, image_number, original_image_path):
    """Create a new image for a text chunk"""
    try:
        
        # Extract theme from original image path
        filename = os.path.basename(original_image_path)
        parts = filename.split('-')
        if len(parts) >= 3:
            theme = parts[2]  # Extract theme from filename
        else:
            theme = 'architectural_design'  # Default
        
        # Generate new image for this chunk
        # image_number is now a simple integer string (e.g., "02", "03")
        try:
            image_number_int = int(image_number)
        except ValueError:
            # If conversion fails, use a simple counter
            image_number_int = 1
        
        new_image_path, _ = generate_image_with_retry(
            prompt=chunk,
            theme=theme,
            image_number=image_number_int,
            image_type="a"
        )
        
        if new_image_path:
            log.info(f"Generated new image for chunk: {os.path.basename(new_image_path)}")
            return new_image_path
        else:
            # Fallback: copy original image with new number
            new_path = original_image_path.replace('.jpg', f'-{image_number}.jpg')
            shutil.copy2(original_image_path, new_path)
            return new_path
            
    except Exception as e:
        log.error(f"Error in enhanced text overlay: {e}")
        performance_monitor.end_timer()
        performance_monitor.record_failure()
        return image_path
        log.error(f"Error creating new image for chunk: {e}")
        # Fallback: copy original image with new number
        new_path = original_image_path.replace('.jpg', f'-{image_number}.jpg')
        shutil.copy2(original_image_path, new_path)
        return new_path


def get_performance_stats():
    """Get performance statistics"""
    return performance_monitor.get_stats()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    log.info("Performance statistics reset")
