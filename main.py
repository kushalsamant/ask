#!/usr/bin/env python3
"""
ASK: Daily Architectural Research - Unified Pipeline
Enhanced main pipeline with all modes and features from simple_pipeline.py
"""

import os
import time
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Import focused orchestrators
from research_orchestrator import ResearchOrchestrator
from image_generation_system import ImageGenerationSystem
from volume_manager import get_next_volume_number, log_volume_info, get_current_volume_info

# Import simple pipeline components
from research_question_generator import generate_single_question_for_category
from research_answer_generator import generate_answer
from image_create_ai import generate_image_with_retry
from image_add_text import add_text_overlay
from research_csv_manager import log_single_question

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

# Validate API key (only if not showing help)
import sys
if len(sys.argv) <= 1 or sys.argv[1].lower() != 'help':
    if not TOGETHER_API_KEY:
        log.error("ERROR: TOGETHER_API_KEY environment variable is not set!")
        console_logger.error("ERROR: TOGETHER_API_KEY environment variable is not set!")
        exit(1)

    if not TOGETHER_API_KEY.startswith('tgp_'):
        log.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")
        console_logger.warning("WARNING: TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")

    log.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")
    console_logger.info(f"SUCCESS: API key configured: {TOGETHER_API_KEY[:10]}...")

