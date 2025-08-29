#!/usr/bin/env python3
"""
*ASK*: Daily Research - Unified Pipeline (Offline-First)
Enhanced main pipeline with offline-first approach and lazy model downloads

This module provides a comprehensive research pipeline with multiple modes:
- Enhanced Simple: Connected Q&A generation with previous content reference
- Hybrid: Cross-disciplinary themes with intelligent connections
- Cross-disciplinary: Explores intersections between research themes

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

# Import offline generation functions
from offline_question_generator import generate_single_question_for_category
from offline_answer_generator import generate_answer as generate_offline_answer
from volume_manager import get_next_question_image_number, get_next_answer_image_number, get_current_volume_info
from research_csv_manager import log_single_question, read_log_csv

# Import image generation functions (lazy loading to avoid environment issues)
# from smart_image_generator import generate_image_with_smart_fallback
# from image_add_text import add_text_overlay

# Global variables for lazy-loaded functions
generate_image_with_smart_fallback = None
add_text_overlay = None
generate_answer = None
QUESTION_TEMPLATES = None

def generate_offline_question(theme: str) -> Optional[str]:
    """Wrapper function for offline question generation"""
    return generate_single_question_for_category(theme)

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
SIMPLE_MODE_THEMES = os.getenv('SIMPLE_MODE_THEMES', 'research_methodology,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology')

# Check if API generation is enabled (offline-first approach)
API_GENERATION_ENABLED = os.getenv('API_IMAGE_GENERATION_ENABLED', 'false').lower() == 'true'

# Validate API key only if API generation is enabled (offline-first approach)
if len(sys.argv) <= 1 or (sys.argv[1].lower() not in ['help', '--help', '-h']):
    if API_GENERATION_ENABLED:
        if not TOGETHER_API_KEY:
            log.error("ERROR: API generation is enabled but TOGETHER_API_KEY is not set!")
            console_logger.error("ERROR: API generation is enabled but TOGETHER_API_KEY is not set!")
            console_logger.info("To run in offline mode, set API_IMAGE_GENERATION_ENABLED=false in ask.env")
            exit(1)

        if not TOGETHER_API_KEY.startswith('tgp_'):
            log.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")
            console_logger.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")

        # Only show success message if API generation is actually enabled
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
    console_logger.info("  python main.py                    - Enhanced Simple Mode (default)")
    console_logger.info("  python main.py hybrid             - [REMOVED] Use Enhanced Simple Mode instead")
    console_logger.info("  python main.py cross-disciplinary - [REMOVED] Use Enhanced Simple Mode instead")
    console_logger.info("  python main.py help              - Show this help")
    console_logger.info("")
    console_logger.info(" Mode Descriptions:")
    console_logger.info("  • Enhanced Simple: Connected Q&A generation with previous content reference (supports 1+ themes)")
    console_logger.info("  • Hybrid: [REMOVED] Enhanced Simple Mode now handles multi-theme exploration")
    console_logger.info("  • Cross-disciplinary: [REMOVED] Enhanced Simple Mode now handles multi-theme exploration")
    console_logger.info("")
    console_logger.info(" Enhanced Simple Mode Features:")
    console_logger.info("  • Reads all previous questions from log.csv")
    console_logger.info("  • Generates questions that reference previous content")
    console_logger.info("  • Creates connected, chained-like experience")
    console_logger.info("  • Supports single or multiple themes per run (configurable via SIMPLE_MODE_THEMES)")
    console_logger.info("")
    console_logger.info("  Configuration: Edit ask.env to customize each mode")
    console_logger.info("  Offline-First: System runs without API key by default")
    console_logger.info("  Lazy Loading: AI models downloaded only when needed")

def _import_required_modules():
    """Import all required modules for the pipeline"""
    global generate_image_with_smart_fallback, add_text_overlay, generate_answer, QUESTION_TEMPLATES
    try:
        from research_orchestrator import ResearchOrchestrator
        from image_generation_system import ImageGenerationSystem
        from volume_manager import get_current_volume_info, get_next_question_image_number, get_next_answer_image_number
        from offline_question_generator import generate_single_question_for_category, QUESTION_TEMPLATES as _QUESTION_TEMPLATES
        from offline_answer_generator import generate_answer as _generate_answer
        from smart_image_generator import generate_image_with_smart_fallback as _generate_image_with_smart_fallback
        from image_add_text import add_text_overlay as _add_text_overlay
        from research_csv_manager import log_single_question, mark_questions_as_used, read_log_csv
        
        # Set global variables
        QUESTION_TEMPLATES = _QUESTION_TEMPLATES
        generate_answer = _generate_answer
        generate_image_with_smart_fallback = _generate_image_with_smart_fallback
        add_text_overlay = _add_text_overlay
        
        return True
    except ImportError as e:
        console_logger.error(f" Import error: {e}")
        console_logger.error(" Please ensure all required modules are available")
        return False

def run_simple_mode():
    """Run the enhanced simple mode with connected, chained-like experience"""
    try:
        console_logger.info(" Starting Enhanced Simple Mode - Connected Chained Experience")
        console_logger.info("=" * 60)
        console_logger.info(" Features:")
        console_logger.info(" • Reads all previous questions from log.csv")
        console_logger.info(" • Generates questions that reference previous content")
        console_logger.info(" • Creates connected, chained-like experience")
        console_logger.info(" Offline-first mode: GPU -> CPU -> API (if enabled)")
        
        # Check hardware availability
        gpu_available = check_gpu_availability()
        
        # Import required modules
        if not _import_required_modules():
            return
        
        # Step 1: Read all previous questions from log.csv
        console_logger.info(" Step 1: Reading all previous questions from log.csv...")
        previous_qa_pairs = read_log_csv()
        
        if not previous_qa_pairs:
            console_logger.warning(" No previous questions found in log.csv")
            console_logger.info(" Starting fresh with standard question generation...")
            # Fall back to original simple mode if no previous questions
            run_original_simple_mode()
            return
        
        console_logger.info(f" Step 1: Found {len(previous_qa_pairs)} previous Q&A pairs")
        
        # Step 2: Analyze previous content for connection opportunities
        console_logger.info(" Step 2: Analyzing previous content for connection opportunities...")
        
        # Extract themes and key concepts from previous questions
        themes_used = {}
        key_concepts = set()
        recent_questions = []
        
        for qa_pair in previous_qa_pairs:
            theme = qa_pair.get('theme', '')
            question = qa_pair.get('question', '')
            
            if theme and question:
                # Count theme usage
                themes_used[theme] = themes_used.get(theme, 0) + 1
                
                # Extract key concepts from questions (simple extraction)
                words = question.lower().split()
                for word in words:
                    if len(word) > 5 and word not in ['design', 'sustainable', 'research', 'technology', 'environmental']:
                        key_concepts.add(word)
                
                # Keep recent questions for reference
                if len(recent_questions) < 5:
                    recent_questions.append(qa_pair)
        
        console_logger.info(f" Step 2: Found {len(themes_used)} themes and {len(key_concepts)} key concepts")
        
        # Step 3: Select theme(s) for new question (support one or multiple themes)
        available_themes = [theme.strip() for theme in SIMPLE_MODE_THEMES.split(',') if theme.strip()]
        
        # Validate that all user-specified themes are available
        valid_themes = []
        invalid_themes = []
        for theme in available_themes:
            if theme in QUESTION_TEMPLATES:
                valid_themes.append(theme)
            else:
                invalid_themes.append(theme)
        
        if invalid_themes:
            console_logger.warning(f" Step 3: Invalid themes found: {invalid_themes}")
            console_logger.info(f" Step 3: Available themes: {list(QUESTION_TEMPLATES.keys())}")
        
        if not valid_themes:
            console_logger.error(" Step 3: No valid themes found!")
            return
        
        # Determine how many themes to use in this run
        if len(valid_themes) == 1:
            # Single theme mode
            selected_themes = [valid_themes[0]]
            console_logger.info(f" Step 3: Single theme mode - exploring {selected_themes[0].upper()}")
        else:
            # Multi-theme mode - select 1-3 themes based on usage
            unused_themes = [theme for theme in valid_themes if theme not in themes_used]
            if unused_themes:
                # Prefer unused themes, select 1-2 themes
                num_themes = min(2, len(unused_themes))
                selected_themes = random.sample(unused_themes, num_themes)
                console_logger.info(f" Step 3: Multi-theme mode - exploring {', '.join([t.upper() for t in selected_themes])}")
            else:
                # All themes used, pick least used themes
                sorted_themes = sorted(themes_used.items(), key=lambda x: x[1])
                num_themes = min(2, len(sorted_themes))
                selected_themes = [theme for theme, count in sorted_themes[:num_themes]]
                console_logger.info(f" Step 3: Multi-theme mode - exploring {', '.join([t.upper() for t in selected_themes])} (least used)")
        
        # For compatibility, keep selected_theme for single theme operations
        selected_theme = selected_themes[0] if len(selected_themes) == 1 else 'multi_theme'
        
        # Step 4: Generate connected question that references previous content
        if len(selected_themes) == 1:
            console_logger.info(f" Step 4: Generating connected question for {selected_theme}...")
            
            # Create context from previous questions
            context_questions = []
            for qa_pair in recent_questions[-3:]:  # Last 3 questions for context
                context_questions.append(qa_pair['question'])
            
            # Generate question with context
            connected_question = generate_connected_question(selected_theme, context_questions, key_concepts)
            
            if not connected_question:
                console_logger.warning(" Failed to generate connected question, using fallback...")
                connected_question = generate_single_question_for_category(selected_theme)
        else:
            console_logger.info(f" Step 4: Generating multi-theme question for {', '.join(selected_themes)}...")
            
            # Create context from previous questions
            context_questions = []
            for qa_pair in recent_questions[-3:]:  # Last 3 questions for context
                context_questions.append(qa_pair['question'])
            
            # Generate multi-theme question
            connected_question = generate_multi_theme_question(selected_themes, context_questions, key_concepts)
            
            if not connected_question:
                console_logger.warning(" Failed to generate multi-theme question, using fallback...")
                connected_question = generate_multi_theme_fallback_question(selected_themes)
        
        if not connected_question:
            console_logger.error(" Failed to generate question")
            return
            
        console_logger.info(f" Step 4: Connected question created: {connected_question[:80]}...")
        
        # Step 5: Generate question image
        question_image_number = get_next_question_image_number()
        console_logger.info(f" Step 5: Generating question image #{question_image_number}...")
        
        try:
            image_path, style = generate_image_with_smart_fallback(
                prompt=connected_question,
                theme=selected_theme,
                image_number=question_image_number,
                image_type="q"
            )
            console_logger.info(f" Step 5: Question image created: {os.path.basename(image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create question image: {e}")
            return
    
        # Step 6: Log question
        console_logger.info(f" Step 6: Logging connected question to CSV...")
        # For multi-theme questions, use the first theme as primary, but log all themes
        log_theme = selected_themes[0] if len(selected_themes) == 1 else f"multi_{'_'.join(selected_themes)}"
        success = log_single_question(
            theme=log_theme,
            question=connected_question,
            image_filename=os.path.basename(image_path),
            style=style,
            is_answer=False,
            mark_as_used=False
        )
        if not success:
            console_logger.error(" Failed to log question")
            return
        console_logger.info(f" Step 6: Connected question logged to CSV")
        
        # Step 7: Add text overlay to question image
        console_logger.info(f" Step 7: Adding text overlay to question image...")
        try:
            final_image_path = add_text_overlay(
                image_path=image_path,
                prompt=connected_question,
                image_number=question_image_number,
                is_question=True
            )
            console_logger.info(f" Step 7: Text overlay added successfully")
            console_logger.info(f" Step 7: Final question image created: {os.path.basename(final_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay: {e}")
            return
    
        # Step 8: Generate connected answer
        console_logger.info(f" Step 8: Generating connected answer...")
        # For multi-theme questions, use the primary theme for answer generation
        answer_theme = selected_themes[0] if len(selected_themes) == 1 else selected_themes[0]
        answer = generate_answer(connected_question, answer_theme)
        if not answer:
            console_logger.error(" Failed to generate answer")
            return
        console_logger.info(f" Step 8: Connected answer generated: {answer[:80]}...")
    
        # Step 9: Mark question as used
        console_logger.info(f" Step 9: Marking question as used...")
        try:
            questions_dict = {selected_theme: connected_question}
            marked_count = mark_questions_as_used(questions_dict)
            if marked_count > 0:
                console_logger.info(f" Step 9: Question marked as used (prevents duplicates)")
            else:
                console_logger.warning(f" Step 9: No questions marked as used")
        except Exception as e:
            console_logger.warning(f" Could not mark question as used: {e}")
    
        # Step 10: Generate answer image
        answer_image_number = get_next_answer_image_number()
        console_logger.info(f" Step 10: Generating answer image #{answer_image_number}...")
        
        try:
            answer_image_path, answer_style = generate_image_with_smart_fallback(
                prompt=answer,
                theme=selected_theme,
                image_number=answer_image_number,
                image_type="a"
            )
            console_logger.info(f" Step 10: Answer image created: {os.path.basename(answer_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create answer image: {e}")
            return
        
        # Step 11: Log answer
        console_logger.info(f" Step 11: Logging connected answer to CSV...")
        success = log_single_question(
            theme=selected_theme,
            question=answer,
            image_filename=os.path.basename(answer_image_path),
            style=answer_style,
            is_answer=True,
            mark_as_used=False
        )
        if not success:
            console_logger.error(" Failed to log answer")
            return
        console_logger.info(f" Step 11: Connected answer logged to CSV")
        
        # Step 12: Add text overlay to answer image
        console_logger.info(f" Step 12: Adding text overlay to answer image...")
        try:
            final_answer_images = add_text_overlay(
                image_path=answer_image_path,
                prompt=answer,
                image_number=answer_image_number,
                is_question=False
            )
            console_logger.info(f" Step 12: Answer text overlay added successfully")
            
            # Handle both single image and multiple images
            if isinstance(final_answer_images, list):
                console_logger.info(f" Step 12: Created {len(final_answer_images)} answer images")
                final_answer_image = final_answer_images[0]  # Use first image for summary
            else:
                final_answer_image = final_answer_images
            console_logger.info(f" Step 12: Final answer image created: {os.path.basename(final_answer_image)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay to answer: {e}")
            return
        
        # Completion summary
        console_logger.info("=" * 60)
        console_logger.info(f" Enhanced Simple Mode completed successfully!")
        console_logger.info(f" Connected question image: {os.path.basename(final_image_path)}")
        console_logger.info(f" Connected answer image: {os.path.basename(final_answer_image)}")
        console_logger.info(f" Theme: {selected_theme}")
        console_logger.info(f" Total Q&A pairs in database: {len(previous_qa_pairs) + 2}")
        console_logger.info(f" Connected experience created!")
        
    except Exception as e:
        console_logger.error(f" Enhanced simple mode failed: {e}")
        raise

def generate_connected_question(theme: str, context_questions: List[str], key_concepts: set) -> Optional[str]:
    """
    Generate a question that connects to previous content
    
    Args:
        theme: The theme for the new question
        context_questions: List of recent questions for context
        key_concepts: Set of key concepts from previous questions
        
    Returns:
        Connected question string or None if failed
    """
    try:
        # Import the offline question generator
        from offline_question_generator import generate_single_question_for_category
        
        # Generate base question
        base_question = generate_single_question_for_category(theme)
        if not base_question:
            return None
        
        # If we have context, try to create connections
        if context_questions and key_concepts:
            # Create connection phrases
            connection_phrases = [
                f"Building on previous research about {random.choice(list(key_concepts))}, ",
                f"Following up on earlier work in {theme}, ",
                f"Expanding on the concept of {random.choice(list(key_concepts))}, ",
                f"Continuing the exploration of {theme}, ",
                f"Drawing from previous findings about {random.choice(list(key_concepts))}, "
            ]
            
            # Add connection to the beginning of the question
            connection = random.choice(connection_phrases)
            connected_question = connection + base_question.lower()
            
            # Capitalize first letter
            connected_question = connected_question[0].upper() + connected_question[1:]
            
            console_logger.info(f" Created connected question referencing previous content")
            return connected_question
        
        # If no context, return base question
        return base_question
        
    except Exception as e:
        console_logger.error(f" Error generating connected question: {e}")
        return None

def generate_multi_theme_question(themes: List[str], context_questions: List[str], key_concepts: set) -> Optional[str]:
    """
    Generate a question that combines multiple themes with context
    
    Args:
        themes: List of themes to combine
        context_questions: List of recent questions for context
        key_concepts: Set of key concepts from previous questions
        
    Returns:
        Multi-theme question string or None if failed
    """
    try:
        # Import the offline question generator
        from offline_question_generator import generate_single_question_for_category
        
        # Generate base questions for each theme
        base_questions = []
        for theme in themes:
            base_question = generate_single_question_for_category(theme)
            if base_question:
                base_questions.append(base_question)
        
        if not base_questions:
            return None
        
        # If we have context, try to create connections
        if context_questions and key_concepts:
            # Create multi-theme connection phrases
            connection_phrases = [
                f"Building on previous research about {random.choice(list(key_concepts))}, how can we integrate {themes[0]} and {themes[1]} to ",
                f"Following up on earlier work, what are the intersections between {themes[0]} and {themes[1]} in ",
                f"Expanding on the concept of {random.choice(list(key_concepts))}, how do {themes[0]} and {themes[1]} work together to ",
                f"Continuing the exploration of multiple themes, how can {themes[0]} and {themes[1]} collaborate to ",
                f"Drawing from previous findings about {random.choice(list(key_concepts))}, what synergies exist between {themes[0]} and {themes[1]} in "
            ]
            
            # Create a multi-theme question template
            if len(themes) == 2:
                # For 2 themes, create integration question
                connection = random.choice(connection_phrases)
                # Extract the core question from one of the base questions
                core_question = base_questions[0].lower()
                # Remove common prefixes
                for prefix in ["how can we ", "what are the ", "how does ", "what role does "]:
                    if core_question.startswith(prefix):
                        core_question = core_question[len(prefix):]
                        break
                
                multi_theme_question = connection + core_question
            else:
                # For 3+ themes, create broader integration question
                connection = f"Exploring the intersections between {', '.join(themes[:-1])} and {themes[-1]}, how can we "
                core_question = base_questions[0].lower()
                for prefix in ["how can we ", "what are the ", "how does ", "what role does "]:
                    if core_question.startswith(prefix):
                        core_question = core_question[len(prefix):]
                        break
                
                multi_theme_question = connection + core_question
            
            # Capitalize first letter
            multi_theme_question = multi_theme_question[0].upper() + multi_theme_question[1:]
            
            console_logger.info(f" Created multi-theme question combining {len(themes)} themes")
            return multi_theme_question
        
        # If no context, create simple multi-theme question
        if len(themes) == 2:
            return f"How can {themes[0]} and {themes[1]} work together to improve sustainable design?"
        else:
            return f"What are the synergies between {', '.join(themes)} in modern research?"
        
    except Exception as e:
        console_logger.error(f" Error generating multi-theme question: {e}")
        return None

def generate_multi_theme_fallback_question(themes: List[str]) -> Optional[str]:
    """
    Generate a fallback multi-theme question when context generation fails
    
    Args:
        themes: List of themes to combine
        
    Returns:
        Fallback multi-theme question string or None if failed
    """
    try:
        if len(themes) == 2:
            return f"How can {themes[0]} and {themes[1]} collaborate to advance research methodology?"
        elif len(themes) == 3:
            return f"What are the key intersections between {themes[0]}, {themes[1]}, and {themes[2]} in sustainable development?"
        else:
            return f"How do {', '.join(themes)} work together to address modern challenges?"
        
    except Exception as e:
        console_logger.error(f" Error generating fallback multi-theme question: {e}")
        return None

def run_original_simple_mode():
    """Run the original simple 12-step pipeline (fallback)"""
    try:
        console_logger.info(" Running original simple mode (fallback)...")
        
        # Import required modules
        if not _import_required_modules():
            return
        
        # Initialize pipeline
        themes = [theme.strip() for theme in SIMPLE_MODE_THEMES.split(',') if theme.strip()]
        console_logger.info(f" Original mode: Available themes: {themes}")
        
        # Ensure directories exist
        os.makedirs('images', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Get current volume info (for internal use only)
        try:
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        except Exception as e:
            console_logger.warning(f" Could not get volume info: {e}")
            current_volume = 1
        
        # Pick a theme
        theme = random.choice(themes)
        console_logger.info(f" Original mode: Theme selected: {theme.upper()}")
        
        # Get next question image number
        question_image_number = get_next_question_image_number()
        console_logger.info(f" Original mode: Next question image number: {question_image_number}")
    
        # Generate question
        console_logger.info(f" Original mode: Generating question for {theme}...")
        question = generate_single_question_for_category(theme)
        if not question:
            console_logger.error(" Failed to generate question")
            return
        console_logger.info(f" Original mode: Question created: {question[:80]}...")
    
        # Generate question image using smart fallback
        console_logger.info(f" Original mode: Generating base image for question...")
        try:
            image_path, style = generate_image_with_smart_fallback(
                prompt=question,
                theme=theme,
                image_number=question_image_number,
                image_type="q"
            )
            console_logger.info(f" Original mode: Base image created: {os.path.basename(image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create question image: {e}")
            return
    
        # Log question with image filename
        console_logger.info(f" Original mode: Logging question to CSV...")
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
        console_logger.info(f" Original mode: Question logged to CSV")
        
        # Get next answer image number (after question is logged)
        answer_image_number = get_next_answer_image_number()
        console_logger.info(f" Original mode: Next answer image number: {answer_image_number}")
    
        # Add text overlay
        console_logger.info(f" Original mode: Adding text overlay to question image...")
        try:
            final_image_path = add_text_overlay(
                image_path=image_path,
                    prompt=question,
                    image_number=question_image_number,
                    is_question=True
                )
            console_logger.info(f" Original mode: Text overlay added successfully")
            console_logger.info(f" Original mode: Final question image created: {os.path.basename(final_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay: {e}")
            return
    
        # Generate answer
        console_logger.info(f" Original mode: Generating answer for question...")
        answer = generate_answer(question, theme)
        if not answer:
            console_logger.error(" Failed to generate answer")
            return
        console_logger.info(f" Original mode: Answer generated: {answer[:80]}...")
    
        # Mark question as used
        console_logger.info(f" Original mode: Marking question as used...")
        try:
            questions_dict = {theme: question}
            marked_count = mark_questions_as_used(questions_dict)
            if marked_count > 0:
                console_logger.info(f" Original mode: Question marked as used (prevents duplicates)")
            else:
                console_logger.warning(f" Original mode: No questions marked as used")
        except Exception as e:
            console_logger.warning(f" Could not mark question as used: {e}")
        
        # Generate answer image
        console_logger.info(f" Original mode: Generating base image for answer...")
        try:
            answer_image_path, answer_style = generate_image_with_smart_fallback(
                prompt=answer,
                theme=theme,
                image_number=answer_image_number,
                image_type="a"
            )
            console_logger.info(f" Original mode: Base image created: {os.path.basename(answer_image_path)}")
        except Exception as e:
            console_logger.error(f" Failed to create answer image: {e}")
            return
        
        # Log answer with image filename
        console_logger.info(f" Original mode: Logging answer to CSV...")
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
        console_logger.info(f" Original mode: Answer logged to CSV")
                
        # Add text overlay to answer image
        console_logger.info(f" Original mode: Adding text overlay to answer image...")
        try:
            final_answer_images = add_text_overlay(
                image_path=answer_image_path,
                prompt=answer,
                image_number=answer_image_number,
                is_question=False
            )
            console_logger.info(f" Original mode: Text overlay added successfully")
            
            # Handle both single image and multiple images
            if isinstance(final_answer_images, list):
                console_logger.info(f" Original mode: Created {len(final_answer_images)} answer images")
                final_answer_image = final_answer_images[0]  # Use first image for summary
            else:
                final_answer_image = final_answer_images
            console_logger.info(f" Original mode: Final answer image created: {os.path.basename(final_answer_image)}")
        except Exception as e:
            console_logger.error(f" Failed to add text overlay to answer: {e}")
            return
        
        # Completion summary
        console_logger.info("=" * 60)
        console_logger.info(f" Original simple mode completed successfully!")
        console_logger.info(f" Question image: {os.path.basename(final_image_path)}")
        console_logger.info(f" Answer image: {os.path.basename(final_answer_image)}")
        console_logger.info(f" Theme: {theme}")

    except Exception as e:
        console_logger.error(f" Original simple mode failed: {e}")
        raise

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
            
            if mode in ["help", "--help", "-h"]:
                show_help()
            elif mode == "hybrid":
                console_logger.warning(" Hybrid mode has been removed.")
                console_logger.info(" Enhanced Simple Mode now provides superior multi-theme capabilities.")
                console_logger.info(" Use: python main.py (with SIMPLE_MODE_THEMES configured)")
                show_help()
            elif mode == "cross-disciplinary":
                console_logger.warning(" Cross-disciplinary mode has been removed.")
                console_logger.info(" Enhanced Simple Mode now supports multi-theme exploration.")
                console_logger.info(" Use: python main.py (with SIMPLE_MODE_THEMES configured)")
                show_help()
            else:
                console_logger.error(f"Unknown mode: {mode}")
                show_help()
        else:
            # Default mode: enhanced simple pipeline
            run_simple_mode()
        
    except Exception as e:
        console_logger.error(f" Pipeline failed: {e}")
        raise

if __name__ == "__main__":
        main()
