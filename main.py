#!/usr/bin/env python3
"""
*ASK*: Daily Research - Unified Pipeline (Offline-First)
Enhanced main pipeline with offline-first approach and lazy model downloads

This module provides a comprehensive research pipeline with multiple modes:
- Simple: Classic 12-step Q&A generation
- Hybrid: Cross-disciplinary themes with chained questions
- Cross-disciplinary: Explores intersections between research themes
- Chained: Creates connected questions that build upon each other

Offline-First Features:
- Primarily GPU-based image generation (offline)
- CPU fallback for image generation (offline)
- API generation as last resort (requires internet)
- Lazy model downloads (only when needed)
- Comprehensive logging and error handling
- Environment-based configuration

Author: ASK Research Tool
Last Updated: 2025-08-25
Version: 3.0 (Offline-First with Lazy Loading)
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from ask.env file
load_dotenv('ask.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
            logging.FileHandler(f"{os.getenv('LOG_DIR', 'logs')}/execution.log")
        ]
)
log = logging.getLogger()

# Setup console logging for user feedback
console_logger = logging.getLogger('console')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
console_logger.addHandler(console_handler)
console_logger.setLevel(logging.INFO)

# Environment variables
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))

# Check if API generation is enabled (offline-first approach)
API_GENERATION_ENABLED = os.getenv('API_IMAGE_GENERATION_ENABLED', 'false').lower() == 'true'

# Validate API key only if API generation is enabled (offline-first approach)
if len(sys.argv) <= 1 or sys.argv[1].lower() != 'help':
    if API_GENERATION_ENABLED:
        if not TOGETHER_API_KEY:
            log.error("ERROR: API generation is enabled but TOGETHER_API_KEY is not set!")
            console_logger.error("ERROR: API generation is enabled but TOGETHER_API_KEY is not set!")
            console_logger.info("To run in offline mode, set API_IMAGE_GENERATION_ENABLED=false in ask.env")
            exit(1)

        if not TOGETHER_API_KEY.startswith('tgp_'):
            log.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")
            console_logger.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")

    log.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")
    console_logger.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")
else:
    log.info("Running in offline mode - API generation disabled")
    console_logger.info("Running in offline mode - API generation disabled")

def download_all_models_upfront() -> bool:
    """
    Download all required AI models upfront before starting the pipeline
    
    Returns:
        bool: True if all models are available (cached or downloaded)
    """
    try:
        console_logger.info("=" * 60)
        console_logger.info(" DOWNLOADING ALL REQUIRED MODELS UPFRONT")
        console_logger.info("=" * 60)
            
        # Get model IDs from environment variables
        gpu_model_id = os.getenv("GPU_MODEL_ID", "runwayml/stable-diffusion-v1-5")
        cpu_model_id = os.getenv("CPU_MODEL_ID", "latent-consistency/lcm-sd15")
        
        # List of all models to download
        models_to_download = [
            (gpu_model_id, "GPU"),
            (cpu_model_id, "CPU"),
        ]
        
        success_count = 0
        total_models = len(models_to_download)
        
        for model_id, model_type in models_to_download:
            console_logger.info(f"")
            console_logger.info(f" [{success_count + 1}/{total_models}] Checking {model_type} model: {model_id}")
            
            if download_model_if_needed(model_id, model_type):
                success_count += 1
                console_logger.info(f" [OK] {model_type} model ready: {model_id}")
            else:
                console_logger.warning(f" [FAIL] {model_type} model failed: {model_id}")
        
        console_logger.info("")
        console_logger.info("=" * 60)
        if success_count == total_models:
            console_logger.info(f" [SUCCESS] ALL MODELS READY! ({success_count}/{total_models})")
            console_logger.info(" Pipeline can now run completely offline!")
        else:
            console_logger.warning(f" [WARNING] SOME MODELS MISSING ({success_count}/{total_models})")
            console_logger.info(" Pipeline will use available models and fallbacks")
        console_logger.info("=" * 60)
        console_logger.info("")
        
        return success_count > 0  # Return True if at least one model is available
        
    except Exception as e:
        console_logger.error(f" Model download process failed: {e}")
        return False

def download_model_if_needed(model_id: str, model_type: str = "gpu") -> bool:
    """
    Download AI model only when needed (lazy loading)
    
    Args:
        model_id: HuggingFace model ID
        model_type: "gpu" or "cpu"
        
    Returns:
        bool: True if model is available (cached or downloaded)
    """
    try:
        # Check if model is already cached
        from huggingface_hub import snapshot_download
        from huggingface_hub import HfApi
        
        # Get cache directory
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        model_path = os.path.join(cache_dir, model_id.replace("/", "_"))
        
        if os.path.exists(model_path):
            console_logger.info(f"   Using cached {model_type.upper()} model: {model_id}")
            return True
        
        # Model not cached, download it
        console_logger.info(f"   Downloading {model_type.upper()} model: {model_id}")
        console_logger.info(f"   This may take a few minutes for the first run...")
        
        # Download with progress tracking
        snapshot_download(
            repo_id=model_id,
            cache_dir=cache_dir,
            local_dir=model_path
        )
        
        console_logger.info(f"   {model_type.upper()} model downloaded successfully!")
        return True
        
    except Exception as e:
        console_logger.error(f"   Failed to download {model_type.upper()} model: {e}")
        return False

def check_gpu_availability() -> bool:
    """Check if GPU is available for image generation"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            console_logger.info(f" GPU detected: {gpu_name} ({gpu_count} device(s))")
            return True
        else:
            console_logger.info(" No GPU detected, will use CPU fallback")
            return False
    except ImportError:
        console_logger.warning(" PyTorch not available, GPU check skipped")
        return False
    except Exception as e:
        console_logger.warning(f" GPU check failed: {e}")
        return False

