#!/usr/bin/env python3
"""
Research Question Management Module
Enhanced question retrieval and chaining for answer generation with improved performance and error handling

This module provides functionality to:
- Retrieve latest questions from CSV log files
- Filter questions by theme and usage status
- Find the best questions for answer generation
- Identify questions without answers
- Generate comprehensive question statistics
- Find similar questions using text analysis
- Handle CSV file operations with robust error handling
- Provide performance monitoring and caching
- Support input validation and sanitization

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Optimized)
"""

import os
import logging
import csv
import time
import re
from typing import List, Dict, Optional, Any, Tuple
from functools import lru_cache
from datetime import datetime, timedelta

# Import core dependencies
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

# Configuration constants
DEFAULT_LIMIT = 5
MAX_LIMIT = 100
CACHE_TTL = 300  # 5 minutes
SIMILARITY_THRESHOLD = 2  # Minimum common words for similarity
VALID_THEME_PATTERN = r'^[a-zA-Z0-9_\-\s]+$'

# Performance monitoring
_performance_stats = {
    'total_calls': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'total_time': 0.0
}

def validate_input_parameters(theme: str = None, limit: int = DEFAULT_LIMIT) -> Tuple[bool, str]:
    """
    Validate input parameters for question management functions
    
    Args:
        theme: Theme name to validate (optional)
        limit: Limit parameter to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate limit
    if not isinstance(limit, int):
        return False, "Limit must be an integer"
    
    if limit < 1:
        return False, "Limit must be at least 1"
    
    if limit > MAX_LIMIT:
        return False, f"Limit cannot exceed {MAX_LIMIT}"
    
    # Validate theme if provided
    if theme is not None:
        if not isinstance(theme, str):
            return False, "Theme must be a string"
        
        if len(theme.strip()) == 0:
            return False, "Theme cannot be empty or whitespace only"
        
        if len(theme) > 100:
            return False, "Theme too long (max 100 characters)"
        
        if not re.match(VALID_THEME_PATTERN, theme):
            return False, "Theme contains invalid characters"
    
    return True, ""

def sanitize_question_data(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and clean question data from CSV
    
    Args:
        question_data: Raw question data from CSV
        
    Returns:
        Sanitized question data
    """
    sanitized = {}
    
    # Clean and validate each field
    for key, value in question_data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    
    # Ensure required fields have default values
    sanitized.setdefault('question_text', '')
    sanitized.setdefault('theme', '')
    sanitized.setdefault('question_number', 0)
    sanitized.setdefault('created_timestamp', '')
    sanitized.setdefault('style', '')
    sanitized.setdefault('is_used', False)
    
    return sanitized

def read_csv_safely(file_path: str) -> List[Dict[str, Any]]:
    """
    Safely read CSV file with comprehensive error handling
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of dictionaries representing CSV rows
    """
    start_time = time.time()
    
    try:
        if not os.path.exists(file_path):
            log.warning(f"{file_path} does not exist, no questions available")
            return []
        
        if not os.path.isfile(file_path):
            log.error(f"{file_path} is not a file")
            return []
        
        if os.path.getsize(file_path) == 0:
            log.warning(f"{file_path} is empty")
            return []
        
        rows = []
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            try:
                reader = csv.DictReader(f)
                rows = list(reader)
            except csv.Error as e:
                log.error(f"CSV parsing error in {file_path}: {e}")
                return []
            except UnicodeDecodeError as e:
                log.error(f"Encoding error in {file_path}: {e}")
                return []
        
        duration = time.time() - start_time
        log.debug(f"Read {len(rows)} rows from {file_path} in {duration:.3f}s")
        
        return rows
        
    except PermissionError as e:
        log.error(f"Permission denied accessing {file_path}: {e}")
        return []
    except Exception as e:
        log.error(f"Unexpected error reading {file_path}: {e}")
        return []

