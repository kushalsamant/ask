#!/usr/bin/env python3
"""
CSV Data Management Module
Handles core CSV operations for research data
"""

import os
import logging
import csv
from datetime import datetime

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
LOG_CSV_FILE = os.getenv('LOG_CSV_FILE', 'log.csv')

def get_questions_and_styles_from_log():
    """Read all questions and styles from log.csv and organize by category"""
    questions_by_category = {}
    styles_by_category = {}
    used_questions = set()

    try:
        if not os.path.exists(LOG_CSV_FILE):
            # Create log.csv with headers if it doesn't exist
            with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['question_number', 'category', 'question', 'question_image', 'style', 'answer', 'answer_image', 'is_used', 'created_timestamp'])
            return questions_by_category, styles_by_category, used_questions

        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)

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

            # Organize questions and styles by category
            for row in rows:
                category = row.get('category', '').strip()
                question = row.get('question', '').strip()
                is_used = row.get('is_used', '').lower() == 'true'
                style = row.get('style', '').strip()

                if category and question:
                    # Organize questions
                    if category not in questions_by_category:
                        questions_by_category[category] = set()
                    questions_by_category[category].add(question)
                    if is_used:
                        used_questions.add(question)

                    # Organize styles
                    if category not in styles_by_category:
                        styles_by_category[category] = set()
                    if style:
                        styles_by_category[category].add(style)

    except Exception as e:
        log.error(f"Error reading from {LOG_CSV_FILE}: {e}")
        raise

    return questions_by_category, styles_by_category, used_questions

def log_single_question(category, question, image_filename, style=None, is_answer=False, mark_as_used=False):
    """Log a single question or answer to log.csv"""
    try:
        # Ensure log.csv exists with proper headers
        if not os.path.exists(LOG_CSV_FILE):
            with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['question_number', 'category', 'question', 'question_image', 'style', 'answer', 'answer_image', 'is_used', 'created_timestamp'])

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
            'category': category,
            'question': question,
            'question_image': image_filename if not is_answer else '',
            'style': style or '',
            'answer': question if is_answer else '',
            'answer_image': image_filename if is_answer else '',
            'is_used': str(mark_as_used).lower(),
            'created_timestamp': datetime.now().isoformat()
        }

        # Add new row
        rows.append(new_row)

        # Write back to file
        with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['question_number', 'category', 'question', 'question_image', 'style', 'answer', 'answer_image', 'is_used', 'created_timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        log.info(f"Logged {'answer' if is_answer else 'question'} for {category}: {question[:50]}...")
        return True

    except Exception as e:
        log.error(f"Error logging question: {e}")
        return False

def mark_questions_as_used(questions_dict):
    """Mark questions as used in log.csv after successful PDF creation"""
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
            category = row.get('category', '').strip()
            question = row.get('question', '').strip()
            
            # Check if this question should be marked as used
            if category in questions_dict and questions_dict[category] == question:
                if row.get('is_used', '').lower() != 'true':
                    row['is_used'] = 'true'
                    questions_marked += 1

        # Write back to file
        with open(LOG_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['question_number', 'category', 'question', 'question_image', 'style', 'answer', 'answer_image', 'is_used', 'created_timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        log.info(f"Marked {questions_marked} questions as used")
        return questions_marked

    except Exception as e:
        log.error(f"Error marking questions as used: {e}")
        return 0

def get_next_image_number():
    """Get the next image number based on existing images in log.csv"""
    try:
        if os.path.exists(LOG_CSV_FILE):
            max_number = 0
            with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check both question and answer image filenames
                    for filename_field in ['question_image', 'answer_image']:
                        if filename_field in row and row[filename_field].strip():
                            # Extract number from filename like "ASK-01-architecture-q.jpg"
                            filename = row[filename_field].strip()
                            if filename.startswith('ASK-') and '-' in filename:
                                try:
                                    # Extract number from "ASK-01-architecture-q.jpg"
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

def export_questions_to_csv(output_filename='questions_export.csv'):
    """Export all questions to a separate CSV file"""
    try:
        questions_by_category, styles_by_category, used_questions = get_questions_and_styles_from_log()
        
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'question', 'is_used', 'available_styles'])
            
            for category, questions in questions_by_category.items():
                for question in questions:
                    is_used = question in used_questions
                    available_styles = ', '.join(styles_by_category.get(category, []))
                    writer.writerow([category, question, is_used, available_styles])
        
        log.info(f"Exported questions to {output_filename}")
        return True
    except Exception as e:
        log.error(f"Error exporting questions: {e}")
        return False

def read_log_csv():
    """Read Q&A pairs from log.csv in format expected by image generation system"""
    qa_pairs = []
    
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist")
            return qa_pairs
            
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row.get('category', '').strip()
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                
                if category and question:
                    qa_pair = {
                        'category': category,
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
