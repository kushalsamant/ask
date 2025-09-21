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
import re
from typing import Optional, Dict, List

# Setup logging
log = logging.getLogger(__name__)

# Predefined question templates for offline generation
QUESTION_TEMPLATES = {
    'research_methodology': [
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
    ],
    'design_research': [
        "How can we research {design_concept} in {context}?",
        "What are the key methodologies for studying {design_element}?",
        "How does {research_method} contribute to {design_outcome}?",
        "What are the challenges of researching {design_topic}?",
        "How can {research_approach} improve {design_process}?",
        "What role does {research_methodology} play in {design_field}?",
        "How can we measure the effectiveness of {design_research}?",
        "What are the emerging trends in {design_research_field}?",
        "How does {research_finding} influence {design_practice}?",
        "What are the best practices for {design_research_method}?"
    ],
    'ure': [
        "How can we design {ural_concept} that responds to {design_challenge}?",
        "What are the key principles for {ural_element} in {context}?",
        "How does {ural_design} influence {building_outcome}?",
        "What are the emerging trends in {ural_approach} for {context}?",
        "How can {ural_system} be optimized for {performance_goal}?",
        "What role does {ural_consideration} play in {design_context}?",
        "How can we integrate {ural_feature} with {related_system}?",
        "What are the challenges of implementing {ural_solution} in {context}?",
        "How does {ural_concept} contribute to {sustainable_outcome}?",
        "What are the best practices for {ural_design} in {modern_context}?"
    ],
    'marketing': [
        "How can we develop {marketing_strategy} that targets {audience_segment}?",
        "What are the key principles for {marketing_campaign} in {market_context}?",
        "How does {marketing_approach} influence {consumer_behavior}?",
        "What are the emerging trends in {marketing_technology} for {industry}?",
        "How can {marketing_channel} be optimized for {business_goal}?",
        "What role does {marketing_concept} play in {brand_strategy}?",
        "How can we integrate {marketing_tool} with {customer_experience}?",
        "What are the challenges of implementing {marketing_solution} in {competitive_market}?",
        "How does {marketing_method} contribute to {business_outcome}?",
        "What are the best practices for {marketing_innovation} in {digital_age}?"
    ],
    'cricket': [
        "How can we improve {cricket_skill} through {training_method}?",
        "What are the key strategies for {cricket_tactic} in {match_situation}?",
        "How does {cricket_technique} influence {game_outcome}?",
        "What are the emerging trends in {cricket_technology} for {performance_improvement}?",
        "How can {cricket_equipment} be optimized for {player_advantage}?",
        "What role does {cricket_strategy} play in {team_performance}?",
        "How can we integrate {cricket_analysis} with {coaching_method}?",
        "What are the challenges of implementing {cricket_innovation} in {competitive_environment}?",
        "How does {cricket_methodology} contribute to {success_metric}?",
        "What are the best practices for {cricket_development} in {modern_era}?"
    ]
}

