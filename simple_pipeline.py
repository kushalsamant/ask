#!/usr/bin/env python3
"""
Simple Pipeline for ASK: Daily Architectural Research
Follows the 12-step process exactly as specified
"""

import os
import logging
import random
from datetime import datetime
from typing import Dict, List

# Import required modules
from research_question_generator import generate_single_question_for_category
from research_answer_generator import generate_answer
from image_create_ai import generate_image_with_retry
from image_add_text import add_text_overlay
from research_csv_manager import log_single_question
from volume_manager import get_next_volume_number, log_volume_info, get_current_volume_info

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(name)s:%(levelname)s:%(message)s')
log = logging.getLogger(__name__)
console_logger = logging.getLogger('console')

class SimplePipeline:
    """Simple 12-step pipeline for Q&A image generation"""
    
    def __init__(self):
        """Initialize the pipeline"""
        self.categories = [
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
        
    def step_1_pick_category(self) -> str:
        """Step 1: Pick a category"""
        category = random.choice(self.categories)
        log.info(f"Step 1: Picked category: {category}")
        console_logger.info(f"📋 Step 1: Category selected: {category.upper()}")
        return category
    
    def step_2_create_question(self, category: str) -> str:
        """Step 2: Create a question using category"""
        log.info(f"Step 2: Creating question for category: {category}")
        console_logger.info(f"❓ Step 2: Generating question for {category}...")
        
        question = generate_single_question_for_category(category)
        if not question:
            raise Exception(f"Failed to generate question for category: {category}")
            
        log.info(f"Step 2: Generated question: {question[:100]}...")
        console_logger.info(f"✅ Step 2: Question created: {question[:80]}...")
        return question
    
    def step_3_log_question(self, question: str, category: str) -> None:
        """Step 3: Paste the question text in the log"""
        log.info(f"Step 3: Logging question to {self.log_file}")
        console_logger.info(f"📝 Step 3: Logging question to CSV...")
        
        # Use the proper CSV manager function
        success = log_single_question(
            category=category,
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
    
    def step_4_create_question_image(self, question: str, category: str) -> str:
        """Step 4: Create an image using question as a prompt"""
        log.info(f"Step 4: Creating image using question as prompt")
        console_logger.info(f"🎨 Step 4: Generating base image for question...")
        
        image_path, _ = generate_image_with_retry(
            prompt=question,
            category=category,
            image_number=self.image_counter,
            image_type="q"
        )
        
        if not image_path:
            raise Exception("Failed to generate question image")
            
        log.info(f"Step 4: Question image created: {image_path}")
        console_logger.info(f"✅ Step 4: Base question image generated")
        return image_path
    
    def step_5_paste_question_text(self, image_path: str, question: str) -> str:
        """Step 5: Paste question text on the image following layout rules"""
        log.info(f"Step 5: Pasting question text on image following layout rules")
        console_logger.info(f"📝 Step 5: Adding question text overlay...")
        
        enhanced_image_path = add_text_overlay(
            image_path=image_path,
            prompt=question,
            image_number=self.image_counter,
            is_question=True
        )
        
        log.info(f"Step 5: Question text pasted on image: {enhanced_image_path}")
        console_logger.info(f"✅ Step 5: Question text overlay applied")
        return enhanced_image_path
    
    def step_6_finalize_question_image(self, image_path: str) -> str:
        """Step 6: Create final question image"""
        log.info(f"Step 6: Finalizing question image")
        console_logger.info(f"🖼️ Step 6: Final question image ready")
        
        # Image is already finalized from step 5
        final_path = image_path
        
        log.info(f"Step 6: Final question image: {final_path}")
        console_logger.info(f"✅ Step 6: Question image finalized: {os.path.basename(final_path)}")
        return final_path
    
    def step_7_answer_question(self, question: str, category: str) -> str:
        """Step 7: Answer the question"""
        log.info(f"Step 7: Answering the question")
        console_logger.info(f"💡 Step 7: Generating answer...")
        
        answer = generate_answer(question, category, None)
        if not answer:
            raise Exception("Failed to generate answer")
            
        log.info(f"Step 7: Generated answer: {answer[:100]}...")
        console_logger.info(f"✅ Step 7: Answer created: {answer[:80]}...")
        return answer
    
    def step_8_log_answer(self, answer: str, category: str) -> None:
        """Step 8: Paste the answer text in the log"""
        log.info(f"Step 8: Logging answer to {self.log_file}")
        console_logger.info(f"📝 Step 8: Logging answer to CSV...")
        
        # Use the proper CSV manager function
        success = log_single_question(
            category=category,
            question='',  # Question already logged in step 3
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
    
    def step_8b_mark_question_as_used(self, question: str, category: str) -> None:
        """Step 8b: Mark question as used to prevent duplicates"""
        try:
            # Check if question marking is enabled
            mark_questions = os.getenv('SIMPLE_PIPELINE_MARK_QUESTIONS_USED', 'true').lower() == 'true'
            
            if not mark_questions:
                return
            
            log.info(f"Step 8b: Marking question as used")
            console_logger.info(f"🏷️  Step 8b: Marking question as used...")
            
            # Import the marking function
            from research_csv_manager import mark_questions_as_used
            
            # Mark the question as used
            questions_dict = {category: question}
            marked_count = mark_questions_as_used(questions_dict)
            
            if marked_count > 0:
                log.info(f"Step 8b: Question marked as used successfully")
                console_logger.info(f"✅ Step 8b: Question marked as used (prevents duplicates)")
            else:
                log.warning(f"Step 8b: Question marking may have failed")
                console_logger.warning(f"⚠️  Step 8b: Question marking may have failed")
                
        except Exception as e:
            log.error(f"Error marking question as used: {e}")
            console_logger.warning(f"⚠️  Step 8b: Could not mark question as used: {e}")
    
    def step_9_create_answer_image(self, answer: str, category: str) -> str:
        """Step 9: Create an image using answer as a prompt"""
        log.info(f"Step 9: Creating image using answer as prompt")
        console_logger.info(f"🎨 Step 9: Generating base image for answer...")
        
        image_path, _ = generate_image_with_retry(
            prompt=answer,
            category=category,
            image_number=self.image_counter,
            image_type="a"
        )
        
        if not image_path:
            raise Exception("Failed to generate answer image")
            
        log.info(f"Step 9: Answer image created: {image_path}")
        console_logger.info(f"✅ Step 9: Base answer image generated")
        return image_path
    
    def step_10_paste_answer_text(self, image_path: str, answer: str) -> list:
        """Step 10: Paste answer text on the image following layout rules"""
        log.info(f"Step 10: Pasting answer text on image following layout rules")
        console_logger.info(f"📝 Step 10: Adding answer text overlay...")
        
        enhanced_image_path = add_text_overlay(
            image_path=image_path,
            prompt=answer,
            image_number=self.image_counter,
            is_question=False
        )
        
        # Check if multiple images were created
        if isinstance(enhanced_image_path, list):
            # Multiple images were created
            image_paths = enhanced_image_path
            log.info(f"Step 10: Multiple answer images created: {len(image_paths)} images")
            console_logger.info(f"✅ Step 10: Created {len(image_paths)} answer images")
            return image_paths
        else:
            # Single image was created
            log.info(f"Step 10: Answer text pasted on image: {enhanced_image_path}")
            console_logger.info(f"✅ Step 10: Answer text overlay applied")
            return [enhanced_image_path]
    
    def step_11_finalize_answer_image(self, image_paths: list) -> list:
        """Step 11: Create final answer images"""
        log.info(f"Step 11: Finalizing answer images")
        console_logger.info(f"🖼️ Step 11: Final answer images ready")
        
        # Images are already finalized from step 10
        final_paths = image_paths
        
        log.info(f"Step 11: Final answer images: {len(final_paths)} images")
        for i, path in enumerate(final_paths, 1):
            console_logger.info(f"✅ Step 11: Answer image {i} finalized: {os.path.basename(path)}")
        return final_paths
    
    def step_12_increment_and_loop(self, answer_images_count: int = 1) -> None:
        """Step 12: Increment counter and prepare for next iteration"""
        # Increment by the number of answer images created (1 for single image, more for multi-image)
        self.image_counter += answer_images_count
        log.info(f"Step 12: Incremented counter to {self.image_counter}, ready for next iteration")
        console_logger.info(f"🔄 Step 12: Q&A pair #{self.image_counter - answer_images_count} completed, ready for next iteration")
    
    def run_single_cycle(self) -> Dict[str, str]:
        """Run a single cycle of the 12-step pipeline"""
        console_logger.info(f"🔄 Starting Cycle #{self.image_counter}")
        console_logger.info(f"=" * 60)
        
        try:
            # Step 1: Pick a category
            category = self.step_1_pick_category()
            
            # Step 2: Create a question using category
            question = self.step_2_create_question(category)
            
            # Step 3: Paste the question text in the log
            self.step_3_log_question(question, category)
            
            # Step 4: Create an image using question as a prompt
            question_image_path = self.step_4_create_question_image(question, category)
            
            # Step 5: Paste question text on the image following layout rules
            enhanced_question_image = self.step_5_paste_question_text(question_image_path, question)
            
            # Step 6: Create final question image
            final_question_image = self.step_6_finalize_question_image(enhanced_question_image)
            
            # Step 7: Answer the question
            answer = self.step_7_answer_question(question, category)
            
            # Step 8: Paste the answer text in the log
            self.step_8_log_answer(answer, category)
            
            # Step 8b: Mark question as used
            self.step_8b_mark_question_as_used(question, category)
            
            # Step 9: Create an image using answer as a prompt
            answer_image_path = self.step_9_create_answer_image(answer, category)
            
            # Step 10: Paste answer text on the image following layout rules
            enhanced_answer_images = self.step_10_paste_answer_text(answer_image_path, answer)
            
            # Step 11: Create final answer images
            final_answer_images = self.step_11_finalize_answer_image(enhanced_answer_images)
            
            # Step 12: Increment and prepare for loop
            self.step_12_increment_and_loop(len(final_answer_images))
            
            # Enhanced: Get volume information
            current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
            
            console_logger.info(f"=" * 60)
            console_logger.info(f"✅ Cycle #{self.image_counter - 1} completed successfully!")
            console_logger.info(f"📂 Question image: {os.path.basename(final_question_image)}")
            console_logger.info(f"📂 Answer images: {len(final_answer_images)} images")
            for i, answer_img in enumerate(final_answer_images, 1):
                console_logger.info(f"   📂 Answer image {i}: {os.path.basename(answer_img)}")
            
            # Enhanced: Show volume progress
            console_logger.info(f"📚 Volume {current_volume}: {qa_pairs_in_volume} Q&A pairs, {total_qa_pairs} total")
            
            return {
                'cycle_number': self.image_counter - 1,
                'category': category,
                'question': question,
                'answer': answer,
                'question_image': final_question_image,
                'answer_images': final_answer_images,
                'volume_number': current_volume,
                'volume_progress': qa_pairs_in_volume,
                'total_qa_pairs': total_qa_pairs
            }
            
        except Exception as e:
            log.error(f"Error in cycle #{self.image_counter}: {e}")
            console_logger.error(f"❌ Error in cycle #{self.image_counter}: {e}")
            raise
    
    def run_continuous(self, cycles: int = 1) -> List[Dict[str, str]]:
        """Run multiple cycles of the pipeline"""
        console_logger.info(f"🎯 Starting Simple Pipeline - {cycles} cycle(s)")
        
        # Enhanced: Show initial volume info
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Starting at Volume {current_volume}: {qa_pairs_in_volume} Q&A pairs, {total_qa_pairs} total")
        
        results = []
        for i in range(cycles):
            try:
                result = self.run_single_cycle()
                results.append(result)
                
                if i < cycles - 1:  # Not the last cycle
                    console_logger.info(f"\n⏳ Preparing for next cycle...")
                    
            except Exception as e:
                console_logger.error(f"❌ Pipeline failed at cycle {i + 1}: {e}")
                break
        
        # Enhanced: Generate final statistics
        self._generate_final_statistics(results)
        
        # Enhanced: Generate cover images if enabled
        self._generate_cover_images(results)
        
        # Enhanced: Create backup
        self._create_backup()
        
        # Enhanced: Export data if enabled
        self._export_data(results)
        
        console_logger.info(f"\n🎉 Pipeline completed! Generated {len(results)} Q&A pairs")
        return results
    
    def _generate_final_statistics(self, results: List[Dict[str, str]]) -> None:
        """Generate and display final statistics"""
        try:
            console_logger.info(f"\n📊 FINAL STATISTICS")
            console_logger.info(f"=" * 40)
            
            # Basic statistics
            total_qa_pairs = len(results)
            categories_used = list(set([r.get('category', 'Unknown') for r in results]))
            
            console_logger.info(f"✅ Total Q&A pairs generated: {total_qa_pairs}")
            console_logger.info(f"✅ Categories used: {len(categories_used)}")
            console_logger.info(f"✅ Categories: {', '.join(categories_used)}")
            
            # Volume statistics
            if results:
                final_result = results[-1]
                final_volume = final_result.get('volume_number', 1)
                final_volume_progress = final_result.get('volume_progress', 0)
                total_qa_pairs = final_result.get('total_qa_pairs', 0)
                
                console_logger.info(f"✅ Final volume: {final_volume}")
                console_logger.info(f"✅ Q&A pairs in current volume: {final_volume_progress}")
                console_logger.info(f"✅ Total Q&A pairs in database: {total_qa_pairs}")
            
            # Enhanced: Try to get research statistics if available
            try:
                from research_orchestrator import ResearchOrchestrator
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
            
            # Enhanced: Research direction analysis
            self._analyze_research_direction(results)
            
            console_logger.info(f"=" * 40)
            
        except Exception as e:
            log.error(f"Error generating final statistics: {e}")
            console_logger.error(f"❌ Error generating statistics: {e}")
    
    def _analyze_research_direction(self, results: List[Dict[str, str]]) -> None:
        """Analyze research direction of generated content"""
        try:
            # Check if analysis is enabled
            enable_analysis = os.getenv('SIMPLE_PIPELINE_ANALYZE_DIRECTION', 'true').lower() == 'true'
            
            if not enable_analysis or not results:
                return
            
            console_logger.info(f"\n🔍 RESEARCH DIRECTION ANALYSIS")
            console_logger.info(f"=" * 40)
            
            # Basic analysis
            categories = [r.get('category', 'Unknown') for r in results]
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Find most common category
            if category_counts:
                most_common = max(category_counts, key=category_counts.get)
                console_logger.info(f"🎯 Primary focus: {most_common.replace('_', ' ').title()}")
                console_logger.info(f"📊 Category distribution:")
                for category, count in category_counts.items():
                    percentage = (count / len(results)) * 100
                    console_logger.info(f"   • {category.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
            
            # Enhanced: Try to get AI-powered analysis
            try:
                from research_orchestrator import ResearchOrchestrator
                research_orchestrator = ResearchOrchestrator()
                
                # Convert results to format expected by analysis function
                qa_pairs_for_analysis = []
                for result in results:
                    qa_pairs_for_analysis.append({
                        'question_text': result.get('question', ''),
                        'answer_text': result.get('answer', ''),
                        'category': result.get('category', 'Unknown')
                    })
                
                analysis = research_orchestrator.analyze_research_direction(qa_pairs_for_analysis)
                
                if analysis:
                    console_logger.info(f"🤖 AI Analysis Insights:")
                    # Display key insights from analysis
                    if 'themes' in analysis:
                        console_logger.info(f"   • Key themes: {', '.join(analysis['themes'][:3])}")
                    if 'trends' in analysis:
                        console_logger.info(f"   • Research trends: {analysis['trends'][:100]}...")
                    if 'recommendations' in analysis:
                        console_logger.info(f"   • Recommendations: {analysis['recommendations'][:100]}...")
                
            except Exception as e:
                log.debug(f"Could not perform AI analysis: {e}")
            
            console_logger.info(f"=" * 40)
            
        except Exception as e:
            log.error(f"Error analyzing research direction: {e}")
            console_logger.warning(f"⚠️  Could not analyze research direction: {e}")
    
    def _create_backup(self) -> None:
        """Create backup of log.csv file"""
        try:
            # Check if backup is enabled
            enable_backup = os.getenv('SIMPLE_PIPELINE_CREATE_BACKUP', 'true').lower() == 'true'
            
            if not enable_backup:
                return
            
            console_logger.info(f"\n💾 CREATING BACKUP")
            console_logger.info(f"=" * 40)
            
            try:
                from research_backup_manager import backup_log_csv
                
                backup_filename = backup_log_csv()
                
                if backup_filename:
                    console_logger.info(f"✅ Backup created: {os.path.basename(backup_filename)}")
                else:
                    console_logger.warning("⚠️  Backup creation failed")
                
            except ImportError:
                console_logger.warning("⚠️  Backup module not available")
            except Exception as e:
                log.error(f"Error creating backup: {e}")
                console_logger.warning(f"⚠️  Backup creation failed: {e}")
            
            console_logger.info(f"=" * 40)
            
        except Exception as e:
            log.error(f"Error in backup creation: {e}")
    
    def _export_data(self, results: List[Dict[str, str]]) -> None:
        """Export research data to CSV"""
        try:
            # Check if export is enabled
            enable_export = os.getenv('SIMPLE_PIPELINE_EXPORT_DATA', 'false').lower() == 'true'
            
            if not enable_export:
                return
            
            console_logger.info(f"\n📤 EXPORTING DATA")
            console_logger.info(f"=" * 40)
            
            try:
                from research_orchestrator import ResearchOrchestrator
                research_orchestrator = ResearchOrchestrator()
                
                # Export research data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_filename = f"research_export_{timestamp}.csv"
                
                success = research_orchestrator.export_research_data(export_filename)
                
                if success:
                    console_logger.info(f"✅ Data exported: {export_filename}")
                else:
                    console_logger.warning("⚠️  Data export failed")
                
            except ImportError:
                console_logger.warning("⚠️  Export module not available")
            except Exception as e:
                log.error(f"Error exporting data: {e}")
                console_logger.warning(f"⚠️  Data export failed: {e}")
            
            console_logger.info(f"=" * 40)
            
        except Exception as e:
            log.error(f"Error in data export: {e}")
    
    def _generate_cover_images(self, results: List[Dict[str, str]]) -> None:
        """Generate cover images if enabled (now uses ImageGenerationSystem)"""
        try:
            # Check if cover generation is enabled
            generate_covers = os.getenv('SIMPLE_PIPELINE_GENERATE_COVERS', 'false').lower() == 'true'
            
            if not generate_covers:
                return
            
            console_logger.info(f"\n🎨 GENERATING COVER IMAGES")
            console_logger.info(f"=" * 40)
            
            # Use ImageGenerationSystem for cover generation
            try:
                from image_generation_system import ImageGenerationSystem
                
                # Get current volume info
                current_volume, _, _ = get_current_volume_info()
                
                # Create image generation system
                image_system = ImageGenerationSystem()
                
                # Generate cover images
                cover_results = image_system.create_cover_image(current_volume, results)
                
                if cover_results:
                    console_logger.info(f"✅ Cover images generated successfully")
                else:
                    console_logger.warning("⚠️  Cover image generation failed")
                
                console_logger.info(f"✅ Cover image generation completed")
                
            except ImportError as e:
                console_logger.warning(f"⚠️  Image generation system not available: {e}")
                console_logger.info("   Install required modules to enable cover generation")
            
        except Exception as e:
            log.error(f"Error generating cover images: {e}")
            console_logger.error(f"❌ Error generating cover images: {e}")

def main():
    """Main function to run the simple pipeline"""
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
        from research_orchestrator import ResearchOrchestrator
        from image_generation_system import ImageGenerationSystem
        
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
        from research_orchestrator import ResearchOrchestrator
        from image_generation_system import ImageGenerationSystem
        
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        theme_count = int(os.getenv('CROSS_DISCIPLINARY_THEME_COUNT', '3'))
        
        console_logger.info(f"Configuration: {theme_count} cross-disciplinary themes")
        
        # Generate cross-disciplinary Q&A pairs
        qa_pairs = research_orchestrator.generate_cross_disciplinary_qa_pairs(theme_count)
        
        if not qa_pairs:
            console_logger.error("No cross-disciplinary Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} cross-disciplinary Q&A pairs")
        
        # Get current volume number
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images
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
        from research_orchestrator import ResearchOrchestrator
        from image_generation_system import ImageGenerationSystem
        
        research_orchestrator = ResearchOrchestrator()
        image_system = ImageGenerationSystem()
        
        # Get configuration
        chain_length = int(os.getenv('CHAIN_LENGTH', '3'))
        categories_to_generate = os.getenv('CATEGORIES_TO_GENERATE', '').split(',') if os.getenv('CATEGORIES_TO_GENERATE') else []
        
        # If no specific categories, use default categories
        if not categories_to_generate or categories_to_generate == ['']:
            categories_to_generate = ['architectural_design', 'construction_technology']
        
        console_logger.info(f"Configuration: {chain_length} questions per chain, {len(categories_to_generate)} categories")
        
        # Generate chained Q&A pairs
        qa_pairs = research_orchestrator.generate_chained_qa_pairs(categories_to_generate, chain_length)
        
        if not qa_pairs:
            console_logger.error("No chained Q&A pairs generated.")
            return
        
        console_logger.info(f"✅ Generated {len(qa_pairs)} chained Q&A pairs")
        
        # Get current volume number
        current_volume, qa_pairs_in_volume, total_qa_pairs = get_current_volume_info()
        console_logger.info(f"📚 Current Volume: {current_volume}")
        
        # Generate images
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
    console_logger.info("🎯 Simple Pipeline - Available Modes")
    console_logger.info("=" * 50)
    console_logger.info("  python simple_pipeline.py                    - Simple 12-step pipeline (default)")
    console_logger.info("  python simple_pipeline.py hybrid             - Hybrid cross-disciplinary chained content")
    console_logger.info("  python simple_pipeline.py cross-disciplinary - Cross-disciplinary content")
    console_logger.info("  python simple_pipeline.py chained           - Chained content")
    console_logger.info("  python simple_pipeline.py help              - Show this help")
    console_logger.info("")
    console_logger.info("🎨 Mode Descriptions:")
    console_logger.info("  • Simple: Classic 12-step Q&A generation")
    console_logger.info("  • Hybrid: Combines cross-disciplinary themes with chained questions")
    console_logger.info("  • Cross-disciplinary: Explores intersections between architectural categories")
    console_logger.info("  • Chained: Creates connected questions that build upon each other")
    console_logger.info("")
    console_logger.info("⚙️  Configuration: Edit ask.env to customize each mode")

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
            from research_orchestrator import ResearchOrchestrator
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
    """Generate cover images if enabled (now uses ImageGenerationSystem)"""
    try:
        # Check if cover generation is enabled
        generate_covers = os.getenv('SIMPLE_PIPELINE_GENERATE_COVERS', 'false').lower() == 'true'
        
        if not generate_covers:
            return
        
        console_logger.info(f"\n🎨 GENERATING COVER IMAGES")
        console_logger.info(f"=" * 40)
        
        # Use ImageGenerationSystem for cover generation
        try:
            from image_generation_system import ImageGenerationSystem
            
            # Get current volume info
            current_volume, _, _ = get_current_volume_info()
            
            # Create image generation system
            image_system = ImageGenerationSystem()
            
            # Generate cover images
            cover_results = image_system.create_cover_image(current_volume, qa_pairs)
            
            if cover_results:
                console_logger.info(f"✅ Cover images generated successfully")
            else:
                console_logger.warning("⚠️  Cover image generation failed")
            
            console_logger.info(f"✅ Cover image generation completed")
            
        except ImportError as e:
            console_logger.warning(f"⚠️  Image generation system not available: {e}")
            console_logger.info("   Install required modules to enable cover generation")
        
    except Exception as e:
        log.error(f"Error generating cover images: {e}")
        console_logger.error(f"❌ Error generating cover images: {e}")

def create_backup_if_enabled():
    """Create backup if enabled"""
    try:
        # Check if backup is enabled
        enable_backup = os.getenv('SIMPLE_PIPELINE_CREATE_BACKUP', 'true').lower() == 'true'
        
        if not enable_backup:
            return
        
        console_logger.info(f"\n💾 CREATING BACKUP")
        console_logger.info(f"=" * 40)
        
        try:
            from research_backup_manager import backup_log_csv
            
            backup_filename = backup_log_csv()
            
            if backup_filename:
                console_logger.info(f"✅ Backup created: {os.path.basename(backup_filename)}")
            else:
                console_logger.warning("⚠️  Backup creation failed")
            
        except ImportError:
            console_logger.warning("⚠️  Backup module not available")
        except Exception as e:
            log.error(f"Error creating backup: {e}")
            console_logger.warning(f"⚠️  Backup creation failed: {e}")
        
        console_logger.info(f"=" * 40)
        
    except Exception as e:
        log.error(f"Error in backup creation: {e}")

def export_data_if_enabled(qa_pairs):
    """Export data if enabled"""
    try:
        # Check if export is enabled
        enable_export = os.getenv('SIMPLE_PIPELINE_EXPORT_DATA', 'false').lower() == 'true'
        
        if not enable_export:
            return
        
        console_logger.info(f"\n📤 EXPORTING DATA")
        console_logger.info(f"=" * 40)
        
        try:
            from research_orchestrator import ResearchOrchestrator
            research_orchestrator = ResearchOrchestrator()
            
            # Export research data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"research_export_{timestamp}.csv"
            
            success = research_orchestrator.export_research_data(export_filename)
            
            if success:
                console_logger.info(f"✅ Data exported: {export_filename}")
            else:
                console_logger.warning("⚠️  Data export failed")
            
        except ImportError:
            console_logger.warning("⚠️  Export module not available")
        except Exception as e:
            log.error(f"Error exporting data: {e}")
            console_logger.warning(f"⚠️  Data export failed: {e}")
        
        console_logger.info(f"=" * 40)
        
    except Exception as e:
        log.error(f"Error in data export: {e}")

if __name__ == "__main__":
    main()
