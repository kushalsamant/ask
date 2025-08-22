#!/usr/bin/env python3
"""
Research Statistics Module
Handles statistics and analytics for research data
"""

import logging
from research_csv_manager import get_questions_and_styles_from_log

# Setup logging
log = logging.getLogger(__name__)

def get_questions_by_category(category, limit=None):
    """Get questions for a specific category"""
    try:
        questions_by_category, _, used_questions = get_questions_and_styles_from_log()
        
        if category in questions_by_category:
            questions = list(questions_by_category[category])
            # Filter out used questions
            available_questions = [q for q in questions if q not in used_questions]
            
            if limit:
                return available_questions[:limit]
            return available_questions
        else:
            return []
    except Exception as e:
        log.error(f"Error getting questions for category {category}: {e}")
        return []

def get_used_questions_count():
    """Get count of used questions"""
    try:
        _, _, used_questions = get_questions_and_styles_from_log()
        return len(used_questions)
    except Exception as e:
        log.error(f"Error getting used questions count: {e}")
        return 0

def get_total_questions_count():
    """Get total count of questions"""
    try:
        questions_by_category, _, _ = get_questions_and_styles_from_log()
        total = sum(len(questions) for questions in questions_by_category.values())
        return total
    except Exception as e:
        log.error(f"Error getting total questions count: {e}")
        return 0

def get_questions_statistics():
    """Get comprehensive statistics about questions"""
    try:
        questions_by_category, styles_by_category, used_questions = get_questions_and_styles_from_log()
        
        stats = {
            'total_categories': len(questions_by_category),
            'total_questions': sum(len(questions) for questions in questions_by_category.values()),
            'used_questions': len(used_questions),
            'available_questions': sum(len(questions) for questions in questions_by_category.values()) - len(used_questions),
            'categories_with_questions': {category: len(questions) for category, questions in questions_by_category.items()},
            'total_styles': sum(len(styles) for styles in styles_by_category.values()),
            'categories_with_styles': {category: len(styles) for category, styles in styles_by_category.items()}
        }
        
        return stats
    except Exception as e:
        log.error(f"Error getting questions statistics: {e}")
        return {}
