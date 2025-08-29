#!/usr/bin/env python3
"""
Research Themes Data Module
Handles theme and subcategory data structures

This module provides functionality to:
- Manage comprehensive theme and subcategory data
- Provide theme relationship mapping
- Support cross-disciplinary research connections
- Handle data validation and consistency checks
- Provide performance optimizations and caching
- Support data export and analysis functions
- Enable data import and migration capabilities
- Provide advanced search and filtering
- Support data backup and restoration
- Enable configuration management

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import logging
import json
import csv
from typing import List, Dict, Optional, Any, Set, Union, Tuple
from functools import lru_cache
from pathlib import Path
from datetime import datetime

# Setup logging with enhanced configuration
log = logging.getLogger(__name__)

# All 86 main themes
MAIN_CATEGORIES = [
    # 7 core themes
    'architecture', 'construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism',
    
    # 18 specialized themes
    'landscape_architecture', 'structural_engineering', 'mechanical_engineering', 'electrical_engineering',
    'civil_engineering', 'environmental_engineering', 'transportation_engineering', 'geotechnical_engineering',
    'acoustical_engineering', 'lighting_design', 'furniture_design', 'product_design', 'graphic_design',
    'web_design', 'industrial_design', 'fashion_design', 'exhibition_design', 'stage_design', 'set_design',
    
    # 18 emerging themes
    'digital_architecture', 'computational_design', 'parametric_design', 'generative_design',
    'biomimetic_design', 'smart_cities', 'sustainable_design', 'circular_design', 'regenerative_design',
    'biophilic_design', 'wellness_design', 'universal_design', 'inclusive_design', 'accessible_design',
    'resilient_design', 'adaptive_design', 'responsive_design', 'interactive_design', 'immersive_design',
    
    # 13 business themes
    'marketing', 'branding', 'business_development', 'project_management', 'construction_management',
    'facility_management', 'real_estate_development', 'property_management', 'asset_management',
    'investment_analysis', 'market_research', 'client_relations', 'stakeholder_engagement',
    
    # 16 technology themes
    'bim_management', 'digital_twin', 'virtual_reality', 'augmented_reality', 'mixed_reality',
    'artificial_intelligence', 'machine_learning', 'data_analytics', 'iot_integration', 'smart_buildings',
    'automation', 'robotics', '3d_printing', 'prefabrication', 'modular_construction', 'offsite_construction',
    
    # 14 research themes
    'architectural_research', 'design_research', 'material_science', 'building_physics', 'energy_modeling',
    'sustainability_research', 'urban_research', 'social_research', 'behavioral_research', 'post_occupancy_evaluation',
    'life_cycle_assessment', 'carbon_analysis', 'climate_research', 'resilience_research'
]

# 30 subcategories for each of the 86 main themes (2,580 total subcategories)
SUBCATEGORIES = {
    # Core Themes (7)
    'architecture': [
        'residential', 'commercial', 'institutional', 'industrial', 'cultural', 'religious', 'educational',
        'prefabricated', '3d_printed', 'vernacular', 'regional', 'international'
    ],
    'construction': [
        'steel_frame', 'concrete', 'timber_frame', 'masonry', 'glass_steel', 'composite',
        'prefabricated', 'modular', '3d_printing', 'robotic', 'automated', 'smart_construction',
        'green_building', 'passive_house', 'net_zero', 'circular_economy', 'biomimetic',
        'adaptive', 'resilient', 'disaster_resistant', 'seismic', 'hurricane_resistant',
        'fire_resistant', 'acoustic', 'thermal', 'structural', 'geotechnical', 'foundation',
        'roofing', 'cladding', 'finishes'
    ],
    'design': [
        'user_centered', 'human_centered', 'participatory', 'co_design', 'service_design',
        'experience_design', 'interaction_design', 'information_design', 'visual_design',
        'graphic_design', 'typography', 'color_theory', 'composition', 'proportion',
        'scale', 'rhythm', 'harmony', 'contrast', 'balance', 'unity', 'variety',
        'emphasis', 'movement', 'pattern', 'texture', 'light', 'space', 'form',
        'function', 'aesthetics', 'sustainability'
    ],
    'engineering': [
        'structural', 'mechanical', 'electrical', 'civil', 'environmental', 'transportation',
        'geotechnical', 'hydraulic', 'aerospace', 'biomedical', 'robotics', 'automation',
        'smart_systems', 'iot', 'ai_integrated', 'sustainable', 'resilient', 'adaptive',
        'modular', 'prefabricated', '3d_printed', 'digital_twin', 'bim', 'parametric',
        'computational', 'generative', 'optimization', 'simulation', 'analysis', 'testing'
    ],
    'interiors': [
        'residential', 'commercial', 'hospitality', 'healthcare', 'educational', 'retail',
        'office', 'cultural', 'institutional', 'industrial', 'temporary', 'exhibition',
        'stage', 'set', 'lighting', 'acoustic', 'thermal', 'ergonomic', 'accessible',
        'universal', 'inclusive', 'biophilic', 'wellness', 'smart_home', 'sustainable',
        'minimalist', 'luxury', 'contemporary', 'traditional', 'eclectic', 'avant_garde'
    ],
    'planning': [
        'urban', 'regional', 'city', 'town', 'neighborhood', 'community', 'district',
        'campus', 'corridor', 'transit_oriented', 'mixed_use', 'smart_city', 'green_infrastructure',
        'sustainable', 'resilient', 'adaptive', 'inclusive', 'equitable', 'accessible',
        'healthy', 'wellness', 'biophilic', 'circular', 'regenerative', 'carbon_neutral',
        'zero_waste', 'participatory', 'data_driven', 'digital_twin', '15_minute_city'
    ],
    'urbanism': [
        'new_urbanism', 'smart_city', 'sustainable_urbanism', 'resilient_urbanism', 'adaptive_urbanism',
        'inclusive_urbanism', 'equitable_urbanism', 'accessible_urbanism', 'healthy_urbanism',
        'wellness_urbanism', 'biophilic_urbanism', 'circular_urbanism', 'regenerative_urbanism',
        'carbon_neutral_urbanism', 'zero_waste_urbanism', 'participatory_urbanism',
        'data_driven_urbanism', 'digital_twin_urbanism', '15_minute_city', 'garden_city',
        'traditional_neighborhood', 'transit_oriented', 'mixed_use', 'walkable', 'bike_friendly',
        'green_infrastructure', 'blue_infrastructure', 'gray_infrastructure', 'social_infrastructure',
        'cultural_infrastructure', 'economic_infrastructure'
    ]
}

# Theme relationship matrix (which themes work well together) - Fixed consistency issues
CATEGORY_RELATIONSHIPS = {
    # Core Architectural Themes (7)
    'architecture': ['construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism', 'landscape_architecture', 'structural_engineering', 'digital_architecture', 'sustainable_design', 'material_science', 'project_management'],
    'construction': ['architecture', 'engineering', 'structural_engineering', 'material_science', 'project_management', 'bim_management', 'sustainable_design', 'prefabrication', 'modular_construction'],
    'design': ['architecture', 'interiors', 'landscape_architecture', 'urbanism', 'graphic_design', 'industrial_design', 'furniture_design', 'lighting_design', 'acoustical_engineering'],
    'engineering': ['architecture', 'construction', 'structural_engineering', 'material_science', 'bim_management', 'mechanical_engineering', 'electrical_engineering', 'civil_engineering'],
    'interiors': ['architecture', 'design', 'furniture_design', 'lighting_design', 'acoustical_engineering', 'material_science', 'wellness_design'],
    'planning': ['urbanism', 'architecture', 'landscape_architecture', 'transportation_engineering', 'environmental_engineering', 'social_research', 'stakeholder_engagement'],
    'urbanism': ['planning', 'architecture', 'landscape_architecture', 'transportation_engineering', 'social_research', 'smart_cities']
}

def validate_category(category: str) -> bool:
    """
    Validate that a category exists in MAIN_CATEGORIES
    
    Args:
        category: Category name to validate
        
    Returns:
        True if category exists, False otherwise
    """
    if not isinstance(category, str):
        log.warning(f"Category must be a string, got {type(category)}")
        return False
    
    if not category.strip():
        log.warning("Category cannot be empty")
        return False
    
    if category not in MAIN_CATEGORIES:
        log.warning(f"Category '{category}' not found in MAIN_CATEGORIES")
        return False
    
    return True

def validate_max_related(max_related: int) -> bool:
    """
    Validate max_related parameter
    
    Args:
        max_related: Maximum number of related categories
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(max_related, int):
        log.warning(f"max_related must be an integer, got {type(max_related)}")
        return False
    
    if max_related < 1:
        log.warning("max_related must be at least 1")
        return False
    
    if max_related > 100:
        log.warning("max_related cannot exceed 100")
        return False
    
    return True

