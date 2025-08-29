#!/usr/bin/env python3
"""
Enhanced Cross-Disciplinary Generator with Research Explorer Integration
Creates intelligent cross-disciplinary questions and analyzes research directions

This module provides functionality to:
- Generate cross-disciplinary research questions
- Analyze research directions and patterns
- Discover insights across multiple themes
- Suggest exploration paths
- Provide comprehensive theme management
- Support research synthesis and analysis
- Enable intelligent question generation
- Provide research summary and statistics

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import os
import logging
import random
import requests
from datetime import datetime
from collections import defaultdict, Counter
from research_theme_data import get_related_categories

# Setup logging
log = logging.getLogger(__name__)

# Environment variables
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
TEXT_MODEL = os.getenv('TEXT_MODEL', 'togethercomputer/llama-3.3-70b-instruct-turbo')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))

class EnhancedCrossDisciplinaryGenerator:
    """Enhanced cross-disciplinary generator with research analysis capabilities"""
    
    def __init__(self):
        # Research exploration capabilities
        self.research_dimensions = {
            'spatial': ['urban', 'rural', 'global', 'local', 'regional'],
            'thematic': ['sustainability', 'technology', 'culture', 'economics', 'social'],
            'methodological': ['analytical', 'creative', 'experimental', 'theoretical', 'practical'],
            'scale': ['micro', 'meso', 'macro', 'mega'],
            'context': ['environmental', 'social', 'political', 'economic', 'cultural']
        }
        
        self.exploration_patterns = {
            'cross_pollination': 'Connecting insights across themes',
            'temporal_analysis': 'Examining evolution and trends over time',
            'spatial_mapping': 'Understanding geographical and contextual variations',
            'thematic_synthesis': 'Identifying common themes and patterns',
            'methodological_experimentation': 'Exploring different research approaches',
            'scale_transformation': 'Understanding how concepts work at different scales'
        }
        
        self.research_insights = []
        self.exploration_history = []
        
        # Cross-disciplinary question patterns (30 different types)
        self.question_patterns = {
            # 1-5: Basic Intersection and Connection Patterns
            'intersection': "How does {category1} intersect with {category2} in {context}?",
            'synthesis': "What insights from {category1} can enhance {category2} approaches?",
            'bridge': "How can {category1} principles be applied to {category2} challenges?",
            'comparison': "What are the similarities and differences between {category1} and {category2} in {context}?",
            'integration': "How can we integrate {category1} and {category2} methodologies for better {context}?",
            
            # 6-10: Evolution and Historical Patterns
            'evolution': "How has {category1} influenced the development of {category2} over time?",
            'historical_impact': "What historical precedents in {category1} inform current {category2} practices?",
            'progression': "How has the relationship between {category1} and {category2} evolved in {context}?",
            'legacy': "What legacy from {category1} continues to shape {category2} approaches?",
            'transformation': "How is {category1} transforming the traditional methods of {category2}?",
            
            # 11-15: Innovation and Future Patterns
            'innovation': "What innovative solutions emerge when combining {category1} and {category2} approaches?",
            'future_convergence': "How will the convergence of {category1} and {category2} shape the future of {context}?",
            'breakthrough': "What breakthrough opportunities exist at the intersection of {category1} and {category2}?",
            'disruption': "How might {category1} disrupt traditional {category2} paradigms?",
            'emerging_synergies': "What emerging synergies are developing between {category1} and {category2}?",
            
            # 16-20: Challenge and Problem-Solving Patterns
            'challenge': "What challenges arise when applying {category1} concepts to {category2} problems?",
            'conflict_resolution': "How can conflicts between {category1} and {category2} approaches be resolved in {context}?",
            'trade_offs': "What trade-offs must be considered when integrating {category1} and {category2}?",
            'complexity_management': "How can the complexity of combining {category1} and {category2} be managed?",
            'risk_assessment': "What risks and opportunities emerge when merging {category1} and {category2} methodologies?",
            
            # 21-25: Opportunity and Value Creation Patterns
            'opportunity': "What opportunities exist at the intersection of {category1} and {category2}?",
            'value_creation': "How can {category1} and {category2} work together to create greater value in {context}?",
            'competitive_advantage': "What competitive advantages can be gained by combining {category1} and {category2}?",
            'market_opportunity': "What market opportunities emerge from the convergence of {category1} and {category2}?",
            'strategic_alliance': "How can {category1} and {category2} form strategic alliances for {context}?",
            
            # 26-30: Advanced Synthesis and Meta-Analysis Patterns
            'meta_analysis': "What patterns emerge when analyzing the relationship between {category1} and {category2} across multiple projects?",
            'systems_thinking': "How do {category1} and {category2} interact as part of a larger system in {context}?",
            'emergent_properties': "What emergent properties arise when {category1} and {category2} are combined?",
            'paradigm_shift': "How might the integration of {category1} and {category2} lead to paradigm shifts in {context}?",
            'holistic_approach': "What holistic approaches can be developed by synthesizing {category1} and {category2} perspectives?"
        }
        
        # Context areas for cross-disciplinary questions (exactly 30 areas)
        self.context_areas = [
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
        
        # All 86 main themes
        self.main_categories = [
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
        self.subcategories = {
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
        
        # Theme relationship matrix (which themes work well together)
        self.category_relationships = {
            # Core Architectural Themes (7)
            'architecture': ['construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism', 'landscape_architecture', 'structural_engineering', 'digital_architecture', 'sustainability', 'materials', 'project_management'],
            'construction': ['architecture', 'engineering', 'structural_engineering', 'materials', 'project_management', 'bim_management', 'safety', 'quality_control', 'cost_management', 'sustainability', 'prefabrication', 'modular_construction'],
            'design': ['architecture', 'interiors', 'landscape_architecture', 'urbanism', 'visual_arts', 'graphic_design', 'industrial_design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'user_experience'],
            'engineering': ['architecture', 'construction', 'structural_engineering', 'materials', 'bim_management', 'mechanical_engineering', 'electrical_engineering', 'civil_engineering', 'safety', 'quality_control', 'performance_analysis', 'systems_integration'],
            'interiors': ['architecture', 'design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'materials', 'color_theory', 'textile_design', 'space_planning', 'user_experience', 'wellness_design'],
            'planning': ['urbanism', 'architecture', 'landscape_architecture', 'transportation', 'environmental_planning', 'community_development', 'social_impact', 'economic_development', 'infrastructure', 'zoning', 'public_policy', 'stakeholder_engagement'],
            'urbanism': ['planning', 'architecture', 'landscape_architecture', 'transportation', 'community_development', 'social_impact', 'smart_cities', 'public_spaces', 'urban_design', 'mobility', 'infrastructure', 'cultural_heritage']
        }
        
        # Cross-disciplinary themes (2,667 themes: 2,580 subcategory themes + 86 main theme themes + 1 all themes theme)
        self.cross_themes = {}
        
        # 1. Create themes from all 2,580 subcategories
        subcategory_themes = {}
        for main_category, subcategories in self.subcategories.items():
            for subcategory in subcategories:
                theme_name = f"{main_category}_{subcategory}"
                # Each subcategory theme includes the main theme plus related themes
                related_categories = self.get_category_relationships(main_category)
                theme_categories = [main_category] + related_categories[:11]  # 12 total themes
                subcategory_themes[theme_name] = theme_categories
        
        # 2. Create themes from all 86 main themes
        main_category_themes = {}
        for main_category in self.main_categories:
            theme_name = f"main_{main_category}"
            related_categories = self.get_category_relationships(main_category)
            theme_categories = [main_category] + related_categories[:11]  # 12 total themes
            main_category_themes[theme_name] = theme_categories
        
        # 3. Create "all themes" theme
        all_categories_theme = {
            'all_categories': self.main_categories
        }
        
        # Combine all themes
        self.cross_themes.update(subcategory_themes)  # 2,580 themes
        self.cross_themes.update(main_category_themes)  # 86 themes  
        self.cross_themes.update(all_categories_theme)  # 1 theme
        
        # Store theme counts for reference
        self.theme_counts = {
            'subcategory_themes': len(subcategory_themes),
            'main_category_themes': len(main_category_themes), 
            'all_categories_theme': 1,
            'total_themes': len(self.cross_themes)
        }
    
    def get_research_dimensions(self):
        """Get research dimensions"""
        return self.research_dimensions
        
    def get_categories_by_category(self, theme):
        """Get related themes for a given theme"""
        return get_related_categories(theme)
    
    def get_category_relationships(self, theme):
        """Get themes that work well with the given theme"""
        return self.category_relationships.get(theme, [])
    
    def get_cross_theme_categories(self, theme):
        """Get themes for a specific cross-disciplinary theme"""
        return self.cross_themes.get(theme, [])
    
    def generate_cross_disciplinary_question(self, primary_category, secondary_category=None, context=None):
        """Generate a cross-disciplinary question between two themes"""
        try:
            # If no secondary theme provided, find a good match
            if not secondary_category:
                related_categories = self.get_category_relationships(primary_category)
                if related_categories:
                    secondary_category = random.choice(related_categories)
                else:
                    # Fallback to a random theme
                    all_categories = list(self.category_relationships.keys())
                    secondary_category = random.choice([c for c in all_categories if c != primary_category])
            
            # If no context provided, choose a relevant one
            if not context:
                context = random.choice(self.context_areas)
            
            # Choose a question pattern
            pattern_type = random.choice(list(self.question_patterns.keys()))
            pattern = self.question_patterns[pattern_type]
            
            # Generate the question using the pattern
            question = pattern.format(
                category1=primary_category.replace('_', ' ').title(),
                category2=secondary_category.replace('_', ' ').title(),
                context=context
            )
            
            # Make it more specific and engaging
            question = self._enhance_question(question, primary_category, secondary_category, context)
            
            return {
                'question': question,
                'primary_category': primary_category,
                'secondary_category': secondary_category,
                'context': context,
                'pattern_type': pattern_type,
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating cross-disciplinary question: {e}")
            return None
    
    def generate_theme_based_question(self, theme):
        """Generate a question based on a cross-disciplinary theme with any number of themes"""
        try:
            themes = self.get_cross_theme_categories(theme)
            if len(themes) < 2:
                return None
            
            # Select 2-6 themes for the question (maximum flexibility)
            max_categories = min(6, len(themes))  # Cap at 6 for readability
            num_categories = random.randint(2, max_categories)
            selected_categories = random.sample(themes, num_categories)
            
            # Create a theme-specific question based on the number of themes
            question = self._create_multi_category_question(selected_categories, theme, num_categories)
            
            # Add theme-specific enhancements
            question = self._enhance_theme_question(question, theme, selected_categories)
            
            return {
                'question': question,
                'theme': theme,
                'themes': selected_categories,
                'num_categories': num_categories,
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating theme-based question: {e}")
            return None
    
    def _create_multi_category_question(self, themes, theme, num_categories):
        """Create questions for any number of themes (2-6)"""
        
        # Format theme names for display
        formatted_categories = [c.replace('_', ' ').title() for c in themes]
        theme_display = theme.replace('_', ' ').title()
        
        if num_categories == 2:
            return f"How do {formatted_categories[0]} and {formatted_categories[1]} work together in {theme_display}?"
        
        elif num_categories == 3:
            return f"What synergies emerge when combining {formatted_categories[0]}, {formatted_categories[1]}, and {formatted_categories[2]} for {theme_display}?"
        
        elif num_categories == 4:
            return f"How can the integration of {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} advance {theme_display}?"
        
        elif num_categories == 5:
            return f"What innovative solutions can be developed by synthesizing {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} approaches in {theme_display}?"
        
        else:  # 6 themes
            return f"How do {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} interact to address complex challenges in {theme_display}?"
    
    def generate_flexible_theme_question(self, theme, min_categories=2, max_categories=6):
        """Generate a theme-based question with specified theme range"""
        try:
            themes = self.get_cross_theme_categories(theme)
            if len(themes) < min_categories:
                return None
            
            # Select themes within the specified range
            available_max = min(max_categories, len(themes))
            if min_categories > available_max:
                min_categories = available_max
            
            num_categories = random.randint(min_categories, available_max)
            selected_categories = random.sample(themes, num_categories)
            
            # Create the question
            question = self._create_multi_category_question(selected_categories, theme, num_categories)
            question = self._enhance_theme_question(question, theme, selected_categories)
            
            return {
                'question': question,
                'theme': theme,
                'themes': selected_categories,
                'num_categories': num_categories,
                'category_range': f"{min_categories}-{max_categories}",
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating flexible theme question: {e}")
            return None
    
    def _enhance_question(self, question, category1, category2, context):
        """Make the question more specific and engaging"""
        enhancements = [
            f"Specifically, what are the practical implications of this intersection?",
            f"What real-world examples demonstrate this relationship?",
            f"How can this understanding improve our approach to {context}?",
            f"What challenges and opportunities does this combination present?",
            f"How might this integration lead to innovative solutions?"
        ]
        
        # Add a random enhancement
        if random.random() < 0.7:  # 70% chance to enhance
            enhancement = random.choice(enhancements)
            question += f" {enhancement}"
        
        return question
    
    def _enhance_theme_question(self, question, theme, selected_categories):
        """Make theme questions more specific"""
        enhancements = [
            f"What specific methodologies can be applied?",
            f"How do these themes complement each other?",
            f"What new approaches emerge from this combination?",
            f"How can we measure the impact of this integration?",
            f"What barriers exist and how can we overcome them?"
        ]
        
        if random.random() < 0.6:  # 60% chance to enhance
            enhancement = random.choice(enhancements)
            question += f" {enhancement}"
        
        return question

# Convenience functions
def generate_cross_disciplinary_question(primary_category, secondary_category=None, context=None):
    """Generate a cross-disciplinary question"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_cross_disciplinary_question(primary_category, secondary_category, context)

