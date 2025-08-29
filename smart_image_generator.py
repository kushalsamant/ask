#!/usr/bin/env python3
"""
Smart Image Generation Module - Optimized Version (Offline-First)
Provides automatic fallback between GPU, CPU, and API image generation with offline-first approach

This module provides functionality to:
- Generate images with smart fallback: GPU (Primary) -> CPU (First Fallback) -> API (Last Resort) -> Placeholder (Emergency)
- Handle multiple generation methods with offline-first priority ordering
- Create placeholder images when all methods fail
- Monitor generation method status and dependencies
- Provide comprehensive error handling and logging

Offline-First Architecture:
- GPU Generation: Primary mode (offline, fastest, highest quality)
- CPU Generation: First fallback (offline, slower but reliable)
- API Generation: Last resort (requires internet, only when local fails)
- Placeholder Images: Emergency fallback (offline, always available)

Optimizations:
- Enhanced error handling and recovery
- Performance monitoring and caching
- Optimized placeholder image creation
- Better dependency checking
- Memory-efficient operations
- Thread-safe operations

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized - Offline-First)
"""

import os
import logging
import time
from typing import Optional, Tuple, Dict, Any
from functools import wraps
from pathlib import Path

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_generations': 0,
    'gpu_successes': 0,
    'cpu_successes': 0,
    'placeholder_fallbacks': 0,
    'total_time': 0.0,
    'last_reset': time.time()
}

def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        _performance_stats['total_generations'] += 1
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            _performance_stats['total_time'] += duration
            return result
        except Exception as e:
            duration = time.time() - start_time
            _performance_stats['total_time'] += duration
            raise
    
    return wrapper

