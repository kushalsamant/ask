#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized CPU Image Generator

This module provides CPU-based image generation using diffusers library
with comprehensive error handling, performance monitoring, and memory optimization.
"""

import os
import sys
import time
import json
import logging
import tempfile
import shutil
import re
from typing import Optional, Dict, Any, Tuple, Union, List
from pathlib import Path
from datetime import datetime
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    import torch
    import torch.nn.functional as F
    from diffusers import AutoPipelineForText2Image, DPMSolverMultistepScheduler
    from diffusers.utils import logging as diffusers_logging
    from transformers import logging as transformers_logging
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    DIFFUSERS_AVAILABLE = True
except ImportError as e:
    DIFFUSERS_AVAILABLE = False
    logging.warning(f"Diffusers not available: {e}")

# Configure logging
logger = logging.getLogger(__name__)

# Suppress diffusers and transformers logging
diffusers_logging.set_verbosity_error()
transformers_logging.set_verbosity_error()

class CPUImageGeneratorConfig:
    """Configuration class for CPU image generation"""
    
    def __init__(self):
        self.model_id = os.getenv('CPU_MODEL_ID', 'latent-consistency/lcm-sd15')
        self.inference_steps = int(os.getenv('CPU_INFERENCE_STEPS', '4'))
        self.guidance_scale = float(os.getenv('CPU_GUIDANCE_SCALE', '1.5'))
        self.width = int(os.getenv('IMAGE_WIDTH', '512'))
        self.height = int(os.getenv('IMAGE_HEIGHT', '512'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '1'))
        self.enable_attention_slicing = os.getenv('CPU_ATTENTION_SLICING', 'true').lower() == 'true'
        self.enable_sequential_cpu_offload = os.getenv('CPU_SEQUENTIAL_OFFLOAD', 'true').lower() == 'true'
        self.enable_vae_tiling = os.getenv('CPU_VAE_TILING', 'true').lower() == 'true'
        self.memory_efficient_attention = os.getenv('CPU_MEMORY_EFFICIENT_ATTENTION', 'true').lower() == 'true'
        self.use_safetensors = os.getenv('CPU_USE_SAFETENSORS', 'true').lower() == 'true'
        self.cache_dir = os.getenv('CPU_CACHE_DIR', None)
        self.output_dir = os.getenv('IMAGES_DIR', 'images')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Performance settings
        self.max_retries = int(os.getenv('CPU_MAX_RETRIES', '3'))
        self.retry_delay = float(os.getenv('CPU_RETRY_DELAY', '1.0'))
        self.timeout = float(os.getenv('CPU_TIMEOUT', '300.0'))
        
        # Quality settings
        self.quality_threshold = float(os.getenv('CPU_QUALITY_THRESHOLD', '0.7'))
        self.enable_quality_check = os.getenv('CPU_QUALITY_CHECK', 'true').lower() == 'true'

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'total_time': 0.0,
            'avg_generation_time': 0.0,
            'memory_usage': [],
            'error_counts': {}
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
    
    def record_failure(self, error_type: str):
        """Record failed generation"""
        self.metrics['failed_generations'] += 1
        self.metrics['error_counts'][error_type] = self.metrics['error_counts'].get(error_type, 0) + 1
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'rss': 0.0, 'vms': 0.0, 'percent': 0.0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.metrics.copy()
        stats['current_memory'] = self.get_memory_usage()
        stats['success_rate'] = (self.metrics['successful_generations'] / max(self.metrics['total_generations'], 1)) * 100
        return stats

class CPUImageGenerator:
    """Optimized CPU-based image generator using diffusers"""
    
    def __init__(self, config: Optional[CPUImageGeneratorConfig] = None):
        self.config = config or CPUImageGeneratorConfig()
        self.pipeline = None
        self.performance_monitor = PerformanceMonitor()
        self.is_initialized = False
        
        # Set up logging
        logging.getLogger().setLevel(getattr(logging, self.config.log_level))
        
        # Initialize the generator
        self._initialize()
    
    def _initialize(self):
        """Initialize the image generation pipeline"""
        try:
            if not DIFFUSERS_AVAILABLE:
                raise ImportError("Diffusers library not available")
            
            logger.info(f" Initializing CPU image generator with model: {self.config.model_id}")
            
            # Load the pipeline
            self.pipeline = AutoPipelineForText2Image.from_pretrained(
                self.config.model_id,
                torch_dtype=torch.float32,
                use_safetensors=self.config.use_safetensors,
                cache_dir=self.config.cache_dir,
                local_files_only=False
            )
            
            # Move to CPU
            self.pipeline = self.pipeline.to("cpu")
            
            # Apply memory optimizations
            self._apply_memory_optimizations()
            
            # Set scheduler for faster inference
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            self.is_initialized = True
            logger.info(" CPU image generator initialized successfully")
            
        except Exception as e:
            logger.error(f" Failed to initialize CPU image generator: {e}")
            self.is_initialized = False
            raise
    
    def _apply_memory_optimizations(self):
        """Apply memory optimization techniques"""
        try:
            if self.config.enable_attention_slicing:
                self.pipeline.enable_attention_slicing()
                logger.info(" Enabled attention slicing")
            
            if self.config.enable_sequential_cpu_offload:
                self.pipeline.enable_sequential_cpu_offload()
                logger.info(" Enabled sequential CPU offload")
            
            if self.config.enable_vae_tiling:
                try:
                    self.pipeline.vae.enable_tiling()
                    logger.info(" Enabled VAE tiling")
                except Exception as e:
                    logger.warning(f"  VAE tiling not available: {e}")
            
            if self.config.memory_efficient_attention:
                try:
                    self.pipeline.enable_memory_efficient_attention()
                    logger.info(" Enabled memory efficient attention")
                except Exception as e:
                    logger.warning(f"  Memory efficient attention not available: {e}")
                    
        except Exception as e:
            logger.warning(f"  Some memory optimizations failed: {e}")
    
    def _validate_input(self, prompt: str, width: int, height: int, 
                       num_inference_steps: int, guidance_scale: float) -> bool:
        """Validate input parameters"""
        try:
            if not prompt or not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            if width < 64 or width > 2048 or height < 64 or height > 2048:
                raise ValueError("Image dimensions must be between 64 and 2048 pixels")
            
            if num_inference_steps < 1 or num_inference_steps > 50:
                raise ValueError("Inference steps must be between 1 and 50")
            
            if guidance_scale < 0.1 or guidance_scale > 20.0:
                raise ValueError("Guidance scale must be between 0.1 and 20.0")
            
            return True
            
        except Exception as e:
            logger.error(f" Input validation failed: {e}")
            return False
    
    def _ensure_output_directory(self) -> bool:
        """Ensure output directory exists"""
        try:
            Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f" Failed to create output directory: {e}")
            return False
    
    def _generate_filename(self, prompt: str, timestamp: Optional[str] = None) -> str:
        """Generate filename for the output image"""
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean prompt for filename
        clean_prompt = re.sub(r'[^a-zA-Z0-9\s-]', '', prompt)[:50].strip()
        clean_prompt = re.sub(r'\s+', '_', clean_prompt)
        
        return f"cpu_generated_{clean_prompt}_{timestamp}.png"
    
    def _check_image_quality(self, image: Image.Image) -> float:
        """Check image quality score"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate quality metrics
            gray = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
            laplacian = np.var(np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]))
            sharpness = np.var(gray)
            
            # Contrast
            contrast = np.std(gray)
            
            # Brightness balance
            brightness = np.mean(gray)
            brightness_balance = 1.0 - abs(brightness - 128) / 128
            
            # Combined quality score
            quality_score = (sharpness * 0.4 + contrast * 0.4 + brightness_balance * 0.2) / 1000
            
            return min(max(quality_score, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"  Quality check failed: {e}")
            return 0.5  # Default quality score
    
    def generate_image(self, prompt: str, width: Optional[int] = None, 
                      height: Optional[int] = None, num_inference_steps: Optional[int] = None,
                      guidance_scale: Optional[float] = None) -> Optional[str]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of the image to generate
            width: Image width (default: config.width)
            height: Image height (default: config.height)
            num_inference_steps: Number of inference steps (default: config.inference_steps)
            guidance_scale: Guidance scale (default: config.guidance_scale)
        
        Returns:
            Path to generated image file or None if generation failed
        """
        if not self.is_initialized:
            logger.error(" CPU image generator not initialized")
            return None
        
        # Use default values if not provided
        width = width or self.config.width
        height = height or self.config.height
        num_inference_steps = num_inference_steps or self.config.inference_steps
        guidance_scale = guidance_scale or self.config.guidance_scale
        
        # Validate input
        if not self._validate_input(prompt, width, height, num_inference_steps, guidance_scale):
            return None
        
        # Start performance monitoring
        self.performance_monitor.start_timer()
        
        try:
            logger.info(f" Generating image: '{prompt[:50]}...' ({width}x{height}, {num_inference_steps} steps)")
            
            # Generate image
            with torch.no_grad():
                result = self.pipeline(
                    prompt=prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    num_images_per_prompt=self.config.batch_size
                )
            
            # Extract the first image
            image = result.images[0]
            
            # Check image quality if enabled
            if self.config.enable_quality_check:
                quality_score = self._check_image_quality(image)
                logger.info(f" Image quality score: {quality_score:.3f}")
                
                if quality_score < self.config.quality_threshold:
                    logger.warning(f"  Image quality below threshold ({quality_score:.3f} < {self.config.quality_threshold})")
            
            # Save image
            if self._ensure_output_directory():
                filename = self._generate_filename(prompt)
                filepath = os.path.join(self.config.output_dir, filename)
                
                image.save(filepath, "PNG", optimize=True)
                logger.info(f" Image saved: {filepath}")
                
                # Record success
                self.performance_monitor.end_timer()
                self.performance_monitor.record_success()
                
                return filepath
            else:
                raise Exception("Failed to create output directory")
                
        except Exception as e:
            logger.error(f" Image generation failed: {e}")
            self.performance_monitor.end_timer()
            self.performance_monitor.record_failure(type(e).__name__)
            return None
    
    def generate_batch(self, prompts: List[str], **kwargs) -> List[Optional[str]]:
        """Generate multiple images from a list of prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f" Processing batch item {i+1}/{len(prompts)}")
            result = self.generate_image(prompt, **kwargs)
            results.append(result)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_monitor.get_stats()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.pipeline:
                del self.pipeline
                self.pipeline = None
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("🧹 Cleanup completed")
            
        except Exception as e:
            logger.warning(f"  Cleanup warning: {e}")

