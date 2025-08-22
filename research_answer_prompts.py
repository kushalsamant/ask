#!/usr/bin/env python3
"""
Research Answer Prompts Module
Handles prompt generation and formatting for answer generation
"""

import logging

# Setup logging
log = logging.getLogger(__name__)

def create_architectural_analysis_prompt(question, category):
    """
    Create a prompt for generating architectural analysis answers
    
    Args:
        question (str): The question to analyze
        category (str): Category name
    
    Returns:
        tuple: (prompt, system_prompt)
    """
    system_prompt = """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications."""
    
    prompt = f"""Question: {question}
    category: {category}

    Analyze this architectural question and provide a comprehensive, academic response in approximately 200-250 words.
    Consider:
    - Key architectural principles and theories involved
    - Contemporary relevance and future implications
    - Connection to {category} specifically
    - Practical and theoretical considerations
    - Historical context and evolution
    - Cross-disciplinary implications
    - Innovation potential and challenges

    Provide your detailed analysis:"""
    
    return prompt, system_prompt

def create_image_based_analysis_prompt(question, category, image_path):
    """
    Create a prompt for generating image-based architectural analysis
    
    Args:
        question (str): The question to analyze
        category (str): Category name
        image_path (str): Path to the image
    
    Returns:
        tuple: (prompt, system_prompt)
    """
    system_prompt = """You are an expert architectural researcher and educator analyzing architectural concepts and imagery.
    Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications."""
    
    prompt = f"""Question: {question}
    category: {category}
    image: {image_path}

    Analyze this architectural question in relation to the provided image and provide a comprehensive, academic response in approximately 200-250 words.
    Consider:
    - Key architectural principles and theories demonstrated in the image
    - Contemporary relevance and future implications
    - Connection to {category} specifically
    - Practical and theoretical considerations
    - Historical context and evolution
    - Cross-disciplinary implications
    - Innovation potential and challenges
    - Visual elements and their significance

    Provide your detailed analysis:"""
    
    return prompt, system_prompt

def validate_answer(answer):
    """
    Validate if a generated answer meets quality standards
    
    Args:
        answer (str): Generated answer
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not answer:
            return False
            
        # Check minimum length for meaningful answer
        if len(answer.strip()) < 100:
            return False
            
        # Check if it's not just a repetition of the question
        if answer.lower().startswith('question:'):
            return False
            
        # Check for basic content indicators
        content_indicators = ['architecture', 'design', 'building', 'construction', 'space', 'form', 'function']
        has_content = any(indicator in answer.lower() for indicator in content_indicators)
        
        if not has_content:
            return False
            
        return True
        
    except Exception as e:
        log.error(f"Error validating answer: {e}")
        return False

def format_answer_for_storage(answer):
    """
    Format answer for storage in database/log files
    
    Args:
        answer (str): Raw answer
    
    Returns:
        str: Formatted answer
    """
    try:
        if not answer:
            return ""
            
        # Clean up whitespace
        formatted = ' '.join(answer.split())
        
        # Ensure proper sentence endings
        if not formatted.endswith(('.', '!', '?')):
            formatted += '.'
            
        return formatted
        
    except Exception as e:
        log.error(f"Error formatting answer: {e}")
        return answer

def process_answer_response(raw_text):
    """
    Process raw API response into a clean answer
    
    Args:
        raw_text (str): Raw response from API
    
    Returns:
        str: Processed answer or None if invalid
    """
    try:
        if not raw_text:
            return None
            
        # Clean up the answer - remove extra whitespace
        answer = ' '.join(raw_text.split())
        
        # Ensure minimum length for meaningful answer
        if len(answer) < 50:
            log.warning("Generated answer is too short")
            return None
            
        return answer
        
    except Exception as e:
        log.error(f"Error processing answer response: {e}")
        return None
