#!/usr/bin/env python3
"""
Research Categories Data Module
Handles category and subcategory data structures
"""

# All 86 main categories
MAIN_CATEGORIES = [
    # 7 core categories
    'architecture', 'construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism',
    
    # 18 specialized categories
    'landscape_architecture', 'structural_engineering', 'mechanical_engineering', 'electrical_engineering',
    'civil_engineering', 'environmental_engineering', 'transportation_engineering', 'geotechnical_engineering',
    'acoustical_engineering', 'lighting_design', 'furniture_design', 'product_design', 'graphic_design',
    'web_design', 'industrial_design', 'fashion_design', 'exhibition_design', 'stage_design', 'set_design',
    
    # 18 emerging categories
    'digital_architecture', 'computational_design', 'parametric_design', 'generative_design',
    'biomimetic_design', 'smart_cities', 'sustainable_design', 'circular_design', 'regenerative_design',
    'biophilic_design', 'wellness_design', 'universal_design', 'inclusive_design', 'accessible_design',
    'resilient_design', 'adaptive_design', 'responsive_design', 'interactive_design', 'immersive_design',
    
    # 13 business categories
    'marketing', 'branding', 'business_development', 'project_management', 'construction_management',
    'facility_management', 'real_estate_development', 'property_management', 'asset_management',
    'investment_analysis', 'market_research', 'client_relations', 'stakeholder_engagement',
    
    # 16 technology categories
    'bim_management', 'digital_twin', 'virtual_reality', 'augmented_reality', 'mixed_reality',
    'artificial_intelligence', 'machine_learning', 'data_analytics', 'iot_integration', 'smart_buildings',
    'automation', 'robotics', '3d_printing', 'prefabrication', 'modular_construction', 'offsite_construction',
    
    # 14 research categories
    'architectural_research', 'design_research', 'material_science', 'building_physics', 'energy_modeling',
    'sustainability_research', 'urban_research', 'social_research', 'behavioral_research', 'post_occupancy_evaluation',
    'life_cycle_assessment', 'carbon_analysis', 'climate_research', 'resilience_research'
]

# 30 subcategories for each of the 86 main categories (2,580 total subcategories)
SUBCATEGORIES = {
    # Core Categories (7)
    'architecture': [
        'residential', 'commercial', 'institutional', 'industrial', 'cultural', 'religious', 'educational',
        'healthcare', 'hospitality', 'retail', 'office', 'mixed_use', 'temporary', 'adaptive_reuse',
        'heritage', 'contemporary', 'modern', 'postmodern', 'deconstructivist', 'parametric',
        'biomimetic', 'sustainable', 'net_zero', 'passive_house', 'smart_building', 'modular',
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

# Category relationship matrix (which categories work well together)
CATEGORY_RELATIONSHIPS = {
    # Core Architectural Categories (7)
    'architecture': ['construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism', 'landscape_architecture', 'structural_engineering', 'digital_architecture', 'sustainability', 'materials', 'project_management'],
    'construction': ['architecture', 'engineering', 'structural_engineering', 'materials', 'project_management', 'bim_management', 'safety', 'quality_control', 'cost_management', 'sustainability', 'prefabrication', 'modular_construction'],
    'design': ['architecture', 'interiors', 'landscape_architecture', 'urbanism', 'visual_arts', 'graphic_design', 'industrial_design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'user_experience'],
    'engineering': ['architecture', 'construction', 'structural_engineering', 'materials', 'bim_management', 'mechanical_engineering', 'electrical_engineering', 'civil_engineering', 'safety', 'quality_control', 'performance_analysis', 'systems_integration'],
    'interiors': ['architecture', 'design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'materials', 'color_theory', 'textile_design', 'space_planning', 'user_experience', 'wellness_design'],
    'planning': ['urbanism', 'architecture', 'landscape_architecture', 'transportation', 'environmental_planning', 'community_development', 'social_impact', 'economic_development', 'infrastructure', 'zoning', 'public_policy', 'stakeholder_engagement'],
    'urbanism': ['planning', 'architecture', 'landscape_architecture', 'transportation', 'community_development', 'social_impact', 'smart_cities', 'public_spaces', 'urban_design', 'mobility', 'infrastructure', 'cultural_heritage']
}

def get_main_categories():
    """Get all main categories"""
    return MAIN_CATEGORIES.copy()

def get_subcategories(category=None):
    """Get subcategories for a category or all subcategories"""
    if category:
        return SUBCATEGORIES.get(category, [])
    return SUBCATEGORIES.copy()

def get_category_relationships(category=None):
    """Get relationships for a category or all relationships"""
    if category:
        return CATEGORY_RELATIONSHIPS.get(category, [])
    return CATEGORY_RELATIONSHIPS.copy()

def get_related_categories(category, max_related=12):
    """Get related categories for a given category"""
    relationships = get_category_relationships(category)
    if not relationships:
        return []
    
    # Return up to max_related categories
    return relationships[:max_related]

def get_all_categories_with_subcategories():
    """Get all categories with their subcategories"""
    result = {}
    for category in MAIN_CATEGORIES:
        result[category] = get_subcategories(category)
    return result
