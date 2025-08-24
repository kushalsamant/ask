#!/usr/bin/env python3
"""
Style Management Module - Optimized Version 2.0
Enhanced style management with improved performance, caching, and monitoring

This module provides functionality to:
- Retrieve and manage styles from CSV log files
- Get latest styles with intelligent filtering
- Find popular and trending styles by theme
- Calculate style statistics and diversity metrics
- Identify similar styles and underutilized options
- Provide best style recommendations for content generation
- Handle large datasets efficiently with caching

Optimizations:
- Enhanced error handling and input validation
- Performance monitoring and statistics
- LRU caching for frequently accessed data
- Thread-safe operations
- Memory-efficient data processing
- Optimized CSV reading and parsing
- Enhanced style similarity algorithms
- Improved trend analysis

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized)
"""

import os
import logging
import csv
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from functools import wraps, lru_cache
from threading import Lock
from typing import List, Dict, Any, Optional, Tuple
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_style_retrievals': 0,
    'total_statistics_calculations': 0,
    'total_similarity_searches': 0,
    'total_trend_analyses': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'total_time': 0.0,
    'last_reset': time.time()
}
_performance_lock = Lock()

def performance_monitor(func):
    """Decorator to monitor function performance with thread safety"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            with _performance_lock:
                _performance_stats['total_time'] += duration
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            with _performance_lock:
                _performance_stats['total_time'] += duration
            
            raise
    
    return wrapper

def validate_input_parameters(limit: int = 5, theme: str = None, timeframe_days: int = 30) -> Tuple[bool, str]:
    """
    Validate input parameters for style operations
    
    Args:
        limit: Number of items to retrieve
        theme: Theme to filter by
        timeframe_days: Number of days for timeframe analysis
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if limit is not None and (not isinstance(limit, int) or limit < 0):
        return False, "Limit must be a non-negative integer"
    
    if theme is not None and not isinstance(theme, str):
        return False, "Theme must be a string"
    
    if timeframe_days is not None and (not isinstance(timeframe_days, int) or timeframe_days <= 0):
        return False, "Timeframe days must be a positive integer"
    
    return True, ""

def safe_int_conversion(value: str, default: int) -> int:
    """
    Safely convert string to integer with fallback
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        int: Converted value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        log.warning(f"Invalid integer value '{value}', using default {default}")
        return default

def _read_csv_data_safely() -> List[Dict[str, str]]:
    """
    Safely read CSV data with enhanced error handling
    
    Returns:
        List of CSV rows as dictionaries
    """
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist")
            return []
        
        rows = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate required fields
                if 'question_number' in row and 'style' in row:
                    rows.append(row)
                else:
                    log.warning(f"Skipping row with missing required fields: {row}")
        
        return rows
        
    except Exception as e:
        log.error(f"Error reading CSV data: {e}")
        return []

def _parse_style_data(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Parse style data from CSV row with validation
    
    Args:
        row: CSV row dictionary
        
    Returns:
        Parsed style data or None if invalid
    """
    try:
        style = row.get('style', '').strip()
        if not style:
            return None
        
        return {
            'style_name': style,
            'theme': row.get('theme', '').strip(),
            'question_number': safe_int_conversion(row.get('question_number', '0'), 0),
            'created_timestamp': row.get('created_timestamp', ''),
            'question': row.get('question', '').strip(),
            'answer': row.get('answer', '').strip()
        }
        
    except Exception as e:
        log.warning(f"Error parsing style data from row: {e}")
        return None

