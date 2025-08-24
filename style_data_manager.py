#!/usr/bin/env python3
"""
Style Data Management Module - Optimized Version 2.0
Handles architectural style data, characteristics, and base style definitions with enhanced performance

This module provides functionality to:
- Manage comprehensive architectural style data across multiple categories
- Provide style characteristics and metadata
- Track style usage trends and patterns
- Load and analyze historical style data from CSV files
- Support performance monitoring and caching
- Handle data validation and error recovery

Optimizations:
- Enhanced data structures and caching
- Performance monitoring and statistics
- Better error handling and validation
- Memory-efficient operations
- Thread-safe operations
- Improved CSV loading and parsing
- Enhanced style characteristics database

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 2.0 (Heavily Optimized)
"""

import os
import logging
import csv
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
from functools import wraps, lru_cache
from threading import Lock

# Setup logging
log = logging.getLogger(__name__)

# Performance monitoring
_performance_stats = {
    'total_style_queries': 0,
    'total_characteristics_queries': 0,
    'total_trend_queries': 0,
    'csv_loads': 0,
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

def validate_input_parameters(theme: str, style: str = None) -> Tuple[bool, str]:
    """
    Validate input parameters for style data operations
    
    Args:
        theme: Theme/category to validate
        style: Style name to validate (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not theme or not isinstance(theme, str) or not theme.strip():
        return False, "Theme must be a non-empty string"
    
    if style is not None and (not isinstance(style, str) or not style.strip()):
        return False, "Style must be a string or None"
    
    # Check for potentially harmful characters
    invalid_chars = ['<', '>', '"', "'", '\\', '/', '|', ':', '*', '?']
    if any(char in theme for char in invalid_chars):
        return False, "Theme contains invalid characters"
    
    if style and any(char in style for char in invalid_chars):
        return False, "Style contains invalid characters"
    
    return True, ""

class StyleDataManager:
    """Manages architectural style data and characteristics with enhanced performance"""

    def __init__(self):
        # Enhanced base styles with more comprehensive data
        self.base_styles = {
            'architecture': [
                'Modern', 'Contemporary', 'Classical', 'Minimalist', 'Brutalist', 'Art Deco', 'Gothic', 'Renaissance',
                'Baroque', 'Neoclassical', 'Victorian', 'Bauhaus', 'International Style', 'Postmodern', 'Deconstructivist',
                'High-Tech', 'Organic', 'Sustainable', 'Parametric', 'Biomimetic', 'Futuristic', 'Vernacular', 'Regional',
                'Tropical', 'Mediterranean', 'Scandinavian', 'Japanese', 'Chinese', 'Islamic', 'African', 'Colonial',
                'Industrial', 'Expressionist', 'Constructivist', 'Art Nouveau', 'Beaux-Arts', 'Palladian', 'Georgian',
                'Federal', 'Greek Revival', 'Romanesque', 'Byzantine', 'Moorish', 'Maya', 'Aztec', 'Incan'
            ],
            'construction': [
                'Industrial', 'Modern', 'Sustainable', 'Innovative', 'Prefabricated', 'Modular', 'Steel Frame', 'Concrete',
                'Timber Frame', 'Masonry', 'Glass and Steel', 'Composite', '3D Printed', 'Robotic', 'Smart Construction',
                'Green Building', 'Passive House', 'Net Zero', 'Circular Economy', 'Biomimetic', 'Adaptive', 'Resilient',
                'Disaster Resistant', 'Seismic', 'Hurricane Resistant', 'Fire Resistant', 'Acoustic', 'Thermal', 'Structural', 'Geotechnical',
                'Mass Timber', 'Cross-Laminated Timber', 'Engineered Wood', 'Bamboo', 'Hempcrete', 'Rammed Earth', 'Straw Bale',
                'Cob', 'Adobe', 'Stone', 'Brick', 'Block', 'Insulated Concrete Forms', 'Structural Insulated Panels'
            ],
            'design': [
                'Contemporary', 'Modern', 'Minimalist', 'Eclectic', 'Scandinavian', 'Japanese', 'Industrial', 'Bohemian',
                'Mid-Century Modern', 'Art Nouveau', 'Art Deco', 'Victorian', 'Rustic', 'Coastal', 'Urban', 'Tropical',
                'Mediterranean', 'Moroccan', 'Asian', 'Nordic', 'Industrial Chic', 'Vintage', 'Retro', 'Futuristic',
                'Sustainable', 'Biophilic', 'Wellness', 'Smart Design', 'Universal', 'Inclusive', 'Accessible', 'Ergonomic',
                'Human-Centered', 'Emotional', 'Sensory', 'Multisensory', 'Interactive', 'Adaptive', 'Responsive', 'Dynamic'
            ],
            'engineering': [
                'Modern', 'Industrial', 'Technical', 'Innovative', 'Structural', 'Mechanical', 'Electrical', 'Civil',
                'Environmental', 'Transportation', 'Geotechnical', 'Hydraulic', 'Aerospace', 'Biomedical', 'Robotics',
                'Automation', 'Smart Systems', 'IoT', 'AI-Integrated', 'Sustainable', 'Resilient', 'Adaptive', 'Modular',
                'Prefabricated', '3D Printed', 'Digital Twin', 'BIM', 'Parametric', 'Computational', 'Generative',
                'Biomimetic', 'Bio-Inspired', 'Nature-Based', 'Circular', 'Regenerative', 'Carbon-Neutral', 'Zero-Waste',
                'Energy-Efficient', 'Passive', 'Active', 'Hybrid', 'Integrated', 'Holistic', 'Systemic'
            ],
            'interiors': [
                'Contemporary', 'Modern', 'Minimalist', 'Luxury', 'Scandinavian', 'Japanese', 'Industrial', 'Bohemian',
                'Mid-Century Modern', 'Art Deco', 'Victorian', 'Rustic', 'Coastal', 'Urban', 'Tropical', 'Mediterranean',
                'Moroccan', 'Asian', 'Nordic', 'Industrial Chic', 'Vintage', 'Retro', 'Futuristic', 'Sustainable',
                'Biophilic', 'Wellness', 'Smart Home', 'Universal Design', 'Inclusive', 'Accessible', 'Ergonomic',
                'Therapeutic', 'Healing', 'Calming', 'Stimulating', 'Creative', 'Productive', 'Social', 'Private',
                'Flexible', 'Adaptable', 'Multifunctional', 'Space-Efficient', 'Storage-Optimized', 'Light-Optimized'
            ],
            'marketing': [
                'Modern', 'Contemporary', 'Professional', 'Creative', 'Digital', 'Social Media', 'Brand Identity',
                'Visual Communication', 'Typography', 'Color Psychology', 'User Experience', 'Interactive', 'Immersive',
                'Storytelling', 'Content Marketing', 'Influencer', 'Viral', 'Authentic', 'Transparent', 'Sustainable',
                'Socially Conscious', 'Inclusive', 'Diverse', 'Accessible', 'Mobile-First', 'Omnichannel', 'Data-Driven',
                'Personalized', 'Experiential', 'Emotional', 'Memorable', 'Engaging', 'Conversational', 'Human-Centered',
                'Empathetic', 'Trust-Building', 'Relationship-Focused', 'Community-Oriented', 'Purpose-Driven'
            ],
            'planning': [
                'Modern', 'Sustainable', 'Urban', 'Contemporary', 'Smart City', 'Green Infrastructure', 'Transit-Oriented',
                'Mixed-Use', 'Walkable', 'Bike-Friendly', 'Resilient', 'Adaptive', 'Inclusive', 'Equitable', 'Accessible',
                'Healthy', 'Wellness', 'Biophilic', 'Circular', 'Regenerative', 'Carbon Neutral', 'Zero Waste',
                'Community-Centered', 'Participatory', 'Data-Driven', 'Digital Twin', '15-Minute City', 'Garden City',
                'New Urbanism', 'Traditional Neighborhood', 'Compact', 'Dense', 'Connected', 'Integrated', 'Holistic',
                'Systemic', 'Place-Based', 'Context-Sensitive', 'Culturally Responsive', 'Historically Informed'
            ],
            'urbanism': [
                'Modern', 'Sustainable', 'Urban', 'Contemporary', 'Smart City', 'Green Infrastructure', 'Transit-Oriented',
                'Mixed-Use', 'Walkable', 'Bike-Friendly', 'Resilient', 'Adaptive', 'Inclusive', 'Equitable', 'Accessible',
                'Healthy', 'Wellness', 'Biophilic', 'Circular', 'Regenerative', 'Carbon Neutral', 'Zero Waste',
                'Community-Centered', 'Participatory', 'Data-Driven', 'Digital Twin', '15-Minute City', 'Garden City',
                'New Urbanism', 'Traditional Neighborhood', 'Compact', 'Dense', 'Connected', 'Integrated', 'Holistic',
                'Systemic', 'Place-Based', 'Context-Sensitive', 'Culturally Responsive', 'Historically Informed',
                'Climate-Responsive', 'Disaster-Resilient', 'Socially Just', 'Economically Viable', 'Environmentally Sound'
            ]
        }

        # Enhanced style characteristics with more detailed metadata
        self.style_characteristics = {
            'Modern': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'},
            'Contemporary': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'},
            'Classical': {'period': 'traditional', 'complexity': 'high', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'high'},
            'Minimalist': {'period': 'contemporary', 'complexity': 'low', 'innovation': 'medium', 'sustainability': 'high', 'popularity': 'high'},
            'Brutalist': {'period': 'modern', 'complexity': 'high', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'medium'},
            'Art Deco': {'period': 'modern', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'low', 'popularity': 'medium'},
            'Gothic': {'period': 'traditional', 'complexity': 'very_high', 'innovation': 'low', 'sustainability': 'low', 'popularity': 'medium'},
            'Renaissance': {'period': 'traditional', 'complexity': 'very_high', 'innovation': 'low', 'sustainability': 'low', 'popularity': 'medium'},
            'Baroque': {'period': 'traditional', 'complexity': 'very_high', 'innovation': 'low', 'sustainability': 'low', 'popularity': 'medium'},
            'Neoclassical': {'period': 'traditional', 'complexity': 'high', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'high'},
            'Victorian': {'period': 'traditional', 'complexity': 'high', 'innovation': 'low', 'sustainability': 'low', 'popularity': 'medium'},
            'Bauhaus': {'period': 'modern', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'medium', 'popularity': 'high'},
            'International Style': {'period': 'modern', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'medium', 'popularity': 'high'},
            'Postmodern': {'period': 'modern', 'complexity': 'high', 'innovation': 'high', 'sustainability': 'medium', 'popularity': 'medium'},
            'Deconstructivist': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high', 'sustainability': 'medium', 'popularity': 'low'},
            'High-Tech': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high', 'sustainability': 'medium', 'popularity': 'medium'},
            'Organic': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'medium'},
            'Sustainable': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'very_high', 'popularity': 'very_high'},
            'Parametric': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high', 'sustainability': 'high', 'popularity': 'medium'},
            'Biomimetic': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high', 'sustainability': 'very_high', 'popularity': 'medium'},
            'Futuristic': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high', 'sustainability': 'high', 'popularity': 'medium'},
            'Vernacular': {'period': 'traditional', 'complexity': 'low', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'medium'},
            'Regional': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'medium'},
            'Tropical': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'high', 'popularity': 'high'},
            'Mediterranean': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'high'},
            'Scandinavian': {'period': 'contemporary', 'complexity': 'low', 'innovation': 'medium', 'sustainability': 'high', 'popularity': 'very_high'},
            'Japanese': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'high', 'popularity': 'high'},
            'Chinese': {'period': 'traditional', 'complexity': 'high', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'medium'},
            'Islamic': {'period': 'traditional', 'complexity': 'very_high', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'medium'},
            'African': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'medium'},
            'Industrial': {'period': 'modern', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'high'},
            'Luxury': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'medium', 'sustainability': 'low', 'popularity': 'high'},
            'Eclectic': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'medium'},
            'Bohemian': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'high'},
            'Mid-Century Modern': {'period': 'modern', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'high'},
            'Art Nouveau': {'period': 'modern', 'complexity': 'high', 'innovation': 'medium', 'sustainability': 'low', 'popularity': 'medium'},
            'Rustic': {'period': 'traditional', 'complexity': 'low', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'high'},
            'Coastal': {'period': 'contemporary', 'complexity': 'low', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'high'},
            'Urban': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'},
            'Moroccan': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'medium'},
            'Asian': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'high'},
            'Nordic': {'period': 'contemporary', 'complexity': 'low', 'innovation': 'medium', 'sustainability': 'high', 'popularity': 'high'},
            'Industrial Chic': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'medium', 'sustainability': 'medium', 'popularity': 'high'},
            'Vintage': {'period': 'traditional', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'high', 'popularity': 'high'},
            'Retro': {'period': 'modern', 'complexity': 'medium', 'innovation': 'low', 'sustainability': 'medium', 'popularity': 'medium'},
            'Biophilic': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'very_high', 'popularity': 'high'},
            'Wellness': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'},
            'Smart Design': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'very_high', 'sustainability': 'high', 'popularity': 'high'},
            'Universal': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'high'},
            'Inclusive': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'},
            'Accessible': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high', 'sustainability': 'high', 'popularity': 'very_high'}
        }

        # Thread-safe style trends storage
        self.style_trends = defaultdict(list)
        self._trends_lock = Lock()

        # Performance monitoring
        self._load_time = 0.0
        self._last_load_time = None

        # Load style history if exists
        self.load_style_history()

    @performance_monitor
    def load_style_history(self):
        """Load style usage history from CSV for trend analysis with enhanced error handling"""
        start_time = time.time()
        
        try:
            log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
            if os.path.exists(log_csv_file):
                with open(log_csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    loaded_count = 0
                    
                    for row in reader:
                        if row.get('style') and row.get('theme'):
                            timestamp = row.get('created_timestamp', '')
                            question = row.get('question', '')
                            
                            # Validate data before adding
                            if self._validate_trend_data(row['style'], row['theme'], timestamp):
                                with self._trends_lock:
                                    self.style_trends[row['theme']].append({
                                        'style': row['style'],
                                        'timestamp': timestamp,
                                        'question': question
                                    })
                                loaded_count += 1
                    
                    self._load_time = time.time() - start_time
                    self._last_load_time = datetime.now()
                    
                    with _performance_lock:
                        _performance_stats['csv_loads'] += 1
                    
                    log.info(f"Loaded style history: {loaded_count} valid entries in {self._load_time:.4f} seconds")
            else:
                log.info("No style history file found, starting with empty trends")
                
        except Exception as e:
            self._load_time = time.time() - start_time
            log.warning(f"Could not load style history: {e}")
            # Continue with empty trends

    def _validate_trend_data(self, style: str, theme: str, timestamp: str) -> bool:
        """
        Validate trend data before adding to storage
        
        Args:
            style: Style name to validate
            theme: Theme name to validate
            timestamp: Timestamp to validate
            
        Returns:
            bool: True if data is valid
        """
        if not style or not theme:
            return False
        
        if not isinstance(style, str) or not isinstance(theme, str):
            return False
        
        # Check if style exists in base styles
        if theme in self.base_styles and style not in self.base_styles[theme]:
            log.debug(f"Style '{style}' not found in theme '{theme}'")
            return False
        
        return True

    @performance_monitor
    def get_base_styles_for_category(self, theme: str) -> List[str]:
        """
        Get base styles for a specific theme with validation
        
        Args:
            theme (str): Theme/category name
            
        Returns:
            List[str]: List of base styles for the theme
        """
        with _performance_lock:
            _performance_stats['total_style_queries'] += 1
        
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme)
        if not is_valid:
            log.error(f"Invalid theme parameter: {error_msg}")
            return []
        
        # Sanitize input
        theme = theme.strip().lower()
        
        # Return styles for the theme
        return self.base_styles.get(theme, [])

    @performance_monitor
    def get_style_characteristics(self, style: str) -> Dict[str, Any]:
        """
        Get characteristics of a given style with enhanced metadata
        
        Args:
            style (str): Style name
            
        Returns:
            Dict[str, Any]: Style characteristics
        """
        with _performance_lock:
            _performance_stats['total_characteristics_queries'] += 1
        
        # Validate input
        if not style or not isinstance(style, str):
            log.warning(f"Invalid style parameter: {style}")
            return self._get_default_characteristics()
        
        # Sanitize input
        style = style.strip()
        
        # Return characteristics or default
        return self.style_characteristics.get(style, self._get_default_characteristics())

    def _get_default_characteristics(self) -> Dict[str, Any]:
        """
        Get default characteristics for unknown styles
        
        Returns:
            Dict[str, Any]: Default characteristics
        """
        return {
            'period': 'contemporary',
            'complexity': 'medium',
            'innovation': 'medium',
            'sustainability': 'medium',
            'popularity': 'medium'
        }

    def get_all_categories(self) -> List[str]:
        """
        Get all available themes/categories
        
        Returns:
            List[str]: List of all available categories
        """
        return list(self.base_styles.keys())

    @performance_monitor
    def get_style_trends_data(self, theme: str) -> List[Dict[str, Any]]:
        """
        Get style trends data for a theme with thread safety
        
        Args:
            theme (str): Theme name
            
        Returns:
            List[Dict[str, Any]]: Style trends data
        """
        with _performance_lock:
            _performance_stats['total_trend_queries'] += 1
        
        # Validate input
        is_valid, error_msg = validate_input_parameters(theme)
        if not is_valid:
            log.error(f"Invalid theme parameter: {error_msg}")
            return []
        
        # Sanitize input
        theme = theme.strip().lower()
        
        # Return trends data with thread safety
        with self._trends_lock:
            return self.style_trends.get(theme, []).copy()

    def add_style_usage(self, theme: str, style: str, question: str, timestamp: Optional[str] = None) -> bool:
        """
        Add a style usage entry to trends with validation
        
        Args:
            theme (str): Theme name
            style (str): Style name
            question (str): Question text
            timestamp (str, optional): Custom timestamp
            
        Returns:
            bool: True if successfully added
        """
        try:
            # Validate inputs
            if not theme or not style or not question:
                log.error("Missing required parameters for style usage")
                return False
            
            if not isinstance(theme, str) or not isinstance(style, str) or not isinstance(question, str):
                log.error("Invalid parameter types for style usage")
                return False
            
            # Sanitize inputs
            theme = theme.strip()
            style = style.strip()
            question = question.strip()
            
            # Generate timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Validate trend data
            if not self._validate_trend_data(style, theme, timestamp):
                log.warning(f"Invalid trend data: theme={theme}, style={style}")
                return False
            
            # Add to trends with thread safety
            with self._trends_lock:
                self.style_trends[theme].append({
                    'style': style,
                    'timestamp': timestamp,
                    'question': question
                })
            
            return True
            
        except Exception as e:
            log.error(f"Error adding style usage: {e}")
            return False

    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for the style data manager
        
        Returns:
            dict: Performance statistics
        """
        with _performance_lock:
            total_queries = (_performance_stats['total_style_queries'] + 
                           _performance_stats['total_characteristics_queries'] + 
                           _performance_stats['total_trend_queries'])
            
            return {
                'total_style_queries': _performance_stats['total_style_queries'],
                'total_characteristics_queries': _performance_stats['total_characteristics_queries'],
                'total_trend_queries': _performance_stats['total_trend_queries'],
                'csv_loads': _performance_stats['csv_loads'],
                'cache_hits': _performance_stats['cache_hits'],
                'cache_misses': _performance_stats['cache_misses'],
                'total_time': _performance_stats['total_time'],
                'average_time_per_query': _performance_stats['total_time'] / max(total_queries, 1),
                'load_time': self._load_time,
                'last_load_time': self._last_load_time.isoformat() if self._last_load_time else None,
                'total_categories': len(self.base_styles),
                'total_styles': sum(len(styles) for styles in self.base_styles.values()),
                'total_characteristics': len(self.style_characteristics),
                'total_trends': sum(len(trends) for trends in self.style_trends.values()),
                'module_version': '2.0',
                'optimization_date': '2025-08-24'
            }

    def reset_performance_stats(self):
        """Reset performance statistics with thread safety"""
        global _performance_stats
        with _performance_lock:
            _performance_stats = {
                'total_style_queries': 0,
                'total_characteristics_queries': 0,
                'total_trend_queries': 0,
                'csv_loads': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_time': 0.0,
                'last_reset': time.time()
            }
        log.info("Performance statistics reset")

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate the environment configuration
        
        Returns:
            dict: Environment validation results
        """
        validation_results = {
            'data_integrity': {
                'categories_count': len(self.base_styles),
                'styles_count': sum(len(styles) for styles in self.base_styles.values()),
                'characteristics_count': len(self.style_characteristics),
                'trends_count': sum(len(trends) for trends in self.style_trends.values())
            },
            'file_access': {
                'log_csv_file': os.getenv('LOG_CSV_FILE', 'log.csv'),
                'file_exists': os.path.exists(os.getenv('LOG_CSV_FILE', 'log.csv')),
                'file_readable': os.access(os.getenv('LOG_CSV_FILE', 'log.csv'), os.R_OK) if os.path.exists(os.getenv('LOG_CSV_FILE', 'log.csv')) else False
            },
            'performance': {
                'load_time': self._load_time,
                'last_load_time': self._last_load_time.isoformat() if self._last_load_time else None,
                'total_queries': _performance_stats['total_style_queries'] + _performance_stats['total_characteristics_queries'] + _performance_stats['total_trend_queries']
            }
        }
        
        return validation_results

# Global instance
style_data_manager = StyleDataManager()

# Convenience functions with caching
@lru_cache(maxsize=128)
def get_base_styles_for_category(theme: str) -> List[str]:
    """
    Get base styles for a specific theme with caching
    
    Args:
        theme (str): Theme/category name
        
    Returns:
        List[str]: List of base styles for the theme
    """
    return style_data_manager.get_base_styles_for_category(theme)

@lru_cache(maxsize=256)
def get_style_characteristics(style: str) -> Dict[str, Any]:
    """
    Get characteristics of a given style with caching
    
    Args:
        style (str): Style name
        
    Returns:
        Dict[str, Any]: Style characteristics
    """
    return style_data_manager.get_style_characteristics(style)

def get_all_categories() -> List[str]:
    """
    Get all available themes/categories
    
    Returns:
        List[str]: List of all available categories
    """
    return style_data_manager.get_all_categories()

def get_style_trends_data(theme: str) -> List[Dict[str, Any]]:
    """
    Get style trends data for a theme
    
    Args:
        theme (str): Theme name
        
    Returns:
        List[Dict[str, Any]]: Style trends data
    """
    return style_data_manager.get_style_trends_data(theme)

def add_style_usage(theme: str, style: str, question: str, timestamp: Optional[str] = None) -> bool:
    """
    Add a style usage entry to trends
    
    Args:
        theme (str): Theme name
        style (str): Style name
        question (str): Question text
        timestamp (str, optional): Custom timestamp
        
    Returns:
        bool: True if successfully added
    """
    return style_data_manager.add_style_usage(theme, style, question, timestamp)

def get_performance_statistics() -> Dict[str, Any]:
    """
    Get performance statistics
    
    Returns:
        dict: Performance statistics
    """
    return style_data_manager.get_performance_statistics()

def reset_performance_stats():
    """Reset performance statistics"""
    style_data_manager.reset_performance_stats()

def validate_environment() -> Dict[str, Any]:
    """
    Validate environment
    
    Returns:
        dict: Environment validation results
    """
    return style_data_manager.validate_environment()

# Export main functions
__all__ = [
    'StyleDataManager',
    'get_base_styles_for_category',
    'get_style_characteristics',
    'get_all_categories',
    'get_style_trends_data',
    'add_style_usage',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
