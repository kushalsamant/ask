#!/usr/bin/env python3
"""
Research Answer Prompts Module
Handles prompt generation and formatting for answer generation

This module provides functionality to:
- Create architectural analysis prompts
- Generate image-based analysis prompts
- Validate answer quality and content
- Format answers for storage
- Process raw API responses
- Handle various error conditions gracefully
- Provide performance optimizations and caching

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import logging
import re
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime
from functools import lru_cache

# Setup logging with enhanced configuration
log = logging.getLogger(__name__)

# Type definitions for better code documentation
PromptTuple = Tuple[str, str]
AnswerValidationResult = Dict[str, Any]

# Configuration constants
MIN_ANSWER_LENGTH = 100
MIN_RESPONSE_LENGTH = 50
MAX_ANSWER_LENGTH = 2000

# Content validation patterns
ARCHITECTURAL_INDICATORS = [
    'architecture', 'architectural', 'design', 'building', 'construction', 
    'space', 'form', 'function', 'structure', 'urban', 'planning', 
    'sustainable', 'modern', 'traditional', 'facade', 'interior', 
    'exterior', 'materials', 'technology', 'innovation', 'sustainability',
    'environmental', 'energy', 'efficiency', 'aesthetics', 'functionality',
    'context', 'site', 'landscape', 'infrastructure', 'development'
]

NON_ARCHITECTURAL_INDICATORS = [
    'cooking', 'recipe', 'food', 'music', 'sports', 'gaming', 'fashion',
    'makeup', 'beauty', 'entertainment', 'celebrity', 'gossip', 'politics',
    'religion', 'philosophy', 'mathematics', 'chemistry', 'biology',
    'medicine', 'finance', 'business', 'marketing', 'advertising'
]

def create_architectural_analysis_prompt(question: str, theme: str) -> PromptTuple:
    """
    Create a prompt for generating architectural analysis answers
    
    Args:
        question: The question to analyze
        theme: Theme name for context
    
    Returns:
        Tuple containing (prompt, system_prompt)
        
    Raises:
        ValueError: If question or theme is empty
    """
    try:
        # Input validation
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if not theme or not theme.strip():
            raise ValueError("Theme cannot be empty")
        
        # Clean inputs
        question = question.strip()
        theme = theme.strip()
        
        system_prompt = """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications.
    Your responses should be comprehensive, well-structured, and academically rigorous."""
        
        prompt = f"""Question: {question}
    Theme: {theme}

    Analyze this architectural question and provide a comprehensive, academic response in approximately 200-250 words.
    Consider:
    - Key architectural principles and theories involved
    - Contemporary relevance and future implications
    - Connection to {theme} specifically
    - Practical and theoretical considerations
    - Historical context and evolution
    - Cross-disciplinary implications
    - Innovation potential and challenges
    - Environmental and sustainability aspects
    - Social and cultural impact
    - Technical feasibility and implementation

    Provide your detailed analysis:"""
        
        log.info(f"Created architectural analysis prompt for theme: {theme}")
        return prompt, system_prompt
        
    except ValueError as e:
        log.error(f"Invalid input for architectural analysis prompt: {e}")
        raise
    except Exception as e:
        log.error(f"Error creating architectural analysis prompt: {e}")
        raise

def create_image_based_analysis_prompt(question: str, theme: str, image_path: str) -> PromptTuple:
    """
    Create a prompt for generating image-based architectural analysis
    
    Args:
        question: The question to analyze
        theme: Theme name for context
        image_path: Path to the image for analysis
    
    Returns:
        Tuple containing (prompt, system_prompt)
        
    Raises:
        ValueError: If any input is empty or invalid
    """
    try:
        # Input validation
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if not theme or not theme.strip():
            raise ValueError("Theme cannot be empty")
        
        if not image_path or not image_path.strip():
            raise ValueError("Image path cannot be empty")
        
        # Clean inputs
        question = question.strip()
        theme = theme.strip()
        image_path = image_path.strip()
        
        system_prompt = """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications.
    When analyzing images, pay attention to visual elements, spatial relationships, and design details."""
        
        prompt = f"""Question: {question}
    Theme: {theme}
    Image: {image_path}

    Analyze this architectural question in relation to the provided image and provide a comprehensive, academic response in approximately 200-250 words.
    Consider:
    - Key architectural principles and theories demonstrated in the image
    - Contemporary relevance and future implications
    - Connection to {theme} specifically
    - Practical and theoretical considerations
    - Historical context and evolution
    - Cross-disciplinary implications
    - Innovation potential and challenges
    - Visual elements and their significance
    - Spatial organization and flow
    - Material choices and construction methods
    - Environmental and contextual factors
    - User experience and functionality

    Provide your detailed analysis:"""
        
        log.info(f"Created image-based analysis prompt for theme: {theme}, image: {image_path}")
        return prompt, system_prompt
        
    except ValueError as e:
        log.error(f"Invalid input for image-based analysis prompt: {e}")
        raise
    except Exception as e:
        log.error(f"Error creating image-based analysis prompt: {e}")
        raise

def validate_answer(answer: str) -> bool:
    """
    Validate if a generated answer meets quality standards
    
    Args:
        answer: Generated answer to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if not answer:
            log.warning("Answer validation failed: Empty answer")
            return False
        
        # Clean the answer
        answer_clean = answer.strip()
        
        # Check minimum length for meaningful answer
        if len(answer_clean) < MIN_ANSWER_LENGTH:
            log.warning(f"Answer validation failed: Too short ({len(answer_clean)} chars)")
            return False
        
        # Check maximum length to avoid overly verbose answers
        if len(answer_clean) > MAX_ANSWER_LENGTH:
            log.warning(f"Answer validation failed: Too long ({len(answer_clean)} chars)")
            return False
        
        # Check if it's not just a repetition of the question
        if answer_clean.lower().startswith('question:'):
            log.warning("Answer validation failed: Starts with 'Question:'")
            return False
        
        # Check for basic content indicators (case-insensitive)
        answer_lower = answer_clean.lower()
        
        # Check for architectural content
        has_architectural_content = any(
            indicator in answer_lower for indicator in ARCHITECTURAL_INDICATORS
        )
        
        if not has_architectural_content:
            log.warning("Answer validation failed: No architectural content detected")
            return False
        
        # Check for non-architectural content dominance
        non_arch_count = sum(
            1 for indicator in NON_ARCHITECTURAL_INDICATORS 
            if indicator in answer_lower
        )
        
        if non_arch_count > 3:  # Allow some non-architectural terms but not dominance
            log.warning("Answer validation failed: Too much non-architectural content")
            return False
        
        # Check for repetitive content
        words = answer_clean.split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                if len(word_lower) > 3:  # Only count significant words
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            # Check if any word appears too frequently
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq > len(words) * 0.15:  # More than 15% repetition
                log.warning("Answer validation failed: Too much repetition")
                return False
        
        log.info(f"Answer validation passed: {len(answer_clean)} chars")
        return True
        
    except Exception as e:
        log.error(f"Error validating answer: {e}")
        return False