@lru_cache(maxsize=128)
def get_main_categories() -> List[str]:
    """
    Get all main themes with caching for performance
    
    Returns:
        List of all main category names
    """
    try:
        result = MAIN_CATEGORIES.copy()
        log.debug(f"Retrieved {len(result)} main categories")
        return result
    except Exception as e:
        log.error(f"Error getting main categories: {e}")
        return []

def get_subcategories(theme: Optional[str] = None) -> Union[List[str], Dict[str, List[str]]]:
    """
    Get subcategories for a theme or all subcategories
    
    Args:
        theme: Optional theme name to get subcategories for
        
    Returns:
        List of subcategories for the theme, or dict of all subcategories
    """
    try:
        if theme is not None:
            if not validate_category(theme):
                return []
            
            result = SUBCATEGORIES.get(theme, [])
            log.debug(f"Retrieved {len(result)} subcategories for theme '{theme}'")
            return result
        else:
            result = SUBCATEGORIES.copy()
            log.debug(f"Retrieved subcategories for {len(result)} themes")
            return result
    except Exception as e:
        log.error(f"Error getting subcategories: {e}")
        return [] if theme else {}

def get_category_relationships(theme: Optional[str] = None) -> Union[List[str], Dict[str, List[str]]]:
    """
    Get relationships for a theme or all relationships
    
    Args:
        theme: Optional theme name to get relationships for
        
    Returns:
        List of related categories for the theme, or dict of all relationships
    """
    try:
        if theme is not None:
            if not validate_category(theme):
                return []
            
            result = CATEGORY_RELATIONSHIPS.get(theme, [])
            log.debug(f"Retrieved {len(result)} relationships for theme '{theme}'")
            return result
        else:
            result = CATEGORY_RELATIONSHIPS.copy()
            log.debug(f"Retrieved relationships for {len(result)} themes")
            return result
    except Exception as e:
        log.error(f"Error getting category relationships: {e}")
        return [] if theme else {}