def check_dependencies() -> Dict[str, bool]:
    """Check if all required dependencies are available"""
    dependencies = {
        'torch': False,
        'diffusers': False,
        'transformers': False,
        'PIL': False,
        'numpy': False
    }
    
    try:
        import torch
        dependencies['torch'] = True
    except ImportError:
        pass
    
    try:
        import diffusers
        dependencies['diffusers'] = True
    except ImportError:
        pass
    
    try:
        import transformers
        dependencies['transformers'] = True
    except ImportError:
        pass
    
    try:
        from PIL import Image
        dependencies['PIL'] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        pass
    
    return dependencies

def create_cpu_image_generator(config: Optional[CPUImageGeneratorConfig] = None) -> Optional[CPUImageGenerator]:
    """Factory function to create CPU image generator"""
    try:
        return CPUImageGenerator(config)
    except Exception as e:
        logger.error(f" Failed to create CPU image generator: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Check dependencies
    deps = check_dependencies()
    print("Dependencies:", deps)
    
    # Create generator
    generator = create_cpu_image_generator()
    
    if generator:
        # Generate test image
        result = generator.generate_image(
            prompt="A beautiful sunset over mountains, digital art style",
            width=512,
            height=512
        )
        
        if result:
            print(f" Image generated successfully: {result}")
        else:
            print(" Image generation failed")
        
        # Print performance stats
        stats = generator.get_performance_stats()
        print("Performance stats:", json.dumps(stats, indent=2))
        
        # Cleanup
        generator.cleanup()
    else:
        print(" Failed to create CPU image generator")
