#!/usr/bin/env python3
"""
*ASK*: Daily Research - Enhanced Simple Pipeline with Cover Generation (Offline-First)
Streamlined pipeline for generating connected Q&A pairs with images and covers

Features:
- Connected Q&A generation with previous content reference
- Multi-theme support
- Cover image generation (volume covers, theme covers)
- Offline-first: GPU -> CPU -> API (if enabled)
- Lazy model downloads
- Comprehensive logging

Author: ASK Research Tool
Version: 4.1 (Enhanced Simple with Covers)
"""

import os
import sys
import random
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Import essential functions
from offline_question_generator import generate_single_question_for_category
from offline_answer_generator import generate_answer
from volume_manager import get_next_question_image_number, get_next_answer_image_number, get_current_volume_info
from research_csv_manager import log_qa_pair, read_log_csv, mark_questions_as_used

# Load environment variables
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

# Setup console logging
console_logger = logging.getLogger('console')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
console_logger.addHandler(console_handler)
console_logger.setLevel(logging.INFO)

# Environment variables
SIMPLE_MODE_THEMES = os.getenv('SIMPLE_MODE_THEMES', 'research_methodology,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology')
CREATE_COVER_IMAGE = os.getenv('CREATE_COVER_IMAGE', 'true').lower() == 'true'

def check_gpu_availability() -> bool:
    """Check if GPU is available for image generation"""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception as e:
        console_logger.warning(f"GPU check failed: {e}")
        return False

def show_help():
    """Show help information"""
    console_logger.info(" *ASK*: Daily Research - Enhanced Simple Pipeline with Covers")
    console_logger.info("=" * 60)
    console_logger.info("  python main.py                    - Enhanced Simple Mode (default)")
    console_logger.info("  python main.py help              - Show this help")
    console_logger.info("")
    console_logger.info(" Enhanced Simple Mode Features:")
    console_logger.info("  • Reads all previous questions from log.csv")
    console_logger.info("  • Generates questions that reference previous content")
    console_logger.info("  • Creates connected, chained-like experience")
    console_logger.info("  • Supports single or multiple themes per run")
    console_logger.info("  • Generates cover images (professional volume covers only)")
    console_logger.info("")
    console_logger.info("  Configuration: Edit ask.env to customize themes and covers")
    console_logger.info("  Offline-first mode: GPU (SDXL) -> CPU -> Placeholder")

def _import_required_modules():
    """Import required modules for the pipeline"""
    try:
        from smart_image_generator import generate_image_with_smart_fallback
        from image_add_text import add_text_overlay
        from offline_question_generator import QUESTION_TEMPLATES
        return True
    except ImportError as e:
        console_logger.error(f"Import error: {e}")
        console_logger.error("Please ensure all required modules are available")
        return False

def generate_connected_question(theme: str, context_questions: List[str], key_concepts: set) -> Optional[str]:
    """Generate a question that connects to previous content"""
    try:
        # Generate base question
        base_question = generate_single_question_for_category(theme)
        if not base_question:
            return None
        
        # If we have context, try to create connections
        if context_questions and key_concepts:
            # Create connection phrases
            connection_phrases = [
                f"Building on previous research about {', '.join(list(key_concepts)[:2])},",
                f"Following up on earlier questions about {', '.join(list(key_concepts)[:2])},",
                f"Expanding on the theme of {', '.join(list(key_concepts)[:2])},",
                f"Continuing our exploration of {', '.join(list(key_concepts)[:2])},"
            ]
            
            # Add connection to question
            connection = random.choice(connection_phrases)
            connected_question = f"{connection} {base_question}"
            return connected_question
        
        return base_question
        
    except Exception as e:
        console_logger.error(f"Error generating connected question: {e}")
        return None

def generate_multi_theme_question(themes: List[str], context_questions: List[str], key_concepts: set) -> Optional[str]:
    """Generate a question that connects multiple themes"""
    try:
        if len(themes) == 1:
            return generate_connected_question(themes[0], context_questions, key_concepts)
        
        # Create multi-theme question
        theme_names = [theme.replace('_', ' ').title() for theme in themes]
        theme_text = ' and '.join(theme_names)
        
        base_question = generate_single_question_for_category(themes[0])
        if not base_question:
            return None
        
        # Add multi-theme context
        multi_theme_question = f"How do {theme_text} intersect in {base_question.lower()}"
        return multi_theme_question
        
    except Exception as e:
        console_logger.error(f"Error generating multi-theme question: {e}")
        return None

def create_cover_if_needed(selected_theme: str, volume_number: int = None):
    """Create professional volume cover image if enabled"""
    if not CREATE_COVER_IMAGE:
        return
    
    try:
        from image_create_cover import create_cover
        
        console_logger.info(" Creating professional volume cover...")
        
        # Create volume cover if we have a volume number
        if volume_number:
            cover_path = create_cover('volume', volume_number, output_dir="images")
            if cover_path:
                console_logger.info(f" Professional volume cover created: {os.path.basename(cover_path)}")
            
    except ImportError as e:
        console_logger.warning(f" Cover generation not available (missing dependencies): {e}")
    except Exception as e:
        console_logger.warning(f" Could not create cover image: {e}")

