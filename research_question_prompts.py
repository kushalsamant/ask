#!/usr/bin/env python3
"""
Research Question Prompts Module
Handles prompt generation and formatting for question generation
"""

import logging

# Setup logging
log = logging.getLogger(__name__)

def create_category_question_prompt(theme):
    """
    Create a prompt for generating questions for a specific theme
    
    Args:
        theme (str): Theme name
    
    Returns:
        tuple: (prompt, system_prompt)
    """
    system_prompt = "You are an expert architectural research assistant specializing in question generation."
    
    prompt = f"""You are an expert architectural researcher and educator. Generate 1 thought-provoking question about {theme} in architecture.

Context: This question will inspire architectural research and creative thinking. It should challenge conventional wisdom and explore the intersection of {theme} with contemporary challenges.

Requirements:
- Create an open-ended question that encourages deep thinking and discussion
- Focus on innovation, sustainability, future trends, and societal impact
- Address real-world challenges and opportunities in {theme}
- Consider global perspectives and cross-cultural implications
- Start the question with "How", "What", or "Why"
- Use clear, professional language
- Make the question unique and thought-provoking
- Format: Single question ending with a question mark (?)

Example format:
How can we design buildings that respond to climate change?

Please generate 1 {theme}-specific question that provokes meaningful architectural discourse:"""
    
    return prompt, system_prompt

def create_answer_based_question_prompt(answer, theme):
    """
    Create a prompt for generating questions based on previous answers
    
    Args:
        answer (str): Previous answer/insight
        theme (str): Theme name
    
    Returns:
        tuple: (prompt, system_prompt)
    """
    system_prompt = "You are an expert architectural research assistant specializing in question generation."
    
    prompt = f"""You are an expert architectural researcher and educator. Based on the following research insight, generate 1 thought-provoking question about {theme} in architecture.

Research Insight: {answer}

Context: This question should build upon the research insight and explore related aspects of {theme}. It should continue the research narrative and encourage further exploration.

Requirements:
- Create an open-ended question that builds upon the research insight
- Focus on innovation, sustainability, future trends, and societal impact
- Address real-world challenges and opportunities in {theme}
- Consider global perspectives and cross-cultural implications
- Start the question with "How", "What", or "Why"
- Use clear, professional language
- Make the question unique and thought-provoking
- Format: Single question ending with a question mark (?)

Example format:
How can we design buildings that respond to climate change?

Please generate 1 {theme}-specific question that builds upon the research insight:"""
    
    return prompt, system_prompt

def validate_question(question):
    """
    Validate if a generated question meets quality standards
    
    Args:
        question (str): Generated question
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not question:
            return False
            
        # Check minimum length
        if len(question.strip()) < 10:
            return False
            
        # Check if it starts with appropriate words
        question_lower = question.strip().lower()
        if not (question_lower.startswith('how') or 
                question_lower.startswith('what') or 
                question_lower.startswith('why')):
            return False
            
        # Check if it ends with a question mark
        if not question_lower.endswith('?'):
            return False
            
        return True
        
    except Exception as e:
        log.error(f"Error validating question: {e}")
        return False

def process_question_response(raw_text):
    """
    Process raw API response into a single question
    
    Args:
        raw_text (str): Raw response from API
    
    Returns:
        str: Processed question or None if invalid
    """
    try:
        if not raw_text:
            return None
            
        # Split into lines and filter valid questions
        questions = [
            q.strip() for q in raw_text.split('\n')
            if q.strip() and len(q.strip()) > 10  # Ensure questions are meaningful
        ]
        
        if questions:
            return questions[0]  # Return the first question
        else:
            log.warning("No valid questions found in response")
            return None
            
    except Exception as e:
        log.error(f"Error processing question response: {e}")
        return None
