#!/usr/bin/env python3
"""
Research Question Prompts Module
Enhanced prompt generation and formatting for question generation with improved performance and error handling

This module provides functionality to:
- Create prompts for generating questions for specific themes
- Create prompts based on previous answers for follow-up questions
- Validate question quality and format
- Process raw API responses into clean questions
- Handle input validation and sanitization
- Provide comprehensive error handling and logging
- Support performance monitoring and caching
- Generate high-quality, thought-provoking architectural questions

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Optimized)
"""

import logging
import re
import time
from typing import Tuple, Optional, Dict, Any
from functools import lru_cache

# Setup logging
log = logging.getLogger(__name__)

# Configuration constants
MIN_QUESTION_LENGTH = 15
MAX_QUESTION_LENGTH = 500
VALID_QUESTION_STARTS = ['how', 'what', 'why']
VALID_QUESTION_PATTERN = r'^[A-Za-z].*\?$'
THEME_MAX_LENGTH = 100
ANSWER_MAX_LENGTH = 2000

# Performance monitoring
_performance_stats = {
    'total_prompts_created': 0,
    'total_validations': 0,
    'total_processing': 0,
    'total_time': 0.0
}

def validate_input_parameters(theme: str = None, answer: str = None) -> Tuple[bool, str]:
    """
    Validate input parameters for prompt generation functions
    
    Args:
        theme: Theme name to validate (optional)
        answer: Answer text to validate (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate theme if provided
    if theme is not None:
        if not isinstance(theme, str):
            return False, "Theme must be a string"
        
        if len(theme.strip()) == 0:
            return False, "Theme cannot be empty or whitespace only"
        
        if len(theme) > THEME_MAX_LENGTH:
            return False, f"Theme too long (max {THEME_MAX_LENGTH} characters)"
        
        # Check for invalid characters
        if re.search(r'[<>"\']', theme):
            return False, "Theme contains invalid characters"
    
    # Validate answer if provided
    if answer is not None:
        if not isinstance(answer, str):
            return False, "Answer must be a string"
        
        if len(answer.strip()) == 0:
            return False, "Answer cannot be empty or whitespace only"
        
        if len(answer) > ANSWER_MAX_LENGTH:
            return False, f"Answer too long (max {ANSWER_MAX_LENGTH} characters)"
    
    return True, ""

def sanitize_text(text: str) -> str:
    """
    Sanitize and clean text input
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text

def create_category_question_prompt(theme: str) -> Tuple[str, str]:
    """
    Create a prompt for generating questions for a specific theme
    
    Enhanced with:
    - Input validation and sanitization
    - Performance monitoring
    - Comprehensive error handling
    - Improved prompt quality
    
    Args:
        theme (str): Theme name for question generation
        
    Returns:
        tuple: (prompt, system_prompt)
        
    Raises:
        ValueError: If theme is invalid
    """
    start_time = time.time()
    _performance_stats['total_prompts_created'] += 1
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme=theme)
        if not is_valid:
            log.error(f"Invalid theme parameter: {error_msg}")
            raise ValueError(f"Invalid theme: {error_msg}")
        
        # Sanitize theme
        theme = sanitize_text(theme)
        
        log.info(f"Creating category question prompt for theme: {theme}")
        
        system_prompt = """You are an expert research assistant specializing in question generation for academic and professional research. You excel at creating thought-provoking, open-ended questions that inspire deep thinking and meaningful discussion. Your questions are clear, specific, and designed to explore complex topics from multiple perspectives."""

        prompt = f"""You are an expert research assistant and educator. Generate 1 thought-provoking question about {theme} in research and practice.

Context: This question will inspire research and creative thinking. It should challenge conventional wisdom and explore the intersection of {theme} with contemporary challenges and opportunities.

Requirements:
- Create an open-ended question that encourages deep thinking and discussion
- Focus on innovation, sustainability, future trends, and societal impact
- Address real-world challenges and opportunities in {theme}
- Consider global perspectives and cross-cultural implications
- Start the question with "How", "What", or "Why"
- Use clear, professional language
- Make the question unique and thought-provoking
- Ensure the question is specific to {theme}
- Format: Single question ending with a question mark (?)
- Minimum length: {MIN_QUESTION_LENGTH} characters
- Maximum length: {MAX_QUESTION_LENGTH} characters

Example format:
How can we design buildings that respond to climate change?

Please generate 1 {theme}-specific question that provokes meaningful research discourse:"""
        
        duration = time.time() - start_time
        _performance_stats['total_time'] += duration
        
        log.info(f" Created category question prompt for '{theme}' in {duration:.3f}s")
        
        return prompt, system_prompt
        
    except ValueError as e:
        log.error(f"Validation error for theme '{theme}': {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error creating category question prompt for theme '{theme}': {e}")
        raise