@performance_monitor
@lru_cache(maxsize=128)
def get_latest_styles_from_log(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the latest styles from log.csv with enhanced caching
    
    Args:
        limit: Maximum number of styles to retrieve
        
    Returns:
        List of style dictionaries
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return []
        
        # Read CSV data
        rows = _read_csv_data_safely()
        if not rows:
            return []
        
        # Filter and parse style data
        style_data = []
        for row in rows:
            parsed_style = _parse_style_data(row)
            if parsed_style:
                style_data.append(parsed_style)
        
        # Sort by question_number (descending) and limit results
        style_data.sort(key=lambda x: x['question_number'], reverse=True)
        result = style_data[:limit]
        
        # Update performance stats
        with _performance_lock:
            _performance_stats['total_style_retrievals'] += 1
        
        log.info(f"Retrieved {len(result)} latest styles from {LOG_CSV_FILE}")
        return result
        
    except Exception as e:
        log.error(f"Error getting latest styles from {LOG_CSV_FILE}: {e}")
        return []

@performance_monitor
def get_latest_styles_for_theme(theme: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Get the latest styles for a specific theme with enhanced filtering
    
    Args:
        theme: Theme to filter by
        limit: Maximum number of styles to retrieve
        
    Returns:
        List of style dictionaries for the theme
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit, theme=theme)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return []
        
        if not theme:
            return []
        
        # Get more styles to filter by theme
        all_styles = get_latest_styles_from_log(limit * 2)
        
        # Filter styles by theme
        theme_styles = [style for style in all_styles if style['theme'] == theme]
        
        # Return the latest ones for this theme
        return theme_styles[:limit]
        
    except Exception as e:
        log.error(f"Error getting latest styles for theme {theme}: {e}")
        return []

@performance_monitor
def get_popular_styles_for_theme(theme: str, limit: int = 5, timeframe_days: int = 30) -> List[Dict[str, Any]]:
    """
    Get the most popular styles for a specific theme with enhanced analysis
    
    Args:
        theme: Theme to analyze
        limit: Maximum number of styles to return
        timeframe_days: Number of days to look back
        
    Returns:
        List of popular styles with counts
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit, theme=theme, timeframe_days=timeframe_days)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return []
        
        if not theme:
            return []
        
        # Read CSV data
        rows = _read_csv_data_safely()
        if not rows:
            return []
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        # Count styles with timeframe filtering
        style_counts = Counter()
        for row in rows:
            if (row.get('theme', '').strip() == theme and 
                row.get('style', '').strip()):
                
                # Check timestamp if available
                timestamp = row.get('created_timestamp', '')
                if timestamp:
                    try:
                        entry_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        if entry_date >= cutoff_date:
                            style_counts[row.get('style', '').strip()] += 1
                    except ValueError:
                        # If timestamp parsing fails, include anyway
                        style_counts[row.get('style', '').strip()] += 1
                else:
                    # If no timestamp, include anyway
                    style_counts[row.get('style', '').strip()] += 1
        
        # Return most popular styles
        return [{'style_name': style, 'count': count} for style, count in style_counts.most_common(limit)]
        
    except Exception as e:
        log.error(f"Error getting popular styles for theme {theme}: {e}")
        return []

@performance_monitor
def get_best_style_for_next_content(target_theme: str, question: str = None, limit: int = 5) -> Optional[Dict[str, Any]]:
    """
    Get the best style for next content generation with enhanced selection logic
    
    Args:
        target_theme: Target theme for content
        question: Optional question context
        limit: Maximum number of styles to consider
        
    Returns:
        Best style dictionary or None
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit, theme=target_theme)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return None
        
        if not target_theme:
            return None
        
        # Get latest styles
        latest_styles = get_latest_styles_from_log(limit)
        if not latest_styles:
            log.info(f"No styles found in {LOG_CSV_FILE} for next content generation")
            return None
        
        # Get configuration from environment variables
        prefer_same_theme = os.getenv('STYLE_PREFER_SAME_THEME', 'true').lower() == 'true'
        prefer_popular = os.getenv('STYLE_PREFER_POPULAR', 'true').lower() == 'true'
        prefer_diverse = os.getenv('STYLE_PREFER_DIVERSE', 'false').lower() == 'true'
        
        # Priority order for style selection
        if prefer_same_theme:
            # First, try to find styles from the same theme
            same_theme_styles = [s for s in latest_styles if s['theme'] == target_theme]
            if same_theme_styles:
                if prefer_popular:
                    # Get popular styles for this theme
                    popular_styles = get_popular_styles_for_theme(target_theme, 3)
                    if popular_styles:
                        # Find the most popular style that's in our latest styles
                        for popular in popular_styles:
                            for style in same_theme_styles:
                                if style['style_name'] == popular['style_name']:
                                    log.info(f"Using popular style from same theme ({target_theme}) for next content")
                                    return style
                
                # Use any style from same theme
                best_style = same_theme_styles[0]  # Latest from same theme
                log.info(f"Using latest style from same theme ({target_theme}) for next content")
                return best_style
        
        if prefer_popular:
            # Look for popular styles from any theme
            all_popular = get_popular_styles_for_theme(target_theme, 5)
            if all_popular:
                # Find the most popular style that's in our latest styles
                for popular in all_popular:
                    for style in latest_styles:
                        if style['style_name'] == popular['style_name']:
                            log.info(f"Using popular style {popular['style_name']} for next content in {target_theme}")
                            return style
        
        if prefer_diverse:
            # Look for diverse styles (less frequently used)
            all_styles = get_latest_styles_from_log(limit * 2)
            style_counts = Counter([s['style_name'] for s in all_styles])
            if style_counts:
                # Find the least used style
                least_used_style = min(style_counts.items(), key=lambda x: x[1])[0]
                for style in latest_styles:
                    if style['style_name'] == least_used_style:
                        log.info(f"Using diverse style {least_used_style} for next content in {target_theme}")
                        return style
        
        # Use the most recent style overall
        best_style = latest_styles[0]  # Most recent overall
        log.info(f"Using latest style {best_style['style_name']} from theme {best_style['theme']} for next content in {target_theme}")
        return best_style
        
    except Exception as e:
        log.error(f"Error getting best style for next content: {e}")
        return None