# Concept dictionaries for filling templates
CONCEPTS = {
    'concept': ['sustainable design', 'user-centered design', 'adaptive ure', 'biophilic design', 'modular systems', 'smart environments', 'resilient infrastructure', 'inclusive design', 'parametric design', 'generative design'],
    'challenge': ['climate change', 'urban density', 'resource scarcity', 'social inequality', 'technological disruption', 'environmental degradation', 'economic uncertainty', 'cultural diversity', 'aging population', 'digital transformation'],
    'context': ['urban environments', 'rural communities', 'coastal regions', 'mountain landscapes', 'desert climates', 'tropical zones', 'industrial areas', 'residential neighborhoods', 'commercial districts', 'public spaces'],
    'outcome': ['sustainability', 'resilience', 'efficiency', 'accessibility', 'well-being', 'productivity', 'creativity', 'social cohesion', 'economic growth', 'environmental protection'],
    'goal': ['carbon neutrality', 'zero waste', 'energy efficiency', 'social equity', 'economic prosperity', 'environmental restoration', 'community engagement', 'cultural preservation', 'technological advancement', 'sustainable development'],
    'related_concept': ['renewable energy', 'circular economy', 'smart cities', 'green infrastructure', 'digital twins', 'artificial intelligence', 'biotechnology', 'nanotechnology', 'robotics', 'virtual reality'],
    'technology': ['artificial intelligence', 'machine learning', 'blockchain', 'internet of things', 'augmented reality', '3D printing', 'robotics', 'drones', 'sensors', 'cloud computing'],
    'field': ['ure', 'urban planning', 'construction', 'engineering', 'design', 'manufacturing', 'healthcare', 'education', 'transportation', 'energy'],
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
    'innovation': ['automation', 'optimization', 'personalization', 'prediction', 'simulation', 'visualization', 'analysis', 'monitoring', 'control', 'communication'],
    'design_concept': ['sustainable design', 'user-centered design', 'adaptive ure', 'biophilic design', 'modular systems', 'smart environments', 'resilient infrastructure', 'inclusive design', 'parametric design', 'generative design'],
    'design_element': ['materials', 'forms', 'colors', 'textures', 'patterns', 'shapes', 'volumes', 'surfaces', 'openings', 'structures'],
    'research_method': ['case study', 'survey', 'interview', 'observation', 'experiment', 'simulation', 'prototyping', 'analysis', 'evaluation', 'testing'],
    'design_outcome': ['sustainability', 'resilience', 'efficiency', 'accessibility', 'well-being', 'productivity', 'creativity', 'social cohesion', 'economic growth', 'environmental protection'],
    'design_topic': ['climate change', 'urban density', 'resource scarcity', 'social inequality', 'technological disruption', 'environmental degradation', 'economic uncertainty', 'cultural diversity', 'aging population', 'digital transformation'],
    'research_approach': ['qualitative', 'quantitative', 'mixed-methods', 'participatory', 'evidence-based', 'action research', 'design thinking', 'systems thinking', 'human-centered', 'sustainable'],
    'design_process': ['concept development', 'schematic design', 'design development', 'construction documents', 'construction administration', 'post-occupancy evaluation', 'lifecycle assessment', 'stakeholder engagement', 'iterative refinement', 'continuous improvement'],
    'research_methodology': ['case study', 'survey research', 'experimental design', 'observational study', 'longitudinal study', 'cross-sectional study', 'comparative analysis', 'systematic review', 'meta-analysis', 'action research'],
    'design_field': ['ure', 'urban planning', 'interior design', 'landscape ure', 'industrial design', 'graphic design', 'fashion design', 'product design', 'service design', 'experience design'],
    'design_research': ['post-occupancy evaluation', 'behavioral research', 'environmental psychology', 'building performance', 'user experience', 'accessibility studies', 'sustainability assessment', 'cultural analysis', 'economic evaluation', 'social impact'],
    'design_research_field': ['environmental psychology', 'building science', 'urban sociology', 'design anthropology', 'ural history', 'construction technology', 'sustainable design', 'digital fabrication', 'smart cities', 'resilient design'],
    'research_finding': ['user preferences', 'environmental impact', 'economic benefits', 'social outcomes', 'technical performance', 'cultural significance', 'behavioral patterns', 'spatial relationships', 'material properties', 'system interactions'],
    'design_practice': ['ural design', 'urban planning', 'interior design', 'landscape design', 'construction management', 'project coordination', 'stakeholder engagement', 'sustainability consulting', 'research collaboration', 'knowledge sharing'],
    'design_research_method': ['post-occupancy evaluation', 'behavioral mapping', 'environmental monitoring', 'user interviews', 'focus groups', 'surveys', 'observational studies', 'case studies', 'experimental design', 'participatory research'],
    'ural_concept': ['sustainable ure', 'modern design', 'classical ure', 'vernacular building', 'adaptive reuse', 'modular construction', 'parametric design', 'biophilic ure', 'smart buildings', 'resilient design'],
    'ural_element': ['facade', 'roof', 'foundation', 'structural system', 'building envelope', 'interior space', 'circulation', 'lighting', 'acoustics', 'thermal mass'],
    'ural_design': ['sustainable building', 'modern structure', 'classical building', 'vernacular ure', 'adaptive design', 'modular building', 'parametric structure', 'biophilic building', 'smart ure', 'resilient structure'],
    'building_outcome': ['energy efficiency', 'thermal comfort', 'acoustic quality', 'daylighting', 'ventilation', 'structural integrity', 'aesthetic appeal', 'functional performance', 'sustainability', 'user satisfaction'],
    'ural_approach': ['sustainable design', 'modern ure', 'classical design', 'vernacular approach', 'adaptive ure', 'modular design', 'parametric approach', 'biophilic design', 'smart ure', 'resilient design'],
    'ural_system': ['structural system', 'mechanical system', 'electrical system', 'plumbing system', 'HVAC system', 'lighting system', 'acoustic system', 'security system', 'communication system', 'fire protection system'],
    'ural_consideration': ['structural integrity', 'energy efficiency', 'thermal comfort', 'acoustic quality', 'daylighting', 'ventilation', 'sustainability', 'accessibility', 'safety', 'aesthetics'],
    'ural_feature': ['green roof', 'solar panels', 'rainwater harvesting', 'natural ventilation', 'daylighting', 'thermal mass', 'shading devices', 'living walls', 'smart controls', 'renewable energy'],
    'ural_solution': ['passive design', 'active systems', 'hybrid approach', 'adaptive reuse', 'modular construction', 'prefabrication', 'green building', 'smart technology', 'renewable energy', 'sustainable materials'],
    'sustainable_outcome': ['carbon neutrality', 'zero waste', 'energy efficiency', 'water conservation', 'biodiversity protection', 'circular economy', 'green building', 'sustainable transport', 'clean energy', 'climate resilience'],
    'modern_context': ['digital transformation', 'climate change', 'urbanization', 'technological advancement', 'social change', 'economic development', 'environmental awareness', 'sustainability goals', 'smart cities', 'resilient communities'],
    'marketing_strategy': ['digital marketing', 'content marketing', 'social media marketing', 'email marketing', 'influencer marketing', 'viral marketing', 'guerilla marketing', 'relationship marketing', 'direct marketing', 'integrated marketing'],
    'audience_segment': ['millennials', 'gen z', 'baby boomers', 'professionals', 'students', 'parents', 'tech enthusiasts', 'environmentalists', 'urban dwellers', 'rural communities'],
    'marketing_campaign': ['brand awareness', 'product launch', 'seasonal promotion', 'holiday campaign', 'social cause', 'loyalty program', 'referral program', 'educational content', 'thought leadership', 'community engagement'],
    'market_context': ['competitive landscape', 'economic conditions', 'social trends', 'technological changes', 'regulatory environment', 'cultural shifts', 'demographic changes', 'consumer behavior', 'industry dynamics', 'global markets'],
    'marketing_approach': ['data-driven', 'customer-centric', 'storytelling', 'experiential', 'personalized', 'omnichannel', 'agile', 'sustainable', 'ethical', 'innovative'],
    'consumer_behavior': ['purchasing decisions', 'brand loyalty', 'online shopping', 'social influence', 'price sensitivity', 'quality preference', 'convenience seeking', 'status consciousness', 'environmental awareness', 'technology adoption'],
    'marketing_technology': ['artificial intelligence', 'machine learning', 'big data analytics', 'customer relationship management', 'marketing automation', 'social media platforms', 'email marketing tools', 'content management systems', 'search engine optimization', 'pay-per-click advertising'],
    'business_goal': ['revenue growth', 'market share', 'brand awareness', 'customer acquisition', 'customer retention', 'profitability', 'market expansion', 'product development', 'competitive advantage', 'sustainability'],
    'marketing_concept': ['brand positioning', 'target audience', 'value proposition', 'customer journey', 'touchpoints', 'conversion funnel', 'customer lifetime value', 'brand equity', 'market segmentation', 'competitive differentiation'],
    'brand_strategy': ['brand identity', 'brand positioning', 'brand messaging', 'brand values', 'brand personality', 'brand voice', 'brand guidelines', 'brand ure', 'brand extension', 'brand revitalization'],
    'marketing_tool': ['social media platforms', 'email marketing software', 'content management systems', 'analytics tools', 'customer relationship management', 'marketing automation', 'advertising platforms', 'survey tools', 'influencer platforms', 'seo tools'],
    'customer_experience': ['user journey', 'touchpoints', 'interactions', 'satisfaction', 'loyalty', 'engagement', 'personalization', 'convenience', 'quality', 'support'],
    'competitive_market': ['saturated market', 'emerging market', 'mature market', 'niche market', 'global market', 'local market', 'online market', 'offline market', 'b2b market', 'b2c market'],
    'marketing_method': ['digital marketing', 'traditional advertising', 'public relations', 'direct marketing', 'event marketing', 'content marketing', 'social media marketing', 'email marketing', 'influencer marketing', 'viral marketing'],
    'business_outcome': ['revenue growth', 'profitability', 'market share', 'customer acquisition', 'customer retention', 'brand awareness', 'competitive advantage', 'operational efficiency', 'innovation', 'sustainability'],
    'marketing_innovation': ['artificial intelligence', 'virtual reality', 'augmented reality', 'blockchain', 'voice search', 'chatbots', 'personalization', 'automation', 'data analytics', 'social commerce'],
    'digital_age': ['online presence', 'mobile-first', 'social media', 'e-commerce', 'digital transformation', 'automation', 'data-driven', 'personalization', 'omnichannel', 'technology integration'],
    'cricket_skill': ['batting', 'bowling', 'fielding', 'wicket-keeping', 'captaincy', 'team coordination', 'mental strength', 'physical fitness', 'tactical awareness', 'technical proficiency'],
    'training_method': ['practice sessions', 'fitness training', 'mental conditioning', 'video analysis', 'simulation exercises', 'match practice', 'skill development', 'strength training', 'endurance training', 'recovery protocols'],
    'cricket_tactic': ['batting strategy', 'bowling plan', 'field placement', 'run chase', 'defense', 'aggressive play', 'conservative approach', 'risk management', 'momentum building', 'pressure handling'],
    'match_situation': ['run chase', 'defending total', 'power play', 'death overs', 'test match', 'limited overs', 't20 format', 'one day international', 'domestic cricket', 'international cricket'],
    'cricket_technique': ['cover drive', 'pull shot', 'yorker', 'googly', 'sweep shot', 'reverse swing', 'spin bowling', 'fast bowling', 'fielding technique', 'wicket-keeping stance'],
    'game_outcome': ['victory', 'defeat', 'draw', 'tie', 'winning margin', 'run rate', 'wicket haul', 'century', 'five-wicket haul', 'man of the match'],
    'cricket_technology': ['hawk-eye', 'hot spot', 'snickometer', 'ball tracking', 'performance analytics', 'biomechanical analysis', 'video technology', 'sensor technology', 'data analytics', 'virtual reality training'],
    'performance_improvement': ['batting average', 'bowling economy', 'fielding efficiency', 'team performance', 'individual skills', 'match awareness', 'decision making', 'pressure handling', 'fitness levels', 'technical skills'],
    'cricket_equipment': ['bat', 'ball', 'protective gear', 'stumps', 'bails', 'sight screen', 'boundary rope', 'scoreboard', 'communication devices', 'training equipment'],
    'player_advantage': ['better performance', 'injury prevention', 'comfort', 'confidence', 'safety', 'efficiency', 'accuracy', 'power', 'control', 'endurance'],
    'cricket_strategy': ['batting order', 'bowling rotation', 'field placement', 'run chase plan', 'defense strategy', 'aggressive tactics', 'conservative approach', 'risk assessment', 'momentum management', 'pressure handling'],
    'team_performance': ['winning percentage', 'team ranking', 'championship success', 'consistency', 'adaptability', 'team chemistry', 'leadership effectiveness', 'skill balance', 'experience level', 'fitness standards'],
    'cricket_analysis': ['performance data', 'match statistics', 'opponent study', 'pitch conditions', 'weather factors', 'historical trends', 'player form', 'team dynamics', 'tactical patterns', 'success metrics'],
    'coaching_method': ['technical coaching', 'tactical guidance', 'mental preparation', 'fitness training', 'video analysis', 'match simulation', 'skill development', 'team building', 'leadership training', 'performance monitoring'],
    'cricket_innovation': ['new formats', 'technology integration', 'training methods', 'equipment design', 'tactical approaches', 'performance analysis', 'fan engagement', 'broadcasting technology', 'safety measures', 'sustainability practices'],
    'competitive_environment': ['international cricket', 'domestic leagues', 'championship tournaments', 'test series', 'limited overs cricket', 't20 leagues', 'world cups', 'bilateral series', 'multi-nation tournaments', 'qualification events'],
    'cricket_methodology': ['training approach', 'coaching philosophy', 'team selection', 'match preparation', 'performance analysis', 'skill development', 'fitness management', 'mental conditioning', 'tactical planning', 'leadership development'],
    'success_metric': ['winning percentage', 'individual records', 'team achievements', 'championship titles', 'ranking improvements', 'performance consistency', 'skill development', 'team chemistry', 'leadership effectiveness', 'fan engagement'],
    'cricket_development': ['youth programs', 'grassroots initiatives', 'talent identification', 'skill development', 'coaching education', 'infrastructure improvement', 'technology integration', 'safety measures', 'sustainability practices', 'global expansion'],
    'modern_era': ['professional cricket', 'technology integration', 'global leagues', 'performance analytics', 'fan engagement', 'broadcasting innovation', 'safety standards', 'sustainability practices', 'diversity inclusion', 'commercial development']
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