class SimplePipeline:
    """Simple 12-step pipeline for Q&A image generation"""
    
    def __init__(self):
        """Initialize the pipeline"""
        self.themes = [
            'architectural_design',
            'construction_technology', 
            'design_innovation',
            'engineering_systems',
            'interior_environments',
            'urban_planning',
            'urban_design',
            'digital_technology'
        ]
        self.log_file = 'log.csv'
        self.image_counter = 1
        
        # Ensure directories exist
        os.makedirs('images', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def step_1_pick_theme(self) -> str:
        """Step 1: Pick a theme"""
        theme = random.choice(self.themes)
        log.info(f"Step 1: Picked theme: {theme}")
        console_logger.info(f"📋 Step 1: Theme selected: {theme.upper()}")
        return theme
    
    def step_2_create_question(self, theme: str) -> str:
        """Step 2: Create a question using theme"""
        log.info(f"Step 2: Creating question for theme: {theme}")
        console_logger.info(f"❓ Step 2: Generating question for {theme}...")
        
        question = generate_single_question_for_category(theme)
        if not question:
            raise Exception(f"Failed to generate question for theme: {theme}")
            
        log.info(f"Step 2: Generated question: {question[:100]}...")
        console_logger.info(f"✅ Step 2: Question created: {question[:80]}...")
        return question
    
    def step_3_log_question(self, question: str, theme: str) -> None:
        """Step 3: Paste the question text in the log"""
        log.info(f"Step 3: Logging question to {self.log_file}")
        console_logger.info(f"📝 Step 3: Logging question to CSV...")
        
        # Use the proper CSV manager function
        success = log_single_question(
            category=theme,
            question=question,
            image_filename='',  # Will be updated later
            style=None,
            is_answer=False,
            mark_as_used=False
        )
        
        if success:
            log.info(f"Step 3: Question logged successfully")
            console_logger.info(f"✅ Step 3: Question logged to CSV")
        else:
            raise Exception("Failed to log question to CSV")
    
    def step_4_create_question_image(self, question: str, theme: str) -> str:
        """Step 4: Create an image using question as a prompt"""
        log.info(f"Step 4: Creating image using question as prompt")
        console_logger.info(f"🎨 Step 4: Generating base image for question...")
        
        image_path, _ = generate_image_with_retry(
            prompt=question,
            category=theme,
            image_number=self.image_counter,
            image_type="q"
        )
        
        if not image_path:
            raise Exception("Failed to generate question image")
            
        log.info(f"Step 4: Question image created: {image_path}")
        console_logger.info(f"✅ Step 4: Base image created: {os.path.basename(image_path)}")
        return image_path
    
    def step_5_add_text_to_question_image(self, image_path: str, question: str, theme: str) -> str:
        """Step 5: Add text overlay to the question image"""
        log.info(f"Step 5: Adding text overlay to question image")
        console_logger.info(f"📝 Step 5: Adding text overlay to question image...")
        
        final_image_path = add_text_overlay(
            image_path=image_path,
            text=question,
            category=theme,
            image_number=self.image_counter,
            image_type="q"
        )
        
        if not final_image_path:
            raise Exception("Failed to add text overlay to question image")
            
        log.info(f"Step 5: Text overlay added successfully")
        console_logger.info(f"✅ Step 5: Text overlay added successfully")
        console_logger.info(f"✅ Step 6: Final question image created: {os.path.basename(final_image_path)}")
        return final_image_path
    
    def step_7_create_answer(self, question: str, theme: str) -> str:
        """Step 7: Create an answer using the question"""
        log.info(f"Step 7: Creating answer for question")
        console_logger.info(f"❓ Step 7: Generating answer for question...")
        
        answer = generate_answer(question, theme)
        if not answer:
            raise Exception("Failed to generate answer")
            
        log.info(f"Step 7: Generated answer: {answer[:100]}...")
        console_logger.info(f"✅ Step 7: Answer generated: {answer[:80]}...")
        return answer
    
    def step_8_log_answer(self, answer: str, theme: str) -> None:
        """Step 8: Log the answer to CSV"""
        log.info(f"Step 8: Logging answer to {self.log_file}")
        console_logger.info(f"📝 Step 8: Logging answer to CSV...")
        
        # Use the proper CSV manager function
        success = log_single_question(
            category=category,
            question='',  # Question was already logged in step 3
            answer=answer,
            image_filename='',  # Will be updated later
            style=None,
            is_answer=True,
            mark_as_used=False
        )
        
        if success:
            log.info(f"Step 8: Answer logged successfully")
            console_logger.info(f"✅ Step 8: Answer logged to CSV")
        else:
            raise Exception("Failed to log answer to CSV")
    
    def step_8b_mark_question_as_used(self, question: str, theme: str) -> None:
        """Step 8b: Mark question as used to prevent duplicates"""
        try:
            from research_csv_manager import mark_questions_as_used
            
            # Create a dictionary to mark this question as used
            questions_dict = {theme: question}
            marked_count = mark_questions_as_used(questions_dict)
            
            if marked_count > 0:
                log.info(f"Step 8b: Marked {marked_count} question as used")
                console_logger.info(f"🏷️  Step 8b: Marking question as used...")
                console_logger.info(f"✅ Step 8b: Question marked as used (prevents duplicates)")
            else:
                log.warning(f"Step 8b: No questions marked as used")
                
        except Exception as e:
            log.error(f"Step 8b: Error marking question as used: {e}")
            console_logger.warning(f"⚠️  Step 8b: Could not mark question as used: {e}")
    
    def step_9_create_answer_image(self, answer: str, theme: str) -> str:
        """Step 9: Create an image using answer as a prompt"""
        log.info(f"Step 9: Creating image using answer as prompt")
        console_logger.info(f"🎨 Step 9: Generating base image for answer...")
        
        image_path, _ = generate_image_with_retry(
            prompt=answer,
            category=theme,
            image_number=self.image_counter,
            image_type="a"
        )
        
        if not image_path:
            raise Exception("Failed to generate answer image")
            
        log.info(f"Step 9: Answer image created: {image_path}")
        console_logger.info(f"✅ Step 9: Base image created: {os.path.basename(image_path)}")
        return image_path
    
    def step_10_add_text_to_answer_image(self, image_path: str, answer: str, theme: str) -> str:
        """Step 10: Add text overlay to the answer image"""
        log.info(f"Step 10: Adding text overlay to answer image")
        console_logger.info(f"📝 Step 10: Adding text overlay to answer image...")
        
        final_image_path = add_text_overlay(
            image_path=image_path,
            text=answer,
            category=theme,
            image_number=self.image_counter,
            image_type="a"
        )
        
        if not final_image_path:
            raise Exception("Failed to add text overlay to answer image")
            
        log.info(f"Step 10: Text overlay added successfully")
        console_logger.info(f"✅ Step 10: Text overlay added successfully")
        console_logger.info(f"✅ Step 11: Final answer image created: {os.path.basename(final_image_path)}")
        return final_image_path
    
    def step_12_increment_counter(self) -> None:
        """Step 12: Increment counter and prepare for next cycle"""
        log.info(f"Step 12: Incrementing counter")
        console_logger.info(f"🔄 Step 12: Incrementing counter and preparing for next cycle...")
        
        self.image_counter += 1
        log.info(f"Step 12: Counter incremented to {self.image_counter}")
    
    def run_single_cycle(self) -> Dict:
        """Run a single complete cycle of the 12-step pipeline"""
        try:
            console_logger.info(f"🔄 Starting Cycle #{self.image_counter}")
            console_logger.info("=" * 60)
            
            # Get current volume info
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
            console_logger.info(f"📚 Starting at Volume {current_volume}: {qa_pairs_in_volume} Q&A pairs, {total_qa_pairs} total")
            
            # Step 1: Pick a theme
            theme = self.step_1_pick_theme()
            
            # Step 2: Create a question
            question = self.step_2_create_question(theme)
            
            # Step 3: Log the question
            self.step_3_log_question(question, theme)
            
            # Step 4: Create question image
            question_image_path = self.step_4_create_question_image(question, theme)
            
            # Step 5: Add text to question image
            final_question_image = self.step_5_add_text_to_question_image(question_image_path, question, theme)
            
            # Step 7: Create an answer
            answer = self.step_7_create_answer(question, theme)
            
            # Step 8: Log the answer
            self.step_8_log_answer(answer, theme)
            
            # Step 8b: Mark question as used
            self.step_8b_mark_question_as_used(question, theme)
            
            # Step 9: Create answer image
            answer_image_path = self.step_9_create_answer_image(answer, theme)
            
            # Step 10: Add text to answer image
            final_answer_image = self.step_10_add_text_to_answer_image(answer_image_path, answer, theme)
            
            # Step 12: Increment counter
            self.step_12_increment_counter()
            
            # Get updated volume info
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
            
            console_logger.info("=" * 60)
            console_logger.info(f"✅ Cycle #{self.image_counter-1} completed successfully!")
            console_logger.info(f"📂 Question image: {os.path.basename(final_question_image)}")
            console_logger.info(f"📂 Answer images: 1 images")
            console_logger.info(f"   📂 Answer image 1: {os.path.basename(final_answer_image)}")
            console_logger.info(f"📚 Volume {current_volume}: {qa_pairs_in_volume} Q&A pairs, {total_qa_pairs} total")
            
            return {
                'category': theme,
                'question': question,
                'answer': answer,
                'question_image': final_question_image,
                'answer_image': final_answer_image,
                'volume': current_volume
            }
            
        except Exception as e:
            log.error(f"Error in cycle {self.image_counter}: {e}")
            console_logger.error(f"❌ Cycle #{self.image_counter} failed: {e}")
            raise
    
    def run_continuous(self, cycles: int = 1) -> List[Dict]:
        """Run multiple cycles of the pipeline"""
        results = []
        
        for i in range(cycles):
            try:
                result = self.run_single_cycle()
                results.append(result)
                
                # Add delay between cycles if running multiple
                if cycles > 1 and i < cycles - 1:
                    time.sleep(RATE_LIMIT_DELAY)
                    
            except Exception as e:
                log.error(f"Failed to complete cycle {i+1}: {e}")
                console_logger.error(f"❌ Failed to complete cycle {i+1}: {e}")
                break
        
        return results

def generate_enhanced_statistics(qa_pairs):
    """Generate enhanced statistics for advanced modes"""
    try:
        console_logger.info(f"\n📊 ENHANCED STATISTICS")
        console_logger.info(f"=" * 40)
        
        # Basic statistics
        total_qa_pairs = len(qa_pairs)
        categories_used = list(set([qa.get('category', 'Unknown') for qa in qa_pairs]))
        
        console_logger.info(f"✅ Total Q&A pairs generated: {total_qa_pairs}")
        console_logger.info(f"✅ Categories used: {len(categories_used)}")
        console_logger.info(f"✅ Categories: {', '.join(categories_used)}")
        
        # Get current volume info
        current_volume, qa_pairs_in_volume, total_qa_pairs_db = get_current_volume_info()
        console_logger.info(f"✅ Current volume: {current_volume}")
        console_logger.info(f"✅ Q&A pairs in current volume: {qa_pairs_in_volume}")
        console_logger.info(f"✅ Total Q&A pairs in database: {total_qa_pairs_db}")
        
        # Enhanced: Try to get research statistics if available
        try:
            research_orchestrator = ResearchOrchestrator()
            stats = research_orchestrator.get_research_statistics()
            
            if stats:
                total_questions = stats.get('total_questions', 0)
                used_questions = stats.get('used_questions', 0)
                questions_by_category = stats.get('questions_by_category', {})
                
                console_logger.info(f"✅ Total questions in database: {total_questions}")
                console_logger.info(f"✅ Used questions: {used_questions}")
                
                if questions_by_category:
                    console_logger.info(f"✅ Questions by category:")
                    for category, count in questions_by_category.items():
                        console_logger.info(f"   • {category}: {count}")
                
        except Exception as e:
            log.debug(f"Could not load research statistics: {e}")
        
        console_logger.info(f"=" * 40)
        
    except Exception as e:
        log.error(f"Error generating enhanced statistics: {e}")
        console_logger.error(f"❌ Error generating statistics: {e}")

def generate_cover_images_if_enabled(qa_pairs):
    """Generate cover images if enabled"""
    try:
        # Check if cover generation is enabled
        generate_covers = os.getenv('SIMPLE_PIPELINE_GENERATE_COVERS', 'false').lower() == 'true'
        
        if not generate_covers:
            return
        
        console_logger.info(f"\n🎨 GENERATING COVER IMAGES")
        console_logger.info(f"=" * 40)
        
        # Initialize image generation system
        image_system = ImageGenerationSystem()
        
        # Get current volume info
        current_volume, _, _ = get_current_volume_info()
        
        # Generate volume cover
        console_logger.info(f"📚 Creating volume cover for Volume {current_volume}...")
        try:
            volume_cover = image_system.create_cover_image(
                title=f"ASK: Daily Architectural Research - Volume {current_volume}",
                subtitle="Comprehensive Research Collection",
                volume_number=current_volume
            )
            if volume_cover:
                console_logger.info(f"✅ Volume cover created: {os.path.basename(volume_cover)}")
        except Exception as e:
            console_logger.warning(f"⚠️  Could not create volume cover: {e}")
        
        # Generate category covers
        categories = list(set([qa.get('category', 'Unknown') for qa in qa_pairs]))
        console_logger.info(f"📂 Creating category covers for {len(categories)} categories...")
        
        for category in categories:
            try:
                category_cover = image_system.create_cover_image(
                    title=f"ASK: {category.replace('_', ' ').title()}",
                    subtitle="Research Collection",
                    category=category
                )
                if category_cover:
                    console_logger.info(f"✅ Category cover created for {category}: {os.path.basename(category_cover)}")
            except Exception as e:
                console_logger.warning(f"⚠️  Could not create category cover for {category}: {e}")
        
        console_logger.info(f"✅ Cover image generation completed")
        
    except Exception as e:
        log.error(f"Error generating cover images: {e}")
        console_logger.error(f"❌ Error generating cover images: {e}")

def create_backup_if_enabled():
    """Create backup if enabled"""
    try:
        create_backup = os.getenv('SIMPLE_PIPELINE_CREATE_BACKUP', 'true').lower() == 'true'
        
        if not create_backup:
            return
        
        console_logger.info(f"\n💾 CREATING BACKUP")
        console_logger.info(f"=" * 40)
        
        from research_backup_manager import create_backup
        
        backup_file = create_backup()
        if backup_file:
            console_logger.info(f"✅ Backup created: {os.path.basename(backup_file)}")
        else:
            console_logger.warning(f"⚠️  Could not create backup")
        
    except Exception as e:
        log.error(f"Error creating backup: {e}")
        console_logger.error(f"❌ Error creating backup: {e}")

def export_data_if_enabled(qa_pairs):
    """Export data if enabled"""
    try:
        export_data = os.getenv('SIMPLE_PIPELINE_EXPORT_DATA', 'false').lower() == 'true'
        
        if not export_data:
            return
        
        console_logger.info(f"\n📤 EXPORTING DATA")
        console_logger.info(f"=" * 40)
        
        from research_csv_manager import export_questions_to_csv
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"research_export_{timestamp}.csv"
        
        success = export_questions_to_csv(export_file)
        if success:
            console_logger.info(f"✅ Data exported: {export_file}")
        else:
            console_logger.warning(f"⚠️  Could not export data")
        
    except Exception as e:
        log.error(f"Error exporting data: {e}")
        console_logger.error(f"❌ Error exporting data: {e}")

def run_simple_mode():
    """Run the original simple 12-step pipeline"""
    try:
        console_logger.info("🎯 Starting Simple 12-Step Pipeline")
        console_logger.info("=" * 50)
        
        # Initialize pipeline
        pipeline = SimplePipeline()
        
        # Run single cycle (can be changed to run multiple cycles)
        cycles = int(os.getenv('PIPELINE_CYCLES', '1'))
        results = pipeline.run_continuous(cycles)
        
        console_logger.info(f"✅ Simple pipeline completed successfully!")
        console_logger.info(f"📊 Generated {len(results)} Q&A pairs")
        
    except Exception as e:
        console_logger.error(f"❌ Simple pipeline failed: {e}")
        raise

def run_hybrid_mode():
    """Run hybrid cross-disciplinary chained content generation"""
    try:
        console_logger.info("🎯 Starting Hybrid Cross-Disciplinary Chained Pipeline")
        console_logger.info("=" * 50)
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        theme_count = int(os.getenv('HYBRID_THEME_COUNT', '5'))
        chain_length = int(os.getenv('HYBRID_CHAIN_LENGTH', '2'))
        
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
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images for all Q&A pairs
        console_logger.info("Generating images for hybrid content...")
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        if qa_pairs_with_images:
            console_logger.info(f"✅ Generated images for {len(qa_pairs_with_images)} Q&A pairs")
        
        # Generate enhanced statistics
        generate_enhanced_statistics(qa_pairs)
        
        # Generate cover images if enabled
        generate_cover_images_if_enabled(qa_pairs)
        
        # Create backup
        create_backup_if_enabled()
        
        # Export data if enabled
        export_data_if_enabled(qa_pairs)
        
        console_logger.info("🎉 Hybrid cross-disciplinary chained content generation completed!")
        
    except Exception as e:
        console_logger.error(f"❌ Hybrid pipeline failed: {e}")
        raise

def run_cross_disciplinary_mode():
    """Run cross-disciplinary content generation"""
    try:
        console_logger.info("🎯 Starting Cross-Disciplinary Pipeline")
        console_logger.info("=" * 50)
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        theme_count = int(os.getenv('CROSS_DISCIPLINARY_THEME_COUNT', '10'))
        
        console_logger.info(f"Configuration: {theme_count} themes")
        
        # Generate cross-disciplinary Q&A pairs
        qa_pairs = research_orchestrator.generate_cross_disciplinary_qa_pairs(theme_count)
        
        if not qa_pairs:
            console_logger.error("No cross-disciplinary Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} cross-disciplinary Q&A pairs")
        
        # Get current volume number
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images for all Q&A pairs
        console_logger.info("Generating images for cross-disciplinary content...")
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        if qa_pairs_with_images:
            console_logger.info(f"✅ Generated images for {len(qa_pairs_with_images)} Q&A pairs")
        
        # Generate enhanced statistics
        generate_enhanced_statistics(qa_pairs)
        
        # Generate cover images if enabled
        generate_cover_images_if_enabled(qa_pairs)
        
        # Create backup
        create_backup_if_enabled()
        
        # Export data if enabled
        export_data_if_enabled(qa_pairs)
        
        console_logger.info("🎉 Cross-disciplinary content generation completed!")
        
    except Exception as e:
        console_logger.error(f"❌ Cross-disciplinary pipeline failed: {e}")
        raise

def run_chained_mode():
    """Run chained content generation"""
    try:
        console_logger.info("🎯 Starting Chained Content Pipeline")
        console_logger.info("=" * 50)
        
        # Initialize orchestrators
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        chain_length = int(os.getenv('CHAIN_LENGTH', '5'))
        themes_to_generate = os.getenv('CATEGORIES_TO_GENERATE', '').split(',') if os.getenv('CATEGORIES_TO_GENERATE') else []
        
        # If no specific themes, use default themes
        if not themes_to_generate or themes_to_generate == ['']:
            themes_to_generate = ['architectural_design', 'construction_technology']
        
        console_logger.info(f"Configuration: {chain_length} questions per chain, {len(themes_to_generate)} themes")
        
        # Generate chained Q&A pairs
        qa_pairs = research_orchestrator.generate_chained_qa_pairs(themes_to_generate, chain_length)
        
        if not qa_pairs:
            console_logger.error("No chained Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} chained Q&A pairs")
        
        # Get current volume number
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images for all Q&A pairs
        console_logger.info("Generating images for chained content...")
        qa_pairs_with_images = image_system.generate_qa_images(qa_pairs)
        
        if qa_pairs_with_images:
            console_logger.info(f"✅ Generated images for {len(qa_pairs_with_images)} Q&A pairs")
        
        # Generate enhanced statistics
        generate_enhanced_statistics(qa_pairs)
        
        # Generate cover images if enabled
        generate_cover_images_if_enabled(qa_pairs)
        
        # Create backup
        create_backup_if_enabled()
        
        # Export data if enabled
        export_data_if_enabled(qa_pairs)
        
        console_logger.info("🎉 Chained content generation completed!")

    except Exception as e:
        console_logger.error(f"❌ Chained pipeline failed: {e}")
        raise

def show_help():
    """Show help information for available modes"""
    console_logger.info("🎯 ASK: Daily Architectural Research - Available Modes")
    console_logger.info("=" * 60)
    console_logger.info("  python main.py                    - Simple 12-step pipeline (default)")
    console_logger.info("  python main.py hybrid             - Hybrid cross-disciplinary chained content")
    console_logger.info("  python main.py cross-disciplinary - Cross-disciplinary content")
    console_logger.info("  python main.py chained           - Chained content")
    console_logger.info("  python main.py help              - Show this help")
    console_logger.info("")
    console_logger.info("🎨 Mode Descriptions:")
    console_logger.info("  • Simple: Classic 12-step Q&A generation")
    console_logger.info("  • Hybrid: Combines cross-disciplinary themes with chained questions")
    console_logger.info("  • Cross-disciplinary: Explores intersections between architectural themes")
    console_logger.info("  • Chained: Creates connected questions that build upon each other")
    console_logger.info("")
    console_logger.info("⚙️  Configuration: Edit ask.env to customize each mode")

def main():
    """Main execution function - Enhanced with all modes"""
    try:
        # Check command line arguments for different modes
        import sys
        
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
        console_logger.error(f"❌ Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
