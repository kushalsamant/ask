#!/usr/bin/env python3
"""
Research Answer Generator Module
Handles main answer generation orchestration
"""

import logging
from api_client import call_together_api_for_answer
from research_answer_prompts import process_answer_response
from research_answer_prompts import (
    create_architectural_analysis_prompt,
    create_image_based_analysis_prompt,
    validate_answer,
    format_answer_for_storage
)

# Setup logging
log = logging.getLogger(__name__)

def generate_answer(question, theme, image_path):
    """
    Generate a 200-250 word answer analyzing the Question-Image pair using Llama 3.2 11B
    
    Args:
        question (str): The question to analyze
        theme (str): Theme name
        image_path (str): Path to the image (optional)
    
    Returns:
        str: Generated answer or None if failed
    """
    try:
        # Create appropriate prompt based on whether image is provided
        if image_path:
            prompt, system_prompt = create_image_based_analysis_prompt(question, theme, image_path)
        else:
            prompt, system_prompt = create_architectural_analysis_prompt(question, theme)
        
        # Call API
        raw_response = call_together_api_for_answer(prompt, system_prompt)
        
        if not raw_response:
            log.warning(f"No response generated for question: {question[:50]}...")
            return None
        
        # Process response into answer
        answer = process_answer_response(raw_response)
        
        if not answer:
            log.warning(f"No valid answer generated for question: {question[:50]}...")
            return None
        
        # Validate answer quality
        if not validate_answer(answer):
            log.warning(f"Generated answer for question failed validation: {question[:50]}...")
            return None
        
        # Format answer for storage
        formatted_answer = format_answer_for_storage(answer)
        
        log.info(f" Generated answer for {theme}: {formatted_answer[:50]}...")
        return formatted_answer
        
    except Exception as e:
        log.error(f"Error generating answer: {e}")
        return None

def generate_answer_without_image(question, theme):
    """
    Generate answer without image reference
    
    Args:
        question (str): The question to analyze
        theme (str): Theme name
    
    Returns:
        str: Generated answer or None if failed
    """
    return generate_answer(question, theme, None)

def generate_answer_with_image(question, theme, image_path):
    """
    Generate answer with image reference
    
    Args:
        question (str): The question to analyze
        theme (str): Theme name
        image_path (str): Path to the image
    
    Returns:
        str: Generated answer or None if failed
    """
    return generate_answer(question, theme, image_path)