def show_help():
    """Show help information for available modes"""
    console_logger.info(" *ASK*: Daily Research - Available Modes")
    console_logger.info("=" * 60)
    console_logger.info("  python main.py                    - Simple 12-step pipeline (default)")
    console_logger.info("  python main.py hybrid             - Hybrid cross-disciplinary chained content")
    console_logger.info("  python main.py cross-disciplinary - Cross-disciplinary content")
    console_logger.info("  python main.py chained           - Chained content")
    console_logger.info("  python main.py help              - Show this help")
    console_logger.info("")
    console_logger.info(" Mode Descriptions:")
    console_logger.info("  • Simple: Classic 12-step Q&A generation")
    console_logger.info("  • Hybrid: Combines cross-disciplinary themes with chained questions")
    console_logger.info("  • Cross-disciplinary: Explores intersections between research themes")
    console_logger.info("  • Chained: Creates connected questions that build upon each other")
    console_logger.info("")
    console_logger.info("  Configuration: Edit ask.env to customize each mode")
    console_logger.info("  Offline-First: System runs without API key by default")
    console_logger.info("  Lazy Loading: AI models downloaded only when needed")

def run_simple_mode():
    """Run the original simple 12-step pipeline"""
    try:
        console_logger.info(" Starting Simple 12-Step Pipeline")
        console_logger.info("=" * 50)
        console_logger.info(" Offline-first mode: GPU -> CPU -> API (if enabled)")
        
        # Check hardware availability
        gpu_available = check_gpu_availability()
        
        # Import required modules
        try:
            from research_orchestrator import ResearchOrchestrator
            from image_generation_system import ImageGenerationSystem
            from volume_manager import get_current_volume_info, get_next_question_image_number, get_next_answer_image_number
            from offline_question_generator import generate_single_question_for_category
            from offline_answer_generator import generate_answer
            from smart_image_generator import generate_image_with_smart_fallback
            from image_add_text import add_text_overlay
            from research_csv_manager import log_single_question, mark_questions_as_used
        except ImportError as e:
            console_logger.error(f" Import error: {e}")
            console_logger.error(" Please ensure all required modules are available")
            return
        
        # Initialize pipeline
        themes_config = os.getenv('SIMPLE_MODE_THEMES', 'design_research,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology')
        themes = [theme.strip() for theme in themes_config.split(',') if theme.strip()]
        
        # Ensure directories exist
        os.makedirs('images', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Get current volume info
        try:
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
            console_logger.info(f" Starting at Volume {current_volume}: {qa_pairs_in_volume} Q&A pairs, {total_qa_pairs} total")
        except Exception as e:
            console_logger.warning(f" Could not get volume info: {e}")
            current_volume = 1
        
                # Pick a theme
        theme = random.choice(themes)
        console_logger.info(f" Step 1: Theme selected: {theme.upper()}")
        
        # Get next question image number
        question_image_number = get_next_question_image_number()
        console_logger.info(f" Step 1b: Next question image number: {question_image_number}")
    
        # Generate question
        console_logger.info(f" Step 2: Generating question for {theme}...")
        question = generate_single_question_for_category(theme)
        if not question:
            console_logger.error(" Failed to generate question")
            return
        console_logger.info(f" Step 2: Question created: {question[:80]}...")
    
        # Generate question image using smart fallback
        console_logger.info(f" Step 4: Generating base image for question...")
        try:
            image_path, style = generate_image_with_smart_fallback(
                prompt=question,
                theme=theme,
                image_number=question_image_number,
                image_type="q"
            )
            console_logger.info(f" Step 4: Base image created: {os.path.basename(image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create question image: {e}")
            return
    
        # Log question with image filename
        console_logger.info(f" Step 3: Logging question to CSV...")
        success = log_single_question(
            theme=theme,
            question=question,
            image_filename=os.path.basename(image_path),
            style=style,
            is_answer=False,
            mark_as_used=False
        )
        if not success:
            console_logger.error(" Failed to log question")
            return
        console_logger.info(f" Step 3: Question logged to CSV")
        
        # Get next answer image number (after question is logged)
        answer_image_number = get_next_answer_image_number()
        console_logger.info(f" Step 3b: Next answer image number: {answer_image_number}")
    
        # Add text overlay
        console_logger.info(f" Step 5: Adding text overlay to question image...")
        try:
            final_image_path = add_text_overlay(
                image_path=image_path,
                prompt=question,
                image_number=question_image_number,
                is_question=True
            )
            console_logger.info(f" Step 5: Text overlay added successfully")
            console_logger.info(f" Step 6: Final question image created: {os.path.basename(final_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay: {e}")
            return
    
        # Generate answer
        console_logger.info(f" Step 7: Generating answer for question...")
        answer = generate_answer(question, theme)
        if not answer:
            console_logger.error(" Failed to generate answer")
            return
        console_logger.info(f" Step 7: Answer generated: {answer[:80]}...")
    
        # Mark question as used
        console_logger.info(f" Step 8b: Marking question as used...")
        try:
            questions_dict = {theme: question}
            marked_count = mark_questions_as_used(questions_dict)
            if marked_count > 0:
                console_logger.info(f" Step 8b: Question marked as used (prevents duplicates)")
            else:
                console_logger.warning(f" Step 8b: No questions marked as used")
        except Exception as e:
            console_logger.warning(f" Could not mark question as used: {e}")
    
        # Generate answer image
        console_logger.info(f" Step 9: Generating base image for answer...")
        try:
            answer_image_path, answer_style = generate_image_with_smart_fallback(
                prompt=answer,
                theme=theme,
                image_number=answer_image_number,
                image_type="a"
            )
            console_logger.info(f" Step 9: Base image created: {os.path.basename(answer_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create answer image: {e}")
            return
        
        # Log answer with image filename
        console_logger.info(f" Step 8: Logging answer to CSV...")
        success = log_single_question(
            theme=theme,
            question=answer,
            image_filename=os.path.basename(answer_image_path),
            style=answer_style,
            is_answer=True,
            mark_as_used=False
        )
        if not success:
            console_logger.error(" Failed to log answer")
            return
        console_logger.info(f" Step 8: Answer logged to CSV")
        
        # Add text overlay to answer image
        console_logger.info(f" Step 10: Adding text overlay to answer image...")
        try:
            final_answer_image = add_text_overlay(
                image_path=answer_image_path,
                prompt=answer,
                image_number=answer_image_number,
                is_question=False
            )
            console_logger.info(f" Step 10: Text overlay added successfully")
            console_logger.info(f" Step 11: Final answer image created: {os.path.basename(final_answer_image)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay to answer: {e}")
            return
        
        # Completion summary
        console_logger.info("=" * 60)
        console_logger.info(f" Cycle #1 completed successfully!")
        console_logger.info(f" Question image: {os.path.basename(final_image_path)}")
        console_logger.info(f" Answer image: {os.path.basename(final_answer_image)}")
        console_logger.info(f" Theme: {theme}")
        console_logger.info(f" Simple pipeline completed successfully!")
        
    except Exception as e:
        console_logger.error(f" Simple pipeline failed: {e}")
        raise

def run_hybrid_mode():
    """Run hybrid cross-disciplinary chained content generation"""
    console_logger.info(" Starting Hybrid Cross-Disciplinary Chained Pipeline")
    console_logger.info("=" * 50)
    console_logger.info(" This mode is not yet implemented in the simplified version")
    console_logger.info(" Please use simple mode for now")

def run_cross_disciplinary_mode():
    """Run cross-disciplinary content generation"""
    console_logger.info(" Starting Cross-Disciplinary Pipeline")
    console_logger.info("=" * 50)
    console_logger.info(" This mode is not yet implemented in the simplified version")
    console_logger.info(" Please use simple mode for now")

def run_chained_mode():
    """Run chained content generation"""
    console_logger.info(" Starting Chained Content Pipeline")
    console_logger.info("=" * 50)
    console_logger.info(" This mode is not yet implemented in the simplified version")
    console_logger.info(" Please use simple mode for now")

def main():
    """Main execution function - Enhanced with all modes"""
    try:
        # Download all models upfront before starting any pipeline operations
        console_logger.info("")
        console_logger.info(" *ASK*: Daily Research - Offline-First Pipeline")
        console_logger.info("=" * 60)
        console_logger.info(" Step 0: Downloading all required AI models upfront...")
        
        models_ready = download_all_models_upfront()
        
        if not models_ready:
            console_logger.warning(" [WARNING] No models available - pipeline may fail")
            console_logger.info(" Continuing with fallback options...")
        
        console_logger.info("")
        console_logger.info(" Step 1: Starting pipeline execution...")
        console_logger.info("=" * 60)

        # Check command line arguments for different modes
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == "hybrid":
                run_hybrid_mode()
            elif mode == "cross-disciplinary":
                run_cross_disciplinary_mode()
            elif mode == "chained":
                run_chained_mode()
            elif mode == "help":
                show_help()
            else:
                console_logger.error(f"Unknown mode: {mode}")
                show_help()
        else:
            # Default mode: simple 12-step pipeline
            run_simple_mode()
        
    except Exception as e:
        console_logger.error(f" Pipeline failed: {e}")
        raise

if __name__ == "__main__":
        main()
