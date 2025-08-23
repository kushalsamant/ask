#!/usr/bin/env python3
"""
Style Management Module
Handles comprehensive style management, retrieval, and chaining for research content
"""

import os
import logging
import csv
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

def get_latest_styles_from_log(limit=5):
    """Get the latest styles from log.csv for generating next content"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, no styles available")
            return []

        styles = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Filter rows that have styles (non-empty style field)
            style_rows = [row for row in rows if row.get('style', '').strip()]
            
            # Sort by question_number to get the latest ones
            style_rows.sort(key=lambda x: int(x.get('question_number', 0)), reverse=True)
            
            # Get the latest styles up to the limit
            for row in style_rows[:limit]:
                style_data = {
                    'style_name': row.get('style', '').strip(),
                    'theme': row.get('theme', '').strip(),
                    'question_number': int(row.get('question_number', 0)),
                    'created_timestamp': row.get('created_timestamp', ''),
                    'question': row.get('question', '').strip(),
                    'answer': row.get('answer', '').strip()
                }
                styles.append(style_data)
        
        log.info(f"Retrieved {len(styles)} latest styles from {LOG_CSV_FILE}")
        return styles
        
    except Exception as e:
        log.error(f"Error getting latest styles from {LOG_CSV_FILE}: {e}")
        return []

def get_latest_styles_for_theme(theme, limit=3):
    """Get the latest styles for a specific theme from log.csv"""
    try:
        all_styles = get_latest_styles_from_log(limit * 2)  # Get more to filter by theme
        
        # Filter styles by theme
        theme_styles = [style for style in all_styles if style['theme'] == theme]
        
        # Return the latest ones for this theme
        return theme_styles[:limit]
        
    except Exception as e:
        log.error(f"Error getting latest styles for theme {theme}: {e}")
        return []

def get_popular_styles_for_theme(theme, limit=5, timeframe_days=30):
    """Get the most popular styles for a specific theme"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            return []

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        style_counts = Counter()
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
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
                        except:
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

def get_best_style_for_next_content(target_theme, question=None, limit=5):
    """Get the best style from log.csv to generate the next content for a target theme"""
    try:
        latest_styles = get_latest_styles_from_log(limit)
        
        if not latest_styles:
            log.info(f"No styles found in {LOG_CSV_FILE} for next content generation")
            return None
        
        # Get configuration from environment variables
        prefer_same_theme = os.getenv('STYLE_PREFER_SAME_THEME', 'true').lower() == 'true'
        prefer_popular = os.getenv('STYLE_PREFER_POPULAR', 'true').lower() == 'true'
        prefer_diverse = os.getenv('STYLE_PREFER_DIVERSE', 'false').lower() == 'true'
        
        # Priority order for style selection:
        # 1. Popular style from the same theme (if prefer_same_theme and prefer_popular are true)
        # 2. Latest style from the same theme (if prefer_same_theme is true)
        # 3. Popular style from any theme (if prefer_popular is true)
        # 4. Diverse style from any theme (if prefer_diverse is true)
        # 5. Latest style from any theme
        
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

def get_styles_without_content(limit=10):
    """Get styles that don't have associated content yet"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, no styles available")
            return []

        styles_without_content = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Filter rows that have styles but no questions or answers
            for row in rows:
                style = row.get('style', '').strip()
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                
                if style and (not question or not answer):
                    style_data = {
                        'style_name': style,
                        'theme': row.get('theme', '').strip(),
                        'question_number': int(row.get('question_number', 0)),
                        'created_timestamp': row.get('created_timestamp', ''),
                        'question': question,
                        'answer': answer
                    }
                    styles_without_content.append(style_data)
            
            # Sort by question_number to get the oldest ones first
            styles_without_content.sort(key=lambda x: x['question_number'])
            
            # Return up to the limit
            return styles_without_content[:limit]
        
    except Exception as e:
        log.error(f"Error getting styles without content: {e}")
        return []

def get_style_statistics():
    """Get statistics about styles in the log"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            return {
                'total_styles': 0,
                'unique_styles': 0,
                'styles_by_theme': {},
                'most_popular_styles': [],
                'least_used_styles': [],
                'style_diversity_score': 0.0
            }

        stats = {
            'total_styles': 0,
            'unique_styles': 0,
            'styles_by_theme': defaultdict(int),
            'style_counts': Counter(),
            'most_popular_styles': [],
            'least_used_styles': [],
            'style_diversity_score': 0.0
        }
        
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
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
        stats['most_popular_styles'] = stats['style_counts'].most_common(5)
        stats['least_used_styles'] = stats['style_counts'].most_common()[-5:]
        
        # Calculate diversity score (0-1, higher = more diverse)
        if stats['total_styles'] > 0:
            stats['style_diversity_score'] = stats['unique_styles'] / stats['total_styles']
        
        log.info(f"Style statistics: {stats}")
        return stats
        
    except Exception as e:
        log.error(f"Error getting style statistics: {e}")
        return {}

def find_similar_styles(style_name, theme=None, limit=3):
    """Find styles similar to the given style name"""
    try:
        all_styles = get_latest_styles_from_log(limit * 5)  # Get more to search
        
        # Simple similarity check (can be enhanced with more sophisticated algorithms)
        similar_styles = []
        style_lower = style_name.lower()
        
        for style in all_styles:
            if style['style_name'].lower() != style_lower:  # Not the same style
                # Check for common words
                common_words = set(style_lower.split()) & set(style['style_name'].lower().split())
                if len(common_words) >= 1:  # At least 1 common word
                    similar_styles.append(style)
        
        # Sort by number of common words (most similar first)
        similar_styles.sort(key=lambda s: len(set(style_lower.split()) & set(s['style_name'].lower().split())), reverse=True)
        
        return similar_styles[:limit]
        
    except Exception as e:
        log.error(f"Error finding similar styles: {e}")
        return []

def get_style_trends(theme, timeframe_days=30):
    """Get style usage trends for a specific theme"""
    try:
        if not os.path.exists(LOG_CSV_FILE):
            return {}

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        recent_styles = []
        with open(LOG_CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            for row in rows:
                if (row.get('theme', '').strip() == theme and 
                    row.get('style', '').strip()):
                    
                    timestamp = row.get('created_timestamp', '')
                    if timestamp:
                        try:
                            entry_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                            if entry_date >= cutoff_date:
                                recent_styles.append(row.get('style', '').strip())
                        except:
                            continue
        
        # Calculate trends
        style_counts = Counter(recent_styles)
        
        trends = {
            'most_popular': style_counts.most_common(5),
            'trending_up': identify_trending_styles(theme, style_counts),
            'underutilized': identify_underutilized_styles(theme, style_counts),
            'total_usage': len(recent_styles),
            'unique_styles': len(style_counts)
        }
        
        return trends
        
    except Exception as e:
        log.error(f"Error getting style trends for theme {theme}: {e}")
        return {}

def identify_trending_styles(theme, style_counts):
    """Identify styles that are trending upward"""
    if not style_counts:
        return []
    
    avg_usage = sum(style_counts.values()) / len(style_counts)
    trending = [style for style, count in style_counts.items() if count > avg_usage * 1.5]
    return trending[:3]

def identify_underutilized_styles(theme, style_counts):
    """Identify styles that are underutilized"""
    # This would need to be enhanced with a complete style list for the theme
    # For now, return styles with low usage
    if not style_counts:
        return []
    
    avg_usage = sum(style_counts.values()) / len(style_counts)
    underutilized = [style for style, count in style_counts.items() if count < avg_usage * 0.5]
    return underutilized[:5]
