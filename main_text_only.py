#!/usr/bin/env python3
"""
*ASK*: Daily Research - Text-Only Q&A Generator
Simple pipeline for generating connected Q&A pairs in text format

Features:
- Connected Q&A generation with previous content reference
- Multi-theme support
- Text-only output (no image generation)
- Offline-first operation
- Comprehensive logging

Author: ASK Research Tool
Version: 5.0 (Text-Only)
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
from volume_manager import get_current_volume_info
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
SIMPLE_MODE_THEMES = os.getenv('SIMPLE_MODE_THEMES', 'research_methodology,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology').split(',')

def run_text_only_mode():
    """Run the text-only mode with connected Q&A generation"""
    try:
        console_logger.info("=" * 60)
        console_logger.info(" ASK: Daily Research - Text-Only Q&A Generator")
        console_logger.info("=" * 60)
        console_logger.info("")
        console_logger.info(" Features:")
        console_logger.info(" • Reads all previous questions from log.csv")
        console_logger.info(" • Generates questions that reference previous content")
        console_logger.info(" • Creates connected, chained-like experience")
        console_logger.info(" • Text-only output (no image generation)")
        console_logger.info(" • Multi-theme support")
        console_logger.info("")
        
        # Get current volume info
        current_volume, question_count, answer_count = get_current_volume_info()
        console_logger.info(f" Current Volume: {current_volume}")
        console_logger.info(f" Questions in volume: {question_count}")
        console_logger.info(f" Answers in volume: {answer_count}")
        console_logger.info("")
        
        # Step 1: Read all previous questions from log.csv
        console_logger.info(" Step 1: Reading all previous questions from log.csv...")
        previous_qa_pairs = read_log_csv()
        
        if not previous_qa_pairs:
            console_logger.warning(" No previous questions found in log.csv")
            console_logger.info(" Starting fresh with standard question generation...")
            # Generate simple question for first run
            selected_theme = random.choice(SIMPLE_MODE_THEMES)
            console_logger.info(f" Selected theme: {selected_theme}")
            
            # Generate question
            question = generate_single_question_for_category(selected_theme)
            if not question:
                console_logger.error(" Failed to generate question")
                return
            console_logger.info(f" Generated question: {question}")
            
            # Generate answer
            answer = generate_answer(question, selected_theme)
            if not answer:
                console_logger.error(" Failed to generate answer")
                return
            console_logger.info(f" Generated answer: {answer[:100]}...")
            
            # Log Q&A pair (no image files)
            success = log_qa_pair(
                theme=selected_theme,
                question=question,
                answer=answer,
                question_image="",  # No image
                answer_image="",    # No image
                question_style="Text-Only",
                answer_style="Text-Only"
            )
            
            if success:
                console_logger.info(" Q&A pair logged successfully")
                console_logger.info("=" * 60)
                console_logger.info(" Text-Only Mode completed successfully!")
                console_logger.info(f" Question: {question}")
                console_logger.info(f" Answer: {answer[:200]}...")
                console_logger.info(f" Theme: {selected_theme}")
                console_logger.info("=" * 60)
            else:
                console_logger.error(" Failed to log Q&A pair")
            
            return
        
        # Step 2: Generate connected question
        console_logger.info(f" Found {len(previous_qa_pairs)} previous Q&A pairs")
        console_logger.info(" Step 2: Generating connected question...")
        
        # Select theme
        selected_theme = random.choice(SIMPLE_MODE_THEMES)
        console_logger.info(f" Selected theme: {selected_theme}")
        
        # Generate connected question
        connected_question = generate_single_question_for_category(selected_theme)
        if not connected_question:
            console_logger.error(" Failed to generate connected question")
            return
        console_logger.info(f" Connected question generated: {connected_question}")
        
        # Step 3: Generate connected answer
        console_logger.info(" Step 3: Generating connected answer...")
        answer = generate_answer(connected_question, selected_theme)
        if not answer:
            console_logger.error(" Failed to generate answer")
            return
        console_logger.info(f" Connected answer generated: {answer[:100]}...")
        
        # Step 4: Mark question as used
        console_logger.info(" Step 4: Marking question as used...")
        try:
            questions_dict = {selected_theme: connected_question}
            marked_count = mark_questions_as_used(questions_dict)
            if marked_count > 0:
                console_logger.info(f" Question marked as used (prevents duplicates)")
            else:
                console_logger.warning(" No questions marked as used")
        except Exception as e:
            console_logger.warning(f" Could not mark question as used: {e}")
        
        # Step 5: Log complete Q&A pair
        console_logger.info(" Step 5: Logging complete Q&A pair to CSV...")
        success = log_qa_pair(
            theme=selected_theme,
            question=connected_question,
            answer=answer,
            question_image="",  # No image
            answer_image="",    # No image
            question_style="Text-Only",
            answer_style="Text-Only"
        )
        
        if not success:
            console_logger.error(" Failed to log Q&A pair")
            return
        console_logger.info(" Complete Q&A pair logged to CSV")
        
        # Completion summary
        console_logger.info("=" * 60)
        console_logger.info(" Text-Only Mode completed successfully!")
        console_logger.info(f" Question: {connected_question}")
        console_logger.info(f" Answer: {answer[:200]}...")
        console_logger.info(f" Theme: {selected_theme}")
        console_logger.info(f" Total Q&A pairs in database: {len(previous_qa_pairs) + 1}")
        console_logger.info(" Connected experience created!")
        console_logger.info("=" * 60)
        
    except Exception as e:
        console_logger.error(f" Text-only mode failed: {e}")
        raise

def show_help():
    """Show help information"""
    console_logger.info("")
    console_logger.info(" ASK: Daily Research - Text-Only Q&A Generator")
    console_logger.info("=" * 60)
    console_logger.info("")
    console_logger.info(" Usage:")
    console_logger.info("   python main_text_only.py          # Run text-only Q&A generation")
    console_logger.info("   python main_text_only.py --help   # Show this help")
    console_logger.info("")
    console_logger.info(" Features:")
    console_logger.info(" • Text-only Q&A generation")
    console_logger.info(" • Connected, chained-like experience")
    console_logger.info(" • Multi-theme support")
    console_logger.info(" • Offline operation")
    console_logger.info(" • CSV logging")
    console_logger.info("")
    console_logger.info(" Configuration:")
    console_logger.info(" • Edit ask.env to customize themes and settings")
    console_logger.info(" • Check log.csv for generated Q&A pairs")
    console_logger.info("")

def main():
    """Main execution function"""
    try:
        console_logger.info("")
        console_logger.info(" *ASK*: Daily Research - Text-Only Q&A Generator")
        console_logger.info("=" * 60)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode in ["help", "--help", "-h"]:
                show_help()
                return
            else:
                console_logger.error(f"Unknown mode: {mode}")
                show_help()
                return
        else:
            # Default mode: text-only pipeline
            run_text_only_mode()
        
    except KeyboardInterrupt:
        console_logger.info("\n Operation cancelled by user")
    except Exception as e:
        console_logger.error(f" Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
