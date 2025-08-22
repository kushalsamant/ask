#!/usr/bin/env python3
"""
Main Instagram Story Generator
Connects all modules to create the complete pipeline using focused orchestrators
"""

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import focused orchestrators
from research_orchestrator import ResearchOrchestrator
from image_generation_system import ImageGenerationSystem
from volume_manager import get_next_volume_number, log_volume_info

# Load environment variables from ask.env file
load_dotenv('ask.env')

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
            logging.FileHandler(f"{os.getenv('LOG_DIR', 'logs')}/execution.log")
        ]
)
log = logging.getLogger()

# Console logger for user-friendly output
console_logger = logging.getLogger('console')
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_logger.addHandler(console_handler)

# Environment variables
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))

# Validate API key
if not TOGETHER_API_KEY:
    log.error("ERROR: TOGETHER_API_KEY environment variable is not set!")
    console_logger.error("ERROR: TOGETHER_API_KEY environment variable is not set!")
    exit(1)

if not TOGETHER_API_KEY.startswith('tgp_'):
    log.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")
    console_logger.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")

log.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")
console_logger.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")

def main():
    """Main execution function"""
    try:
        console_logger.info("Starting Instagram Story Generation...")
        log.info("Starting Instagram Story Generation...")
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        questions_per_category = int(os.getenv('QUESTIONS_PER_CATEGORY', '1'))
        categories_to_generate = os.getenv('CATEGORIES_TO_GENERATE', '').split(',') if os.getenv('CATEGORIES_TO_GENERATE') else []
        
        # If no specific categories, use only one category for 1 Q&A pair per run
        if not categories_to_generate or categories_to_generate == ['']:
            # Use single category to ensure 1 Q&A pair per run
            categories_to_generate = ['architectural_design']
        
        console_logger.info(f"Configuration: {questions_per_category} questions per category")
        console_logger.info(f"Categories to generate: {len(categories_to_generate)}")
        
        # Step 1: Generate Q&A pairs
        console_logger.info("Generating Instagram stories with chained questions...")
        qa_pairs = research_orchestrator.generate_qa_pairs(
            categories=categories_to_generate,
            questions_per_category=questions_per_category
        )
        
        if not qa_pairs:
            console_logger.error("No Q&A pairs generated. Exiting.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} Q&A pairs")
        
        # Get current volume number based on log.csv
        current_volume = get_next_volume_number()
        log_volume_info()
        
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Step 2: Generate complete image set (Q&A images + covers)
        console_logger.info("Generating complete image set...")
        complete_image_set = image_system.generate_complete_image_set(qa_pairs, volume_number=current_volume)
        
        if not complete_image_set['qa_pairs']:
            console_logger.error("No images generated. Exiting.")
            return
        
        console_logger.info(f"✅ Generated {complete_image_set['total_images']} total images")
        console_logger.info(f"✅ Generated {len(complete_image_set['qa_pairs'])} Q&A image pairs")
        console_logger.info(f"✅ Generated {len(complete_image_set['covers'])} cover images")
        
        # Step 3: Generate research statistics
        console_logger.info("Generating research statistics...")
        stats = research_orchestrator.get_research_statistics()
        
        if stats:
            console_logger.info(f"✅ Research statistics: {stats.get('total_questions', 0)} total questions")
        
        # Step 4: Mark questions as used
        console_logger.info("Marking questions as used...")
        marked_count = research_orchestrator.mark_questions_as_used(qa_pairs)
        
        if marked_count > 0:
            console_logger.info(f"✅ Marked {marked_count} questions as used")
        
        console_logger.info("🎉 Instagram Story Generation completed successfully!")
        log.info("Instagram Story Generation completed successfully!")
        
    except Exception as e:
        console_logger.error(f"❌ Error in main execution: {e}")
        log.error(f"Error in main execution: {e}")
        raise