def create_answer_based_question_prompt(answer: str, theme: str) -> Tuple[str, str]:
    """
    Create a prompt for generating questions based on previous answers
    
    Enhanced with:
    - Input validation and sanitization
    - Performance monitoring
    - Comprehensive error handling
    - Improved prompt quality
    
    Args:
        answer (str): Previous answer/insight to build upon
        theme (str): Theme name for context
        
    Returns:
        tuple: (prompt, system_prompt)
        
    Raises:
        ValueError: If parameters are invalid
    """
    start_time = time.time()
    _performance_stats['total_prompts_created'] += 1
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme=theme, answer=answer)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            raise ValueError(f"Invalid parameters: {error_msg}")
        
        # Sanitize inputs
        theme = sanitize_text(theme)
        answer = sanitize_text(answer)
        
        log.info(f"Creating answer-based question prompt for theme: {theme}")
        
        system_prompt = """You are an expert research assistant specializing in question generation for academic and professional research. You excel at creating thought-provoking, open-ended questions that build upon previous insights and continue research narratives. Your questions are clear, specific, and designed to explore complex topics from multiple perspectives."""

        prompt = f"""You are an expert research assistant and educator. Based on the following research insight, generate 1 thought-provoking question about {theme} in research and practice.

Research Insight: {answer}

Context: This question should build upon the research insight and explore related aspects of {theme}. It should continue the research narrative and encourage further exploration and analysis.

Requirements:
- Create an open-ended question that builds upon the research insight
- Focus on innovation, sustainability, future trends, and societal impact
- Address real-world challenges and opportunities in {theme}
- Consider global perspectives and cross-cultural implications
- Start the question with "How", "What", or "Why"
- Use clear, professional language
- Make the question unique and thought-provoking
- Ensure the question relates to both the insight and {theme}
- Format: Single question ending with a question mark (?)
- Minimum length: {MIN_QUESTION_LENGTH} characters
- Maximum length: {MAX_QUESTION_LENGTH} characters

Example format:
How can we design buildings that respond to climate change?

Please generate 1 {theme}-specific question that builds upon the research insight:"""
        
        duration = time.time() - start_time
        _performance_stats['total_time'] += duration
        
        log.info(f" Created answer-based question prompt for '{theme}' in {duration:.3f}s")
        
        return prompt, system_prompt
        
    except ValueError as e:
        log.error(f"Validation error for answer-based prompt (theme: '{theme}'): {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error creating answer-based question prompt for theme '{theme}': {e}")
        raise