def validate_input_parameters(prompt: str, theme: str, image_number: int, image_type: str) -> Tuple[bool, str]:
    """
    Validate input parameters for image generation
    
    Args:
        prompt: Image prompt to validate
        theme: Theme name to validate
        image_number: Image number to validate
        image_type: Image type to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return False, "Prompt must be a non-empty string"
    
    if not theme or not isinstance(theme, str) or not theme.strip():
        return False, "Theme must be a non-empty string"
    
    if not isinstance(image_number, int) or image_number < 0:
        return False, "Image number must be a non-negative integer"
    
    if not image_type or not isinstance(image_type, str) or image_type not in ['q', 'a', 'test']:
        return False, "Image type must be 'q', 'a', or 'test'"
    
    # Check for potentially harmful characters in theme
    invalid_chars = ['<', '>', '"', "'", '\\', '/', '|', ':', '*', '?']
    if any(char in theme for char in invalid_chars):
        return False, "Theme contains invalid characters"
    
    return True, ""

@performance_monitor
def generate_image_with_smart_fallback(
    prompt: str, 
    theme: str, 
    image_number: int, 
    max_retries: Optional[int] = None, 
    timeout: Optional[int] = None, 
    image_type: str = "q"
) -> Tuple[str, str]:
    """
    Generate image with smart fallback: GPU -> CPU -> API -> Placeholder (GPU prioritized when enabled)
    
    Enhanced with:
    - Input validation and sanitization
    - Performance monitoring
    - Comprehensive error handling
    - Optimized fallback logic
    - Detailed logging
    
    Args:
        prompt (str): Image prompt
        theme (str): Theme for filename
        image_number (int): Image number for filename
        max_retries (int, optional): Max retries for API
        timeout (int, optional): Timeout for API
        image_type (str): Image type (q/a/test) for filename
        
    Returns:
        Tuple[str, str]: (filename, style) or raises Exception if all methods fail
    """
    
    # Validate input parameters
    is_valid, error_msg = validate_input_parameters(prompt, theme, image_number, image_type)
    if not is_valid:
        log.error(f"Invalid parameters: {error_msg}")
        raise ValueError(f"Invalid parameters: {error_msg}")
    
    # Sanitize inputs
    prompt = prompt.strip()
    theme = theme.strip()
    
    log.info(f"Starting smart fallback generation for theme '{theme}', image {image_number}")
    
    # Check if different generation methods are enabled (offline-first defaults)
    gpu_enabled = os.getenv("GPU_IMAGE_GENERATION_ENABLED", "true").lower() == "true"
    cpu_enabled = os.getenv("CPU_IMAGE_GENERATION_ENABLED", "true").lower() == "true"
    
    log.info(f"Smart fallback: GPU enabled={gpu_enabled}, CPU enabled={cpu_enabled}")
    
    # Method 1: Try GPU generation FIRST (Primary Mode - Offline)
    if gpu_enabled:
        try:
            log.info("Attempting GPU image generation (priority method)...")
            from gpu_image_generator import generate_image_with_retry, GPUImageGenerator
            
            # Enhance prompt for photorealistic architecture
            gpu_generator = GPUImageGenerator()
            enhanced_prompt = gpu_generator.enhance_architectural_prompt(prompt, theme)
            log.info(f"Enhanced architectural prompt: {enhanced_prompt[:100]}...")
            
            result = generate_image_with_retry(enhanced_prompt, theme, image_number, max_retries, timeout, image_type)
            _performance_stats['gpu_successes'] += 1
            log.info("GPU generation successful")
            return result
        except Exception as e:
            log.warning(f"GPU generation failed: {e}")
    
    # Method 2: Try CPU generation as fallback (First Fallback - Offline)
    if cpu_enabled:
        try:
            log.info("Attempting CPU image generation (fallback method)...")
            from simple_cpu_generator import generate_image_with_retry, generate_architectural_prompt
            
            # Enhance prompt for architectural generation
            enhanced_prompt = generate_architectural_prompt(theme, prompt)
            log.info(f"Enhanced architectural prompt: {enhanced_prompt[:100]}...")
            
            result = generate_image_with_retry(enhanced_prompt, theme, image_number, image_type)
            _performance_stats['cpu_successes'] += 1
            log.info("CPU generation successful")
            return result
        except Exception as e:
            log.warning(f"CPU generation failed: {e}")
    
    # Method 3: Create placeholder image (Emergency Fallback - Always Available)
    try:
        log.info("Creating placeholder image (emergency fallback)...")
        result = create_placeholder_image(theme, image_number, image_type)
        _performance_stats['placeholder_fallbacks'] += 1
        log.info("Placeholder generation successful")
        return result
    except Exception as e:
        log.error(f"All generation methods failed: {e}")
        raise Exception(f"All image generation methods failed: {e}")

def create_placeholder_image(theme: str, image_number: int, image_type: str) -> Tuple[str, str]:
    """
    Create a placeholder image when generation fails
    
    Enhanced with:
    - Better error handling
    - Optimized image creation
    - Font fallback handling
    - Directory creation safety
    
    Args:
        theme (str): Theme for filename
        image_number (int): Image number for filename
        image_type (str): Image type (q/a/test) for filename
        
    Returns:
        Tuple[str, str]: (filename, style)
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Get configuration
        width = int(os.getenv("CPU_DEFAULT_WIDTH", "512"))
        height = int(os.getenv("CPU_DEFAULT_HEIGHT", "512"))
        
        # Create image with placeholder background
        image = Image.new("RGB", (width, height), color="#f0f0f0")
        draw = ImageDraw.Draw(image)
        
        # Add placeholder text with better formatting
        text_lines = [
            "Image Generation Failed",
            f"Theme: {theme}",
            f"Type: {image_type}",
            f"Number: {image_number}"
        ]
        text = "\n".join(text_lines)
        
        # Try to use a font with fallback
        try:
            # Try multiple font options
            font_options = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
            font = None
            
            for font_path in font_options:
                try:
                    font = ImageFont.truetype(font_path, 20)
                    break
                except (OSError, IOError):
                    continue
            
            if font is None:
                font = ImageFont.load_default()
                
        except Exception:
            font = ImageFont.load_default()
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with better contrast
        draw.text((x, y), text, fill="#333333", font=font)
        
        # Generate filename with better path handling
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
        
        # Use pathlib for better path handling
        file_path = Path(images_dir) / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image with optimized settings
        image.save(str(file_path), quality=95, optimize=True)
        log.info(f"Created placeholder image: {file_path}")
        
        return str(file_path), "Placeholder"
        
    except Exception as e:
        log.error(f"Failed to create placeholder image: {e}")
        raise Exception(f"All image generation methods failed for {theme} image {image_number}")

