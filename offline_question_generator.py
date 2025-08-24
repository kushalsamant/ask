#!/usr/bin/env python3
"""
Offline Question Generator Module
Provides question generation without requiring API access

This module provides functionality to:
- Generate questions from predefined templates
- Work completely offline
- Support all research themes
- Provide fallback questions when API is unavailable

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 1.0 (Offline-First)
"""

import random
import logging
from typing import Optional, Dict, List

# Setup logging
log = logging.getLogger(__name__)

# Predefined question templates for offline generation
QUESTION_TEMPLATES = {
    'design_research': [
        "How can we design {concept} that responds to {challenge}?",
        "What are the key principles for {concept} in {context}?",
        "How does {concept} influence {outcome} in {context}?",
        "What are the emerging trends in {concept} for {context}?",
        "How can {concept} be optimized for {goal}?",
        "What role does {concept} play in {context}?",
        "How can we integrate {concept} with {related_concept}?",
        "What are the challenges of implementing {concept} in {context}?",
        "How does {concept} contribute to {outcome}?",
        "What are the best practices for {concept} in {context}?"
    ],
    'technology_innovation': [
        "How can {technology} revolutionize {field}?",
        "What are the implications of {technology} for {context}?",
        "How does {technology} enable {capability}?",
        "What are the challenges of adopting {technology} in {context}?",
        "How can {technology} improve {process}?",
        "What role does {technology} play in {trend}?",
        "How can we leverage {technology} for {goal}?",
        "What are the ethical considerations of {technology}?",
        "How does {technology} transform {industry}?",
        "What are the future applications of {technology}?"
    ],
    'sustainability_science': [
        "How can we achieve {sustainability_goal} through {approach}?",
        "What are the environmental impacts of {practice}?",
        "How does {sustainability_concept} contribute to {outcome}?",
        "What are the challenges of implementing {sustainable_solution}?",
        "How can {technology} support {sustainability_goal}?",
        "What role does {sustainability_concept} play in {context}?",
        "How can we measure the effectiveness of {sustainable_practice}?",
        "What are the economic benefits of {sustainable_approach}?",
        "How does {sustainability_concept} address {environmental_challenge}?",
        "What are the social implications of {sustainable_solution}?"
    ],
    'engineering_systems': [
        "How can we optimize {system} for {performance_goal}?",
        "What are the key components of {system} in {context}?",
        "How does {system} integrate with {related_system}?",
        "What are the failure modes of {system} and how can we prevent them?",
        "How can we scale {system} for {application}?",
        "What are the design principles for {system} in {environment}?",
        "How does {system} respond to {external_factor}?",
        "What are the maintenance requirements for {system}?",
        "How can we improve the efficiency of {system}?",
        "What are the safety considerations for {system}?"
    ],
    'environmental_design': [
        "How can we design {space} to respond to {environmental_factor}?",
        "What are the principles of {environmental_concept} in {context}?",
        "How does {design_element} contribute to {environmental_goal}?",
        "What are the challenges of implementing {environmental_solution}?",
        "How can {material} enhance {environmental_performance}?",
        "What role does {design_strategy} play in {environmental_context}?",
        "How can we measure the environmental impact of {design_decision}?",
        "What are the benefits of {environmental_approach} in {context}?",
        "How does {environmental_concept} address {climate_challenge}?",
        "What are the long-term effects of {environmental_design}?"
    ],
    'urban_planning': [
        "How can we plan {urban_element} to support {community_goal}?",
        "What are the key considerations for {urban_development} in {context}?",
        "How does {urban_strategy} impact {community_outcome}?",
        "What are the challenges of implementing {urban_solution}?",
        "How can {urban_technology} improve {city_function}?",
        "What role does {urban_concept} play in {city_context}?",
        "How can we measure the success of {urban_initiative}?",
        "What are the social benefits of {urban_approach}?",
        "How does {urban_planning} address {urban_challenge}?",
        "What are the economic implications of {urban_strategy}?"
    ],
    'spatial_design': [
        "How can we design {space} to enhance {user_experience}?",
        "What are the principles of {spatial_concept} in {context}?",
        "How does {spatial_element} influence {behavior}?",
        "What are the challenges of creating {spatial_solution}?",
        "How can {spatial_strategy} improve {function}?",
        "What role does {spatial_consideration} play in {design_context}?",
        "How can we optimize {space} for {purpose}?",
        "What are the psychological effects of {spatial_design}?",
        "How does {spatial_concept} address {design_challenge}?",
        "What are the cultural implications of {spatial_approach}?"
    ],
    'digital_technology': [
        "How can {digital_technology} enhance {process}?",
        "What are the implications of {digital_concept} for {field}?",
        "How does {digital_solution} improve {capability}?",
        "What are the challenges of implementing {digital_technology}?",
        "How can {digital_approach} transform {industry}?",
        "What role does {digital_concept} play in {modern_context}?",
        "How can we leverage {digital_technology} for {goal}?",
        "What are the security considerations of {digital_solution}?",
        "How does {digital_technology} enable {innovation}?",
        "What are the future applications of {digital_concept}?"
    ]
}