def get_validation_details(answer: str) -> AnswerValidationResult:
    """
    Get detailed validation results for an answer
    
    Args:
        answer: Answer to analyze
    
    Returns:
        Dictionary with validation details
    """
    try:
        if not answer:
            return {
                'valid': False,
                'length': 0,
                'has_architectural_content': False,
                'non_architectural_count': 0,
                'repetition_score': 0,
                'issues': ['Empty answer']
            }
        
        answer_clean = answer.strip()
        answer_lower = answer_clean.lower()
        
        # Calculate metrics
        length = len(answer_clean)
        has_arch_content = any(
            indicator in answer_lower for indicator in ARCHITECTURAL_INDICATORS
        )
        non_arch_count = sum(
            1 for indicator in NON_ARCHITECTURAL_INDICATORS 
            if indicator in answer_lower
        )
        
        # Calculate repetition score
        words = answer_clean.split()
        repetition_score = 0
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                if len(word_lower) > 3:
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            max_freq = max(word_freq.values()) if word_freq else 0
            repetition_score = max_freq / len(words) if words else 0
        
        # Identify issues
        issues = []
        if length < MIN_ANSWER_LENGTH:
            issues.append(f"Too short ({length} chars, minimum {MIN_ANSWER_LENGTH})")
        if length > MAX_ANSWER_LENGTH:
            issues.append(f"Too long ({length} chars, maximum {MAX_ANSWER_LENGTH})")
        if answer_clean.lower().startswith('question:'):
            issues.append("Starts with 'Question:'")
        if not has_arch_content:
            issues.append("No architectural content")
        if non_arch_count > 3:
            issues.append(f"Too much non-architectural content ({non_arch_count} terms)")
        if repetition_score > 0.15:
            issues.append(f"Too much repetition (score: {repetition_score:.2f})")
        
        return {
            'valid': len(issues) == 0,
            'length': length,
            'has_architectural_content': has_arch_content,
            'non_architectural_count': non_arch_count,
            'repetition_score': repetition_score,
            'issues': issues
        }
        
    except Exception as e:
        log.error(f"Error getting validation details: {e}")
        return {
            'valid': False,
            'length': 0,
            'has_architectural_content': False,
            'non_architectural_count': 0,
            'repetition_score': 0,
            'issues': [f'Error: {str(e)}']
        }