def generate_theme_based_question(theme):
    """Generate a theme-based cross-disciplinary question"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_theme_based_question(theme)

def generate_flexible_theme_question(theme, min_categories=2, max_categories=6):
    """Generate theme-based question with specified theme range"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_flexible_theme_question(theme, min_categories, max_categories)

def get_theme_counts():
    """Get counts of all theme types"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.theme_counts

def get_all_themes():
    """Get all available themes"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return list(generator.cross_themes.keys())

def get_all_categories():
    """Get all main themes"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.main_categories

def get_theme_categories(theme_name):
    """Get themes for a specific theme"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.cross_themes.get(theme_name, [])

def get_research_explorer():
    """Get enhanced cross-disciplinary generator instance"""
    return EnhancedCrossDisciplinaryGenerator()

# Placeholder functions for compatibility
def generate_synthesis_question_from_answers(answers, target_category):
    """Generate synthesis question from multiple answers"""
    return None

def get_cross_disciplinary_insights(question_data, answers):
    """Get cross-disciplinary insights"""
    return None

def analyze_research_direction(theme, current_questions, previous_insights=None):
    """Analyze research direction for a theme"""
    return None

def discover_cross_disciplinary_insights(categories_data):
    """Discover cross-disciplinary insights"""
    return None

def suggest_exploration_path(current_category, available_categories):
    """Suggest next exploration path"""
    return None

def get_research_summary():
    """Get research summary"""
    return None

def generate_intelligent_theme_question(research_context=None, current_questions=None):
    """Generate intelligent theme question based on research analysis"""
    return None

def get_category_for_question(question, available_categories=None):
    """Get best theme for a question"""
    return None