def generate_cross_disciplinary_content():
    """Generate cross-disciplinary content"""
    try:
        console_logger.info("Generating cross-disciplinary content...")
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        theme_count = int(os.getenv('CROSS_DISCIPLINARY_THEME_COUNT', '5'))
        
        # Generate cross-disciplinary Q&A pairs
        qa_pairs = research_orchestrator.generate_cross_disciplinary_qa_pairs(theme_count)
        
        if not qa_pairs:
            console_logger.error("No cross-disciplinary Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} cross-disciplinary Q&A pairs")
        
        # Generate images
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        console_logger.info("🎉 Cross-disciplinary content generation completed!")
        
    except Exception as e:
        console_logger.error(f"❌ Error in cross-disciplinary generation: {e}")
        log.error(f"Error in cross-disciplinary generation: {e}")
        raise

def generate_chained_content():
    """Generate chained content"""
    try:
        console_logger.info("Generating chained content...")
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        chain_length = int(os.getenv('CHAIN_LENGTH', '2'))
        categories_to_generate = os.getenv('CATEGORIES_TO_GENERATE', '').split(',') if os.getenv('CATEGORIES_TO_GENERATE') else []
        
        # If no specific categories, use all available categories
        if not categories_to_generate or categories_to_generate == ['']:
            # Use simple category list instead of complex research module
            categories_to_generate = ['architectural_design', 'construction_technology']
        
        # Generate chained Q&A pairs
        qa_pairs = research_orchestrator.generate_chained_qa_pairs(categories_to_generate, chain_length)
        
        if not qa_pairs:
            console_logger.error("No chained Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} chained Q&A pairs")
        
        # Generate images
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        console_logger.info("🎉 Chained content generation completed!")

    except Exception as e:
        console_logger.error(f"❌ Error in chained generation: {e}")
        log.error(f"Error in chained generation: {e}")
        raise

def generate_hybrid_content():
    """Generate hybrid cross-disciplinary chained content"""
    try:
        console_logger.info("Generating hybrid cross-disciplinary chained content...")
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        theme_count = int(os.getenv('HYBRID_THEME_COUNT', '2'))
        chain_length = int(os.getenv('HYBRID_CHAIN_LENGTH', '3'))
        
        console_logger.info(f"Configuration: {theme_count} themes, {chain_length} questions per chain")
        
        # Generate hybrid cross-disciplinary chained Q&A pairs
        qa_pairs = research_orchestrator.generate_hybrid_cross_disciplinary_chain(
            theme_count=theme_count,
            chain_length=chain_length
        )
        
        if not qa_pairs:
            console_logger.error("No hybrid Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} hybrid Q&A pairs")
        
        # Get current volume number
        current_volume = get_next_volume_number()
        log_volume_info()
        
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images for all Q&A pairs
        console_logger.info("Generating images for hybrid content...")
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        if qa_pairs_with_images:
            console_logger.info(f"✅ Generated images for {len(qa_pairs_with_images)} Q&A pairs")
        
        # Generate research statistics
        console_logger.info("Generating research statistics...")
        stats = research_orchestrator.get_research_statistics()
        
        if stats:
            console_logger.info(f"✅ Research statistics: {stats.get('total_questions', 0)} total questions")
        
        # Mark questions as used
        console_logger.info("Marking questions as used...")
        marked_count = research_orchestrator.mark_questions_as_used(qa_pairs)
        
        if marked_count > 0:
            console_logger.info(f"✅ Marked {marked_count} questions as used")
        
        console_logger.info("🎉 Hybrid cross-disciplinary chained content generation completed!")
        
    except Exception as e:
        console_logger.error(f"❌ Error in hybrid generation: {e}")
        log.error(f"Error in hybrid generation: {e}")
        raise

if __name__ == "__main__":
    # Check command line arguments for different modes
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "cross-disciplinary":
            generate_cross_disciplinary_content()
        elif mode == "chained":
            generate_chained_content()
        elif mode == "hybrid":
            generate_hybrid_content()
        elif mode == "help":
            console_logger.info("Available modes:")
            console_logger.info("  main.py                    - Standard generation")
            console_logger.info("  main.py cross-disciplinary - Cross-disciplinary content")
            console_logger.info("  main.py chained           - Chained content")
            console_logger.info("  main.py hybrid            - Hybrid cross-disciplinary chained content")
            console_logger.info("  main.py help              - Show this help")
        else:
            console_logger.error(f"Unknown mode: {mode}")
            console_logger.info("Use 'main.py help' for available modes")
    else:
        # Default mode: standard generation
        main()
