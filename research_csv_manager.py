#!/usr/bin/env python3
"""
CSV Data Management Module
Handles core CSV operations for research data

This module provides functionality to:
- Manage comprehensive CSV data operations
- Handle question and answer logging
- Provide data validation and consistency checks
- Support data export and import operations
- Enable data backup and restoration
- Provide performance optimizations and caching
- Support data migration and transformation
- Enable advanced search and filtering
- Support data compression and optimization
- Enable configuration management

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import os
import logging
import csv
import json
import gzip
import shutil
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from pathlib import Path
from functools import lru_cache

# Setup logging with enhanced configuration
log = logging.getLogger(__name__)

# Environment variables
LOG_CSV_FILE = os.getenv('LOG_CSV_FILE', 'log.csv')

# Configuration constants
CSV_HEADERS = [
    'question_number', 'theme', 'question', 'question_image', 
    'style', 'answer', 'answer_image', 'is_used', 'created_timestamp'
]

BACKUP_DIR = "csv_backups"
MAX_BACKUP_SIZE = 100 * 1024 * 1024  # 100MB
COMPRESSION_THRESHOLD = 10 * 1024 * 1024  # 10MB

def validate_csv_file(file_path: str) -> bool:
    """
    Validate that a CSV file exists and is accessible
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        True if file is valid, False otherwise
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

