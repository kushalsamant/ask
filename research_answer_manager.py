#!/usr/bin/env python3
"""
Research Answer Management Module
Handles answer retrieval and chaining for question generation

This module provides functionality to:
- Retrieve latest answers from the log file
- Filter answers by theme/category
- Select the best answer for next question generation
- Handle various error conditions gracefully
- Provide performance optimizations and caching

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import os
import logging
import csv
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import lru_cache
from research_csv_manager import LOG_CSV_FILE

# Setup logging with enhanced configuration
log = logging.getLogger(__name__)

# Type definitions for better code documentation
AnswerData = Dict[str, Any]
AnswerList = List[AnswerData]

def validate_csv_file(file_path: str) -> bool:
    """
    Validate that the CSV file exists and is readable
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            log.warning(f"CSV file does not exist: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            log.warning(f"Path is not a file: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            log.warning(f"CSV file is not readable: {file_path}")
            return False
        
        return True
    except Exception as e:
        log.error(f"Error validating CSV file {file_path}: {e}")
        return False

def parse_csv_row(row: Dict[str, str]) -> Optional[AnswerData]:
    """
    Parse a CSV row into structured answer data
    
    Args:
        row: Dictionary representing a CSV row
        
    Returns:
        Optional[AnswerData]: Parsed answer data or None if invalid
    """
    try:
        # Extract and validate required fields
        answer_text = row.get('answer', '').strip()
        if not answer_text:
            return None
        
        question_number = row.get('question_number', '0')
        try:
            question_number = int(question_number)
        except (ValueError, TypeError):
            question_number = 0
        
        # Create structured answer data
        answer_data = {
            'answer_text': answer_text,
            'theme': row.get('theme', '').strip(),
            'question_number': question_number,
            'created_timestamp': row.get('created_timestamp', ''),
            'style': row.get('style', '').strip(),
            'category': row.get('category', '').strip(),  # Additional field for compatibility
            'metadata': {
                'parsed_at': datetime.now().isoformat(),
                'source_file': LOG_CSV_FILE
            }
        }
        
        return answer_data
    except Exception as e:
        log.error(f"Error parsing CSV row: {e}")
        return None

@lru_cache(maxsize=128)
def get_csv_headers(file_path: str) -> List[str]:
    """
    Get CSV headers with caching for performance
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List[str]: List of column headers
    """
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            return headers
    except Exception as e:
        log.error(f"Error reading CSV headers from {file_path}: {e}")
        return []

def get_latest_answers_from_log(limit: int = 5) -> AnswerList:
    """
    Get the latest answers from log.csv for generating next questions
    
    Args:
        limit: Maximum number of answers to return (default: 5)
        
    Returns:
        AnswerList: List of answer data dictionaries, sorted by question number (latest first)
        
    Raises:
        ValueError: If limit is negative
        IOError: If there are file system issues
    """
    try:
        # Input validation
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        
        if not validate_csv_file(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} is not valid, no answers available")
            return []

        answers: AnswerList = []
        
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            
            # Read all rows and parse them
            for row in reader:
                answer_data = parse_csv_row(row)
                if answer_data:
                    answers.append(answer_data)
            
            # Sort by question number (descending) to get latest first
            answers.sort(key=lambda x: x.get('question_number', 0), reverse=True)
            
            # Return the latest answers up to the limit
            result = answers[:limit]
        
        log.info(f"Retrieved {len(result)} latest answers from {LOG_CSV_FILE} (total available: {len(answers)})")
        return result
        
    except ValueError as e:
        log.error(f"Invalid input parameter: {e}")
        return []
    except IOError as e:
        log.error(f"IO error reading {LOG_CSV_FILE}: {e}")
        return []
    except Exception as e:
        log.error(f"Unexpected error getting latest answers from {LOG_CSV_FILE}: {e}")
        return []

def get_latest_answer_for_category(theme: str, limit: int = 3) -> AnswerList:
    """
    Get the latest answers for a specific theme from log.csv
    
    Args:
        theme: Theme/category to filter by
        limit: Maximum number of answers to return (default: 3)
        
    Returns:
        AnswerList: List of answer data for the specified theme, sorted by question number
        
    Raises:
        ValueError: If theme is empty or limit is negative
    """
    try:
        # Input validation
        if not theme or not theme.strip():
            raise ValueError("Theme cannot be empty")
        
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        
        # Get more answers to filter by theme
        all_answers = get_latest_answers_from_log(limit * 2)
        
        # Filter answers by theme (case-insensitive)
        theme_lower = theme.lower().strip()
        category_answers = [
            answer for answer in all_answers 
            if answer.get('theme', '').lower().strip() == theme_lower
        ]
        
        # Return the latest ones for this theme
        result = category_answers[:limit]
        
        log.info(f"Retrieved {len(result)} answers for theme '{theme}' (total available: {len(category_answers)})")
        return result
        
    except ValueError as e:
        log.error(f"Invalid input parameter for theme {theme}: {e}")
        return []
    except Exception as e:
        log.error(f"Error getting latest answers for theme {theme}: {e}")
        return []

def get_best_answer_for_next_question(target_category: str, limit: int = 5) -> Optional[AnswerData]:
    """
    Get the best answer from log.csv to generate the next question for a target theme
    
    This function implements a priority-based selection algorithm:
    1. Latest answer from the same theme (if prefer_same_category is true)
    2. Latest answer from any theme
    3. Most recent answer overall
    
    Args:
        target_category: Target theme/category for the next question
        limit: Maximum number of answers to consider (default: 5)
        
    Returns:
        Optional[AnswerData]: Best answer data or None if no answers available
        
    Raises:
        ValueError: If target_category is empty or limit is negative
    """
    try:
        # Input validation
        if not target_category or not target_category.strip():
            raise ValueError("Target category cannot be empty")
        
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        
        latest_answers = get_latest_answers_from_log(limit)
        
        if not latest_answers:
            log.info(f"No answers found in {LOG_CSV_FILE} for next question generation")
            return None
        
        # Get configuration from environment variables with fallback
        prefer_same_category = os.getenv('ANSWER_PREFER_SAME_CATEGORY', 'true').lower() == 'true'
        
        # Priority order for answer selection
        if prefer_same_category:
            # First, try to find answers from the same theme (case-insensitive)
            target_lower = target_category.lower().strip()
            same_category_answers = [
                answer for answer in latest_answers 
                if answer.get('theme', '').lower().strip() == target_lower
            ]
            
            if same_category_answers:
                best_answer = same_category_answers[0]  # Latest from same theme
                log.info(f"Using latest answer from same theme ({target_category}) for next question")
                return best_answer
        
        # If no same theme answers or prefer_same_category is false, use the most recent answer
        best_answer = latest_answers[0]  # Most recent overall
        log.info(f"Using latest answer from theme {best_answer.get('theme', 'unknown')} for next question in {target_category}")
        return best_answer
        
    except ValueError as e:
        log.error(f"Invalid input parameter for target category {target_category}: {e}")
        return None
    except Exception as e:
        log.error(f"Error getting best answer for next question: {e}")
        return None

def get_answer_statistics() -> Dict[str, Any]:
    """
    Get statistics about answers in the log file
    
    Returns:
        Dict[str, Any]: Statistics including total answers, themes, etc.
    """
    try:
        if not validate_csv_file(LOG_CSV_FILE):
            return {
                'total_answers': 0,
                'themes': [],
                'error': 'CSV file not accessible'
            }
        
        answers = get_latest_answers_from_log(limit=1000)  # Get all answers
        
        if not answers:
            return {
                'total_answers': 0,
                'themes': [],
                'latest_question_number': 0
            }
        
        # Calculate statistics
        themes = list(set(answer.get('theme', '') for answer in answers if answer.get('theme')))
        latest_question = max(answer.get('question_number', 0) for answer in answers)
        
        stats = {
            'total_answers': len(answers),
            'themes': themes,
            'latest_question_number': latest_question,
            'theme_count': len(themes),
            'generated_at': datetime.now().isoformat()
        }
        
        log.info(f"Generated statistics: {stats['total_answers']} answers across {stats['theme_count']} themes")
        return stats
        
    except Exception as e:
        log.error(f"Error generating answer statistics: {e}")
        return {
            'total_answers': 0,
            'themes': [],
            'error': str(e)
        }

def clear_answer_cache() -> None:
    """
    Clear the LRU cache for CSV headers
    
    This function can be called to refresh cached data if the CSV file has been updated
    """
    try:
        get_csv_headers.cache_clear()
        log.info("Answer cache cleared successfully")
    except Exception as e:
        log.error(f"Error clearing answer cache: {e}")

# Export main functions for easy access
__all__ = [
    'get_latest_answers_from_log',
    'get_latest_answer_for_category', 
    'get_best_answer_for_next_question',
    'get_answer_statistics',
    'clear_answer_cache',
    'validate_csv_file',
    'parse_csv_row'
]
