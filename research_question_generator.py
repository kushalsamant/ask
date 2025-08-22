#!/usr/bin/env python3
"""
Research Question Generator Module
Handles main question generation orchestration
"""

import logging
from api_client import call_together_api
from research_question_prompts import process_question_response
from research_question_prompts import (
    create_category_question_prompt, 
    create_answer_based_question_prompt,
    validate_question
)

# Setup logging
log = logging.getLogger(__name__)

def generate_single_question_for_category(category):
    """
    Generate a single architectural question for a specific category using Together AI
    
    Args:
        category (str): Category name
    
    Returns:
        str: Generated question or None if failed
    """
    try:
        # Create prompt for category
        prompt, system_prompt = create_category_question_prompt(category)
        
        # Call API
        raw_response = call_together_api(prompt, system_prompt)
        
        if not raw_response:
            log.warning(f"No response generated for {category}")
            return None
        
        # Process response into question
        question = process_question_response(raw_response)
        
        if not question:
            log.warning(f"No valid question generated for {category}")
            return None
        
        # Validate question quality
        if not validate_question(question):
            log.warning(f"Generated question for {category} failed validation")
            return None
        
        log.info(f"✅ Generated question for {category}: {question[:50]}...")
        return question
        
    except Exception as e:
        log.error(f"Error generating single question for {category}: {e}")
        return None

def generate_question_from_answer(answer, category):
    """
    Generate a new question based on a previous answer for a specific category
    
    Args:
        answer (str): Previous answer/insight
        category (str): Category name
    
    Returns:
        str: Generated question or None if failed
    """
    try:
        # Create prompt based on answer
        prompt, system_prompt = create_answer_based_question_prompt(answer, category)
        
        # Call API
        raw_response = call_together_api(prompt, system_prompt)
        
        if not raw_response:
            log.warning(f"No response generated from answer for {category}")
            return None
        
        # Process response into question
        question = process_question_response(raw_response)
        
        if not question:
            log.warning(f"No valid question generated from answer for {category}")
            return None
        
        # Validate question quality
        if not validate_question(question):
            log.warning(f"Generated question from answer for {category} failed validation")
            return None
        
        log.info(f"✅ Generated question from answer for {category}: {question[:50]}...")
        return question
        
    except Exception as e:
        log.error(f"Error generating question from answer for {category}: {e}")
        return None