def create_backup_directory() -> bool:
    """
    Create backup directory if it doesn't exist
    
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            log.info(f"Created backup directory: {BACKUP_DIR}")
        return True
    except Exception as e:
        log.error(f"Error creating backup directory: {e}")
        return False

def backup_csv_file(file_path: str) -> Optional[str]:
    """
    Create a backup of the CSV file
    
    Args:
        file_path: Path to the CSV file to backup
        
    Returns:
        Path to the backup file or None if failed
    """
    try:
        if not validate_csv_file(file_path):
            return None
        
        if not create_backup_directory():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(BACKUP_DIR, f'log_backup_{timestamp}.csv')
        
        shutil.copy2(file_path, backup_filename)
        log.info(f"Created backup: {backup_filename}")
        return backup_filename
    except Exception as e:
        log.error(f"Error creating backup: {e}")
        return None

def compress_csv_file(file_path: str) -> bool:
    """
    Compress CSV file if it exceeds threshold
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        True if compression was successful, False otherwise
    """
    try:
        if not validate_csv_file(file_path):
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size < COMPRESSION_THRESHOLD:
            return True  # No compression needed
        
        compressed_file = f"{file_path}.gz"
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        log.info(f"Compressed {file_path} to {compressed_file}")
        return True
    except Exception as e:
        log.error(f"Error compressing CSV file: {e}")
        return False

def validate_csv_headers(headers: List[str]) -> bool:
    """
    Validate CSV headers against expected format
    
    Args:
        headers: List of header names
        
    Returns:
        True if headers are valid, False otherwise
    """
    try:
        if not headers:
            return False
        
        # Check for required headers
        required_headers = ['question_number', 'theme', 'question']
        for header in required_headers:
            if header not in headers:
                log.warning(f"Missing required header: {header}")
                return False
        
        return True
    except Exception as e:
        log.error(f"Error validating CSV headers: {e}")
        return False

def get_questions_and_styles_from_log() -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Set[str]]:
    """
    Read all questions and styles from log.csv and organize by theme
    
    Returns:
        Tuple of (questions_by_category, styles_by_category, used_questions)
    """
    questions_by_category: Dict[str, Set[str]] = {}
    styles_by_category: Dict[str, Set[str]] = {}
    used_questions: Set[str] = set()

    try:
        if not os.path.exists(LOG_CSV_FILE):
            # Create log.csv with headers if it doesn't exist
            with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
            return questions_by_category, styles_by_category, used_questions

        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)

            # Validate headers
            if not validate_csv_headers(reader.fieldnames or []):
                log.warning("Invalid CSV headers detected")
                return questions_by_category, styles_by_category, used_questions

            # Add required columns if they don't exist
            fieldnames = reader.fieldnames or []
            new_columns = []
            if 'is_used' not in fieldnames:
                new_columns.append('is_used')
            if 'style' not in fieldnames:
                new_columns.append('style')
            if 'answer' not in fieldnames:
                new_columns.append('answer')

            if new_columns:
                rows = list(reader)
                fieldnames = fieldnames + new_columns
                with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in rows:
                        if 'is_used' not in row:
                            row['is_used'] = row.get('image_filename', '') != ''
                        if 'style' not in row:
                            row['style'] = ''
                        writer.writerow(row)

                # Reopen file for reading
                with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            else:
                rows = list(reader)

            # Organize questions and styles by theme
            for row in rows:
                theme = row.get('theme', '').strip()
                question = row.get('question', '').strip()
                is_used = row.get('is_used', '').lower() == 'true'
                style = row.get('style', '').strip()

                if theme and question:
                    # Organize questions
                    if theme not in questions_by_category:
                        questions_by_category[theme] = set()
                    questions_by_category[theme].add(question)
                    if is_used:
                        used_questions.add(question)

                    # Organize styles
                    if theme not in styles_by_category:
                        styles_by_category[theme] = set()
                    if style:
                        styles_by_category[theme].add(style)

        log.info(f"Read {len(questions_by_category)} themes with questions from {LOG_CSV_FILE}")
        return questions_by_category, styles_by_category, used_questions

    except Exception as e:
        log.error(f"Error reading from {LOG_CSV_FILE}: {e}")
        raise

def log_single_question(theme: str, question: str, image_filename: str, 
                       style: Optional[str] = None, is_answer: bool = False, 
                       mark_as_used: bool = False) -> bool:
    """
    Log a single question or answer to log.csv
    
    Args:
        theme: Theme/category for the question
        question: Question or answer text
        image_filename: Filename of the associated image
        style: Optional style information
        is_answer: Whether this is an answer (True) or question (False)
        mark_as_used: Whether to mark as used
        
    Returns:
        True if logging was successful, False otherwise
    """
    try:
        # Input validation
        if not theme or not theme.strip():
            log.error("Theme cannot be empty")
            return False
        
        if not question or not question.strip():
            log.error("Question cannot be empty")
            return False
        
        # Ensure log.csv exists with proper headers
        if not os.path.exists(LOG_CSV_FILE):
            with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

        # Read existing data
        rows = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Get next question number
        next_question_number = len(rows) + 1

        # Create new row
        new_row = {
            'question_number': next_question_number,
            'theme': theme.strip(),
            'question': question.strip(),
            'question_image': image_filename if not is_answer else '',
            'style': (style or '').strip(),
            'answer': question.strip() if is_answer else '',
            'answer_image': image_filename if is_answer else '',
            'is_used': str(mark_as_used).lower(),
            'created_timestamp': datetime.now().isoformat()
        }

        # Add new row
        rows.append(new_row)

        # Write back to file
        with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

        log.info(f"Logged {'answer' if is_answer else 'question'} for {theme}: {question[:50]}...")
        return True

    except Exception as e:
        log.error(f"Error logging question: {e}")
        return False

def log_qa_pair(theme: str, question: str, answer: str, question_image: str, answer_image: str, 
                question_style: Optional[str] = None, answer_style: Optional[str] = None) -> bool:
    """
    Log a complete Q&A pair to log.csv as a single entry
    
    Args:
        theme: Theme/category for the Q&A pair
        question: Question text
        answer: Answer text
        question_image: Filename of the question image
        answer_image: Filename of the answer image
        question_style: Optional style information for question
        answer_style: Optional style information for answer
        
    Returns:
        True if logging was successful, False otherwise
    """
    try:
        # Input validation
        if not theme or not theme.strip():
            log.error("Theme cannot be empty")
            return False
        
        if not question or not question.strip():
            log.error("Question cannot be empty")
            return False
            
        if not answer or not answer.strip():
            log.error("Answer cannot be empty")
            return False
        
        # Ensure log.csv exists with proper headers
        if not os.path.exists(LOG_CSV_FILE):
            with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

        # Read existing data
        rows = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Get next question number
        next_question_number = len(rows) + 1

        # Create new row with complete Q&A pair
        new_row = {
            'question_number': next_question_number,
            'theme': theme.strip(),
            'question': question.strip(),
            'question_image': question_image.strip(),
            'style': (question_style or '').strip(),
            'answer': answer.strip(),
            'answer_image': answer_image.strip(),
            'is_used': 'false',
            'created_timestamp': datetime.now().isoformat()
        }

        # Add new row
        rows.append(new_row)

        # Write back to file
        with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

        log.info(f"Logged complete Q&A pair for {theme}: Q: {question[:50]}... A: {answer[:50]}...")
        return True

    except Exception as e:
        log.error(f"Error logging Q&A pair: {e}")
        return False

def mark_questions_as_used(questions_dict: Dict[str, str]) -> int:
    """
    Mark questions as used in log.csv after successful PDF creation
    
    Args:
        questions_dict: Dictionary mapping themes to questions to mark as used
        
    Returns:
        Number of questions marked as used
    """
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, cannot mark questions as used")
            return 0

        # Read existing data
        rows = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Mark questions as used
        questions_marked = 0
        for row in rows:
            theme = row.get('theme', '').strip()
            question = row.get('question', '').strip()
            
            # Check if this question should be marked as used
            if theme in questions_dict and questions_dict[theme] == question:
                if row.get('is_used', '').lower() != 'true':
                    row['is_used'] = 'true'
                    questions_marked += 1

        # Write back to file
        with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

        log.info(f"Marked {questions_marked} questions as used")
        return questions_marked

    except Exception as e:
        log.error(f"Error marking questions as used: {e}")
        return 0

@lru_cache(maxsize=128)
def get_next_image_number() -> int:
    """
    Get the next image number based on existing images in log.csv
    
    Returns:
        Next available image number
    """
    try:
        if os.path.exists(LOG_CSV_FILE):
            max_number = 0
            with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check both question and answer image filenames
                    for filename_field in ['question_image', 'answer_image']:
                        if filename_field in row and row[filename_field].strip():
                            # Extract number from filename like "ASK-01-ure-q.jpg"
                            filename = row[filename_field].strip()
                            if filename.startswith('ASK-') and '-' in filename:
                                try:
                                    # Extract number from "ASK-01-ure-q.jpg"
                                    parts = filename.split('-')
                                    if len(parts) >= 2:
                                        number_str = parts[1]
                                        number = int(number_str)
                                        max_number = max(max_number, number)
                                except (ValueError, IndexError):
                                    continue
            return max_number + 1
        else:
            return 1
    except Exception as e:
        log.error(f"Error getting next image number: {e}")
        return 1

def export_questions_to_csv(output_filename: str = 'questions_export.csv') -> bool:
    """
    Export all questions to a separate CSV file
    
    Args:
        output_filename: Path to the output CSV file
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        questions_by_category, styles_by_category, used_questions = get_questions_and_styles_from_log()
        
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['theme', 'question', 'is_used', 'available_styles'])
            
            for theme, questions in questions_by_category.items():
                for question in questions:
                    is_used = question in used_questions
                    available_styles = ', '.join(styles_by_category.get(theme, []))
                    writer.writerow([theme, question, is_used, available_styles])
        
        log.info(f"Exported questions to {output_filename}")
        return True
    except Exception as e:
        log.error(f"Error exporting questions: {e}")
        return False