# Concept dictionaries for filling templates
CONCEPTS = {
    'concept': ['sustainable design', 'user-centered design', 'adaptive architecture', 'biophilic design', 'modular systems', 'smart environments', 'resilient infrastructure', 'inclusive design', 'parametric design', 'generative design'],
    'challenge': ['climate change', 'urban density', 'resource scarcity', 'social inequality', 'technological disruption', 'environmental degradation', 'economic uncertainty', 'cultural diversity', 'aging population', 'digital transformation'],
    'context': ['urban environments', 'rural communities', 'coastal regions', 'mountain landscapes', 'desert climates', 'tropical zones', 'industrial areas', 'residential neighborhoods', 'commercial districts', 'public spaces'],
    'outcome': ['sustainability', 'resilience', 'efficiency', 'accessibility', 'well-being', 'productivity', 'creativity', 'social cohesion', 'economic growth', 'environmental protection'],
    'goal': ['carbon neutrality', 'zero waste', 'energy efficiency', 'social equity', 'economic prosperity', 'environmental restoration', 'community engagement', 'cultural preservation', 'technological advancement', 'sustainable development'],
    'related_concept': ['renewable energy', 'circular economy', 'smart cities', 'green infrastructure', 'digital twins', 'artificial intelligence', 'biotechnology', 'nanotechnology', 'robotics', 'virtual reality'],
    'technology': ['artificial intelligence', 'machine learning', 'blockchain', 'internet of things', 'augmented reality', '3D printing', 'robotics', 'drones', 'sensors', 'cloud computing'],
    'field': ['architecture', 'urban planning', 'construction', 'engineering', 'design', 'manufacturing', 'healthcare', 'education', 'transportation', 'energy'],
    'capability': ['automation', 'optimization', 'prediction', 'simulation', 'visualization', 'analysis', 'monitoring', 'control', 'communication', 'collaboration'],
    'trend': ['digital transformation', 'sustainability', 'automation', 'personalization', 'connectivity', 'mobility', 'health', 'education', 'entertainment', 'work'],
    'industry': ['construction', 'manufacturing', 'healthcare', 'education', 'transportation', 'energy', 'retail', 'finance', 'entertainment', 'agriculture'],
    'sustainability_goal': ['carbon neutrality', 'zero waste', 'renewable energy', 'water conservation', 'biodiversity protection', 'circular economy', 'green building', 'sustainable transport', 'clean energy', 'climate resilience'],
    'approach': ['biophilic design', 'passive design', 'renewable energy', 'water harvesting', 'green materials', 'adaptive reuse', 'modular construction', 'smart systems', 'community engagement', 'lifecycle assessment'],
    'practice': ['conventional construction', 'linear economy', 'fossil fuel use', 'single-use materials', 'car-dependent design', 'energy-intensive processes', 'wasteful consumption', 'environmental degradation', 'social exclusion', 'economic inequality'],
    'sustainability_concept': ['biophilic design', 'circular economy', 'green infrastructure', 'renewable energy', 'sustainable materials', 'passive design', 'adaptive reuse', 'community resilience', 'environmental justice', 'regenerative design'],
    'sustainable_solution': ['green roofs', 'solar panels', 'rainwater harvesting', 'composting systems', 'bike lanes', 'public transit', 'community gardens', 'renewable energy', 'green building', 'sustainable transport'],
    'sustainable_practice': ['recycling', 'composting', 'energy conservation', 'water saving', 'green building', 'sustainable transport', 'local sourcing', 'waste reduction', 'renewable energy', 'biodiversity protection'],
    'sustainable_approach': ['biophilic design', 'circular economy', 'green infrastructure', 'renewable energy', 'sustainable materials', 'passive design', 'adaptive reuse', 'community resilience', 'environmental justice', 'regenerative design'],
    'environmental_challenge': ['climate change', 'biodiversity loss', 'pollution', 'resource depletion', 'waste accumulation', 'air quality', 'water scarcity', 'soil degradation', 'ocean acidification', 'deforestation'],
    'system': ['building automation', 'energy management', 'water systems', 'waste management', 'transportation', 'communication', 'security', 'climate control', 'lighting', 'ventilation'],
    'performance_goal': ['energy efficiency', 'cost reduction', 'reliability', 'safety', 'comfort', 'productivity', 'sustainability', 'accessibility', 'flexibility', 'durability'],
    'related_system': ['electrical systems', 'mechanical systems', 'plumbing systems', 'structural systems', 'communication systems', 'security systems', 'fire protection', 'HVAC systems', 'lighting systems', 'acoustic systems'],
    'application': ['residential buildings', 'commercial spaces', 'industrial facilities', 'public infrastructure', 'healthcare facilities', 'educational institutions', 'transportation hubs', 'recreational areas', 'cultural venues', 'mixed-use developments'],
    'environment': ['urban areas', 'rural settings', 'coastal regions', 'mountain terrain', 'desert climates', 'tropical zones', 'industrial sites', 'residential neighborhoods', 'commercial districts', 'natural landscapes'],
    'external_factor': ['climate change', 'population growth', 'technological advancement', 'economic fluctuations', 'social changes', 'regulatory requirements', 'market demands', 'environmental conditions', 'cultural shifts', 'political factors'],
    'space': ['buildings', 'parks', 'streets', 'plazas', 'interiors', 'landscapes', 'neighborhoods', 'districts', 'cities', 'regions'],
    'environmental_factor': ['climate', 'topography', 'vegetation', 'water', 'wind', 'sunlight', 'noise', 'air quality', 'biodiversity', 'geology'],
    'design_element': ['materials', 'forms', 'colors', 'textures', 'patterns', 'shapes', 'volumes', 'surfaces', 'openings', 'structures'],
    'environmental_performance': ['energy efficiency', 'thermal comfort', 'acoustic quality', 'daylighting', 'ventilation', 'water efficiency', 'waste reduction', 'carbon footprint', 'biodiversity', 'resilience'],
    'design_strategy': ['passive design', 'biophilic design', 'adaptive reuse', 'modular construction', 'prefabrication', 'green building', 'sustainable materials', 'renewable energy', 'water conservation', 'waste management'],
    'environmental_context': ['urban areas', 'natural landscapes', 'coastal regions', 'mountain terrain', 'desert climates', 'tropical zones', 'industrial sites', 'agricultural land', 'forests', 'wetlands'],
    'design_decision': ['material selection', 'orientation', 'form', 'size', 'location', 'technology', 'systems', 'finishes', 'furniture', 'landscaping'],
    'climate_challenge': ['global warming', 'extreme weather', 'sea level rise', 'drought', 'flooding', 'heat waves', 'storms', 'air pollution', 'water scarcity', 'biodiversity loss'],
    'environmental_design': ['green building', 'sustainable landscape', 'eco-friendly interior', 'biophilic design', 'passive design', 'adaptive reuse', 'modular construction', 'renewable energy', 'water conservation', 'waste management'],
    'urban_element': ['neighborhoods', 'districts', 'streets', 'parks', 'plazas', 'buildings', 'infrastructure', 'transportation', 'public spaces', 'green spaces'],
    'community_goal': ['social equity', 'economic prosperity', 'environmental sustainability', 'public health', 'safety', 'accessibility', 'cultural diversity', 'community engagement', 'quality of life', 'resilience'],
    'urban_development': ['mixed-use projects', 'transit-oriented development', 'green infrastructure', 'affordable housing', 'commercial districts', 'industrial areas', 'recreational facilities', 'cultural venues', 'educational institutions', 'healthcare facilities'],
    'community_outcome': ['social cohesion', 'economic growth', 'environmental protection', 'public health', 'safety', 'accessibility', 'cultural diversity', 'community engagement', 'quality of life', 'resilience'],
    'urban_solution': ['transit-oriented development', 'green infrastructure', 'affordable housing', 'mixed-use development', 'pedestrian-friendly design', 'bike lanes', 'public transit', 'parks', 'community centers', 'smart cities'],
    'urban_technology': ['smart sensors', 'data analytics', 'mobile apps', 'digital platforms', 'automated systems', 'renewable energy', 'electric vehicles', 'shared mobility', 'digital twins', 'artificial intelligence'],
    'city_function': ['transportation', 'energy management', 'waste management', 'public safety', 'healthcare', 'education', 'commerce', 'entertainment', 'governance', 'communication'],
    'urban_concept': ['smart cities', 'sustainable development', 'resilient cities', 'inclusive design', 'green infrastructure', 'transit-oriented development', 'mixed-use development', 'pedestrian-friendly design', 'bike-friendly cities', 'climate-adaptive cities'],
    'city_context': ['dense urban areas', 'suburban communities', 'rural-urban fringe', 'historic districts', 'industrial areas', 'commercial centers', 'residential neighborhoods', 'cultural districts', 'educational campuses', 'transportation hubs'],
    'urban_initiative': ['bike share programs', 'green building codes', 'renewable energy projects', 'public transit expansion', 'park development', 'affordable housing programs', 'smart city projects', 'climate action plans', 'community engagement programs', 'cultural preservation efforts'],
    'urban_approach': ['participatory planning', 'evidence-based design', 'sustainable development', 'smart city technology', 'green infrastructure', 'transit-oriented development', 'mixed-use development', 'pedestrian-friendly design', 'bike-friendly design', 'climate-adaptive planning'],
    'urban_challenge': ['traffic congestion', 'air pollution', 'housing affordability', 'social inequality', 'climate change', 'aging infrastructure', 'population growth', 'economic development', 'public health', 'safety'],
    'urban_strategy': ['transit-oriented development', 'green infrastructure', 'affordable housing', 'mixed-use development', 'pedestrian-friendly design', 'bike lanes', 'public transit', 'smart city technology', 'climate adaptation', 'community engagement'],
    'user_experience': ['comfort', 'efficiency', 'safety', 'accessibility', 'well-being', 'productivity', 'creativity', 'social interaction', 'learning', 'entertainment'],
    'spatial_concept': ['flow', 'hierarchy', 'rhythm', 'balance', 'proportion', 'scale', 'unity', 'variety', 'emphasis', 'harmony'],
    'behavior': ['movement', 'interaction', 'communication', 'learning', 'work', 'relaxation', 'socialization', 'exploration', 'creation', 'reflection'],
    'spatial_solution': ['open floor plans', 'flexible spaces', 'multi-functional areas', 'adaptive environments', 'smart spaces', 'biophilic design', 'ergonomic layouts', 'accessible design', 'sustainable spaces', 'technology-integrated environments'],
    'function': ['work', 'learning', 'living', 'entertainment', 'socialization', 'relaxation', 'exercise', 'cooking', 'sleeping', 'storage'],
    'spatial_consideration': ['lighting', 'acoustics', 'ventilation', 'temperature', 'privacy', 'accessibility', 'safety', 'aesthetics', 'functionality', 'sustainability'],
    'purpose': ['collaboration', 'focus', 'creativity', 'relaxation', 'socialization', 'learning', 'work', 'entertainment', 'exercise', 'storage'],
    'spatial_design': ['open layouts', 'flexible spaces', 'multi-functional areas', 'adaptive environments', 'smart spaces', 'biophilic design', 'ergonomic layouts', 'accessible design', 'sustainable spaces', 'technology-integrated environments'],
    'design_challenge': ['limited space', 'budget constraints', 'technical requirements', 'user needs', 'sustainability goals', 'accessibility requirements', 'safety regulations', 'aesthetic preferences', 'functional requirements', 'environmental conditions'],
    'spatial_approach': ['user-centered design', 'evidence-based design', 'sustainable design', 'inclusive design', 'adaptive design', 'smart design', 'biophilic design', 'ergonomic design', 'accessible design', 'technology-integrated design'],
    'process': ['design', 'construction', 'manufacturing', 'communication', 'collaboration', 'decision-making', 'problem-solving', 'innovation', 'research', 'development'],
    'digital_concept': ['artificial intelligence', 'machine learning', 'big data', 'cloud computing', 'internet of things', 'blockchain', 'augmented reality', 'virtual reality', 'cybersecurity', 'digital twins'],
    'modern_context': ['digital transformation', 'remote work', 'e-commerce', 'smart cities', 'connected devices', 'social media', 'online education', 'telemedicine', 'digital entertainment', 'fintech'],
    'innovation': ['automation', 'optimization', 'personalization', 'prediction', 'simulation', 'visualization', 'analysis', 'monitoring', 'control', 'communication']
}

