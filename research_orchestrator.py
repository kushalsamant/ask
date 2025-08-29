#!/usr/bin/env python3
"""
Research Orchestrator Module
Focused wrapper for all research pipeline operations

This module provides functionality to:
- Generate Q&A pairs for research themes
- Create chained Q&A sequences
- Generate multi-theme content
- Provide enhanced research approaches
- Manage research statistics and analysis
- Export research data
- Mark questions as used

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import os
import logging
import random
import time
from typing import List, Optional, Dict, Tuple

# Import core research modules
from research_question_generator import generate_single_question_for_category, generate_question_from_answer
from research_answer_generator import generate_answer
from research_csv_manager import (
    get_questions_and_styles_from_log,
    get_next_image_number,
    log_single_question,
    mark_questions_as_used,
    export_questions_to_csv
)
from research_statistics import (
    get_questions_by_category,
    get_used_questions_count,
    get_total_questions_count,
    get_questions_statistics
)
from research_answer_manager import (
    get_latest_answers_from_log,
    get_latest_answer_for_category,
    get_best_answer_for_next_question
)
from research_find_path import (
    generate_cross_disciplinary_question,
    generate_theme_based_question,
    get_cross_disciplinary_insights,
    analyze_research_direction,
    get_all_categories,
    get_all_themes
)
from api_client import api_client
from research_question_prompts import process_question_response
from research_question_prompts import create_category_question_prompt

# Setup logging
log = logging.getLogger(__name__)

# Fixed retry delays: 30, 60, 90, 120, 150 seconds
RETRY_DELAYS = [30, 60, 90, 120, 150]

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
        # Validate input parameters
        if themes is None:
            themes = []
        if not isinstance(themes, list):
            themes = []
        if questions_per_category is None or questions_per_category < 1:
            questions_per_category = 1
            
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
                    
                    log.info(f" Generated Q&A pair for {theme}: {question[:50]}...")
                    
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
        # Validate input parameters
        if themes is None:
            themes = []
        if not isinstance(themes, list):
            themes = []
        if chain_length is None or chain_length < 1:
            chain_length = 2
            
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
                        
                        log.info(f" Generated chained Q&A pair {i+1}/{chain_length} for {theme}")
                        
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
    
    def generate_multi_theme_qa_pairs(self, theme_count: int = 5) -> List[dict]:
        """
        Generate multi-theme Q&A pairs using themes
        
        Args:
            theme_count: Number of themes to explore
            
        Returns:
            List of Q&A pair dictionaries
        """
        log.info(f"Generating multi-theme Q&A pairs for {theme_count} themes...")
        
        qa_pairs = []
        
        try:
            # Get available themes
            themes = get_all_themes()
            if not themes:
                log.error("No themes available for multi-theme generation")
                return qa_pairs
            
            # Select themes for multi-theme exploration
            selected_themes = random.sample(themes, min(theme_count, len(themes)))
            
            for i, theme in enumerate(selected_themes, 1):
                try:
                    log.info(f"Generating multi-theme Q&A pair {i}/{theme_count} for theme: {theme}")
                    
                    # Generate multi-theme question
                    question_data = generate_theme_based_question(theme)
                    if not question_data:
                        log.error(f"Failed to generate multi-theme question for theme: {theme}")
                        continue
                    
                    question = question_data.get('question', '')
                    if not question:
                        log.error(f"No question in multi-theme data for theme: {theme}")
                        continue
                    
                    # Generate answer
                    answer = self._generate_answer_for_question(question, "multi_theme")
                    if not answer:
                        log.error(f"Failed to generate multi-theme answer for theme: {theme}")
                        continue
                    
                    # Get next image number
                    image_number = get_next_image_number()
                    
                    # Create Q&A pair
                    qa_pair = {
                        'theme': 'multi_theme',
                        'question_text': question,
                        'answer_text': answer,
                        'image_number': image_number,
                        'original_theme': theme
                    }
                    
                    qa_pairs.append(qa_pair)
                    
                    # Log to CSV
                    log_single_question('multi_theme', question, answer, image_number)
                    
                    log.info(f" Generated multi-theme Q&A pair {i}: {question[:50]}...")
                    
                except Exception as e:
                    log.error(f"Failed to generate multi-theme Q&A pair {i}: {e}")
        
        except Exception as e:
            log.error(f"Failed to generate multi-theme Q&A pairs: {e}")
        
        return qa_pairs
    
    def generate_enhanced_multi_theme_chain(self, theme_count: int = 3, chain_length: int = 3) -> List[dict]:
        """
        Generate enhanced content that combines multi-theme and chained approaches
        
        Args:
            theme_count: Number of themes to explore
            chain_length: Number of chained questions per theme
            
        Returns:
            List of Q&A pair dictionaries with multi-theme chains
        """
        log.info(f"Generating enhanced multi-theme chains for {theme_count} themes...")
        
        qa_pairs = []
        
        try:
            # Get available themes
            themes = get_all_themes()
            if not themes:
                log.error("No themes available for enhanced generation")
                return qa_pairs
            
            # Select themes for multi-theme exploration
            selected_themes = random.sample(themes, min(theme_count, len(themes)))
            
            for theme_idx, theme in enumerate(selected_themes, 1):
                try:
                    log.info(f"Generating enhanced chain {theme_idx}/{theme_count} for theme: {theme}")
                    
                    # Step 1: Generate initial multi-theme question
                    question_data = generate_theme_based_question(theme)
                    if not question_data:
                        log.error(f"Failed to generate multi-theme question for theme: {theme}")
                        continue
                    
                    initial_question = question_data.get('question', '')
                    if not initial_question:
                        log.error(f"No question in multi-theme data for theme: {theme}")
                        continue
                    
                    # Step 2: Generate answer for initial multi-theme question
                    initial_answer = self._generate_answer_for_question(initial_question, "multi_theme")
                    if not initial_answer:
                        log.error(f"Failed to generate answer for multi-theme question: {theme}")
                        continue
                    
                    # Get next image number
                    image_number = get_next_image_number()
                    
                    # Create initial Q&A pair
                    initial_qa_pair = {
                        'theme': 'multi_theme',
                        'question_text': initial_question,
                        'answer_text': initial_answer,
                        'image_number': image_number,
                        'original_theme': theme,
                        'chain_position': 1,
                        'chain_id': f"chain_{theme_idx}",
                        'is_multi_theme': True
                    }
                    
                    qa_pairs.append(initial_qa_pair)
                    
                    # Log to CSV
                    log_single_question('multi_theme', initial_question, initial_answer, image_number)
                    
                    log.info(f" Generated initial multi-theme Q&A for theme {theme_idx}: {initial_question[:50]}...")
                    
                    # Step 3: Generate chained questions based on the multi-theme answer
                    current_question = initial_question
                    current_answer = initial_answer
                    
                    for chain_step in range(2, chain_length + 1):
                        try:
                            # Generate next question based on the previous answer
                            next_question = self._generate_chained_multi_theme_question(
                                current_answer, theme, question_data
                            )
                            
                            if not next_question:
                                log.warning(f"Failed to generate chained question {chain_step} for theme: {theme}")
                                break
                            
                            # Generate answer for the chained question
                            next_answer = self._generate_answer_for_question(next_question, "multi_theme")
                            if not next_answer:
                                log.warning(f"Failed to generate answer for chained question {chain_step}: {theme}")
                                break
                            
                            # Get next image number
                            image_number = get_next_image_number()
                            
                            # Create chained Q&A pair
                            chained_qa_pair = {
                                'theme': 'multi_theme',
                                'question_text': next_question,
                                'answer_text': next_answer,
                                'image_number': image_number,
                                'original_theme': theme,
                                'chain_position': chain_step,
                                'chain_id': f"chain_{theme_idx}",
                                'is_multi_theme': True,
                                'is_chained': True
                            }
                            
                            qa_pairs.append(chained_qa_pair)
                            
                            # Log to CSV
                            log_single_question('multi_theme', next_question, next_answer, image_number)
                            
                            log.info(f" Generated chained Q&A {chain_step}/{chain_length} for theme {theme_idx}: {next_question[:50]}...")
                            
                            # Update for next iteration
                            current_question = next_question
                            current_answer = next_answer
                            
                        except Exception as e:
                            log.error(f"Failed to generate chained Q&A {chain_step} for theme {theme}: {e}")
                            break
                    
                    log.info(f" Completed enhanced chain {theme_idx}/{theme_count} for theme: {theme}")
                    
                except Exception as e:
                    log.error(f"Failed to generate enhanced chain for theme {theme}: {e}")
        
        except Exception as e:
            log.error(f"Failed to generate enhanced multi-theme chains: {e}")
        
        log.info(f" Generated {len(qa_pairs)} total Q&A pairs in enhanced chains")
        return qa_pairs
    
    def _generate_question_for_category(self, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate question for specific theme with retry logic"""
        for attempt in range(max_retries):
            try:
                question = generate_single_question_for_category(theme)
                if question:
                    return question
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No question generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating question for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAYS[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate question for {theme} after {max_retries} attempts")
        return None
    
    def _generate_question_from_answer(self, answer: str, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate question based on previous answer with retry logic"""
        for attempt in range(max_retries):
            try:
                question = generate_question_from_answer(answer, theme)
                if question:
                    return question
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No chained question generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating chained question for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAYS[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate chained question for {theme} after {max_retries} attempts")
        return None
    
    def _generate_answer_for_question(self, question: str, theme: str, max_retries: int = 5) -> Optional[str]:
        """Generate answer for specific question with retry logic"""
        for attempt in range(max_retries):
            try:
                answer = generate_answer(question, theme, None)  # Pass None for image_path
                if answer:
                    return answer
                log.warning(f"Attempt {attempt + 1}/{max_retries}: No answer generated for {theme}")
            except Exception as e:
                log.error(f"Attempt {attempt + 1}/{max_retries}: Error generating answer for {theme}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAYS[attempt]
                log.info(f"Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}")
                time.sleep(wait_time)
        
        log.error(f"Failed to generate answer for {theme} after {max_retries} attempts")
        return None
    
    def _generate_chained_multi_theme_question(self, previous_answer: str, theme: str, original_question_data: dict) -> Optional[str]:
        """
        Generate a chained question that builds on a multi-theme answer
        
        Args:
            previous_answer: The previous answer to build upon
            theme: The multi-theme theme
            original_question_data: Data from the original multi-theme question
            
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
            
            # Create a prompt for generating chained multi-theme questions
            prompt = f"""
            Previous Multi-Theme Question: {original_question_data.get('question', '')}
            Theme: {theme}
            Themes Involved: {', '.join(themes)}
            Previous Answer: {previous_answer}
            
            Generate a follow-up question that:
            1. Builds upon the insights from the previous answer
            2. Explores deeper aspects of the multi-theme intersection
            3. Maintains the connection between the involved themes
            4. Advances the exploration of the theme
            5. Is specific and actionable
            
            The question should be engaging and lead to practical insights.
            """
            
            # Use the existing question generation infrastructure
            system_prompt = "You are an expert architectural researcher specializing in multi-theme exploration. Generate insightful follow-up questions that build upon previous answers and explore deeper connections between architectural themes."
            
            # Call API to generate the chained question
            raw_response = api_client.call_text_api(prompt, system_prompt)
            
            if not raw_response:
                log.warning("No response generated for chained multi-theme question")
                return None
            
            # Process the response to extract the question
            question = process_question_response(raw_response)
            
            if not question:
                log.warning("No valid question extracted from chained multi-theme response")
                return None
            
            log.info(f" Generated chained multi-theme question: {question[:50]}...")
            return question
            
        except Exception as e:
            log.error(f"Error generating chained multi-theme question: {e}")
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
            log.info(f" Exported research data to {output_file}")
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
            
            log.info(f" Marked {marked_count} questions as used")
            return marked_count
            
        except Exception as e:
            log.error(f"Error marking questions as used: {e}")
            return 0

# Convenience functions
def generate_qa_pairs(themes: List[str], questions_per_category: int = 1) -> List[dict]:
    """Generate Q&A pairs for specified themes"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.generate_qa_pairs(themes, questions_per_category)

def generate_chained_qa_pairs(themes: List[str], chain_length: int = 2) -> List[dict]:
    """Generate chained Q&A pairs for specified themes"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.generate_chained_qa_pairs(themes, chain_length)

def generate_multi_theme_qa_pairs(theme_count: int = 5) -> List[dict]:
    """Generate multi-theme Q&A pairs"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.generate_multi_theme_qa_pairs(theme_count)

def generate_enhanced_multi_theme_chain(theme_count: int = 3, chain_length: int = 3) -> List[dict]:
    """Generate enhanced multi-theme chains"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.generate_enhanced_multi_theme_chain(theme_count, chain_length)

def get_research_statistics() -> Dict[str, any]:
    """Get comprehensive research statistics"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.get_research_statistics()

def analyze_research_direction(qa_pairs: List[dict]) -> Dict[str, any]:
    """Analyze research direction based on Q&A pairs"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.analyze_research_direction(qa_pairs)

def export_research_data(output_file: str = "research_export.csv"):
    """Export research data to CSV"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.export_research_data(output_file)

def mark_questions_as_used(qa_pairs: List[dict]) -> int:
    """Mark questions as used in the research log"""
    orchestrator = ResearchOrchestrator()
    return orchestrator.mark_questions_as_used(qa_pairs)