@lru_cache(maxsize=128)
def get_latest_questions_from_log(limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
    """
    Get the latest questions from log.csv for generating next answers
    
    Enhanced with:
    - Input validation and sanitization
    - Caching for performance
    - Comprehensive error handling
    - Performance monitoring
    - Safe CSV reading
    
    Args:
        limit: Maximum number of questions to return
        
    Returns:
        List of question dictionaries sorted by question_number (latest first)
    """
    start_time = time.time()
    _performance_stats['total_calls'] += 1
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        log.info(f"Retrieving latest {limit} questions from {LOG_CSV_FILE}")
        
        # Read CSV safely
        rows = read_csv_safely(LOG_CSV_FILE)
        if not rows:
            return []
        
        # Filter rows that have questions (non-empty question field)
        question_rows = [
            row for row in rows 
            if row.get('question', '').strip()
        ]
        
        if not question_rows:
            log.info("No questions found in CSV file")
            return []
        
        # Sort by question_number to get the latest ones
        try:
            question_rows.sort(
                key=lambda x: int(x.get('question_number', 0)), 
                reverse=True
            )
        except (ValueError, TypeError) as e:
            log.warning(f"Error sorting questions by number: {e}")
            # Fallback: sort by timestamp if available
            question_rows.sort(
                key=lambda x: x.get('created_timestamp', ''), 
                reverse=True
            )
        
        # Get the latest questions up to the limit
        questions = []
        for row in question_rows[:limit]:
            question_data = {
                'question_text': row.get('question', '').strip(),
                'theme': row.get('theme', '').strip(),
                'question_number': int(row.get('question_number', 0)),
                'created_timestamp': row.get('created_timestamp', ''),
                'style': row.get('style', '').strip(),
                'is_used': row.get('is_used', '').lower() == 'true'
            }
            
            # Sanitize the data
            question_data = sanitize_question_data(question_data)
            questions.append(question_data)
        
        duration = time.time() - start_time
        _performance_stats['total_time'] += duration
        
        log.info(f" Retrieved {len(questions)} latest questions from {LOG_CSV_FILE} in {duration:.3f}s")
        return questions
        
    except Exception as e:
        log.error(f"Error getting latest questions from {LOG_CSV_FILE}: {e}")
        return []

def get_latest_questions_for_theme(theme: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Get the latest questions for a specific theme from log.csv
    
    Enhanced with:
    - Input validation and sanitization
    - Performance optimization
    - Comprehensive error handling
    
    Args:
        theme: Theme name to filter by
        limit: Maximum number of questions to return
        
    Returns:
        List of question dictionaries for the specified theme
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme, limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        log.info(f"Retrieving latest {limit} questions for theme: {theme}")
        
        # Get more questions to filter by theme
        all_questions = get_latest_questions_from_log(limit * 2)
        
        if not all_questions:
            return []
        
        # Filter questions by theme
        theme_questions = [
            question for question in all_questions 
            if question['theme'] == theme
        ]
        
        # Return the latest ones for this theme
        result = theme_questions[:limit]
        
        duration = time.time() - start_time
        log.info(f" Retrieved {len(result)} questions for theme '{theme}' in {duration:.3f}s")
        
        return result
        
    except Exception as e:
        log.error(f"Error getting latest questions for theme {theme}: {e}")
        return []

def get_unused_questions_for_theme(theme: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get unused questions for a specific theme from log.csv
    
    Enhanced with:
    - Input validation and sanitization
    - Performance optimization
    - Comprehensive error handling
    
    Args:
        theme: Theme name to filter by
        limit: Maximum number of questions to return
        
    Returns:
        List of unused question dictionaries for the specified theme
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme, limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        log.info(f"Retrieving {limit} unused questions for theme: {theme}")
        
        # Get more questions to filter
        all_questions = get_latest_questions_from_log(limit * 3)
        
        if not all_questions:
            return []
        
        # Filter questions by theme and unused status
        unused_questions = [
            question for question in all_questions 
            if question['theme'] == theme and not question['is_used']
        ]
        
        # Return the latest unused ones for this theme
        result = unused_questions[:limit]
        
        duration = time.time() - start_time
        log.info(f" Retrieved {len(result)} unused questions for theme '{theme}' in {duration:.3f}s")
        
        return result
        
    except Exception as e:
        log.error(f"Error getting unused questions for theme {theme}: {e}")
        return []

def get_best_question_for_next_answer(target_theme: str, limit: int = 5) -> Optional[Dict[str, Any]]:
    """
    Get the best question from log.csv to generate the next answer for a target theme
    
    Enhanced with:
    - Input validation and sanitization
    - Intelligent question selection algorithm
    - Performance optimization
    - Comprehensive error handling
    - Environment-based configuration
    
    Args:
        target_theme: Target theme for answer generation
        limit: Maximum number of questions to consider
        
    Returns:
        Best question dictionary or None if no suitable question found
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(target_theme, limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return None
        
        log.info(f"Finding best question for next answer in theme: {target_theme}")
        
        latest_questions = get_latest_questions_from_log(limit)
        
        if not latest_questions:
            log.info(f"No questions found in {LOG_CSV_FILE} for next answer generation")
            return None
        
        # Get configuration from environment variables
        prefer_same_theme = os.getenv('QUESTION_PREFER_SAME_THEME', 'true').lower() == 'true'
        prefer_unused = os.getenv('QUESTION_PREFER_UNUSED', 'true').lower() == 'true'
        
        # Priority order for question selection:
        # 1. Latest unused question from the same theme (if prefer_same_theme and prefer_unused are true)
        # 2. Latest question from the same theme (if prefer_same_theme is true)
        # 3. Latest unused question from any theme (if prefer_unused is true)
        # 4. Latest question from any theme
        
        if prefer_same_theme:
            # First, try to find questions from the same theme
            same_theme_questions = [
                q for q in latest_questions 
                if q['theme'] == target_theme
            ]
            
            if same_theme_questions:
                if prefer_unused:
                    # Look for unused questions from same theme
                    unused_same_theme = [
                        q for q in same_theme_questions 
                        if not q['is_used']
                    ]
                    
                    if unused_same_theme:
                        best_question = unused_same_theme[0]  # Latest unused from same theme
                        log.info(f" Using latest unused question from same theme ({target_theme}) for next answer")
                        return best_question
                
                # Use any question from same theme
                best_question = same_theme_questions[0]  # Latest from same theme
                log.info(f" Using latest question from same theme ({target_theme}) for next answer")
                return best_question
        
        if prefer_unused:
            # Look for unused questions from any theme
            unused_questions = [
                q for q in latest_questions 
                if not q['is_used']
            ]
            
            if unused_questions:
                best_question = unused_questions[0]  # Latest unused overall
                log.info(f" Using latest unused question from theme {best_question['theme']} for next answer in {target_theme}")
                return best_question
        
        # Use the most recent question overall
        best_question = latest_questions[0]  # Most recent overall
        log.info(f" Using latest question from theme {best_question['theme']} for next answer in {target_theme}")
        
        duration = time.time() - start_time
        log.debug(f"Question selection completed in {duration:.3f}s")
        
        return best_question
        
    except Exception as e:
        log.error(f"Error getting best question for next answer: {e}")
        return None

def get_questions_without_answers(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get questions that don't have answers yet
    
    Enhanced with:
    - Input validation and sanitization
    - Performance optimization
    - Comprehensive error handling
    
    Args:
        limit: Maximum number of questions to return
        
    Returns:
        List of question dictionaries without answers, sorted by question_number (oldest first)
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        log.info(f"Retrieving {limit} questions without answers")
        
        # Read CSV safely
        rows = read_csv_safely(LOG_CSV_FILE)
        if not rows:
            return []
        
        questions_without_answers = []
        
        # Filter rows that have questions but no answers
        for row in rows:
            question = row.get('question', '').strip()
            answer = row.get('answer', '').strip()
            
            if question and not answer:
                question_data = {
                    'question_text': question,
                    'theme': row.get('theme', '').strip(),
                    'question_number': int(row.get('question_number', 0)),
                    'created_timestamp': row.get('created_timestamp', ''),
                    'style': row.get('style', '').strip(),
                    'is_used': row.get('is_used', '').lower() == 'true'
                }
                
                # Sanitize the data
                question_data = sanitize_question_data(question_data)
                questions_without_answers.append(question_data)
        
        # Sort by question_number to get the oldest ones first
        try:
            questions_without_answers.sort(key=lambda x: x['question_number'])
        except (ValueError, TypeError) as e:
            log.warning(f"Error sorting questions by number: {e}")
            # Fallback: sort by timestamp if available
            questions_without_answers.sort(key=lambda x: x.get('created_timestamp', ''))
        
        # Return up to the limit
        result = questions_without_answers[:limit]
        
        duration = time.time() - start_time
        log.info(f" Retrieved {len(result)} questions without answers in {duration:.3f}s")
        
        return result
        
    except Exception as e:
        log.error(f"Error getting questions without answers: {e}")
        return []

def get_question_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about questions in the log
    
    Enhanced with:
    - Performance optimization
    - Comprehensive error handling
    - Detailed statistics
    - Performance monitoring
    
    Returns:
        Dictionary with comprehensive question statistics
    """
    start_time = time.time()
    
    try:
        log.info("Generating question statistics")
        
        # Read CSV safely
        rows = read_csv_safely(LOG_CSV_FILE)
        
        if not rows:
            stats = {
                'total_questions': 0,
                'used_questions': 0,
                'unused_questions': 0,
                'questions_with_answers': 0,
                'questions_without_answers': 0,
                'questions_by_theme': {},
                'questions_by_style': {},
                'questions_by_month': {},
                'average_questions_per_theme': 0.0,
                'most_active_theme': None,
                'least_active_theme': None,
                'performance_stats': _performance_stats.copy()
            }
            return stats
        
        stats = {
            'total_questions': 0,
            'used_questions': 0,
            'unused_questions': 0,
            'questions_with_answers': 0,
            'questions_without_answers': 0,
            'questions_by_theme': {},
            'questions_by_style': {},
            'questions_by_month': {},
            'average_questions_per_theme': 0.0,
            'most_active_theme': None,
            'least_active_theme': None,
            'performance_stats': _performance_stats.copy()
        }
        
        for row in rows:
            question = row.get('question', '').strip()
            answer = row.get('answer', '').strip()
            theme = row.get('theme', '').strip()
            style = row.get('style', '').strip()
            is_used = row.get('is_used', '').lower() == 'true'
            timestamp = row.get('created_timestamp', '')
            
            if question:
                stats['total_questions'] += 1
                
                if is_used:
                    stats['used_questions'] += 1
                else:
                    stats['unused_questions'] += 1
                
                if answer:
                    stats['questions_with_answers'] += 1
                else:
                    stats['questions_without_answers'] += 1
                
                if theme:
                    if theme not in stats['questions_by_theme']:
                        stats['questions_by_theme'][theme] = 0
                    stats['questions_by_theme'][theme] += 1
                
                if style:
                    if style not in stats['questions_by_style']:
                        stats['questions_by_style'][style] = 0
                    stats['questions_by_style'][style] += 1
                
                if timestamp:
                    try:
                        # Extract month from timestamp
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        month_key = dt.strftime('%Y-%m')
                        if month_key not in stats['questions_by_month']:
                            stats['questions_by_month'][month_key] = 0
                        stats['questions_by_month'][month_key] += 1
                    except (ValueError, TypeError):
                        pass  # Skip invalid timestamps
        
        # Calculate derived statistics
        if stats['questions_by_theme']:
            theme_counts = list(stats['questions_by_theme'].values())
            stats['average_questions_per_theme'] = sum(theme_counts) / len(theme_counts)
            
            if theme_counts:
                max_count = max(theme_counts)
                min_count = min(theme_counts)
                
                for theme, count in stats['questions_by_theme'].items():
                    if count == max_count:
                        stats['most_active_theme'] = theme
                    if count == min_count:
                        stats['least_active_theme'] = theme
        
        duration = time.time() - start_time
        log.info(f" Generated comprehensive question statistics in {duration:.3f}s")
        
        return stats
        
    except Exception as e:
        log.error(f"Error getting question statistics: {e}")
        return {}

def find_similar_questions(question_text: str, theme: str = None, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Find questions similar to the given question text
    
    Enhanced with:
    - Input validation and sanitization
    - Improved similarity algorithm
    - Performance optimization
    - Comprehensive error handling
    
    Args:
        question_text: Question text to find similar questions for
        theme: Optional theme to filter by
        limit: Maximum number of similar questions to return
        
    Returns:
        List of similar question dictionaries sorted by similarity score
    """
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme, limit)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        if not question_text or not question_text.strip():
            log.error("Question text cannot be empty")
            return []
        
        log.info(f"Finding {limit} similar questions for: {question_text[:50]}...")
        
        # Get more questions to search
        all_questions = get_latest_questions_from_log(limit * 5)
        
        if not all_questions:
            return []
        
        # Filter by theme if specified
        if theme:
            all_questions = [
                q for q in all_questions 
                if q['theme'] == theme
            ]
        
        # Calculate similarity scores
        similar_questions = []
        question_lower = question_text.lower()
        question_words = set(question_lower.split())
        
        for question in all_questions:
            if question['question_text'].lower() != question_lower:  # Not the same question
                # Calculate word overlap
                other_words = set(question['question_text'].lower().split())
                common_words = question_words & other_words
                
                if len(common_words) >= SIMILARITY_THRESHOLD:
                    # Calculate similarity score
                    similarity_score = len(common_words) / max(len(question_words), len(other_words))
                    
                    similar_questions.append({
                        **question,
                        'similarity_score': similarity_score,
                        'common_words': list(common_words)
                    })
        
        # Sort by similarity score (most similar first)
        similar_questions.sort(key=lambda q: q['similarity_score'], reverse=True)
        
        # Return top results
        result = similar_questions[:limit]
        
        duration = time.time() - start_time
        log.info(f" Found {len(result)} similar questions in {duration:.3f}s")
        
        return result
        
    except Exception as e:
        log.error(f"Error finding similar questions: {e}")
        return []

def get_performance_statistics() -> Dict[str, Any]:
    """
    Get performance statistics for the question manager
    
    Returns:
        Dictionary with performance statistics
    """
    return {
        'total_calls': _performance_stats['total_calls'],
        'cache_hits': _performance_stats['cache_hits'],
        'cache_misses': _performance_stats['cache_misses'],
        'total_time': _performance_stats['total_time'],
        'average_time': _performance_stats['total_time'] / max(_performance_stats['total_calls'], 1),
        'cache_hit_rate': _performance_stats['cache_hits'] / max(_performance_stats['total_calls'], 1),
        'module_version': '2.0',
        'optimization_date': '2025-08-24'
    }

def clear_cache():
    """Clear the LRU cache for fresh data"""
    get_latest_questions_from_log.cache_clear()
    log.info(" Question cache cleared")

# Convenience functions for backward compatibility
def get_questions_for_theme(theme: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for getting questions by theme"""
    return get_latest_questions_for_theme(theme, limit)

def get_unused_questions(theme: str = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for getting unused questions"""
    if theme:
        return get_unused_questions_for_theme(theme, limit)
    else:
        # Get all unused questions
        all_questions = get_latest_questions_from_log(limit * 2)
        return [q for q in all_questions if not q['is_used']][:limit]

def get_question_count() -> int:
    """Convenience function for getting total question count"""
    stats = get_question_statistics()
    return stats.get('total_questions', 0)