def run_simple_mode():
    """Run the enhanced simple mode with connected, chained-like experience and covers"""
    try:
        console_logger.info(" Starting Enhanced Simple Mode - Connected Chained Experience with Covers")
        console_logger.info("=" * 60)
        console_logger.info(" Features:")
        console_logger.info(" • Reads all previous questions from log.csv")
        console_logger.info(" • Generates questions that reference previous content")
        console_logger.info(" • Creates connected, chained-like experience")
        console_logger.info(" • Generates cover images (professional volume covers only)")
        console_logger.info(" Offline-first mode: GPU (SDXL) -> CPU -> Placeholder")
        
        # Check hardware availability
        gpu_available = check_gpu_availability()
        
        # Import required modules
        if not _import_required_modules():
            return
        
        # Get current volume info for cover generation
        try:
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        except Exception as e:
            console_logger.warning(f" Could not get volume info: {e}")
            current_volume = 1
        
        # Step 1: Read all previous questions from log.csv
        console_logger.info(" Step 1: Reading all previous questions from log.csv...")
        previous_qa_pairs = read_log_csv()
        
        if not previous_qa_pairs:
            console_logger.warning(" No previous questions found in log.csv")
            console_logger.info(" Starting fresh with standard question generation...")
            # Generate simple question for first run
            available_themes = [theme.strip() for theme in SIMPLE_MODE_THEMES.split(',') if theme.strip()]
            if available_themes:
                selected_theme = random.choice(available_themes)
                connected_question = generate_single_question_for_category(selected_theme)
                if not connected_question:
                    console_logger.error(" Failed to generate question")
                    return
                selected_themes = [selected_theme]
            else:
                console_logger.error(" No valid themes found!")
                return
        else:
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
                    themes_used[theme] = themes_used.get(theme, 0) + 1
                    
                    # Extract key concepts from questions
                    words = question.lower().split()
                    for word in words:
                        if len(word) > 5 and word not in ['design', 'sustainable', 'research', 'technology', 'environmental']:
                            key_concepts.add(word)
                    
                    # Keep recent questions for reference
                    if len(recent_questions) < 5:
                        recent_questions.append(qa_pair)
            
            console_logger.info(f" Step 2: Found {len(themes_used)} themes and {len(key_concepts)} key concepts")
            
            # Step 3: Select theme(s) for new question
            available_themes = [theme.strip() for theme in SIMPLE_MODE_THEMES.split(',') if theme.strip()]
            
            # Determine how many themes to use
            if len(available_themes) == 1:
                selected_themes = [available_themes[0]]
                console_logger.info(f" Step 3: Single theme mode - exploring {selected_themes[0].upper()}")
            else:
                # Multi-theme mode - select 1-2 themes
                unused_themes = [theme for theme in available_themes if theme not in themes_used]
                if unused_themes:
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
            
            # Step 4: Generate connected question
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
                    connected_question = generate_single_question_for_category(selected_themes[0])
            
            if not connected_question:
                console_logger.error(" Failed to generate question")
                return
                
            console_logger.info(f" Step 4: Connected question created: {connected_question[:80]}...")
        
        # Step 5: Generate question image
        question_image_number = get_next_question_image_number()
        console_logger.info(f" Step 5: Generating question image #{question_image_number}...")
        
        try:
            from smart_image_generator import generate_image_with_smart_fallback
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
    
        # Step 6: Log question (temporarily, will be updated with answer)
        console_logger.info(f" Step 6: Logging connected question to CSV...")
        # For multi-theme questions, use the first theme as primary, but log all themes
        log_theme = selected_themes[0] if len(selected_themes) == 1 else f"multi_{'_'.join(selected_themes)}"
        
        # Note: We'll log the complete Q&A pair after generating the answer
        console_logger.info(f" Step 6: Question prepared for logging (will log with answer)")
        
        # Step 7: Add text overlay to question image
        console_logger.info(f" Step 7: Adding text overlay to question image...")
        try:
            from image_add_text import add_text_overlay
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
        
        # Step 11: Log complete Q&A pair
        console_logger.info(f" Step 11: Logging complete Q&A pair to CSV...")
        success = log_qa_pair(
            theme=selected_theme,
            question=connected_question,
            answer=answer,
            question_image=os.path.basename(image_path),
            answer_image=os.path.basename(answer_image_path),
            question_style=style,
            answer_style=answer_style
        )
        if not success:
            console_logger.error(" Failed to log Q&A pair")
            return
        console_logger.info(f" Step 11: Complete Q&A pair logged to CSV")
        
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
        
        # Step 13: Create cover images (optional)
        console_logger.info(f" Step 13: Creating cover images...")
        create_cover_if_needed(selected_theme, current_volume)
        
        # Completion summary
        console_logger.info("=" * 60)
        console_logger.info(f" Enhanced Simple Mode completed successfully!")
        console_logger.info(f" Connected question image: {os.path.basename(final_image_path)}")
        console_logger.info(f" Connected answer image: {os.path.basename(final_answer_image)}")
        console_logger.info(f" Theme: {selected_theme}")
        console_logger.info(f" Total Q&A pairs in database: {len(previous_qa_pairs) + 2}")
        console_logger.info(f" Connected experience created!")
        if CREATE_COVER_IMAGE:
            console_logger.info(f" Cover images generated!")
        
    except Exception as e:
        console_logger.error(f" Enhanced simple mode failed: {e}")
        raise

def main():
    """Main execution function"""
    try:
        console_logger.info("")
        console_logger.info(" *ASK*: Daily Research - Enhanced Simple Pipeline with Covers")
        console_logger.info("=" * 60)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode in ["help", "-help", "-h"]:
                show_help()
                return
            else:
                console_logger.error(f"Unknown mode: {mode}")
                show_help()
                return
        else:
            # Default mode: enhanced simple pipeline
            run_simple_mode()
        
    except Exception as e:
        console_logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