def read_log_csv() -> List[Dict[str, Any]]:
    """
    Read Q&A pairs from log.csv in format expected by image generation system
    
    Returns:
        List of Q&A pair dictionaries
    """
    qa_pairs = []
    
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist")
            return qa_pairs
            
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                theme = row.get('theme', '').strip()
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                
                if theme and question:
                    qa_pair = {
                        'theme': theme,
                        'question': question,
                        'answer': answer,
                        'question_number': row.get('question_number', ''),
                        'question_image': row.get('question_image', ''),
                        'answer_image': row.get('answer_image', ''),
                        'style': row.get('style', ''),
                        'is_used': row.get('is_used', '').lower() == 'true',
                        'created_timestamp': row.get('created_timestamp', '')
                    }
                    qa_pairs.append(qa_pair)
                    
        log.info(f"Read {len(qa_pairs)} Q&A pairs from {LOG_CSV_FILE}")
        return qa_pairs
        
    except Exception as e:
        log.error(f"Error reading Q&A pairs from {LOG_CSV_FILE}: {e}")
        return qa_pairs

def search_questions(query: str, search_type: str = 'contains') -> List[Dict[str, Any]]:
    """
    Search for questions based on a query
    
    Args:
        query: Search query string
        search_type: Type of search ('contains', 'starts_with', 'ends_with', 'exact')
        
    Returns:
        List of matching question dictionaries
    """
    try:
        if not query or not query.strip():
            return []
        
        qa_pairs = read_log_csv()
        query_lower = query.lower().strip()
        results = []
        
        for qa_pair in qa_pairs:
            question_lower = qa_pair['question'].lower()
            
            if search_type == 'contains' and query_lower in question_lower:
                results.append(qa_pair)
            elif search_type == 'starts_with' and question_lower.startswith(query_lower):
                results.append(qa_pair)
            elif search_type == 'ends_with' and question_lower.endswith(query_lower):
                results.append(qa_pair)
            elif search_type == 'exact' and question_lower == query_lower:
                results.append(qa_pair)
        
        log.debug(f"Search '{query}' ({search_type}) returned {len(results)} results")
        return results
    except Exception as e:
        log.error(f"Error searching questions: {e}")
        return []

