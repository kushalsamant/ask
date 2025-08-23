import os
import logging
from typing import List, Optional, Dict, Tuple
from research_question_generator import generate_single_question_for_category, generate_question_from_answer
from research_answer_generator import generate_answer
from research_csv_manager import (
from research_statistics import (
from research_answer_manager import (
from research_find_path import (
            import random
                import time
            from research_question_api import call_together_api
            from research_question_prompts import create_category_question_prompt
            from research_question_api import process_question_response
#!/usr/bin/env python3
"""
Research Orchestrator Module
Focused wrapper for all research pipeline operations
"""


# Import core research modules
    get_questions_and_styles_from_log,
    get_next_image_number,
    log_single_question,
    mark_questions_as_used,
    export_questions_to_csv
)
    get_questions_by_category,
    get_used_questions_count,
    get_total_questions_count,
    get_questions_statistics
)
    get_latest_answers_from_log,
    get_latest_answer_for_category,
    get_best_answer_for_next_question
)
    generate_cross_disciplinary_question,
    generate_theme_based_question,
    get_cross_disciplinary_insights,
    analyze_research_direction,
    get_all_categories,
    get_all_themes
)

# Setup logging
log = logging.getLogger(__name__)

class ResearchOrchestrator:
    """Orchestrates all research pipeline operations"""
    
    def __init__(self, log_file: str = "log.csv"):
        """Initialize research orchestrator"""
        self.log_file = log_file
    
    def generate_qa_pairs(self, themes: List[str], questions_per_category: int = 1) -> List[dict]:
        """
        Generate Q&A pairs for specified themes
        
        Args:
            themes: List of themes to generate Q&A pairs for
            questions_per_category: Number of questions per theme
            
        Returns:
            List of Q&A pair dictionaries
        """
        log.info(f"Generating Q&A pairs for {len(themes)} themes...")
        
        qa_pairs = []
        
        for theme in themes:
            for i in range(questions_per_category):
                try:
                    log.info(f"Generating Q&A pair {i+1}/{questions_per_category} for {theme}")
                    
                    # Generate question
                    question = self._generate_question_for_category(theme)
                    if not question:
                        log.error(f"Failed to generate question for {theme}")
                        continue
                    
                    # Generate answer
                    answer = self._generate_answer_for_question(question, theme)
                    if not answer:
                        log.error(f"Failed to generate answer for {theme}")
                        continue
                    
                    # Get next image number
                    image_number = get_next_image_number()
                    
                    # Create Q&A pair
                    qa_pair = {
                        'theme': theme,
                        'question_text': question,
                        'answer_text': answer,
                        'image_number': image_number
                    }
                    
                    qa_pairs.append(qa_pair)
                    
                    # Log to CSV
                    log_single_question(theme, question, answer, image_number)
                    
                    log.info(f"✅ Generated Q&A pair for {theme}: {question[:50]}...")
                    
                except Exception as e:
                    log.error(f"Failed to generate Q&A pair for {theme}: {e}")
        
        return qa_pairs
    
    def generate_chained_qa_pairs(self, themes: List[str], chain_length: int = 2) -> List[dict]:
        """
        Generate chained Q&A pairs where each question builds on the previous answer
        
        Args:
            themes: List of themes to generate Q&A pairs for
            chain_length: Number of Q&A pairs in the chain
            
        Returns:
            List of Q&A pair dictionaries
        """
        log.info(f"Generating chained Q&A pairs for {len(themes)} themes...")
        
        qa_pairs = []
        
        for theme in themes:
            try:
                log.info(f"Generating chained Q&A pairs for {theme}")
                
                # Generate initial question
                current_question = self._generate_question_for_category(theme)
                if not current_question:
                    log.error(f"Failed to generate initial question for {theme}")
                    continue
                
                for i in range(chain_length):
                    try:
                        # Generate answer for current question
                        current_answer = self._generate_answer_for_question(current_question, theme)
                        if not current_answer:
                            log.error(f"Failed to generate answer for {theme} (step {i+1})")
                            break
                        
                        # Get next image number
                        image_number = get_next_image_number()
                        
                        # Create Q&A pair
                        qa_pair = {
                            'theme': theme,
                            'question_text': current_question,
                            'answer_text': current_answer,
                            'image_number': image_number
                        }
                        
                        qa_pairs.append(qa_pair)
                        
                        # Log to CSV
                        log_single_question(theme, current_question, current_answer, image_number)
                        
                        log.info(f"✅ Generated chained Q&A pair {i+1}/{chain_length} for {theme}")
                        
                        # Generate next question based on answer (if not the last iteration)
                        if i < chain_length - 1:
                            current_question = self._generate_question_from_answer(current_answer, theme)
                            if not current_question:
                                log.error(f"Failed to generate chained question for {theme} (step {i+1})")
                                break
                        
                    except Exception as e:
                        log.error(f"Failed to generate chained Q&A pair {i+1} for {theme}: {e}")
                        break
                        
            except Exception as e:
                log.error(f"Failed to generate chained Q&A pairs for {theme}: {e}")
        
        return qa_pairs
    
    def generate_cross_disciplinary_qa_pairs(self, theme_count: int = 5) -> List[dict]:
        """
        Generate cross-disciplinary Q&A pairs using themes
        
        Args:
            theme_count: Number of cross-disciplinary themes to explore
            
        Returns:
            List of Q&A pair dictionaries
        """
        log.info(f"Generating cross-disciplinary Q&A pairs for {theme_count} themes...")
        
        qa_pairs = []
        
        try:
            # Get available themes
            themes = get_all_themes()
            if not themes:
                log.error("No themes available for cross-disciplinary generation")
                return qa_pairs
            
            # Select themes for cross-disciplinary exploration
            selected_themes = random.sample(themes, min(theme_count, len(themes)))
            
            for i, theme in enumerate(selected_themes, 1):
                try:
                    log.info(f"Generating cross-disciplinary Q&A pair {i}/{theme_count} for theme: {theme}")
                    
                    # Generate cross-disciplinary question
                    question = generate_cross_disciplinary_question(theme)
                    if not question:
                        log.error(f"Failed to generate cross-disciplinary question for theme: {theme}")
                        continue
                    
                    # Generate answer
                    answer = self._generate_answer_for_question(question, "cross_disciplinary")
                    if not answer:
                        log.error(f"Failed to generate cross-disciplinary answer for theme: {theme}")
                        continue
                    
                    # Get next image number
                    image_number = get_next_image_number()
                    
                    # Create Q&A pair
                    qa_pair = {
                        'theme': 'cross_disciplinary',
                        'question_text': question,
                        'answer_text': answer,
                        'image_number': image_number,
                        'theme': theme
                    }
                    
                    qa_pairs.append(qa_pair)
                    
                    # Log to CSV
                    log_single_question('cross_disciplinary', question, answer, image_number)
                    
                    log.info(f"✅ Generated cross-disciplinary Q&A pair {i}: {question[:50]}...")
                    
                except Exception as e:
                    log.error(f"Failed to generate cross-disciplinary Q&A pair {i}: {e}")
        
        except Exception as e:
            log.error(f"Failed to generate cross-disciplinary Q&A pairs: {e}")
        
        return qa_pairs
    
    def generate_hybrid_cross_disciplinary_chain(self, theme_count: int = 3, chain_length: int = 3) -> List[dict]:
        """
        Generate hybrid content that combines cross-disciplinary and chained approaches
        
        Args:
            theme_count: Number of cross-disciplinary themes to explore
            chain_length: Number of chained questions per theme
            
        Returns:
            List of Q&A pair dictionaries with cross-disciplinary chains
        """
        log.info(f"Generating hybrid cross-disciplinary chains for {theme_count} themes...")
        
        qa_pairs = []
        
        try:
            # Get available themes
            themes = get_all_themes()
            if not themes:
                log.error("No themes available for hybrid generation")
                return qa_pairs
            
            # Select themes for cross-disciplinary exploration
            selected_themes = random.sample(themes, min(theme_count, len(themes)))
            
            for theme_idx, theme in enumerate(selected_themes, 1):
                try:
                    log.info(f"Generating hybrid chain {theme_idx}/{theme_count} for theme: {theme}")
                    
                    # Step 1: Generate initial cross-disciplinary question
                    cross_question_data = generate_cross_disciplinary_question(theme)
                    if not cross_question_data:
                        log.error(f"Failed to generate cross-disciplinary question for theme: {theme}")
                        continue
                    
                    initial_question = cross_question_data.get('question', '')
                    if not initial_question:
                        log.error(f"No question in cross-disciplinary data for theme: {theme}")
                        continue
                    
                    # Step 2: Generate answer for initial cross-disciplinary question
                    initial_answer = self._generate_answer_for_question(initial_question, "cross_disciplinary")
                    if not initial_answer:
                        log.error(f"Failed to generate answer for cross-disciplinary question: {theme}")
                        continue
                    
                    # Get next image number
                    image_number = get_next_image_number()
                    
                    # Create initial Q&A pair
                    initial_qa_pair = {
                        'theme': 'cross_disciplinary',
                        'question_text': initial_question,
                        'answer_text': initial_answer,
                        'image_number': image_number,
                        'theme': theme,
                        'chain_position': 1,
                        'chain_id': f"chain_{theme_idx}",
                        'is_cross_disciplinary': True
                    }
                    
                    qa_pairs.append(initial_qa_pair)
                    
                    # Log to CSV
                    log_single_question('cross_disciplinary', initial_question, initial_answer, image_number)
                    
                    log.info(f"✅ Generated initial cross-disciplinary Q&A for theme {theme_idx}: {initial_question[:50]}...")
                    
                    # Step 3: Generate chained questions based on the cross-disciplinary answer
                    current_question = initial_question
                    current_answer = initial_answer
                    
                    for chain_step in range(2, chain_length + 1):
                        try:
                            # Generate next question based on the previous answer
                            next_question = self._generate_chained_cross_disciplinary_question(
                                current_answer, theme, cross_question_data
                            )
                            
                            if not next_question:
                                log.warning(f"Failed to generate chained question {chain_step} for theme: {theme}")
                                break
                            
                            # Generate answer for the chained question
                            next_answer = self._generate_answer_for_question(next_question, "cross_disciplinary")
                            if not next_answer:
                                log.warning(f"Failed to generate answer for chained question {chain_step}: {theme}")
                                break
                            
                            # Get next image number
                            image_number = get_next_image_number()
                            
                            # Create chained Q&A pair
                            chained_qa_pair = {
                                'theme': 'cross_disciplinary',
                                'question_text': next_question,
                                'answer_text': next_answer,
                                'image_number': image_number,
                                'theme': theme,
                                'chain_position': chain_step,
                                'chain_id': f"chain_{theme_idx}",
                                'is_cross_disciplinary': True,
                                'is_chained': True
                            }
                            
                            qa_pairs.append(chained_qa_pair)
                            
                            # Log to CSV
                            log_single_question('cross_disciplinary', next_question, next_answer, image_number)
                            
                            log.info(f"✅ Generated chained Q&A {chain_step}/{chain_length} for theme {theme_idx}: {next_question[:50]}...")
                            
                            # Update for next iteration
                            current_question = next_question
                            current_answer = next_answer
                            
                        except Exception as e:
                            log.error(f"Failed to generate chained Q&A {chain_step} for theme {theme}: {e}")
                            break
                    
                    log.info(f"✅ Completed hybrid chain {theme_idx}/{theme_count} for theme: {theme}")
                    
                except Exception as e:
                    log.error(f"Failed to generate hybrid chain for theme {theme}: {e}")
        
        except Exception as e:
            log.error(f"Failed to generate hybrid cross-disciplinary chains: {e}")
        
        log.info(f"✅ Generated {len(qa_pairs)} total Q&A pairs in hybrid chains")
        return qa_pairs
    
    def _generate_question_for_category(self, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate question for specific theme with retry logic"""
        # Fixed retry delays: 30, 60, 90, 120, 150 seconds
        retry_delays = [30, 60, 90, 120, 150]
        
        for attempt in range(max_retries):
            try:
                question = generate_single_question_for_category(theme)
                if question:
                    return question
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No question generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating question for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = retry_delays[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate question for {theme} after {max_retries} attempts")
        return None
    
    def _generate_question_from_answer(self, answer: str, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate question based on previous answer with retry logic"""
        # Fixed retry delays: 30, 60, 90, 120, 150 seconds
        retry_delays = [30, 60, 90, 120, 150]
        
        for attempt in range(max_retries):
            try:
                question = generate_question_from_answer(answer, theme)
                if question:
                    return question
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No chained question generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating chained question for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = retry_delays[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate chained question for {theme} after {max_retries} attempts")
        return None
    
    def _generate_answer_for_question(self, question: str, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate answer for specific question with retry logic"""
        # Fixed retry delays: 30, 60, 90, 120, 150 seconds
        retry_delays = [30, 60, 90, 120, 150]
        
        for attempt in range(max_retries):
            try:
                answer = generate_answer(question, theme, None)  # Pass None for image_path
                if answer:
                    return answer
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No answer generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating answer for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = retry_delays[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate answer for {theme} after {max_retries} attempts")
        return None
    
    def _generate_chained_cross_disciplinary_question(self, previous_answer: str, theme: str, original_question_data: dict) -> Optional[str]:
        """
        Generate a chained question that builds on a cross-disciplinary answer
        
        Args:
            previous_answer: The previous answer to build upon
            theme: The cross-disciplinary theme
            original_question_data: Data from the original cross-disciplinary question
            
        Returns:
            Generated chained question or None if failed
        """
        try:
            # Extract themes from original question data
            themes = []
            if 'primary_category' in original_question_data:
                themes.extend([original_question_data['primary_category'], original_question_data['secondary_category']])
            elif 'themes' in original_question_data:
                themes.extend(original_question_data['themes'])
            
            # Create a prompt for generating chained cross-disciplinary questions
            prompt = f"""
            Previous Cross-Disciplinary Question: {original_question_data.get('question', '')}
            Theme: {theme}
            Themes Involved: {', '.join(themes)}
            Previous Answer: {previous_answer}
            
            Generate a follow-up question that:
            1. Builds upon the insights from the previous answer
            2. Explores deeper aspects of the cross-disciplinary intersection
            3. Maintains the connection between the involved themes
            4. Advances the exploration of the theme
            5. Is specific and actionable
            
            The question should be engaging and lead to practical insights.
            """
            
            # Use the existing question generation infrastructure
            
            system_prompt = "You are an expert architectural researcher specializing in cross-disciplinary exploration. Generate insightful follow-up questions that build upon previous answers and explore deeper connections between architectural themes."
            
            # Call API to generate the chained question
            raw_response = call_together_api(prompt, system_prompt)
            
            if not raw_response:
                log.warning("No response generated for chained cross-disciplinary question")
                return None
            
            # Process the response to extract the question
            question = process_question_response(raw_response)
            
            if not question:
                log.warning("No valid question extracted from chained cross-disciplinary response")
                return None
            
            log.info(f"✅ Generated chained cross-disciplinary question: {question[:50]}...")
            return question
            
        except Exception as e:
            log.error(f"Error generating chained cross-disciplinary question: {e}")
            return None
    
    def get_research_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive research statistics
        
        Returns:
            Dictionary with research statistics
        """
        try:
            stats = {
                'total_questions': get_total_questions_count(),
                'used_questions': get_used_questions_count(),
                'questions_by_category': get_questions_by_category(),
                'questions_statistics': get_questions_statistics(),
                'available_categories': get_all_categories(),
                'available_themes': get_all_themes()
            }
            
            return stats
            
        except Exception as e:
            log.error(f"Error getting research statistics: {e}")
            return {}
    
    def analyze_research_direction(self, qa_pairs: List[dict]) -> Dict[str, any]:
        """
        Analyze research direction based on Q&A pairs
        
        Args:
            qa_pairs: List of Q&A pairs to analyze
            
        Returns:
            Dictionary with research analysis
        """
        try:
            # Extract questions and answers
            questions = [qa['question_text'] for qa in qa_pairs]
            answers = [qa['answer_text'] for qa in qa_pairs]
            
            # Analyze research direction
            analysis = analyze_research_direction(questions, answers)
            
            return analysis
            
        except Exception as e:
            log.error(f"Error analyzing research direction: {e}")
            return {}
    
    def export_research_data(self, output_file: str = "research_export.csv"):
        """
        Export research data to CSV
        
        Args:
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_questions_to_csv(output_file)
            log.info(f"✅ Exported research data to {output_file}")
            return True
            
        except Exception as e:
            log.error(f"Error exporting research data: {e}")
            return False
    
    def mark_questions_as_used(self, qa_pairs: List[dict]) -> int:
        """
        Mark questions as used in the research log
        
        Args:
            qa_pairs: List of Q&A pairs to mark as used
            
        Returns:
            Number of questions marked as used
        """
        try:
            questions_dict = {qa['theme']: qa['question_text'] for qa in qa_pairs}
            marked_count = mark_questions_as_used(questions_dict)
            
            log.info(f"✅ Marked {marked_count} questions as used")
            return marked_count
            
        except Exception as e:
            log.error(f"Error marking questions as used: {e}")
            return 0


