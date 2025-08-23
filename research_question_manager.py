#!/usr/bin/env python3
"""
Research Question Management Module
Handles question retrieval and chaining for answer generation
"""

import os
import logging
import csv
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

def get_latest_questions_from_log(limit=5):
    """Get the latest questions from log.csv for generating next answers"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, no questions available")
            return []

        questions = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Filter rows that have questions (non-empty question field)
            question_rows = [row for row in rows if row.get('question', '').strip()]
            
            # Sort by question_number to get the latest ones
            question_rows.sort(key=lambda x: int(x.get('question_number', 0)), reverse=True)
            
            # Get the latest questions up to the limit
            for row in question_rows[:limit]:
                question_data = {
                    'question_text': row.get('question', '').strip(),
                    'theme': row.get('theme', '').strip(),
                    'question_number': int(row.get('question_number', 0)),
                    'created_timestamp': row.get('created_timestamp', ''),
                    'style': row.get('style', '').strip(),
                    'is_used': row.get('is_used', '').lower() == 'true'
                }
                questions.append(question_data)
        
        log.info(f"Retrieved {len(questions)} latest questions from {LOG_CSV_FILE}")
        return questions
        
    except Exception as e:
        log.error(f"Error getting latest questions from {LOG_CSV_FILE}: {e}")
        return []

def get_latest_questions_for_theme(theme, limit=3):
    """Get the latest questions for a specific theme from log.csv"""
    try:
        all_questions = get_latest_questions_from_log(limit * 2)  # Get more to filter by theme
        
        # Filter questions by theme
        theme_questions = [question for question in all_questions if question['theme'] == theme]
        
        # Return the latest ones for this theme
        return theme_questions[:limit]
        
    except Exception as e:
        log.error(f"Error getting latest questions for theme {theme}: {e}")
        return []

def get_unused_questions_for_theme(theme, limit=5):
    """Get unused questions for a specific theme from log.csv"""
    try:
        all_questions = get_latest_questions_from_log(limit * 3)  # Get more to filter
        
        # Filter questions by theme and unused status
        unused_questions = [
            question for question in all_questions 
            if question['theme'] == theme and not question['is_used']
        ]
        
        # Return the latest unused ones for this theme
        return unused_questions[:limit]
        
    except Exception as e:
        log.error(f"Error getting unused questions for theme {theme}: {e}")
        return []

def get_best_question_for_next_answer(target_theme, limit=5):
    """Get the best question from log.csv to generate the next answer for a target theme"""
    try:
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
            same_theme_questions = [q for q in latest_questions if q['theme'] == target_theme]
            if same_theme_questions:
                if prefer_unused:
                    # Look for unused questions from same theme
                    unused_same_theme = [q for q in same_theme_questions if not q['is_used']]
                    if unused_same_theme:
                        best_question = unused_same_theme[0]  # Latest unused from same theme
                        log.info(f"Using latest unused question from same theme ({target_theme}) for next answer")
                        return best_question
                
                # Use any question from same theme
                best_question = same_theme_questions[0]  # Latest from same theme
                log.info(f"Using latest question from same theme ({target_theme}) for next answer")
                return best_question
        
        if prefer_unused:
            # Look for unused questions from any theme
            unused_questions = [q for q in latest_questions if not q['is_used']]
            if unused_questions:
                best_question = unused_questions[0]  # Latest unused overall
                log.info(f"Using latest unused question from theme {best_question['theme']} for next answer in {target_theme}")
                return best_question
        
        # Use the most recent question overall
        best_question = latest_questions[0]  # Most recent overall
        log.info(f"Using latest question from theme {best_question['theme']} for next answer in {target_theme}")
        return best_question
        
    except Exception as e:
        log.error(f"Error getting best question for next answer: {e}")
        return None

def get_questions_without_answers(limit=10):
    """Get questions that don't have answers yet"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, no questions available")
            return []

        questions_without_answers = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
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
                    questions_without_answers.append(question_data)
            
            # Sort by question_number to get the oldest ones first
            questions_without_answers.sort(key=lambda x: x['question_number'])
            
            # Return up to the limit
            return questions_without_answers[:limit]
        
    except Exception as e:
        log.error(f"Error getting questions without answers: {e}")
        return []

def get_question_statistics():
    """Get statistics about questions in the log"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            return {
                'total_questions': 0,
                'used_questions': 0,
                'unused_questions': 0,
                'questions_with_answers': 0,
                'questions_without_answers': 0,
                'questions_by_theme': {}
            }

        stats = {
            'total_questions': 0,
            'used_questions': 0,
            'unused_questions': 0,
            'questions_with_answers': 0,
            'questions_without_answers': 0,
            'questions_by_theme': {}
        }
        
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            for row in rows:
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                theme = row.get('theme', '').strip()
                is_used = row.get('is_used', '').lower() == 'true'
                
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
        
        log.info(f"Question statistics: {stats}")
        return stats
        
    except Exception as e:
        log.error(f"Error getting question statistics: {e}")
        return {}

def find_similar_questions(question_text, theme=None, limit=3):
    """Find questions similar to the given question text"""
    try:
        all_questions = get_latest_questions_from_log(limit * 5)  # Get more to search
        
        # Simple similarity check (can be enhanced with more sophisticated algorithms)
        similar_questions = []
        question_lower = question_text.lower()
        
        for question in all_questions:
            if question['question_text'].lower() != question_lower:  # Not the same question
                # Check for common words
                common_words = set(question_lower.split()) & set(question['question_text'].lower().split())
                if len(common_words) >= 2:  # At least 2 common words
                    similar_questions.append(question)
        
        # Sort by number of common words (most similar first)
        similar_questions.sort(key=lambda q: len(set(question_lower.split()) & set(q['question_text'].lower().split())), reverse=True)
        
        return similar_questions[:limit]
        
    except Exception as e:
        log.error(f"Error finding similar questions: {e}")
        return []