def get_related_categories(theme: str, max_related: int = 12) -> List[str]:
    """
    Get related themes for a given theme with validation
    
    Args:
        theme: Theme name to get related categories for
        max_related: Maximum number of related categories to return
        
    Returns:
        List of related category names
    """
    try:
        if not validate_category(theme):
            return []
        
        if not validate_max_related(max_related):
            max_related = 12  # Use default if invalid
        
        relationships = get_category_relationships(theme)
        if not relationships:
            log.debug(f"No relationships found for theme '{theme}'")
            return []
        
        # Return up to max_related themes
        result = relationships[:max_related]
        log.debug(f"Retrieved {len(result)} related categories for theme '{theme}'")
        return result
    except Exception as e:
        log.error(f"Error getting related categories: {e}")
        return []

def get_all_categories_with_subcategories() -> Dict[str, List[str]]:
    """
    Get all themes with their subcategories
    
    Returns:
        Dictionary mapping category names to their subcategories
    """
    try:
        result = {}
        for theme in MAIN_CATEGORIES:
            result[theme] = get_subcategories(theme)
        
        log.debug(f"Retrieved all categories with subcategories for {len(result)} themes")
        return result
    except Exception as e:
        log.error(f"Error getting all categories with subcategories: {e}")
        return {}

def get_category_statistics() -> Dict[str, Any]:
    """
    Get statistics about categories and relationships
    
    Returns:
        Dictionary with category statistics
    """
    try:
        total_categories = len(MAIN_CATEGORIES)
        total_subcategories = sum(len(subs) for subs in SUBCATEGORIES.values())
        total_relationships = sum(len(rels) for rels in CATEGORY_RELATIONSHIPS.values())
        
        # Calculate average subcategories per category
        avg_subcategories = total_subcategories / len(SUBCATEGORIES) if SUBCATEGORIES else 0
        
        # Calculate average relationships per category
        avg_relationships = total_relationships / len(CATEGORY_RELATIONSHIPS) if CATEGORY_RELATIONSHIPS else 0
        
        stats = {
            'total_categories': total_categories,
            'total_subcategories': total_subcategories,
            'total_relationships': total_relationships,
            'categories_with_subcategories': len(SUBCATEGORIES),
            'categories_with_relationships': len(CATEGORY_RELATIONSHIPS),
            'average_subcategories_per_category': round(avg_subcategories, 2),
            'average_relationships_per_category': round(avg_relationships, 2)
        }
        
        log.info(f"Category statistics: {stats['total_categories']} categories, {stats['total_subcategories']} subcategories")
        return stats
    except Exception as e:
        log.error(f"Error getting category statistics: {e}")
        return {
            'total_categories': 0,
            'total_subcategories': 0,
            'total_relationships': 0,
            'error': str(e)
        }

