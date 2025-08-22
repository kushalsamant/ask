#!/usr/bin/env python3
"""
Research Theme System Module
Handles theme generation and management (2,667 themes)
"""

import random
from research_categories_data import get_main_categories, get_subcategories

# Context areas for cross-disciplinary questions (exactly 30 areas)
CONTEXT_AREAS = [
    # Sustainable Development & Environmental Contexts (5)
    'sustainable development', 'green building', 'carbon neutrality', 'climate resilience', 'environmental stewardship',
    
    # Urban & Planning Contexts (5)
    'urban planning', 'smart cities', 'community development', 'public spaces', 'transportation systems',
    
    # Building & Construction Contexts (5)
    'building design', 'construction methods', 'adaptive reuse', 'historic preservation', 'building performance',
    
    # Digital & Technology Contexts (5)
    'digital transformation', 'building information modeling', 'artificial intelligence', 'virtual reality', 'parametric design',
    
    # Material & Innovation Contexts (5)
    'material science', 'advanced materials', 'smart materials', 'material innovation', 'biomaterials',
    
    # Social & Cultural Contexts (5)
    'social equity', 'cultural preservation', 'inclusive design', 'community engagement', 'social sustainability'
]

def generate_cross_themes():
    """
    Generate the complete cross-disciplinary theme system (2,667 themes)
    
    Returns:
        dict: Complete theme system with 2,667 themes
    """
    main_categories = get_main_categories()
    cross_themes = {}
    
    # 1. Generate subcategory-specific themes (2,580 themes)
    # Each subcategory becomes a theme
    for category in main_categories:
        subcategories = get_subcategories(category)
        for subcategory in subcategories:
            theme_name = f"{category}_{subcategory}"
            cross_themes[theme_name] = [category, subcategory]
    
    # 2. Generate main category themes (86 themes)
    # Each main category becomes a theme
    for category in main_categories:
        theme_name = f"main_{category}"
        cross_themes[theme_name] = [category]
    
    # 3. Generate "all categories" theme (1 theme)
    # Single theme that includes all categories
    cross_themes['all_categories'] = main_categories
    
    return cross_themes

def get_theme_categories(theme_name):
    """
    Get categories for a specific theme
    
    Args:
        theme_name (str): Theme name
    
    Returns:
        list: Categories for the theme
    """
    cross_themes = generate_cross_themes()
    return cross_themes.get(theme_name, [])

def get_all_themes():
    """
    Get all available themes
    
    Returns:
        list: All theme names
    """
    cross_themes = generate_cross_themes()
    return list(cross_themes.keys())

def get_subcategory_themes():
    """
    Get all subcategory-based themes
    
    Returns:
        list: Subcategory theme names
    """
    cross_themes = generate_cross_themes()
    return [theme for theme in cross_themes.keys() if '_' in theme and not theme.startswith('main_') and theme != 'all_categories']

def get_main_category_themes():
    """
    Get all main category-based themes
    
    Returns:
        list: Main category theme names
    """
    cross_themes = generate_cross_themes()
    return [theme for theme in cross_themes.keys() if theme.startswith('main_')]

def get_theme_counts():
    """
    Get counts of all theme types
    
    Returns:
        dict: Theme counts
    """
    cross_themes = generate_cross_themes()
    subcategory_count = len(get_subcategory_themes())
    main_category_count = len(get_main_category_themes())
    total_count = len(cross_themes)
    
    return {
        'total_themes': total_count,
        'subcategory_themes': subcategory_count,
        'main_category_themes': main_category_count,
        'all_categories_theme': 1
    }

def select_random_theme(theme_type=None):
    """
    Select a random theme
    
    Args:
        theme_type (str): Type of theme to select ('subcategory', 'main_category', 'all')
    
    Returns:
        tuple: (theme_name, categories)
    """
    cross_themes = generate_cross_themes()
    
    if theme_type == 'subcategory':
        available_themes = get_subcategory_themes()
    elif theme_type == 'main_category':
        available_themes = get_main_category_themes()
    elif theme_type == 'all':
        available_themes = ['all_categories']
    else:
        available_themes = list(cross_themes.keys())
    
    if not available_themes:
        return None, []
    
    theme_name = random.choice(available_themes)
    categories = cross_themes[theme_name]
    
    return theme_name, categories

def get_context_area():
    """
    Get a random context area
    
    Returns:
        str: Random context area
    """
    return random.choice(CONTEXT_AREAS)

def get_context_areas():
    """
    Get all context areas
    
    Returns:
        list: All context areas
    """
    return CONTEXT_AREAS.copy()