def validate_question(question: str) -> bool:
    """
    Validate if a generated question meets quality standards
    
    Enhanced with:
    - Comprehensive validation rules
    - Performance monitoring
    - Detailed error logging
    - Input sanitization
    
    Args:
        question (str): Generated question to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    start_time = time.time()
    _performance_stats['total_validations'] += 1
    
    try:
        if not question:
            log.debug("Question validation failed: Empty question")
            return False
        
        # Sanitize and check length
        question = sanitize_text(question)
        
        if len(question) < MIN_QUESTION_LENGTH:
            log.debug(f"Question validation failed: Too short ({len(question)} chars, min {MIN_QUESTION_LENGTH})")
            return False
        
        if len(question) > MAX_QUESTION_LENGTH:
            log.debug(f"Question validation failed: Too long ({len(question)} chars, max {MAX_QUESTION_LENGTH})")
            return False
        
        # Check if it starts with appropriate words
        question_lower = question.lower()
        if not any(question_lower.startswith(start) for start in VALID_QUESTION_STARTS):
            log.debug(f"Question validation failed: Doesn't start with {VALID_QUESTION_STARTS}")
            return False
        
        # Check if it ends with a question mark
        if not question_lower.endswith('?'):
            log.debug("Question validation failed: Doesn't end with question mark")
            return False
        
        # Check overall pattern
        if not re.match(VALID_QUESTION_PATTERN, question):
            log.debug("Question validation failed: Invalid question pattern")
            return False
        
        # Check for common issues
        if question_lower.startswith('the answer is'):
            log.debug("Question validation failed: Appears to be an answer, not a question")
            return False
        
        if len(question.split()) < 3:
            log.debug("Question validation failed: Too few words")
            return False
        
        duration = time.time() - start_time
        log.debug(f" Question validation passed in {duration:.3f}s")
        
        return True
        
    except Exception as e:
        log.error(f"Error validating question: {e}")
        return False

def process_question_response(raw_text: str) -> Optional[str]:
    """
    Process raw API response into a single question
    
    Enhanced with:
    - Comprehensive text processing
    - Performance monitoring
    - Detailed error handling
    - Quality validation
    
    Args:
        raw_text (str): Raw response from API
        
    Returns:
        str: Processed question or None if invalid
    """
    start_time = time.time()
    _performance_stats['total_processing'] += 1
    
    try:
        if not raw_text:
            log.warning("No raw text provided for processing")
            return None
        
        log.info("Processing raw question response")
        
        # Clean and split the text
        lines = [
            line.strip() for line in raw_text.split('\n')
            if line.strip() and len(line.strip()) > MIN_QUESTION_LENGTH
        ]
        
        if not lines:
            log.warning("No valid lines found in response")
            return None
        
        # Process each line to find valid questions
        valid_questions = []
        for line in lines:
            # Remove common prefixes and suffixes
            cleaned_line = re.sub(r'^[0-9]+\.\s*', '', line)  # Remove numbering
            cleaned_line = re.sub(r'^[-*]\s*', '', cleaned_line)  # Remove list markers
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line.strip())  # Normalize whitespace
            
            # Validate the cleaned question
            if validate_question(cleaned_line):
                valid_questions.append(cleaned_line)
        
        if not valid_questions:
            log.warning("No valid questions found in response")
            return None
        
        # Return the first valid question
        result = valid_questions[0]
        
        duration = time.time() - start_time
        log.info(f" Processed question response in {duration:.3f}s: {result[:50]}...")
        
        return result
        
    except Exception as e:
        log.error(f"Error processing question response: {e}")
        return None

def get_prompt_statistics() -> Dict[str, Any]:
    """
    Get statistics about prompt generation performance
    
    Returns:
        Dictionary with prompt generation statistics
    """
    return {
        'total_prompts_created': _performance_stats['total_prompts_created'],
        'total_validations': _performance_stats['total_validations'],
        'total_processing': _performance_stats['total_processing'],
        'total_time': _performance_stats['total_time'],
        'average_time_per_prompt': _performance_stats['total_time'] / max(_performance_stats['total_prompts_created'], 1),
        'validation_success_rate': _performance_stats['total_validations'] / max(_performance_stats['total_processing'], 1),
        'configuration': {
            'min_question_length': MIN_QUESTION_LENGTH,
            'max_question_length': MAX_QUESTION_LENGTH,
            'valid_question_starts': VALID_QUESTION_STARTS,
            'theme_max_length': THEME_MAX_LENGTH,
            'answer_max_length': ANSWER_MAX_LENGTH
        },
        'module_version': '2.0',
        'optimization_date': '2025-08-24'
    }

def create_cross_disciplinary_prompt(theme1: str, theme2: str) -> Tuple[str, str]:
    """
    Create a prompt for generating cross-disciplinary questions
    
    Args:
        theme1 (str): First theme
        theme2 (str): Second theme
        
    Returns:
        tuple: (prompt, system_prompt)
    """
    start_time = time.time()
    _performance_stats['total_prompts_created'] += 1
    
    try:
        # Validate inputs
        is_valid1, error_msg1 = validate_input_parameters(theme=theme1)
        is_valid2, error_msg2 = validate_input_parameters(theme=theme2)
        
        if not is_valid1:
            raise ValueError(f"Invalid theme1: {error_msg1}")
        if not is_valid2:
            raise ValueError(f"Invalid theme2: {error_msg2}")
        
        # Sanitize themes
        theme1 = sanitize_text(theme1)
        theme2 = sanitize_text(theme2)
        
        log.info(f"Creating cross-disciplinary prompt for themes: {theme1} and {theme2}")
        
        system_prompt = """You are an expert research assistant specializing in cross-disciplinary question generation. You excel at creating questions that bridge different fields and explore innovative intersections between disciplines."""
        
        prompt = f"""You are an expert research assistant and educator. Generate 1 thought-provoking cross-disciplinary question that explores the intersection of {theme1} and {theme2}.

Context: This question should explore how these two themes can inform and enhance each other, leading to innovative research directions and practical applications.

Requirements:
- Create an open-ended question that bridges {theme1} and {theme2}
- Focus on innovation, collaboration, and mutual enhancement
- Address real-world challenges that benefit from cross-disciplinary approaches
- Consider global perspectives and cross-cultural implications
- Start the question with "How", "What", or "Why"
- Use clear, professional language
- Make the question unique and thought-provoking
- Format: Single question ending with a question mark (?)
- Minimum length: {MIN_QUESTION_LENGTH} characters
- Maximum length: {MAX_QUESTION_LENGTH} characters

Please generate 1 cross-disciplinary question that explores {theme1} and {theme2}:"""
        
        duration = time.time() - start_time
        _performance_stats['total_time'] += duration
        
        log.info(f" Created cross-disciplinary prompt in {duration:.3f}s")
        
        return prompt, system_prompt
        
    except Exception as e:
        log.error(f"Error creating cross-disciplinary prompt: {e}")
        raise

# Convenience functions for backward compatibility
def create_theme_prompt(theme: str) -> Tuple[str, str]:
    """Convenience function for creating category question prompt"""
    return create_category_question_prompt(theme)

def create_follow_up_prompt(answer: str, theme: str) -> Tuple[str, str]:
    """Convenience function for creating answer-based question prompt"""
    return create_answer_based_question_prompt(answer, theme)

def is_valid_question(question: str) -> bool:
    """Convenience function for question validation"""
    return validate_question(question)

def extract_question(raw_text: str) -> Optional[str]:
    """Convenience function for processing question response"""
    return process_question_response(raw_text)