def get_csv_statistics() -> Dict[str, Any]:
    """
    Get statistics about the CSV file
    
    Returns:
        Dictionary with CSV statistics
    """
    try:
        if not os.path.exists(LOG_CSV_FILE):
            return {
                'total_rows': 0,
                'file_size': 0,
                'themes': [],
                'questions': 0,
                'answers': 0,
                'used_questions': 0,
                'error': 'File does not exist'
            }
        
        qa_pairs = read_log_csv()
        file_size = os.path.getsize(LOG_CSV_FILE)
        
        themes = list(set(qa_pair['theme'] for qa_pair in qa_pairs))
        questions = len([qa for qa in qa_pairs if qa['question']])
        answers = len([qa for qa in qa_pairs if qa['answer']])
        used_questions = len([qa for qa in qa_pairs if qa['is_used']])
        
        stats = {
            'total_rows': len(qa_pairs),
            'file_size': file_size,
            'themes': themes,
            'questions': questions,
            'answers': answers,
            'used_questions': used_questions,
            'theme_count': len(themes)
        }
        
        log.info(f"CSV statistics: {stats['total_rows']} rows, {stats['theme_count']} themes")
        return stats
    except Exception as e:
        log.error(f"Error getting CSV statistics: {e}")
        return {
            'total_rows': 0,
            'file_size': 0,
            'themes': [],
            'questions': 0,
            'answers': 0,
            'used_questions': 0,
            'error': str(e)
        }

def clear_csv_cache() -> None:
    """
    Clear the LRU cache for get_next_image_number
    """
    try:
        get_next_image_number.cache_clear()
        log.debug("CSV cache cleared")
    except Exception as e:
        log.error(f"Error clearing CSV cache: {e}")

# Export main functions for easy access
__all__ = [
    'get_questions_and_styles_from_log',
    'log_single_question',
    'mark_questions_as_used',
    'get_next_image_number',
    'export_questions_to_csv',
    'read_log_csv',
    'search_questions',
    'get_csv_statistics',
    'backup_csv_file',
    'compress_csv_file',
    'validate_csv_file',
    'clear_csv_cache'
]