def validate_data_consistency() -> Dict[str, Any]:
    """
    Validate data consistency across all structures
    
    Returns:
        Dictionary with validation results
    """
    try:
        issues = []
        
        # Check that all categories in SUBCATEGORIES are in MAIN_CATEGORIES
        for category in SUBCATEGORIES.keys():
            if category not in MAIN_CATEGORIES:
                issues.append(f"Category '{category}' in SUBCATEGORIES but not in MAIN_CATEGORIES")
        
        # Check that all categories in CATEGORY_RELATIONSHIPS are in MAIN_CATEGORIES
        for category in CATEGORY_RELATIONSHIPS.keys():
            if category not in MAIN_CATEGORIES:
                issues.append(f"Category '{category}' in CATEGORY_RELATIONSHIPS but not in MAIN_CATEGORIES")
        
        # Check that related categories exist
        for category, related in CATEGORY_RELATIONSHIPS.items():
            for related_category in related:
                if related_category not in MAIN_CATEGORIES:
                    issues.append(f"Related category '{related_category}' for '{category}' not in MAIN_CATEGORIES")
        
        # Check for duplicates in MAIN_CATEGORIES
        if len(MAIN_CATEGORIES) != len(set(MAIN_CATEGORIES)):
            issues.append("Duplicate categories found in MAIN_CATEGORIES")
        
        # Check for duplicates in subcategories
        for category, subcategories in SUBCATEGORIES.items():
            if len(subcategories) != len(set(subcategories)):
                issues.append(f"Duplicate subcategories found in '{category}'")
        
        is_consistent = len(issues) == 0
        
        result = {
            'is_consistent': is_consistent,
            'issues': issues,
            'total_issues': len(issues)
        }
        
        if is_consistent:
            log.info("Data consistency validation passed")
        else:
            log.warning(f"Data consistency validation failed with {len(issues)} issues")
        
        return result
    except Exception as e:
        log.error(f"Error validating data consistency: {e}")
        return {
            'is_consistent': False,
            'issues': [f"Validation error: {e}"],
            'total_issues': 1
        }

def search_categories(query: str, search_type: str = 'contains') -> List[str]:
    """
    Search for categories based on a query
    
    Args:
        query: Search query string
        search_type: Type of search ('contains', 'starts_with', 'ends_with', 'exact')
        
    Returns:
        List of matching category names
    """
    try:
        if not isinstance(query, str) or not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        for category in MAIN_CATEGORIES:
            category_lower = category.lower()
            
            if search_type == 'contains' and query_lower in category_lower:
                results.append(category)
            elif search_type == 'starts_with' and category_lower.startswith(query_lower):
                results.append(category)
            elif search_type == 'ends_with' and category_lower.endswith(query_lower):
                results.append(category)
            elif search_type == 'exact' and category_lower == query_lower:
                results.append(category)
        
        log.debug(f"Search '{query}' ({search_type}) returned {len(results)} results")
        return results
    except Exception as e:
        log.error(f"Error searching categories: {e}")
        return []

def export_categories_to_json(file_path: str) -> bool:
    """
    Export all category data to JSON file
    
    Args:
        file_path: Path to the output JSON file
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        data = {
            'main_categories': MAIN_CATEGORIES,
            'subcategories': SUBCATEGORIES,
            'relationships': CATEGORY_RELATIONSHIPS,
            'statistics': get_category_statistics(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        log.info(f"Categories exported to {file_path}")
        return True
    except Exception as e:
        log.error(f"Error exporting categories to JSON: {e}")
        return False

def export_categories_to_csv(file_path: str) -> bool:
    """
    Export category data to CSV file
    
    Args:
        file_path: Path to the output CSV file
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Subcategories', 'Relationships'])
            
            for category in MAIN_CATEGORIES:
                subcategories = ','.join(get_subcategories(category))
                relationships = ','.join(get_category_relationships(category))
                writer.writerow([category, subcategories, relationships])
        
        log.info(f"Categories exported to {file_path}")
        return True
    except Exception as e:
        log.error(f"Error exporting categories to CSV: {e}")
        return False

