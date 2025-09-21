#!/usr/bin/env python3
"""
Optimized GPU Image Generation Module
Handles GPU-accelerated image generation using diffusers for NVIDIA GPUs
Optimized for GTX 1650 and similar mid-range GPUs
Enhanced with better error handling, performance monitoring, and configuration management
"""

import os
import logging
import random
import torch
from PIL import Image
from typing import Optional, Tuple, Dict, Any
import time
import json
from datetime import datetime

# Setup logging
log = logging.getLogger(__name__)

# Environment variables with enhanced defaults
IMAGES_DIR = os.getenv("IMAGES_DIR", "images")
IMAGE_FILENAME_TEMPLATE = os.getenv("IMAGE_FILENAME_TEMPLATE", "ASK-{image_number:02d}-{theme}-{image_type}.jpg")

class PerformanceMonitor:
    """Performance monitoring for GPU image generation"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'total_time': 0.0,
            'avg_generation_time': 0.0
        }
    
    def start_timer(self):
        """Start performance timer"""
        self.start_time = time.time()
    
    def end_timer(self):
        """End performance timer and update metrics"""
        if self.start_time:
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            self.metrics['total_time'] += duration
            self.metrics['total_generations'] += 1
            
            if self.metrics['total_generations'] > 0:
                self.metrics['avg_generation_time'] = self.metrics['total_time'] / self.metrics['total_generations']
    
    def record_success(self):
        """Record successful generation"""
        self.metrics['successful_generations'] += 1
    
    def record_failure(self):
        """Record failed generation"""
        self.metrics['failed_generations'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.metrics.copy()
        stats['success_rate'] = (self.metrics['successful_generations'] / max(self.metrics['total_generations'], 1)) * 100
        return stats

class GPUImageGenerator:
    """Enhanced GPU-accelerated image generator using diffusers"""
    
    def __init__(self):
        """Initialize GPU image generator with enhanced features"""
        self.pipe = None
        self.model_loaded = False
        self.model_id = os.getenv("GPU_MODEL_ID", "runwayml/stable-diffusion-v1-5")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.performance_monitor = PerformanceMonitor()
        
        # Enhanced GPU optimization settings for GTX 1650
        self.enable_attention_slicing = os.getenv("GPU_ATTENTION_SLICING", "true").lower() == "true"
        self.enable_memory_efficient_attention = os.getenv("GPU_MEMORY_EFFICIENT_ATTENTION", "true").lower() == "true"
        self.enable_vae_slicing = os.getenv("GPU_VAE_SLICING", "true").lower() == "true"
        self.enable_model_cpu_offload = os.getenv("GPU_MODEL_CPU_OFFLOAD", "false").lower() == "true"
        
        # Enhanced generation settings optimized for GTX 1650
        self.default_steps = int(os.getenv("GPU_DEFAULT_STEPS", "20"))
        self.default_guidance_scale = float(os.getenv("GPU_DEFAULT_GUIDANCE_SCALE", "7.5"))
        self.default_height = int(os.getenv("GPU_DEFAULT_HEIGHT", "512"))
        self.default_width = int(os.getenv("GPU_DEFAULT_WIDTH", "512"))
        
        # Enhanced configuration
        self.max_retries = int(os.getenv("GPU_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("GPU_RETRY_DELAY", "1.0"))
        
        # Check GPU capabilities with enhanced logging
        self._check_gpu_capabilities()
        
        log.info(f"Enhanced GPU Image Generator initialized with model: {self.model_id}")
    
    def _check_gpu_capabilities(self):
        """Enhanced GPU capability checking"""
        try:
            if torch.cuda.is_available():
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                log.info(f"GPU detected: {self.gpu_name} ({self.gpu_memory:.1f}GB)")
                
                # Enhanced settings based on GPU memory
                if self.gpu_memory < 4:  # GTX 1650 has 4GB
                    self.enable_attention_slicing = True
                    self.enable_vae_slicing = True
                    self.default_height = 512
                    self.default_width = 512
                    log.info("Applied enhanced memory optimizations for 4GB GPU")
                elif self.gpu_memory < 8:  # Mid-range GPUs
                    self.enable_attention_slicing = True
                    log.info("Applied memory optimizations for mid-range GPU")
                else:
                    log.info("High-end GPU detected, using standard optimizations")
            else:
                log.warning("No CUDA GPU detected, falling back to CPU")
                self.device = "cpu"
        except Exception as e:
            log.error(f"Error checking GPU capabilities: {e}")
            self.device = "cpu"
    
    def _validate_input(self, prompt: str, theme: str, image_number: int, 
                       image_type: str, style: Optional[str]) -> bool:
        """Enhanced input validation"""
        try:
            if not prompt or not prompt.strip():
                log.error("Prompt cannot be empty")
                return False
            
            if not theme or not theme.strip():
                log.error("Theme cannot be empty")
                return False
            
            if not isinstance(image_number, int) or image_number < 0:
                log.error("Image number must be a positive integer")
                return False
            
            if not image_type or image_type not in ['q', 'a', 'test']:
                log.error("Image type must be 'q', 'a', or 'test'")
                return False
            
            return True
            
        except Exception as e:
            log.error(f"Input validation error: {e}")
            return False
    
    def _ensure_output_directory(self) -> bool:
        """Ensure output directory exists"""
        try:
            os.makedirs(IMAGES_DIR, exist_ok=True)
            return True
        except Exception as e:
            log.error(f"Failed to create output directory: {e}")
            return False
    
    def load_model(self):
        """Enhanced model loading with better error handling"""
        if self.model_loaded:
            return True
            
        try:
            log.info(f"Loading model: {self.model_id}")
            
            # Import diffusers here to avoid dependency issues if not installed
            from diffusers import AutoPipelineForText2Image
            
            # Load the pipeline with enhanced GPU optimizations
            self.pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True
            )
            
            # Move to device
            self.pipe = self.pipe.to(self.device)
            
            # Apply enhanced GPU optimizations
            if self.device == "cuda":
                if self.enable_attention_slicing:
                    self.pipe.enable_attention_slicing()
                    log.info("Enabled attention slicing for GPU optimization")
                
                if self.enable_memory_efficient_attention:
                    try:
                        self.pipe.enable_xformers_memory_efficient_attention()
                        log.info("Enabled memory efficient attention")
                    except Exception as e:
                        log.warning(f"Memory efficient attention not available: {e}")
                
                if self.enable_vae_slicing:
                    self.pipe.enable_vae_slicing()
                    log.info("Enabled VAE slicing for memory optimization")
                
                if self.enable_model_cpu_offload:
                    self.pipe.enable_model_cpu_offload()
                    log.info("Enabled model CPU offload")
            
            self.model_loaded = True
            log.info("Enhanced GPU model loaded successfully")
            return True
            
        except ImportError:
            log.error("Diffusers not installed. Install with: pip install diffusers transformers accelerate safetensors")
            return False
        except Exception as e:
            log.error(f"Failed to load enhanced GPU model: {e}")
            return False
    
    def generate_image(self, prompt: str, theme: str, image_number: int, 
                      image_type: str = "q", style: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Enhanced image generation using GPU-accelerated diffusion
        
        Args:
            prompt (str): Image prompt
            theme (str): Theme for filename
            image_number (int): Image number for filename
            image_type (str): Image type (q/a) for filename
            style (str): ural style to apply
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (filename, style) or (None, None) if failed
        """
        # Start performance monitoring
        self.performance_monitor.start_timer()
        
        try:
            # Enhanced input validation
            if not self._validate_input(prompt, theme, image_number, image_type, style):
                self.performance_monitor.record_failure()
                return None, None
            
            # Load model if not already loaded
            if not self.load_model():
                self.performance_monitor.record_failure()
                return None, None
            
            # Get style if not provided
            if not style:
                style = self._get_style_for_theme(theme)
            
            # Craft enhanced prompt for GPU generation
            formatted_prompt = self._format_prompt(prompt, theme, style)
            
            log.info(f"Generating enhanced GPU image for {theme} (style: {style})")
            
            # Generate image with enhanced GPU optimizations
            with torch.autocast("cuda" if self.device == "cuda" else "cpu"):
                image = self.pipe(
                    prompt=formatted_prompt,
                    negative_prompt=self.get_ural_negative_prompt(),
                    num_inference_steps=self.default_steps,
                    guidance_scale=self.default_guidance_scale,
                    height=self.default_height,
                    width=self.default_width
                ).images[0]
            
            # Ensure output directory exists
            if not self._ensure_output_directory():
                self.performance_monitor.record_failure()
                return None, None
            
            # Generate filename
            filename = f"{IMAGES_DIR}/{IMAGE_FILENAME_TEMPLATE.format(image_number=int(image_number), theme=theme, image_type=image_type)}"
            
            # Save image with enhanced quality
            image.save(filename, quality=95)
            log.info(f"Generated enhanced {theme} image {image_number}: {filename}")
            
            # Record success and end timer
            self.performance_monitor.end_timer()
            self.performance_monitor.record_success()
            
            return filename, style
            
        except Exception as e:
            log.error(f"Failed to generate enhanced GPU image: {e}")
            self.performance_monitor.end_timer()
            self.performance_monitor.record_failure()
            return None, None
    
    def enhance_research_prompt(self, prompt: str, theme: str) -> str:
    """
    Enhance prompt for photorealistic research generation
        
        Args:
            prompt (str): Original prompt
            theme (str): Theme name
            
        Returns:
            str: Enhanced ural prompt
        """
        research_enhancements = {
            'design_research': "photorealistic research visualization, modern research facility, glass facade, sustainable design, natural lighting, professional photography, 8k resolution, research photography, detailed textures, realistic materials",
            'technology_innovation': "photorealistic research visualization, futuristic tech facility, smart glass, LED lighting, digital infrastructure, professional photography, 8k resolution, modern research, cutting-edge design, technological integration",
            'sustainability_science': "photorealistic research visualization, green research facility, living walls, solar panels, sustainable materials, natural environment, professional photography, 8k resolution, eco-friendly design, renewable energy",
            'engineering_systems': "photorealistic research visualization, industrial facility, structural engineering, mechanical systems, technical infrastructure, professional photography, 8k resolution, functional research, technical design",
            'environmental_design': "photorealistic research visualization, environmental facility, natural integration, landscape design, sustainable design, professional photography, 8k resolution, environmental harmony, natural materials",
            'urban_planning': "photorealistic research visualization, urban development, city planning, mixed-use facility, urban infrastructure, professional photography, 8k resolution, modern urban design, sustainable urban planning",
            'spatial_design': "photorealistic research visualization, spatial design, interior design, spatial planning, modern interior, professional photography, 8k resolution, interior design, space planning",
            'digital_technology': "photorealistic research visualization, digital facility, smart technology, technological integration, modern digital design, professional photography, 8k resolution, smart systems, technological innovation"
        }
        
        enhancement = research_enhancements.get(theme.lower(), research_enhancements['design_research'])
        enhanced_prompt = f"{prompt}, {enhancement}"
        
        return enhanced_prompt
    
    def get_research_negative_prompt(self) -> str:
    """
    Get negative prompt to avoid common issues in research generation
        
        Returns:
            str: Negative prompt for ural images
        """
        return "blurry, low quality, cartoon, anime, painting, sketch, drawing, abstract, unrealistic, distorted, deformed, ugly, bad anatomy, watermark, signature, text, logo, oversaturated, underexposed, overexposed, noise, artifacts"
    
    def _get_style_for_theme(self, theme: str) -> str:
        """Enhanced style selection for theme"""
        try:
            # Import style-related modules
            from style_data_manager import get_base_styles_for_category
            from style_ai_generator import get_ai_generated_style_suggestion, create_dynamic_style_combination
            
            # Get available styles
            available_styles = get_base_styles_for_category(theme)
            if not available_styles:
                log.warning(f"No styles found for theme {theme}, using default")
                return "Modern"  # Fallback
            
            # Try AI suggestions first
            ai_suggestions = get_ai_generated_style_suggestion(theme, "")
            if ai_suggestions:
                selected_style = random.choice(ai_suggestions)
                return create_dynamic_style_combination(theme, selected_style, "")
            else:
                # Fallback to random selection
                return random.choice(available_styles)
                
        except Exception as e:
            log.warning(f"Could not get style for theme {theme}: {e}")
            return "Modern"  # Default fallback
    
    def _format_prompt(self, prompt: str, theme: str, style: str) -> str:
        """Enhanced prompt formatting for GPU generation with contextual ural focus"""
        # Determine if theme benefits from ural context
        ural_themes = {
            'design_research', 'ural_design', 'urban_planning', 'urban_design', 
            'spatial_design', 'interior_environments', 'construction_technology', 
            'engineering_systems', 'environmental_design'
        }
        
        non_ural_themes = {
            'technology_innovation', 'digital_technology', 'sustainability_science'
        }
        
        if theme.lower() in ural_themes:
            # ural focus for design/construction themes
            return (
                f"Professional ural visualization, {style} ural style. "
                f"Focus on {theme} aspects. {prompt} "
                f"High-quality, photorealistic, detailed, professional photography, ural visualisation, 8k resolution, "
                f"real-life objects, natural lighting, realistic materials, authentic ural elements"
            )
        elif theme.lower() in non_ural_themes:
            # Broader focus for technology/innovation themes
            return (
                f"Professional research visualization, {style} style. "
                f"Focus on {theme} aspects. {prompt} "
                f"High-quality, photorealistic, detailed, professional photography, 8k resolution, "
                f"real-life objects, natural lighting, realistic materials, modern technology, innovation"
            )
        else:
            # Balanced approach for other themes
            return (
                f"Professional research visualization, {style} style with ural elements. "
                f"Focus on {theme} aspects. {prompt} "
                f"High-quality, photorealistic, detailed, professional photography, 8k resolution, "
                f"real-life objects, natural lighting, realistic materials, modern context"
            )
    
    def get_model_info(self) -> dict:
        """Enhanced model information retrieval"""
        return {
            "model_id": self.model_id,
            "device": self.device,
            "loaded": self.model_loaded,
            "gpu_name": getattr(self, "gpu_name", "None"),
            "gpu_memory_gb": getattr(self, "gpu_memory", 0),
            "default_steps": self.default_steps,
            "default_guidance_scale": self.default_guidance_scale,
            "default_height": self.default_height,
            "default_width": self.default_width,
            "optimizations": {
                "attention_slicing": self.enable_attention_slicing,
                "memory_efficient_attention": self.enable_memory_efficient_attention,
                "vae_slicing": self.enable_vae_slicing,
                "model_cpu_offload": self.enable_model_cpu_offload
            },
            "performance_stats": self.performance_monitor.get_stats()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_monitor.get_stats()

# Global instance
gpu_generator = GPUImageGenerator()

def generate_image_with_retry(prompt, theme, image_number, max_retries=None, timeout=None, image_type="q"):
    """
    Enhanced image generation with retry logic (compatible with existing API interface)
    
    Args:
        prompt (str): Image prompt
        theme (str): Theme for filename
        image_number (int): Image number for filename
        max_retries (int): Maximum retry attempts
        timeout (int): Timeout in seconds
        image_type (str): Image type (q/a) for filename
        
    Returns:
        Tuple[str, str]: (filename, style) or raises Exception if failed
    """
    max_retries = max_retries or gpu_generator.max_retries
    timeout = timeout or 300  # 5 minutes default
    
    for attempt in range(max_retries):
        try:
            filename, style = gpu_generator.generate_image(prompt, theme, image_number, image_type)
            
            if filename and style:
                return filename, style
            else:
                log.warning(f"Generation attempt {attempt + 1} failed")
                if attempt < max_retries - 1:
                    time.sleep(gpu_generator.retry_delay)
                    
        except Exception as e:
            log.error(f"Generation attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                time.sleep(gpu_generator.retry_delay)
    
    raise Exception(f"Failed to generate GPU image for {theme} image {image_number} after {max_retries} attempts")

def get_gpu_generator_info():
    """Get enhanced information about the GPU generator"""
    return gpu_generator.get_model_info()

def test_gpu_generation():
    """Enhanced GPU image generation test"""
    try:
        log.info("Testing enhanced GPU image generation...")
        
        # Test prompt
        test_prompt = "Modern ural building with clean lines and glass facade"
        test_theme = "ure"
        test_number = 777
        
        filename, style = generate_image_with_retry(test_prompt, test_theme, test_number, image_type="test")
        
        if filename and style:
            log.info(f"Enhanced GPU generation test successful: {filename}")
            return True
        else:
            log.error("Enhanced GPU generation test failed")
            return False
            
    except Exception as e:
        log.error(f"Enhanced GPU generation test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the enhanced GPU generator
    print("Testing Enhanced GPU Image Generator...")
    success = test_gpu_generation()
    if success:
        print("Enhanced GPU Image Generator is working!")
        # Print performance stats
        stats = gpu_generator.get_performance_stats()
        print("Performance stats:", json.dumps(stats, indent=2))
    else:
        print("Enhanced GPU Image Generator test failed")
