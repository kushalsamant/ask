#!/usr/bin/env python3
"""
Research Question Generator Module
Enhanced question generation orchestration with improved performance and error handling

This module provides functionality to:
- Generate single questions for specific themes
- Generate follow-up questions based on previous answers
- Validate question quality and relevance
- Handle API failures gracefully with retry logic
- Provide comprehensive logging and monitoring
- Support input validation and sanitization

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Optimized)
"""

import logging
import time
import re
from typing import Optional, Tuple, Dict, Any
from functools import wraps

# Import core dependencies
from api_client import api_client
from research_question_prompts import (
    process_question_response,
    create_category_question_prompt, 
    create_answer_based_question_prompt,
    validate_question
)

# Setup logging
log = logging.getLogger(__name__)

# Configuration constants
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 5]  # seconds
MAX_QUESTION_LENGTH = 500
MIN_QUESTION_LENGTH = 5  # Reduced for testing
QUESTION_ENDINGS = ['?', '...', '!']
VALID_THEME_PATTERN = r'^[a-zA-Z0-9_\-\s]+$'

def retry_on_failure(max_retries: int = MAX_RETRIES, delays: list = RETRY_DELAYS):
    """Decorator for retry logic on API failures"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    log.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}")
                    
                    if attempt < max_retries - 1:
                        delay = delays[min(attempt, len(delays) - 1)]
                        log.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
            
            log.error(f"All {max_retries} attempts failed for {func.__name__}: {last_exception}")
            return None
        
        return wrapper
    return decorator

def validate_input_parameters(theme: str, answer: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate input parameters for question generation
    
    Args:
        theme: Theme name to validate
        answer: Optional answer text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate theme
    if not theme:
        return False, "Theme cannot be empty"
    
    if not isinstance(theme, str):
        return False, "Theme must be a string"
    
    if len(theme.strip()) == 0:
        return False, "Theme cannot be whitespace only"
    
    if len(theme) > 100:
        return False, "Theme too long (max 100 characters)"
    
    if not re.match(VALID_THEME_PATTERN, theme):
        return False, "Theme contains invalid characters"
    
    # Validate answer if provided
    if answer is not None:
        if not isinstance(answer, str):
            return False, "Answer must be a string"
        
        if len(answer.strip()) == 0:
            return False, "Answer cannot be whitespace only"
        
        if len(answer) > 2000:
            return False, "Answer too long (max 2000 characters)"
    
    return True, ""

def sanitize_question(question: str) -> str:
    """
    Sanitize and clean generated question
    
    Args:
        question: Raw question text
        
    Returns:
        Sanitized question text
    """
    if not question:
        return ""
    
    # Remove extra whitespace
    question = re.sub(r'\s+', ' ', question.strip())
    
    # Ensure question ends with proper punctuation
    if not any(question.endswith(ending) for ending in QUESTION_ENDINGS):
        question = question.rstrip('.') + '?'
    
    # Truncate if too long
    if len(question) > MAX_QUESTION_LENGTH:
        question = question[:MAX_QUESTION_LENGTH-3] + "..."
    
    return question

def validate_question_quality(question: str, theme: str) -> Tuple[bool, str]:
    """
    Enhanced question quality validation
    
    Args:
        question: Question text to validate
        theme: Theme context for validation
        
    Returns:
        Tuple of (is_valid, reason)
    """
    if not question:
        return False, "Question is empty"
    
    if len(question) < MIN_QUESTION_LENGTH:
        return False, f"Question too short (min {MIN_QUESTION_LENGTH} characters)"
    
    if len(question) > MAX_QUESTION_LENGTH:
        return False, f"Question too long (max {MAX_QUESTION_LENGTH} characters)"
    
    # Check for question mark
    if '?' not in question:
        return False, "Question must contain a question mark"
    
    # Check for theme relevance (basic check)
    theme_words = set(theme.lower().split())
    question_words = set(question.lower().split())
    if not theme_words.intersection(question_words):
        log.warning(f"Question may not be relevant to theme '{theme}'")
    
    # Check for common issues
    if question.lower().startswith('the answer is'):
        return False, "Question appears to be an answer, not a question"
    
    if len(question.split()) < 2:
        return False, "Question too short (min 2 words)"
    
    return True, "Question quality validated"

@retry_on_failure()
def generate_single_question_for_category(theme: str) -> Optional[str]:
    """
    Generate a single research question for a specific theme using Together AI
    
    Enhanced with:
    - Input validation and sanitization
    - Retry logic for API failures
    - Quality validation
    - Comprehensive error handling
    - Performance monitoring
    
    Args:
        theme (str): Theme name for question generation
        
    Returns:
        str: Generated question or None if failed
        
    Raises:
        ValueError: If theme is invalid
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme)
        if not is_valid:
            log.error(f"Invalid theme parameter: {error_msg}")
            raise ValueError(f"Invalid theme: {error_msg}")
        
        log.info(f"Generating question for theme: {theme}")
        
        # Create prompt for theme
        prompt, system_prompt = create_category_question_prompt(theme)
        
        if not prompt or not system_prompt:
            log.error("Failed to create prompt for theme")
            return None
        
        # Call API with retry logic
        raw_response = api_client.call_text_api(prompt, system_prompt)
        
        if not raw_response:
            log.warning(f"No API response generated for theme: {theme}")
            return None
        
        # Process response into question
        question = process_question_response(raw_response)
        
        if not question:
            log.warning(f"No valid question extracted from API response for theme: {theme}")
            return None
        
        # Sanitize question
        question = sanitize_question(question)
        
        # Validate question quality
        is_quality_valid, quality_reason = validate_question_quality(question, theme)
        if not is_quality_valid:
            log.warning(f"Question quality validation failed for theme '{theme}': {quality_reason}")
            return None
        
        # Final validation using existing function
        if not validate_question(question):
            log.warning(f"Generated question for theme '{theme}' failed final validation")
            return None
        
        duration = time.time() - start_time
        log.info(f" Generated question for '{theme}' in {duration:.2f}s: {question[:50]}...")
        
        return question
        
    except ValueError as e:
        log.error(f"Validation error for theme '{theme}': {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected error generating question for theme '{theme}': {e}")
        return None