def generate_offline_question(theme: str) -> Optional[str]:
    """
    Generate a question offline using predefined templates
    
    Args:
        theme (str): Theme name for question generation
        
    Returns:
        str: Generated question or None if failed
    """
    try:
        # Normalize theme name
        theme = theme.lower().replace(' ', '_')
        
        # Get templates for theme
        if theme not in QUESTION_TEMPLATES:
            log.warning(f"No templates available for theme: {theme}")
            return None
        
        templates = QUESTION_TEMPLATES[theme]
        
        # Select random template
        template = random.choice(templates)
        
        # Fill template with random concepts
        question = template
        for placeholder, concepts in CONCEPTS.items():
            if placeholder in question:
                concept = random.choice(concepts)
                question = question.replace(f"{{{placeholder}}}", concept)
        
        # Clean up any remaining placeholders
        import re
        question = re.sub(r'\{[^}]+\}', 'sustainable design', question)
        
        log.info(f"Generated offline question for theme '{theme}': {question}")
        return question
        
    except Exception as e:
        log.error(f"Error generating offline question for theme '{theme}': {e}")
        return None

def generate_single_question_for_category(theme: str) -> Optional[str]:
    """
    Generate a single research question for a specific theme (offline version)
    
    Args:
        theme (str): Theme name for question generation
        
    Returns:
        str: Generated question or None if failed
    """
    return generate_offline_question(theme)