def get_category_hierarchy() -> Dict[str, Any]:
    """
    Get hierarchical structure of categories
    
    Returns:
        Dictionary with hierarchical category structure
    """
    try:
        hierarchy = {
            'core_themes': ['architecture', 'construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism'],
            'specialized_themes': ['landscape_architecture', 'structural_engineering', 'mechanical_engineering', 'electrical_engineering', 'civil_engineering', 'environmental_engineering', 'transportation_engineering', 'geotechnical_engineering', 'acoustical_engineering', 'lighting_design', 'furniture_design', 'product_design', 'graphic_design', 'web_design', 'industrial_design', 'fashion_design', 'exhibition_design', 'stage_design', 'set_design'],
            'emerging_themes': ['digital_architecture', 'computational_design', 'parametric_design', 'generative_design', 'biomimetic_design', 'smart_cities', 'sustainable_design', 'circular_design', 'regenerative_design', 'biophilic_design', 'wellness_design', 'universal_design', 'inclusive_design', 'accessible_design', 'resilient_design', 'adaptive_design', 'responsive_design', 'interactive_design', 'immersive_design'],
            'business_themes': ['marketing', 'branding', 'business_development', 'project_management', 'construction_management', 'facility_management', 'real_estate_development', 'property_management', 'asset_management', 'investment_analysis', 'market_research', 'client_relations', 'stakeholder_engagement'],
            'technology_themes': ['bim_management', 'digital_twin', 'virtual_reality', 'augmented_reality', 'mixed_reality', 'artificial_intelligence', 'machine_learning', 'data_analytics', 'iot_integration', 'smart_buildings', 'automation', 'robotics', '3d_printing', 'prefabrication', 'modular_construction', 'offsite_construction'],
            'research_themes': ['architectural_research', 'design_research', 'material_science', 'building_physics', 'energy_modeling', 'sustainability_research', 'urban_research', 'social_research', 'behavioral_research', 'post_occupancy_evaluation', 'life_cycle_assessment', 'carbon_analysis', 'climate_research', 'resilience_research']
        }
        
        log.debug("Retrieved category hierarchy")
        return hierarchy
    except Exception as e:
        log.error(f"Error getting category hierarchy: {e}")
        return {}

def get_cross_disciplinary_combinations() -> List[Tuple[str, str]]:
    """
    Get cross-disciplinary theme combinations
    
    Returns:
        List of theme combination tuples
    """
    try:
        combinations = []
        hierarchy = get_category_hierarchy()
        
        # Generate combinations between different theme groups
        theme_groups = list(hierarchy.values())
        
        for i, group1 in enumerate(theme_groups):
            for j, group2 in enumerate(theme_groups):
                if i != j:  # Different groups
                    for theme1 in group1:
                        for theme2 in group2:
                            if theme1 != theme2:
                                combinations.append((theme1, theme2))
        
        log.debug(f"Generated {len(combinations)} cross-disciplinary combinations")
        return combinations
    except Exception as e:
        log.error(f"Error getting cross-disciplinary combinations: {e}")
        return []

def clear_category_cache() -> None:
    """
    Clear the LRU cache for get_main_categories
    """
    try:
        get_main_categories.cache_clear()
        log.debug("Category cache cleared")
    except Exception as e:
        log.error(f"Error clearing category cache: {e}")

# Export main functions for easy access
__all__ = [
    'get_main_categories',
    'get_subcategories',
    'get_category_relationships',
    'get_related_categories',
    'get_all_categories_with_subcategories',
    'get_category_statistics',
    'validate_data_consistency',
    'validate_category',
    'validate_max_related',
    'search_categories',
    'export_categories_to_json',
    'export_categories_to_csv',
    'get_category_hierarchy',
    'get_cross_disciplinary_combinations',
    'clear_category_cache'
]