@performance_monitor
def get_styles_without_content(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get styles that don't have associated content yet with enhanced filtering
    
    Args:
        limit: Maximum number of styles to retrieve
        
    Returns:
        List of styles without content
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return []
        
        # Read CSV data
        rows = _read_csv_data_safely()
        if not rows:
            return []
        
        # Filter styles without content
        styles_without_content = []
        for row in rows:
            style = row.get('style', '').strip()
            question = row.get('question', '').strip()
            answer = row.get('answer', '').strip()
            
            if style and (not question or not answer):
                parsed_style = _parse_style_data(row)
                if parsed_style:
                    styles_without_content.append(parsed_style)
        
        # Sort by question_number (oldest first) and limit
        styles_without_content.sort(key=lambda x: x['question_number'])
        return styles_without_content[:limit]
        
    except Exception as e:
        log.error(f"Error getting styles without content: {e}")
        return []

@performance_monitor
def get_style_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about styles in the log with enhanced metrics
    
    Returns:
        Dictionary with style statistics
    """
    try:
        # Read CSV data
        rows = _read_csv_data_safely()
        if not rows:
            return {
                'total_styles': 0,
                'unique_styles': 0,
                'styles_by_theme': {},
                'most_popular_styles': [],
                'least_used_styles': [],
                'style_diversity_score': 0.0,
                'themes_count': 0,
                'average_styles_per_theme': 0.0
            }
        
        # Initialize statistics
        stats = {
            'total_styles': 0,
            'unique_styles': 0,
            'styles_by_theme': defaultdict(int),
            'style_counts': Counter(),
            'most_popular_styles': [],
            'least_used_styles': [],
            'style_diversity_score': 0.0,
            'themes_count': 0,
            'average_styles_per_theme': 0.0
        }
        
        # Process rows
        for row in rows:
            style = row.get('style', '').strip()
            theme = row.get('theme', '').strip()
            
            if style:
                stats['total_styles'] += 1
                stats['style_counts'][style] += 1
                
                if theme:
                    stats['styles_by_theme'][theme] += 1
        
        # Calculate derived statistics
        stats['unique_styles'] = len(stats['style_counts'])
        stats['themes_count'] = len(stats['styles_by_theme'])
        
        if stats['total_styles'] > 0:
            stats['style_diversity_score'] = stats['unique_styles'] / stats['total_styles']
            stats['average_styles_per_theme'] = stats['total_styles'] / max(stats['themes_count'], 1)
        
        # Get most and least popular styles
        if stats['style_counts']:
            stats['most_popular_styles'] = stats['style_counts'].most_common(5)
            stats['least_used_styles'] = stats['style_counts'].most_common()[-5:]
        
        # Update performance stats
        with _performance_lock:
            _performance_stats['total_statistics_calculations'] += 1
        
        log.info(f"Style statistics calculated: {stats}")
        return stats
        
    except Exception as e:
        log.error(f"Error getting style statistics: {e}")
        return {}

@performance_monitor
def find_similar_styles(style_name: str, theme: str = None, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Find styles similar to the given style name with enhanced similarity algorithm
    
    Args:
        style_name: Style name to find similar styles for
        theme: Optional theme filter
        limit: Maximum number of similar styles to return
        
    Returns:
        List of similar styles
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(limit=limit, theme=theme)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return []
        
        if not style_name:
            return []
        
        # Get more styles to search
        all_styles = get_latest_styles_from_log(limit * 5)
        
        # Enhanced similarity check
        similar_styles = []
        style_lower = style_name.lower()
        style_words = set(style_lower.split())
        
        for style in all_styles:
            if style['style_name'].lower() != style_lower:  # Not the same style
                # Apply theme filter if specified
                if theme and style['theme'] != theme:
                    continue
                
                # Calculate similarity score
                other_style_lower = style['style_name'].lower()
                other_style_words = set(other_style_lower.split())
                
                # Common words
                common_words = style_words & other_style_words
                similarity_score = len(common_words)
                
                # Check for partial matches
                if similarity_score == 0:
                    # Check if one style name contains the other
                    if style_lower in other_style_lower or other_style_lower in style_lower:
                        similarity_score = 1
                
                if similarity_score >= 1:  # At least 1 common word or partial match
                    similar_styles.append({
                        **style,
                        'similarity_score': similarity_score
                    })
        
        # Sort by similarity score (most similar first)
        similar_styles.sort(key=lambda s: s['similarity_score'], reverse=True)
        
        # Update performance stats
        with _performance_lock:
            _performance_stats['total_similarity_searches'] += 1
        
        return similar_styles[:limit]
        
    except Exception as e:
        log.error(f"Error finding similar styles: {e}")
        return []

@performance_monitor
def get_style_trends(theme: str, timeframe_days: int = 30) -> Dict[str, Any]:
    """
    Get style usage trends for a specific theme with enhanced analysis
    
    Args:
        theme: Theme to analyze
        timeframe_days: Number of days to look back
        
    Returns:
        Dictionary with trend analysis
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme=theme, timeframe_days=timeframe_days)
        if not is_valid:
            log.error(f"Invalid input parameters: {error_msg}")
            return {}
        
        if not theme:
            return {}
        
        # Read CSV data
        rows = _read_csv_data_safely()
        if not rows:
            return {}
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        # Filter recent styles
        recent_styles = []
        for row in rows:
            if (row.get('theme', '').strip() == theme and 
                row.get('style', '').strip()):
                
                timestamp = row.get('created_timestamp', '')
                if timestamp:
                    try:
                        entry_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        if entry_date >= cutoff_date:
                            recent_styles.append(row.get('style', '').strip())
                    except ValueError:
                        continue
        
        # Calculate trends
        style_counts = Counter(recent_styles)
        
        trends = {
            'most_popular': style_counts.most_common(5),
            'trending_up': identify_trending_styles(theme, style_counts),
            'underutilized': identify_underutilized_styles(theme, style_counts),
            'total_usage': len(recent_styles),
            'unique_styles': len(style_counts),
            'timeframe_days': timeframe_days,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Update performance stats
        with _performance_lock:
            _performance_stats['total_trend_analyses'] += 1
        
        return trends
        
    except Exception as e:
        log.error(f"Error getting style trends for theme {theme}: {e}")
        return {}

def identify_trending_styles(theme: str, style_counts: Counter) -> List[str]:
    """
    Identify styles that are trending upward with enhanced algorithm
    
    Args:
        theme: Theme being analyzed
        style_counts: Counter of style usage
        
    Returns:
        List of trending style names
    """
    try:
        if not style_counts:
            return []
        
        avg_usage = sum(style_counts.values()) / len(style_counts)
        trending = [style for style, count in style_counts.items() if count > avg_usage * 1.5]
        return trending[:3]
        
    except Exception as e:
        log.error(f"Error identifying trending styles: {e}")
        return []

def identify_underutilized_styles(theme: str, style_counts: Counter) -> List[str]:
    """
    Identify styles that are underutilized with enhanced algorithm
    
    Args:
        theme: Theme being analyzed
        style_counts: Counter of style usage
        
    Returns:
        List of underutilized style names
    """
    try:
        if not style_counts:
            return []
        
        avg_usage = sum(style_counts.values()) / len(style_counts)
        underutilized = [style for style, count in style_counts.items() if count < avg_usage * 0.5]
        return underutilized[:5]
        
    except Exception as e:
        log.error(f"Error identifying underutilized styles: {e}")
        return []

def get_performance_statistics() -> Dict[str, Any]:
    """
    Get performance statistics for the style manager
    
    Returns:
        dict: Performance statistics
    """
    with _performance_lock:
        total_operations = (_performance_stats['total_style_retrievals'] + 
                           _performance_stats['total_statistics_calculations'] + 
                           _performance_stats['total_similarity_searches'] + 
                           _performance_stats['total_trend_analyses'])
        
        return {
            'total_style_retrievals': _performance_stats['total_style_retrievals'],
            'total_statistics_calculations': _performance_stats['total_statistics_calculations'],
            'total_similarity_searches': _performance_stats['total_similarity_searches'],
            'total_trend_analyses': _performance_stats['total_trend_analyses'],
            'cache_hits': _performance_stats['cache_hits'],
            'cache_misses': _performance_stats['cache_misses'],
            'cache_hit_ratio': _performance_stats['cache_hits'] / max(_performance_stats['cache_hits'] + _performance_stats['cache_misses'], 1),
            'total_time': _performance_stats['total_time'],
            'average_time_per_operation': _performance_stats['total_time'] / max(total_operations, 1),
            'last_reset': _performance_stats['last_reset'],
            'module_version': '2.0',
            'optimization_date': '2025-08-24'
        }

def reset_performance_stats():
    """Reset performance statistics with thread safety"""
    global _performance_stats
    with _performance_lock:
        _performance_stats = {
            'total_style_retrievals': 0,
            'total_statistics_calculations': 0,
            'total_similarity_searches': 0,
            'total_trend_analyses': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0,
            'last_reset': time.time()
        }
    log.info("Performance statistics reset")

def validate_environment() -> Dict[str, Any]:
    """
    Validate the environment configuration
    
    Returns:
        dict: Environment validation results
    """
    validation_results = {
        'log_file_exists': os.path.exists(LOG_CSV_FILE),
        'log_file_readable': os.access(LOG_CSV_FILE, os.R_OK) if os.path.exists(LOG_CSV_FILE) else False,
        'environment_variables': {
            'STYLE_PREFER_SAME_THEME': os.getenv('STYLE_PREFER_SAME_THEME', 'true'),
            'STYLE_PREFER_POPULAR': os.getenv('STYLE_PREFER_POPULAR', 'true'),
            'STYLE_PREFER_DIVERSE': os.getenv('STYLE_PREFER_DIVERSE', 'false')
        },
        'performance': {
            'total_operations': _performance_stats['total_style_retrievals'] + 
                               _performance_stats['total_statistics_calculations'] +
                               _performance_stats['total_similarity_searches'] +
                               _performance_stats['total_trend_analyses'],
            'cache_hit_ratio': _performance_stats['cache_hits'] / max(_performance_stats['cache_hits'] + _performance_stats['cache_misses'], 1)
        }
    }
    
    return validation_results

# Export main functions
__all__ = [
    'get_latest_styles_from_log',
    'get_latest_styles_for_theme',
    'get_popular_styles_for_theme',
    'get_best_style_for_next_content',
    'get_styles_without_content',
    'get_style_statistics',
    'find_similar_styles',
    'get_style_trends',
    'identify_trending_styles',
    'identify_underutilized_styles',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