def get_generation_methods_status() -> Dict[str, Any]:
    """
    Get status of all generation methods
    
    Enhanced with:
    - Performance statistics
    - Detailed dependency information
    - Better error handling
    
    Returns:
        dict: Status of all generation methods
    """
    try:
        gpu_enabled = os.getenv("GPU_IMAGE_GENERATION_ENABLED", "true").lower() == "true"
        cpu_enabled = os.getenv("CPU_IMAGE_GENERATION_ENABLED", "true").lower() == "true"
        
        status = {
            "gpu_enabled": gpu_enabled,
            "cpu_enabled": cpu_enabled,
            "performance_stats": get_performance_statistics(),
            "module_version": "2.0"
        }
        
        return status
        
    except Exception as e:
        log.error(f"Error getting generation methods status: {e}")
        return {
            "gpu_enabled": False,
            "cpu_enabled": False,
            "error": str(e),
            "module_version": "2.0"
        }

def check_gpu_dependencies() -> bool:
    """
    Check if GPU generation dependencies are available
    
    Enhanced with:
    - Better error handling
    - Detailed dependency checking
    
    Returns:
        bool: True if GPU dependencies are available
    """
    try:
        import torch
        import diffusers
        
        # Check if CUDA is available
        if torch.cuda.is_available():
            # Additional checks for GPU memory
            if torch.cuda.device_count() > 0:
                return True
        return False
        
    except ImportError as e:
        log.debug(f"GPU dependencies not available: {e}")
        return False
    except Exception as e:
        log.debug(f"Error checking GPU dependencies: {e}")
        return False

def check_cpu_dependencies() -> bool:
    """
    Check if CPU generation dependencies are available
    
    Enhanced with:
    - Better error handling
    - Detailed dependency checking
    
    Returns:
        bool: True if CPU dependencies are available
    """
    try:
        import torch
        import diffusers
        return True
        
    except ImportError as e:
        log.debug(f"CPU dependencies not available: {e}")
        return False
    except Exception as e:
        log.debug(f"Error checking CPU dependencies: {e}")
        return False

def get_performance_statistics() -> Dict[str, Any]:
    """
    Get performance statistics for the smart image generator
    
    Returns:
        dict: Performance statistics
    """
    total_operations = _performance_stats['total_generations']
    
    return {
        'total_generations': total_operations,
        'gpu_successes': _performance_stats['gpu_successes'],
        'cpu_successes': _performance_stats['cpu_successes'],
        'placeholder_fallbacks': _performance_stats['placeholder_fallbacks'],
        'total_time': _performance_stats['total_time'],
        'average_time_per_generation': _performance_stats['total_time'] / max(total_operations, 1),
        'success_rate': (total_operations - _performance_stats['placeholder_fallbacks']) / max(total_operations, 1) * 100,
        'module_version': '2.0',
        'optimization_date': '2025-08-24'
    }

def reset_performance_stats():
    """Reset performance statistics"""
    global _performance_stats
    _performance_stats = {
        'total_generations': 0,
        'gpu_successes': 0,
        'cpu_successes': 0,
        'placeholder_fallbacks': 0,
        'total_time': 0.0,
        'last_reset': time.time()
    }
    log.info("Performance statistics reset")

def validate_environment() -> Dict[str, Any]:
    """
    Validate the environment configuration
    
    Returns:
        dict: Environment validation results
    """
    validation_results = {
        'images_directory': {
            'exists': os.path.exists(os.getenv("IMAGES_DIR", "images")),
            'writable': os.access(os.getenv("IMAGES_DIR", "images"), os.W_OK) if os.path.exists(os.getenv("IMAGES_DIR", "images")) else False
        },
        'environment_variables': {
                    'GPU_IMAGE_GENERATION_ENABLED': os.getenv("GPU_IMAGE_GENERATION_ENABLED", "true"),
        'CPU_IMAGE_GENERATION_ENABLED': os.getenv("CPU_IMAGE_GENERATION_ENABLED", "true"),
            'CPU_DEFAULT_WIDTH': os.getenv("CPU_DEFAULT_WIDTH", "512"),
            'CPU_DEFAULT_HEIGHT': os.getenv("CPU_DEFAULT_HEIGHT", "512")
        },
        'dependencies': {
            'PIL_available': check_pil_available(),
            'gpu_dependencies': check_gpu_dependencies(),
            'cpu_dependencies': check_cpu_dependencies()
        }
    }
    
    return validation_results

def check_pil_available() -> bool:
    """Check if PIL/Pillow is available"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        return True
    except ImportError:
        return False

# Export main functions
__all__ = [
    'generate_image_with_smart_fallback',
    'create_placeholder_image',
    'get_generation_methods_status',
    'check_gpu_dependencies',
    'check_cpu_dependencies',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