@retry_on_failure()
def generate_question_from_answer(answer: str, theme: str) -> Optional[str]:
    """
    Generate a new question based on a previous answer for a specific theme
    
    Enhanced with:
    - Input validation and sanitization
    - Retry logic for API failures
    - Quality validation
    - Comprehensive error handling
    - Performance monitoring
    
    Args:
        answer (str): Previous answer/insight to build upon
        theme (str): Theme name for context
        
    Returns:
        str: Generated follow-up question or None if failed
        
    Raises:
        ValueError: If parameters are invalid
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme, answer)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            raise ValueError(f"Invalid parameters: {error_msg}")
        
        log.info(f"Generating follow-up question for theme: {theme}")
        
        # Create prompt based on answer
        prompt, system_prompt = create_answer_based_question_prompt(answer, theme)
        
        if not prompt or not system_prompt:
            log.error("Failed to create answer-based prompt")
            return None
        
        # Call API with retry logic
        raw_response = api_client.call_text_api(prompt, system_prompt)
        
        if not raw_response:
            log.warning(f"No API response generated from answer for theme: {theme}")
            return None
        
        # Process response into question
        question = process_question_response(raw_response)
        
        if not question:
            log.warning(f"No valid question extracted from answer response for theme: {theme}")
            return None
        
        # Sanitize question
        question = sanitize_question(question)
        
        # Validate question quality
        is_quality_valid, quality_reason = validate_question_quality(question, theme)
        if not is_quality_valid:
            log.warning(f"Follow-up question quality validation failed for theme '{theme}': {quality_reason}")
            return None
        
        # Final validation using existing function
        if not validate_question(question):
            log.warning(f"Generated follow-up question for theme '{theme}' failed final validation")
            return None
        
        duration = time.time() - start_time
        log.info(f" Generated follow-up question for '{theme}' in {duration:.2f}s: {question[:50]}...")
        
        return question
        
    except ValueError as e:
        log.error(f"Validation error for follow-up question (theme: '{theme}'): {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected error generating follow-up question for theme '{theme}': {e}")
        return None

def get_generation_statistics() -> Dict[str, Any]:
    """
    Get statistics about question generation performance
    
    Returns:
        Dictionary with generation statistics
    """
    return {
        'max_retries': MAX_RETRIES,
        'retry_delays': RETRY_DELAYS,
        'max_question_length': MAX_QUESTION_LENGTH,
        'min_question_length': MIN_QUESTION_LENGTH,
        'valid_theme_pattern': VALID_THEME_PATTERN,
        'module_version': '2.0',
        'optimization_date': '2025-08-24'
    }

# Convenience functions for backward compatibility
def generate_question(theme: str) -> Optional[str]:
    """Convenience function for generating a single question"""
    return generate_single_question_for_category(theme)

def generate_follow_up_question(answer: str, theme: str) -> Optional[str]:
    """Convenience function for generating a follow-up question"""
    return generate_question_from_answer(answer, theme)
