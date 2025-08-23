#!/usr/bin/env python3
"""
Research Answer Management Module
Handles answer retrieval and chaining for question generation
"""

import os
import logging
import csv
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

def get_latest_answers_from_log(limit=5):
    """Get the latest answers from log.csv for generating next questions"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, no answers available")
            return []

        answers = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Filter rows that have answers (non-empty answer field)
            answer_rows = [row for row in rows if row.get('answer', '').strip()]
            
            # Sort by question_number to get the latest ones
            answer_rows.sort(key=lambda x: int(x.get('question_number', 0)), reverse=True)
            
            # Get the latest answers up to the limit
            for row in answer_rows[:limit]:
                answer_data = {
                    'answer_text': row.get('answer', '').strip(),
                    'theme': row.get('theme', '').strip(),
                    'question_number': int(row.get('question_number', 0)),
                    'created_timestamp': row.get('created_timestamp', ''),
                    'style': row.get('style', '').strip()
                }
                answers.append(answer_data)
        
        log.info(f"Retrieved {len(answers)} latest answers from {LOG_CSV_FILE}")
        return answers
        
    except Exception as e:
        log.error(f"Error getting latest answers from {LOG_CSV_FILE}: {e}")
        return []

def get_latest_answer_for_category(theme, limit=3):
    """Get the latest answers for a specific theme from log.csv"""
    try:
        all_answers = get_latest_answers_from_log(limit * 2)  # Get more to filter by theme
        
        # Filter answers by theme
        category_answers = [answer for answer in all_answers if answer['theme'] == theme]
        
        # Return the latest ones for this theme
        return category_answers[:limit]
        
    except Exception as e:
        log.error(f"Error getting latest answers for theme {theme}: {e}")
        return []

def get_best_answer_for_next_question(target_category, limit=5):
    """Get the best answer from log.csv to generate the next question for a target theme"""
    try:
        latest_answers = get_latest_answers_from_log(limit)
        
        if not latest_answers:
            log.info(f"No answers found in {LOG_CSV_FILE} for next question generation")
            return None
        
        # Get configuration from environment variables
        prefer_same_category = os.getenv('ANSWER_PREFER_SAME_CATEGORY', 'true').lower() == 'true'
        
        # Priority order for answer selection:
        # 1. Latest answer from the same theme (if prefer_same_category is true)
        # 2. Latest answer from any theme
        # 3. Most recent answer overall
        
        if prefer_same_category:
            # First, try to find answers from the same theme
            same_category_answers = [b for b in latest_answers if b['theme'] == target_category]
            if same_category_answers:
                best_answer = same_category_answers[0]  # Latest from same theme
                log.info(f"Using latest answer from same theme ({target_category}) for next question")
                return best_answer
        
        # If no same theme answers or prefer_same_category is false, use the most recent answer
        best_answer = latest_answers[0]  # Most recent overall
        log.info(f"Using latest answer from theme {best_answer['theme']} for next question in {target_category}")
        return best_answer
        
    except Exception as e:
        log.error(f"Error getting best answer for next question: {e}")
        return None