def format_answer_for_storage(answer: str) -> str:
    """
    Format answer for storage in database/log files
    
    Args:
        answer: Raw answer to format
    
    Returns:
        Formatted answer string
    """
    try:
        if not answer:
            return ""
        
        # Clean up whitespace (normalize to single spaces)
        formatted = re.sub(r'\s+', ' ', answer.strip())
        
        # Ensure proper sentence endings
        if formatted and not formatted.endswith(('.', '!', '?')):
            formatted += '.'
        
        # Remove any leading/trailing whitespace
        formatted = formatted.strip()
        
        log.info(f"Formatted answer for storage: {len(formatted)} chars")
        return formatted
        
    except Exception as e:
        log.error(f"Error formatting answer: {e}")
        return answer if answer else ""

def process_answer_response(raw_text: str) -> Optional[str]:
    """
    Process raw API response into a clean answer
    
    Args:
        raw_text: Raw response from API
    
    Returns:
        Processed answer or None if invalid
    """
    try:
        if not raw_text:
            log.warning("Processing failed: Empty raw text")
            return None
        
        # Clean up the answer - remove extra whitespace
        answer = re.sub(r'\s+', ' ', raw_text.strip())
        
        # Ensure minimum length for meaningful answer
        if len(answer) < MIN_RESPONSE_LENGTH:
            log.warning(f"Generated answer is too short: {len(answer)} chars")
            return None
        
        # Remove common API artifacts
        answer = re.sub(r'^[A-Za-z]+:\s*', '', answer)  # Remove "Answer:" prefix
        answer = re.sub(r'\n+', ' ', answer)  # Replace newlines with spaces
        
        # Final cleanup
        answer = answer.strip()
        
        if not answer:
            log.warning("Processing failed: No content after cleanup")
            return None
        
        log.info(f"Processed answer response: {len(answer)} chars")
        return answer
        
    except Exception as e:
        log.error(f"Error processing answer response: {e}")
        return None

@lru_cache(maxsize=128)
def get_prompt_template(template_type: str) -> str:
    """
    Get cached prompt template
    
    Args:
        template_type: Type of template to retrieve
    
    Returns:
        Template string
    """
    templates = {
        'architectural': """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications.
    Your responses should be comprehensive, well-structured, and academically rigorous.""",
        
        'image_based': """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications.
    When analyzing images, pay attention to visual elements, spatial relationships, and design details."""
    }
    
    return templates.get(template_type, templates['architectural'])

def clear_prompt_cache() -> None:
    """
    Clear the LRU cache for prompt templates
    
    This function can be called to refresh cached templates
    """
    try:
        get_prompt_template.cache_clear()
        log.info("Prompt cache cleared successfully")
    except Exception as e:
        log.error(f"Error clearing prompt cache: {e}")

# Export main functions for easy access
__all__ = [
    'create_architectural_analysis_prompt',
    'create_image_based_analysis_prompt',
    'validate_answer',
    'get_validation_details',
    'format_answer_for_storage',
    'process_answer_response',
    'get_prompt_template',
    'clear_prompt_cache'
]
