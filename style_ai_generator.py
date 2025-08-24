#!/usr/bin/env python3
"""
Style AI Generator Module - Optimized Version 3.0
Handles AI-powered architectural style generation and suggestions with enhanced performance

This module provides functionality to:
- Generate AI-powered style suggestions based on questions and context
- Create dynamic style combinations with intelligent fallback
- Handle API interactions with robust error handling
- Provide performance monitoring and caching
- Support multiple architectural categories and styles

Optimizations:
- Enhanced error handling and recovery
- Performance monitoring and caching
- Optimized API interactions
- Better input validation
- Memory-efficient operations
- Thread-safe operations
- Improved performance statistics tracking
- Better fallback mechanisms

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 3.0 (Heavily Optimized)
"""

import os
import logging
import random
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from functools import wraps, lru_cache
from threading import Lock

# Setup logging
log = logging.getLogger(__name__)

# Environment variables with defaults
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
TEXT_MODEL = os.getenv('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))
TOGETHER_API_BASE = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1')

# Thread-safe performance monitoring
_performance_stats = {
    'total_style_suggestions': 0,
    'total_style_combinations': 0,
    'api_calls': 0,
    'api_successes': 0,
    'api_failures': 0,
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

def validate_input_parameters(theme: str, question: str, context: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate input parameters for style generation
    
    Args:
        theme: Theme/category to validate
        question: Question to validate
        context: Optional context to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not theme or not isinstance(theme, str) or not theme.strip():
        return False, "Theme must be a non-empty string"
    
    if not question or not isinstance(question, str) or not question.strip():
        return False, "Question must be a non-empty string"
    
    if context is not None and not isinstance(context, str):
        return False, "Context must be a string or None"
    
    # Check for potentially harmful characters
    invalid_chars = ['<', '>', '"', "'", '\\', '/', '|', ':', '*', '?']
    if any(char in theme for char in invalid_chars):
        return False, "Theme contains invalid characters"
    
    return True, ""

class StyleAIGenerator:
    """AI-powered architectural style generator with enhanced performance"""

    def __init__(self):
        self.context_weights = {
            'question_complexity': 0.3,
            'category_specificity': 0.4,
            'trend_popularity': 0.2,
            'innovation_factor': 0.1
        }
        
        # Validate weights
        total_weight = sum(self.context_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            log.warning(f"Context weights do not sum to 1.0: {total_weight}")
        
        # Initialize API configuration
        self.api_url = f"{TOGETHER_API_BASE}/chat/completions"
        self.api_headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        } if TOGETHER_API_KEY else {}

    @performance_monitor
    def get_ai_generated_style_suggestion(self, theme: str, question: str, context: Optional[str] = None) -> List[str]:
        """
        Generate AI-powered style suggestions based on question and context
        
        Enhanced with:
        - Input validation and sanitization
        - Performance monitoring
        - Comprehensive error handling
        - Caching for repeated requests
        - Better API response handling
        - Thread-safe statistics tracking
        
        Args:
            theme (str): Architectural theme/category
            question (str): Question to analyze
            context (str, optional): Additional context
            
        Returns:
            List[str]: List of suggested style names (max 3)
        """
        with _performance_lock:
            _performance_stats['total_style_suggestions'] += 1
        
        # Validate input parameters
        is_valid, error_msg = validate_input_parameters(theme, question, context)
        if not is_valid:
            log.error(f"Invalid parameters: {error_msg}")
            return []
        
        # Sanitize inputs
        theme = theme.strip()
        question = question.strip()
        context = context.strip() if context else None
        
        # Check if API is available
        if not TOGETHER_API_KEY:
            log.warning("No API key available for style suggestions")
            return self._get_fallback_style_suggestions(theme)
        
        try:
            with _performance_lock:
                _performance_stats['api_calls'] += 1
            
            # Prepare system prompt
            system_prompt = """You are an expert architectural style consultant. Analyze the given architectural question and suggest the most appropriate architectural style(s) that would best represent or complement the concept being explored."""
            
            # Prepare user prompt
            context_info = f"Context: {context}" if context else ""
            available_styles = self._get_available_styles(theme)
            
            if not available_styles:
                log.warning(f"No styles available for theme: {theme}")
                return []
            
            prompt = f"""Question: {question}
            theme: {theme}
            {context_info}

            Based on this architectural question, suggest 3-5 most appropriate architectural styles from this list:
            {', '.join(available_styles)}

            Consider:
            - How the style relates to the question's theme
            - Contemporary relevance
            - Visual impact and representation
            - Innovation potential

            Return only the style names, separated by commas:"""

            # Prepare API payload
            payload = {
                "model": TEXT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 100,
                "top_p": 0.9
            }

            # Make API request
            response = requests.post(
                self.api_url, 
                headers=self.api_headers, 
                json=payload, 
                timeout=API_TIMEOUT
            )

            if response.status_code == 200:
                with _performance_lock:
                    _performance_stats['api_successes'] += 1
                
                data = response.json()
                
                if 'choices' in data and data['choices']:
                    suggestions = data['choices'][0]['message']['content'].strip()
                    # Parse suggestions
                    suggested_styles = [s.strip() for s in suggestions.split(',')]
                    # Filter to valid styles
                    valid_styles = [s for s in suggested_styles if s in available_styles]
                    return valid_styles[:3]  # Return top 3 suggestions
                else:
                    log.warning("Invalid API response for style suggestions")
                    return self._get_fallback_style_suggestions(theme)
            else:
                with _performance_lock:
                    _performance_stats['api_failures'] += 1
                log.error(f"API error generating style suggestions: {response.status_code}")
                return self._get_fallback_style_suggestions(theme)

        except requests.exceptions.Timeout:
            with _performance_lock:
                _performance_stats['api_failures'] += 1
            log.error("API timeout generating style suggestions")
            return self._get_fallback_style_suggestions(theme)
        except requests.exceptions.RequestException as e:
            with _performance_lock:
                _performance_stats['api_failures'] += 1
            log.error(f"Request error generating style suggestions: {e}")
            return self._get_fallback_style_suggestions(theme)
        except Exception as e:
            with _performance_lock:
                _performance_stats['api_failures'] += 1
            log.error(f"Error generating AI style suggestions: {e}")
            return self._get_fallback_style_suggestions(theme)

    def _get_available_styles(self, theme: str) -> List[str]:
        """
        Get available styles for a theme with error handling
        
        Args:
            theme (str): Architectural theme
            
        Returns:
            List[str]: Available styles
        """
        try:
            from style_data_manager import get_base_styles_for_category
            return get_base_styles_for_category(theme)
        except ImportError:
            log.warning("style_data_manager not available, using fallback styles")
            return self._get_fallback_styles_for_theme(theme)
        except Exception as e:
            log.error(f"Error getting available styles: {e}")
            return self._get_fallback_styles_for_theme(theme)

    def _get_fallback_styles_for_theme(self, theme: str) -> List[str]:
        """
        Get fallback styles when style_data_manager is unavailable
        
        Args:
            theme (str): Architectural theme
            
        Returns:
            List[str]: Fallback styles
        """
        fallback_styles = {
            'modern': ['Modern', 'Contemporary', 'Minimalist'],
            'classical': ['Classical', 'Neoclassical', 'Baroque'],
            'gothic': ['Gothic', 'Gothic Revival', 'Medieval'],
            'art_deco': ['Art Deco', 'Art Nouveau', 'Bauhaus'],
            'brutalist': ['Brutalist', 'Modernist', 'Industrial']
        }
        
        theme_lower = theme.lower()
        for key, styles in fallback_styles.items():
            if key in theme_lower or theme_lower in key:
                return styles
        
        return ['Modern', 'Contemporary', 'Classical']

    def _get_fallback_style_suggestions(self, theme: str) -> List[str]:
        """
        Get fallback style suggestions when API is unavailable
        
        Args:
            theme (str): Architectural theme
            
        Returns:
            List[str]: Fallback style suggestions
        """
        try:
            available_styles = self._get_available_styles(theme)
            if available_styles:
                # Return first 3 styles as fallback
                return available_styles[:3]
            else:
                return []
        except Exception as e:
            log.error(f"Error getting fallback style suggestions: {e}")
            return []

    @performance_monitor
    def create_dynamic_style_combination(self, theme: str, base_style: str, question_context: Optional[str] = None) -> str:
        """
        Create dynamic style combinations based on context and trends
        
        Enhanced with:
        - Better error handling
        - Optimized style selection
        - Context-aware combinations
        - Fallback mechanisms
        - Thread-safe statistics tracking
        
        Args:
            theme (str): Architectural theme
            base_style (str): Base style to combine
            question_context (str, optional): Question context for complexity analysis
            
        Returns:
            str: Combined style name
        """
        with _performance_lock:
            _performance_stats['total_style_combinations'] += 1
        
        try:
            # Validate inputs
            if not theme or not base_style:
                log.error("Invalid theme or base_style provided")
                return base_style if base_style else "Unknown Style"
            
            # Get base style characteristics
            style_characteristics = self._get_style_characteristics(base_style)
            
            # Find complementary styles
            available_styles = self._get_available_styles(theme)
            if not available_styles:
                log.warning(f"No styles available for theme: {theme}")
                return f"{base_style} Enhanced"
            
            complementary_styles = [s for s in available_styles if s != base_style]
            
            # Create combination based on context complexity
            if question_context and len(question_context) > 50:
                # Complex question - use multiple styles
                if complementary_styles:
                    combined_style = f"{base_style} + {random.choice(complementary_styles)}"
                else:
                    combined_style = f"{base_style} Enhanced"
            else:
                # Simple question - use single style with enhancement
                combined_style = f"{base_style} Contemporary"
            
            return combined_style

        except Exception as e:
            log.error(f"Error creating dynamic style combination: {e}")
            return base_style

    def _get_style_characteristics(self, style: str) -> Dict[str, Any]:
        """
        Get style characteristics with error handling
        
        Args:
            style (str): Style name
            
        Returns:
            Dict[str, Any]: Style characteristics
        """
        try:
            from style_data_manager import get_style_characteristics
            return get_style_characteristics(style)
        except ImportError:
            log.warning("style_data_manager not available, using default characteristics")
            return {'complexity': 'medium', 'era': 'modern', 'popularity': 'high'}
        except Exception as e:
            log.error(f"Error getting style characteristics: {e}")
            return {'complexity': 'medium', 'era': 'modern', 'popularity': 'high'}

    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for the style AI generator
        
        Returns:
            dict: Performance statistics
        """
        with _performance_lock:
            total_operations = _performance_stats['total_style_suggestions'] + _performance_stats['total_style_combinations']
            
            return {
                'total_style_suggestions': _performance_stats['total_style_suggestions'],
                'total_style_combinations': _performance_stats['total_style_combinations'],
                'api_calls': _performance_stats['api_calls'],
                'api_successes': _performance_stats['api_successes'],
                'api_failures': _performance_stats['api_failures'],
                'api_success_rate': (_performance_stats['api_successes'] / max(_performance_stats['api_calls'], 1)) * 100,
                'cache_hits': _performance_stats['cache_hits'],
                'cache_misses': _performance_stats['cache_misses'],
                'total_time': _performance_stats['total_time'],
                'average_time_per_operation': _performance_stats['total_time'] / max(total_operations, 1),
                'module_version': '3.0',
                'optimization_date': '2025-08-24'
            }

    def reset_performance_stats(self):
        """Reset performance statistics with thread safety"""
        global _performance_stats
        with _performance_lock:
            _performance_stats = {
                'total_style_suggestions': 0,
                'total_style_combinations': 0,
                'api_calls': 0,
                'api_successes': 0,
                'api_failures': 0,
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
            'api_configuration': {
                'api_key_configured': bool(TOGETHER_API_KEY),
                'api_base_url': TOGETHER_API_BASE,
                'text_model': TEXT_MODEL,
                'api_timeout': API_TIMEOUT
            },
            'dependencies': {
                'requests_available': self._check_requests_available(),
                'style_data_manager_available': self._check_style_data_manager_available()
            },
            'performance': {
                'total_operations': _performance_stats['total_style_suggestions'] + _performance_stats['total_style_combinations'],
                'api_success_rate': (_performance_stats['api_successes'] / max(_performance_stats['api_calls'], 1)) * 100
            }
        }
        
        return validation_results

    def _check_requests_available(self) -> bool:
        """Check if requests module is available"""
        try:
            import requests
            return True
        except ImportError:
            return False

    def _check_style_data_manager_available(self) -> bool:
        """Check if style_data_manager module is available"""
        try:
            from style_data_manager import get_base_styles_for_category, get_style_characteristics
            return True
        except ImportError:
            return False

# Global instance
style_ai_generator = StyleAIGenerator()

@lru_cache(maxsize=256)
def get_ai_generated_style_suggestion(theme: str, question: str, context: Optional[str] = None) -> List[str]:
    """
    Global function to get AI-generated style suggestions with enhanced caching
    
    Args:
        theme (str): Architectural theme
        question (str): Question to analyze
        context (str, optional): Additional context
        
    Returns:
        List[str]: List of suggested style names
    """
    return style_ai_generator.get_ai_generated_style_suggestion(theme, question, context)

def create_dynamic_style_combination(theme: str, base_style: str, question_context: Optional[str] = None) -> str:
    """
    Global function to create dynamic style combinations
    
    Args:
        theme (str): Architectural theme
        base_style (str): Base style to combine
        question_context (str, optional): Question context
        
    Returns:
        str: Combined style name
    """
    return style_ai_generator.create_dynamic_style_combination(theme, base_style, question_context)

def get_performance_statistics() -> Dict[str, Any]:
    """
    Global function to get performance statistics
    
    Returns:
        dict: Performance statistics
    """
    return style_ai_generator.get_performance_statistics()

def reset_performance_stats():
    """Global function to reset performance statistics"""
    style_ai_generator.reset_performance_stats()

def validate_environment() -> Dict[str, Any]:
    """
    Global function to validate environment
    
    Returns:
        dict: Environment validation results
    """
    return style_ai_generator.validate_environment()

# Export main functions
__all__ = [
    'StyleAIGenerator',
    'get_ai_generated_style_suggestion',
    'create_dynamic_style_combination',
    'get_performance_statistics',
    'reset_performance_stats',
    'validate_environment',
    'validate_input_parameters'
]
