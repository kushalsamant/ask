#!/usr/bin/env python3
"""
Volume Manager Module
Handles automatic volume number incrementing based on Q&A pair count
"""

import os
import logging
import csv
from typing import Tuple

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
LOG_CSV_FILE = os.getenv('LOG_CSV_FILE', 'log.csv')
QA_PAIRS_PER_VOLUME = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
DEFAULT_VOLUME_NUMBER = int(os.getenv('IMAGE_VOLUME_NUMBER', '1'))

def get_current_volume_info() -> Tuple[int, int, int]:
    """
    Get current volume information based on log.csv
    
    Returns:
        Tuple[int, int, int]: (current_volume, qa_pairs_in_current_volume, total_qa_pairs)
    """
    try:
        # Read environment variable at runtime
        log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        default_volume_number = int(os.getenv('IMAGE_VOLUME_NUMBER', '1'))
        
        if not os.path.exists(log_csv_file):
            log.info(f"{log_csv_file} does not exist, starting with volume {default_volume_number}")
            return default_volume_number, 0, 0
        
        # Count total Q&A pairs (rows with both question and answer)
        total_qa_pairs = 0
        with open(log_csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if this row has both question and answer (complete Q&A pair)
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                if question and answer:
                    total_qa_pairs += 1
                    log.debug(f"Found complete Q&A pair: '{question[:50]}...' -> '{answer[:50]}...'")
        
        log.debug(f"Total complete Q&A pairs found: {total_qa_pairs}")
        log.info(f"Reading from {log_csv_file}")
        
        # Calculate current volume and pairs in current volume
        if total_qa_pairs == 0:
            current_volume = default_volume_number
            qa_pairs_in_current_volume = 0
        else:
            current_volume = ((total_qa_pairs - 1) // qa_pairs_per_volume) + 1
            qa_pairs_in_current_volume = total_qa_pairs % qa_pairs_per_volume
            if qa_pairs_in_current_volume == 0:
                qa_pairs_in_current_volume = qa_pairs_per_volume
        
        log.info(f"Volume info: Volume {current_volume}, {qa_pairs_in_current_volume}/{qa_pairs_per_volume} pairs in current volume, {total_qa_pairs} total pairs")
        return current_volume, qa_pairs_in_current_volume, total_qa_pairs
        
    except Exception as e:
        log.error(f"Error getting current volume info: {e}")
        return int(os.getenv('IMAGE_VOLUME_NUMBER', '1')), 0, 0

def should_increment_volume() -> bool:
    """
    Check if volume should be incremented after adding a new Q&A pair
    
    Returns:
        bool: True if volume should be incremented
    """
    try:
        current_volume, qa_pairs_in_current_volume, total_qa_pairs = get_current_volume_info()
        
        # Volume should increment if current volume is exactly at the limit
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        should_increment = qa_pairs_in_current_volume == qa_pairs_per_volume
        
        if should_increment:
            log.info(f"Volume {current_volume} is complete ({qa_pairs_per_volume} pairs), will increment to volume {current_volume + 1}")
        else:
            log.info(f"Volume {current_volume} has {qa_pairs_in_current_volume}/{qa_pairs_per_volume} pairs, no increment needed")
        
        return should_increment
        
    except Exception as e:
        log.error(f"Error checking volume increment: {e}")
        return False

def get_next_volume_number() -> int:
    """
    Get the next volume number that should be used
    
    Returns:
        int: Next volume number
    """
    try:
        current_volume, qa_pairs_in_current_volume, total_qa_pairs = get_current_volume_info()
        
        # If current volume is full, next volume is current + 1
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        if qa_pairs_in_current_volume == qa_pairs_per_volume:
            next_volume = current_volume + 1
        else:
            next_volume = current_volume
        
        log.info(f"Next volume number: {next_volume}")
        return next_volume
        
    except Exception as e:
        log.error(f"Error getting next volume number: {e}")
        return int(os.getenv('IMAGE_VOLUME_NUMBER', '1'))

def get_next_image_number() -> int:
    """
    Get the next image number that should be used
    
    Returns:
        int: Next image number (starts from 1)
    """
    try:
        log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
        
        if not os.path.exists(log_csv_file):
            log.info(f"{log_csv_file} does not exist, starting with image number 1")
            return 1
        
        # Count total images (rows with question_image or answer_image)
        total_images = 0
        with open(log_csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if this row has question or answer images
                question_image = row.get('question_image', '').strip()
                answer_image = row.get('answer_image', '').strip()
                if question_image:
                    total_images += 1
                    log.debug(f"Found question image: {question_image}")
                if answer_image:
                    total_images += 1
                    log.debug(f"Found answer image: {answer_image}")
        
        next_image_number = total_images + 1
        log.info(f"Next image number: {next_image_number} (total images so far: {total_images})")
        return next_image_number
        
    except Exception as e:
        log.error(f"Error getting next image number: {e}")
        return 1

def get_next_question_image_number() -> int:
    """
    Get the next question image number that should be used
    
    Returns:
        int: Next question image number (odd numbers: 1, 3, 5, 7...)
    """
    try:
        log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
        
        if not os.path.exists(log_csv_file):
            log.info(f"{log_csv_file} does not exist, starting with question image number 1")
            return 1
        
        # Count total question images
        total_question_images = 0
        with open(log_csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                question_image = row.get('question_image', '').strip()
                if question_image:
                    total_question_images += 1
                    log.debug(f"Found question image: {question_image}")
        
        # Question images are odd numbers: 1, 3, 5, 7...
        next_question_image_number = (total_question_images * 2) + 1
        log.info(f"Next question image number: {next_question_image_number} (total question images so far: {total_question_images})")
        return next_question_image_number
        
    except Exception as e:
        log.error(f"Error getting next question image number: {e}")
        return 1

def get_next_answer_image_number() -> int:
    """
    Get the next answer image number that should be used
    
    Returns:
        int: Next answer image number (even numbers: 2, 4, 6, 8...)
    """
    try:
        log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
        
        if not os.path.exists(log_csv_file):
            log.info(f"{log_csv_file} does not exist, starting with answer image number 2")
            return 2
        
        # Count total answer images
        total_answer_images = 0
        with open(log_csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                answer_image = row.get('answer_image', '').strip()
                if answer_image:
                    total_answer_images += 1
                    log.debug(f"Found answer image: {answer_image}")
        
        # Answer images are even numbers: 2, 4, 6, 8...
        next_answer_image_number = (total_answer_images * 2) + 2
        log.info(f"Next answer image number: {next_answer_image_number} (total answer images so far: {total_answer_images})")
        return next_answer_image_number
        
    except Exception as e:
        log.error(f"Error getting next answer image number: {e}")
        return 2

def get_volume_progress() -> dict:
    """
    Get detailed volume progress information
    
    Returns:
        dict: Volume progress information
    """
    try:
        current_volume, qa_pairs_in_current_volume, total_qa_pairs = get_current_volume_info()
        
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        progress = {
            'current_volume': current_volume,
            'qa_pairs_in_current_volume': qa_pairs_in_current_volume,
            'total_qa_pairs': total_qa_pairs,
            'qa_pairs_per_volume': qa_pairs_per_volume,
            'volume_progress_percentage': (qa_pairs_in_current_volume / qa_pairs_per_volume) * 100,
            'pairs_until_next_volume': qa_pairs_per_volume - qa_pairs_in_current_volume,
            'should_increment_volume': should_increment_volume()
        }
        
        return progress
        
    except Exception as e:
        log.error(f"Error getting volume progress: {e}")
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        default_volume_number = int(os.getenv('IMAGE_VOLUME_NUMBER', '1'))
        return {
            'current_volume': default_volume_number,
            'qa_pairs_in_current_volume': 0,
            'total_qa_pairs': 0,
            'qa_pairs_per_volume': qa_pairs_per_volume,
            'volume_progress_percentage': 0,
            'pairs_until_next_volume': qa_pairs_per_volume,
            'should_increment_volume': False
        }

def get_image_progress() -> dict:
    """
    Get detailed image progress information
    
    Returns:
        dict: Image progress information
    """
    try:
        log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
        
        if not os.path.exists(log_csv_file):
            return {
                'total_images': 0,
                'next_image_number': 1,
                'images_in_current_volume': 0
            }
        
        # Count total images and get volume info
        total_images = 0
        with open(log_csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                question_image = row.get('question_image', '').strip()
                answer_image = row.get('answer_image', '').strip()
                if question_image:
                    total_images += 1
                if answer_image:
                    total_images += 1
        
        current_volume, qa_pairs_in_current_volume, total_qa_pairs = get_current_volume_info()
        qa_pairs_per_volume = int(os.getenv('QA_PAIRS_PER_VOLUME', '100'))
        
        # Calculate images in current volume
        images_in_current_volume = total_images % qa_pairs_per_volume
        if images_in_current_volume == 0 and total_images > 0:
            images_in_current_volume = qa_pairs_per_volume
        
        progress = {
            'total_images': total_images,
            'next_image_number': total_images + 1,
            'images_in_current_volume': images_in_current_volume,
            'current_volume': current_volume,
            'qa_pairs_per_volume': qa_pairs_per_volume
        }
        
        return progress
        
    except Exception as e:
        log.error(f"Error getting image progress: {e}")
        return {
            'total_images': 0,
            'next_image_number': 1,
            'images_in_current_volume': 0,
            'current_volume': 1,
            'qa_pairs_per_volume': 100
        }

def log_volume_info():
    """Log current volume information for debugging"""
    try:
        progress = get_volume_progress()
        
        log.info("=" * 50)
        log.info("VOLUME PROGRESS INFORMATION")
        log.info("=" * 50)
        log.info(f"Current Volume: {progress['current_volume']}")
        log.info(f"Q&A Pairs in Current Volume: {progress['qa_pairs_in_current_volume']}/{progress['qa_pairs_per_volume']}")
        log.info(f"Total Q&A Pairs: {progress['total_qa_pairs']}")
        log.info(f"Volume Progress: {progress['volume_progress_percentage']:.1f}%")
        log.info(f"Pairs Until Next Volume: {progress['pairs_until_next_volume']}")
        log.info(f"Should Increment Volume: {progress['should_increment_volume']}")
        log.info("=" * 50)
        
    except Exception as e:
        log.error(f"Error logging volume info: {e}")
