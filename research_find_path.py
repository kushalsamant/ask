#!/usr/bin/env python3
"""
Enhanced Cross-Disciplinary Generator with Research Explorer Integration
Creates intelligent cross-disciplinary questions and analyzes research directions
"""

import os
import logging
import random
import requests
from datetime import datetime
from collections import defaultdict, Counter

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
            'temporal': ['historical', 'contemporary', 'future', 'evolutionary'],
            'spatial': ['urban', 'rural', 'global', 'local', 'regional'],
            'thematic': ['sustainability', 'technology', 'culture', 'economics', 'social'],
            'methodological': ['analytical', 'creative', 'experimental', 'theoretical', 'practical'],
            'scale': ['micro', 'meso', 'macro', 'mega'],
            'context': ['environmental', 'social', 'political', 'economic', 'cultural']
        }
        
        self.exploration_patterns = {
            'cross_pollination': 'Connecting insights across categories',
            'temporal_analysis': 'Examining evolution and trends over time',
            'spatial_mapping': 'Understanding geographical and contextual variations',
            'thematic_synthesis': 'Identifying common themes and patterns',
            'methodological_experimentation': 'Exploring different research approaches',
            'scale_transformation': 'Understanding how concepts work at different scales'
        }
        
        self.research_insights = []
        self.exploration_history = []
        
    def get_research_dimensions(self):
        """Get research dimensions"""
        return self.research_dimensions
        
    def get_categories_by_category(self, category):
        """Get related categories for a given category"""
        from research_categories_data import get_related_categories
        return get_related_categories(category)
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
        
        # All 86 main categories
        self.main_categories = [
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
        self.subcategories = {
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
        self.category_relationships = {
            # Core Architectural Categories (7)
            'architecture': ['construction', 'design', 'engineering', 'interiors', 'planning', 'urbanism', 'landscape_architecture', 'structural_engineering', 'digital_architecture', 'sustainability', 'materials', 'project_management'],
            'construction': ['architecture', 'engineering', 'structural_engineering', 'materials', 'project_management', 'bim_management', 'safety', 'quality_control', 'cost_management', 'sustainability', 'prefabrication', 'modular_construction'],
            'design': ['architecture', 'interiors', 'landscape_architecture', 'urbanism', 'visual_arts', 'graphic_design', 'industrial_design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'user_experience'],
            'engineering': ['architecture', 'construction', 'structural_engineering', 'materials', 'bim_management', 'mechanical_engineering', 'electrical_engineering', 'civil_engineering', 'safety', 'quality_control', 'performance_analysis', 'systems_integration'],
            'interiors': ['architecture', 'design', 'furniture_design', 'lighting_design', 'acoustics', 'ergonomics', 'materials', 'color_theory', 'textile_design', 'space_planning', 'user_experience', 'wellness_design'],
            'planning': ['urbanism', 'architecture', 'landscape_architecture', 'transportation', 'environmental_planning', 'community_development', 'social_impact', 'economic_development', 'infrastructure', 'zoning', 'public_policy', 'stakeholder_engagement'],
            'urbanism': ['planning', 'architecture', 'landscape_architecture', 'transportation', 'community_development', 'social_impact', 'smart_cities', 'public_spaces', 'urban_design', 'mobility', 'infrastructure', 'cultural_heritage'],
            
            # Specialized Architectural Categories (18)
            'landscape_architecture': ['architecture', 'planning', 'urbanism', 'environmental_design', 'horticulture', 'ecology', 'sustainability', 'public_spaces', 'site_planning', 'stormwater_management', 'biodiversity', 'recreation_design'],
            'structural_engineering': ['architecture', 'construction', 'engineering', 'materials', 'safety', 'performance_analysis', 'seismic_design', 'foundation_design', 'structural_analysis', 'load_calculation', 'building_codes', 'risk_assessment'],
            'digital_architecture': ['architecture', 'computational_design', 'bim_management', 'virtual_reality', 'ai_in_architecture', 'parametric_design', 'digital_fabrication', '3d_modeling', 'simulation', 'data_visualization', 'algorithmic_design', 'cyber_physical_systems'],
            'computational_design': ['digital_architecture', 'parametric_design', 'algorithmic_design', 'ai_in_architecture', 'optimization', 'simulation', 'data_analysis', 'machine_learning', 'generative_design', 'digital_fabrication', 'complex_geometry', 'performance_driven_design'],
            'parametric_design': ['computational_design', 'digital_architecture', 'algorithmic_design', 'complex_geometry', 'optimization', 'digital_fabrication', 'performance_driven_design', 'mass_customization', 'adaptive_systems', 'responsive_design', 'form_finding', 'structural_optimization'],
            'ai_in_architecture': ['digital_architecture', 'computational_design', 'machine_learning', 'data_analysis', 'predictive_modeling', 'automation', 'smart_buildings', 'optimization', 'pattern_recognition', 'decision_support', 'generative_ai', 'cognitive_computing'],
            'virtual_reality': ['digital_architecture', 'visualization', 'user_experience', 'interactive_design', 'immersive_environments', 'spatial_computing', 'augmented_reality', 'mixed_reality', 'digital_twin', 'simulation', 'training', 'presentation'],
            'augmented_reality': ['virtual_reality', 'digital_architecture', 'spatial_computing', 'interactive_design', 'mobile_technology', 'visualization', 'real_time_data', 'context_awareness', 'user_interface', 'wearable_technology', 'smart_glasses', 'holographic_display'],
            'smart_cities': ['urbanism', 'planning', 'digital_architecture', 'iot_infrastructure', 'sustainability', 'data_analytics', 'urban_planning', 'transportation', 'energy_management', 'public_services', 'citizen_engagement', 'resilient_infrastructure'],
            'iot_infrastructure': ['smart_cities', 'digital_architecture', 'sensor_networks', 'data_collection', 'real_time_monitoring', 'automation', 'connectivity', 'edge_computing', 'wireless_communication', 'smart_buildings', 'urban_analytics', 'predictive_maintenance'],
            'sustainability': ['architecture', 'construction', 'materials', 'energy_efficiency', 'environmental_design', 'green_building', 'lifecycle_assessment', 'carbon_footprint', 'renewable_energy', 'water_conservation', 'waste_reduction', 'biophilic_design'],
            'energy_efficiency': ['sustainability', 'building_performance', 'mechanical_engineering', 'electrical_engineering', 'renewable_energy', 'smart_buildings', 'energy_modeling', 'passive_design', 'building_envelope', 'hvac_systems', 'lighting_systems', 'energy_management'],
            'environmental_design': ['sustainability', 'landscape_architecture', 'biophilic_design', 'ecology', 'climate_responsive_design', 'natural_ventilation', 'daylighting', 'thermal_comfort', 'acoustic_design', 'indoor_air_quality', 'microclimate', 'ecosystem_services'],
            'biophilic_design': ['environmental_design', 'sustainability', 'wellness_design', 'human_centered_design', 'nature_integration', 'psychological_wellbeing', 'stress_reduction', 'productivity_enhancement', 'natural_materials', 'organic_forms', 'sensory_experience', 'restorative_environments'],
            'wellness_design': ['biophilic_design', 'interiors', 'human_centered_design', 'healthcare_design', 'ergonomics', 'acoustics', 'lighting_design', 'air_quality', 'thermal_comfort', 'stress_reduction', 'mental_health', 'physical_wellbeing'],
            'human_centered_design': ['wellness_design', 'interiors', 'user_experience', 'ergonomics', 'accessibility', 'inclusive_design', 'behavioral_psychology', 'anthropometrics', 'user_research', 'usability_testing', 'design_thinking', 'empathy_mapping'],
            'inclusive_design': ['human_centered_design', 'accessibility', 'universal_design', 'social_equity', 'diversity', 'equity_inclusion', 'barrier_free_design', 'assistive_technology', 'aging_in_place', 'disability_rights', 'social_inclusion', 'community_access'],
            'accessibility': ['inclusive_design', 'universal_design', 'human_centered_design', 'barrier_free_design', 'assistive_technology', 'mobility_aids', 'visual_impairment', 'hearing_impairment', 'cognitive_accessibility', 'physical_accessibility', 'digital_accessibility', 'regulatory_compliance'],
            
            # Emerging Technology Categories (18)
            'machine_learning': ['ai_in_architecture', 'computational_design', 'data_analytics', 'predictive_modeling', 'pattern_recognition', 'optimization', 'automation', 'smart_buildings', 'urban_analytics', 'energy_optimization', 'maintenance_prediction', 'user_behavior_analysis'],
            'data_analytics': ['machine_learning', 'smart_cities', 'building_performance', 'urban_analytics', 'energy_analysis', 'occupant_behavior', 'predictive_modeling', 'performance_optimization', 'decision_support', 'trend_analysis', 'benchmarking', 'continuous_improvement'],
            'predictive_modeling': ['machine_learning', 'data_analytics', 'building_performance', 'energy_modeling', 'maintenance_prediction', 'risk_assessment', 'climate_modeling', 'urban_growth', 'infrastructure_planning', 'resource_optimization', 'disaster_preparedness', 'adaptive_systems'],
            'automation': ['ai_in_architecture', 'smart_buildings', 'iot_infrastructure', 'building_automation', 'process_optimization', 'energy_management', 'security_systems', 'maintenance_automation', 'occupant_comfort', 'operational_efficiency', 'remote_monitoring', 'intelligent_control'],
            'robotics': ['automation', 'digital_fabrication', 'construction_automation', 'maintenance_robotics', 'inspection_robots', 'assembly_automation', 'material_handling', 'precision_construction', 'safety_robotics', 'collaborative_robots', 'autonomous_systems', 'human_robot_interaction'],
            'digital_fabrication': ['computational_design', 'parametric_design', '3d_printing', 'cnc_machining', 'laser_cutting', 'robotic_assembly', 'prefabrication', 'mass_customization', 'complex_geometry', 'material_efficiency', 'rapid_prototyping', 'custom_components'],
            '3d_printing': ['digital_fabrication', 'additive_manufacturing', 'rapid_prototyping', 'custom_components', 'complex_geometry', 'material_innovation', 'construction_automation', 'on_site_fabrication', 'waste_reduction', 'mass_customization', 'biomimetic_structures', 'sustainable_construction'],
            'additive_manufacturing': ['3d_printing', 'digital_fabrication', 'material_innovation', 'complex_geometry', 'custom_manufacturing', 'rapid_prototyping', 'sustainable_manufacturing', 'waste_reduction', 'material_efficiency', 'design_freedom', 'functional_gradients', 'multi_material_printing'],
            'blockchain': ['smart_contracts', 'supply_chain_management', 'project_management', 'bim_management', 'digital_twin', 'asset_management', 'intellectual_property', 'collaboration_platforms', 'transparency', 'trust_systems', 'decentralized_governance', 'sustainable_certification'],
            'smart_contracts': ['blockchain', 'project_management', 'supply_chain_management', 'automation', 'trust_systems', 'transparency', 'compliance_automation', 'payment_systems', 'quality_assurance', 'warranty_management', 'maintenance_contracts', 'performance_guarantees'],
            'supply_chain_management': ['blockchain', 'project_management', 'materials', 'logistics', 'quality_control', 'cost_management', 'risk_management', 'sustainability', 'transparency', 'vendor_management', 'inventory_optimization', 'just_in_time_delivery'],
            'logistics': ['supply_chain_management', 'transportation', 'project_management', 'materials', 'inventory_management', 'route_optimization', 'warehouse_design', 'last_mile_delivery', 'reverse_logistics', 'sustainable_transport', 'real_time_tracking', 'demand_forecasting'],
            'quality_control': ['construction', 'materials', 'project_management', 'safety', 'testing', 'inspection', 'compliance', 'standards', 'certification', 'continuous_improvement', 'defect_prevention', 'performance_verification'],
            'testing': ['quality_control', 'materials', 'structural_engineering', 'building_performance', 'energy_efficiency', 'acoustics', 'fire_safety', 'environmental_testing', 'durability_testing', 'performance_validation', 'compliance_testing', 'research_development'],
            'inspection': ['quality_control', 'safety', 'maintenance', 'structural_engineering', 'building_performance', 'compliance', 'risk_assessment', 'condition_assessment', 'preventive_maintenance', 'remote_inspection', 'drone_inspection', 'ai_inspection'],
            'certification': ['quality_control', 'sustainability', 'green_building', 'safety', 'compliance', 'standards', 'accreditation', 'performance_rating', 'sustainable_certification', 'energy_certification', 'accessibility_certification', 'wellness_certification'],
            'standards': ['certification', 'quality_control', 'compliance', 'building_codes', 'safety', 'performance_standards', 'accessibility_standards', 'sustainability_standards', 'interoperability', 'best_practices', 'industry_guidelines', 'regulatory_frameworks'],
            'compliance': ['standards', 'building_codes', 'safety', 'regulatory_requirements', 'certification', 'quality_control', 'legal_compliance', 'environmental_compliance', 'accessibility_compliance', 'fire_safety', 'energy_codes', 'zoning_regulations'],
            
            # Business and Management Categories (13)
            'marketing': ['branding', 'business_development', 'client_relations', 'market_research', 'competitive_analysis', 'digital_marketing', 'content_strategy', 'social_media', 'public_relations', 'stakeholder_engagement', 'value_proposition', 'market_positioning'],
            'branding': ['marketing', 'visual_identity', 'graphic_design', 'brand_strategy', 'corporate_identity', 'user_experience', 'brand_positioning', 'visual_communication', 'brand_guidelines', 'identity_systems', 'brand_experience', 'reputation_management'],
            'business_development': ['marketing', 'client_relations', 'strategic_planning', 'market_expansion', 'partnership_development', 'sales_strategy', 'growth_strategy', 'competitive_advantage', 'market_opportunity', 'value_creation', 'relationship_building', 'opportunity_identification'],
            'client_relations': ['business_development', 'marketing', 'project_management', 'stakeholder_management', 'communication', 'customer_service', 'relationship_management', 'trust_building', 'expectation_management', 'feedback_management', 'satisfaction_measurement', 'loyalty_development'],
            'project_management': ['construction', 'architecture', 'bim_management', 'team_coordination', 'budget_management', 'schedule_management', 'risk_management', 'quality_management', 'stakeholder_management', 'communication', 'resource_allocation', 'performance_monitoring'],
            'team_coordination': ['project_management', 'collaboration', 'communication', 'leadership', 'conflict_resolution', 'team_building', 'role_definition', 'workflow_optimization', 'cross_functional_teams', 'remote_collaboration', 'performance_management', 'skill_development'],
            'budget_management': ['project_management', 'cost_management', 'financial_planning', 'value_engineering', 'cost_optimization', 'financial_control', 'cash_flow_management', 'investment_analysis', 'financial_reporting', 'cost_benefit_analysis', 'budget_tracking', 'financial_risk_management'],
            'cost_management': ['budget_management', 'value_engineering', 'project_management', 'materials', 'construction', 'cost_optimization', 'lifecycle_cost_analysis', 'total_cost_of_ownership', 'cost_control', 'procurement_optimization', 'waste_reduction', 'efficiency_improvement'],
            'value_engineering': ['cost_management', 'budget_management', 'project_management', 'optimization', 'performance_improvement', 'cost_benefit_analysis', 'function_analysis', 'alternative_solutions', 'value_maximization', 'stakeholder_value', 'sustainable_value', 'innovation_value'],
            'financial_planning': ['budget_management', 'cost_management', 'investment_analysis', 'financial_strategy', 'cash_flow_planning', 'financial_risk_management', 'capital_planning', 'financial_modeling', 'scenario_planning', 'financial_forecasting', 'resource_allocation', 'financial_performance'],
            'investment_analysis': ['financial_planning', 'real_estate_development', 'market_analysis', 'risk_assessment', 'return_on_investment', 'financial_modeling', 'market_research', 'competitive_analysis', 'investment_strategy', 'portfolio_management', 'financial_risk_management', 'value_creation'],
            'real_estate_development': ['investment_analysis', 'urban_planning', 'market_analysis', 'project_management', 'financial_planning', 'stakeholder_management', 'regulatory_compliance', 'market_research', 'development_strategy', 'risk_management', 'value_creation', 'sustainable_development'],
            'market_analysis': ['investment_analysis', 'real_estate_development', 'market_research', 'competitive_analysis', 'trend_analysis', 'demand_forecasting', 'market_positioning', 'opportunity_identification', 'risk_assessment', 'market_strategy', 'customer_segmentation', 'market_intelligence'],
            
            # Technology and Digital Categories (16)
            'bim_management': ['architecture', 'construction', 'digital_architecture', 'project_management', 'collaboration', 'information_management', 'model_coordination', 'clash_detection', 'quantity_takeoff', 'scheduling', 'facility_management', 'lifecycle_management'],
            'information_management': ['bim_management', 'data_management', 'knowledge_management', 'document_management', 'information_architecture', 'data_governance', 'information_security', 'data_quality', 'metadata_management', 'information_strategy', 'digital_transformation', 'information_systems'],
            'data_management': ['information_management', 'data_analytics', 'machine_learning', 'data_governance', 'data_quality', 'data_security', 'data_architecture', 'data_integration', 'data_warehousing', 'big_data', 'data_strategy', 'data_ops'],
            'knowledge_management': ['information_management', 'collaboration', 'learning_organizations', 'best_practices', 'knowledge_sharing', 'expertise_management', 'organizational_learning', 'knowledge_transfer', 'intellectual_capital', 'knowledge_strategy', 'innovation_management', 'continuous_improvement'],
            'document_management': ['information_management', 'bim_management', 'collaboration', 'version_control', 'access_control', 'workflow_automation', 'compliance_management', 'archival_systems', 'search_functionality', 'document_workflow', 'electronic_signatures', 'mobile_access'],
            'collaboration': ['bim_management', 'project_management', 'team_coordination', 'communication', 'knowledge_sharing', 'remote_work', 'virtual_teams', 'collaborative_tools', 'workflow_optimization', 'cross_functional_teams', 'stakeholder_engagement', 'partnership_development'],
            'communication': ['collaboration', 'stakeholder_management', 'client_relations', 'presentation_skills', 'visual_communication', 'technical_writing', 'interpersonal_skills', 'negotiation', 'conflict_resolution', 'public_speaking', 'media_relations', 'crisis_communication'],
            'presentation_skills': ['communication', 'visual_communication', 'graphic_design', 'public_speaking', 'storytelling', 'data_visualization', 'audience_engagement', 'persuasion_techniques', 'visual_aids', 'presentation_design', 'delivery_skills', 'feedback_handling'],
            'visual_communication': ['presentation_skills', 'graphic_design', 'data_visualization', 'user_experience', 'branding', 'visual_identity', 'information_design', 'visual_storytelling', 'visual_literacy', 'design_thinking', 'visual_strategy', 'multimedia_design'],
            'graphic_design': ['visual_communication', 'branding', 'visual_identity', 'typography', 'layout_design', 'color_theory', 'visual_hierarchy', 'brand_guidelines', 'marketing_materials', 'publication_design', 'digital_design', 'print_design'],
            'data_visualization': ['visual_communication', 'data_analytics', 'information_design', 'visual_storytelling', 'dashboard_design', 'interactive_visualization', 'infographics', 'chart_design', 'mapping', 'spatial_visualization', 'real_time_visualization', 'predictive_visualization'],
            'visualization': ['data_visualization', 'digital_architecture', 'virtual_reality', '3d_modeling', 'rendering', 'animation', 'simulation', 'visual_storytelling', 'immersive_visualization', 'interactive_visualization', 'real_time_rendering', 'photorealistic_rendering'],
            '3d_modeling': ['visualization', 'digital_architecture', 'bim_management', 'parametric_design', 'rendering', 'animation', 'simulation', 'complex_geometry', 'digital_fabrication', 'virtual_reality', 'augmented_reality', 'digital_twin'],
            'rendering': ['3d_modeling', 'visualization', 'digital_architecture', 'photorealistic_rendering', 'lighting_design', 'material_visualization', 'animation', 'virtual_reality', 'augmented_reality', 'real_time_rendering', 'architectural_visualization', 'product_visualization'],
            'animation': ['rendering', '3d_modeling', 'visualization', 'motion_graphics', 'storytelling', 'virtual_reality', 'augmented_reality', 'interactive_animation', 'simulation', 'visual_effects', 'character_animation', 'environmental_animation'],
            'simulation': ['3d_modeling', 'visualization', 'building_performance', 'energy_modeling', 'structural_analysis', 'acoustic_simulation', 'thermal_simulation', 'daylight_simulation', 'wind_simulation', 'occupant_behavior', 'emergency_evacuation', 'climate_simulation'],
            
            # Research and Innovation Categories (14)
            'architectural_research': ['research_methodology', 'design_research', 'building_science', 'performance_research', 'user_research', 'sustainability_research', 'material_research', 'technology_research', 'social_research', 'historical_research', 'theoretical_research', 'applied_research'],
            'research_methodology': ['architectural_research', 'data_analysis', 'qualitative_research', 'quantitative_research', 'mixed_methods', 'experimental_design', 'case_study_research', 'survey_research', 'observational_research', 'action_research', 'participatory_research', 'longitudinal_studies'],
            'design_research': ['architectural_research', 'user_research', 'design_thinking', 'prototype_development', 'iterative_design', 'design_validation', 'user_testing', 'design_innovation', 'design_strategy', 'design_process', 'design_outcomes', 'design_evaluation'],
            'building_science': ['architectural_research', 'building_performance', 'energy_efficiency', 'thermal_comfort', 'acoustics', 'daylighting', 'indoor_air_quality', 'moisture_management', 'structural_behavior', 'material_science', 'environmental_physics', 'building_envelope'],
            'performance_research': ['building_science', 'building_performance', 'energy_modeling', 'thermal_simulation', 'acoustic_simulation', 'daylight_simulation', 'occupant_comfort', 'post_occupancy_evaluation', 'performance_monitoring', 'benchmarking', 'performance_optimization', 'continuous_improvement'],
            'user_research': ['design_research', 'human_centered_design', 'user_experience', 'behavioral_psychology', 'anthropometrics', 'usability_testing', 'user_interviews', 'observation_studies', 'user_journey_mapping', 'persona_development', 'user_needs_analysis', 'user_behavior_analysis'],
            'sustainability_research': ['architectural_research', 'sustainability', 'environmental_research', 'lifecycle_assessment', 'carbon_footprint', 'renewable_energy', 'green_building', 'climate_research', 'ecological_research', 'social_sustainability', 'economic_sustainability', 'sustainable_development'],
            'material_research': ['architectural_research', 'material_science', 'advanced_materials', 'biomaterials', 'smart_materials', 'material_innovation', 'material_testing', 'material_properties', 'material_development', 'sustainable_materials', 'material_performance', 'material_lifecycle'],
            'technology_research': ['architectural_research', 'digital_architecture', 'computational_design', 'ai_in_architecture', 'virtual_reality', 'augmented_reality', 'digital_fabrication', 'smart_technology', 'emerging_technology', 'technology_innovation', 'technology_integration', 'future_technology'],
            'social_research': ['architectural_research', 'social_impact', 'community_development', 'social_equity', 'cultural_research', 'behavioral_research', 'social_psychology', 'sociology', 'anthropology', 'social_innovation', 'social_sustainability', 'community_engagement'],
            'historical_research': ['architectural_research', 'historic_preservation', 'cultural_heritage', 'architectural_history', 'cultural_research', 'heritage_management', 'conservation_research', 'archaeological_research', 'historical_analysis', 'cultural_identity', 'heritage_tourism', 'cultural_memory'],
            'theoretical_research': ['architectural_research', 'philosophy_of_architecture', 'architectural_theory', 'critical_theory', 'phenomenology', 'semiotics', 'aesthetics', 'spatial_theory', 'urban_theory', 'design_theory', 'cultural_theory', 'social_theory'],
            'applied_research': ['architectural_research', 'practical_applications', 'real_world_problems', 'industry_collaboration', 'technology_transfer', 'innovation_implementation', 'pilot_projects', 'field_studies', 'practical_validation', 'implementation_research', 'impact_assessment', 'scalability_research'],
            'innovation_management': ['applied_research', 'technology_research', 'design_research', 'innovation_strategy', 'research_development', 'intellectual_property', 'technology_transfer', 'innovation_ecosystems', 'startup_collaboration', 'open_innovation', 'innovation_culture', 'innovation_metrics']
        }
        
        # Cross-disciplinary themes (2,667 themes: 2,580 subcategory themes + 86 main category themes + 1 all categories theme)
        self.cross_themes = {}
        
        # 1. Create themes from all 2,580 subcategories
        subcategory_themes = {}
        for main_category, subcategories in self.subcategories.items():
            for subcategory in subcategories:
                theme_name = f"{main_category}_{subcategory}"
                # Each subcategory theme includes the main category plus related categories
                related_categories = self.get_category_relationships(main_category)
                theme_categories = [main_category] + related_categories[:11]  # 12 total categories
                subcategory_themes[theme_name] = theme_categories
        
        # 2. Create themes from all 86 main categories
        main_category_themes = {}
        for main_category in self.main_categories:
            theme_name = f"main_{main_category}"
            related_categories = self.get_category_relationships(main_category)
            theme_categories = [main_category] + related_categories[:11]  # 12 total categories
            main_category_themes[theme_name] = theme_categories
        
        # 3. Create "all categories" theme
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
    
    def get_category_relationships(self, category):
        """Get categories that work well with the given category"""
        return self.category_relationships.get(category, [])
    
    def get_cross_theme_categories(self, theme):
        """Get categories for a specific cross-disciplinary theme"""
        return self.cross_themes.get(theme, [])
    
    def generate_cross_disciplinary_question(self, primary_category, secondary_category=None, context=None):
        """Generate a cross-disciplinary question between two categories"""
        try:
            import requests
            
            # If no secondary category provided, find a good match
            if not secondary_category:
                related_categories = self.get_category_relationships(primary_category)
                if related_categories:
                    secondary_category = random.choice(related_categories)
                else:
                    # Fallback to a random category
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
        """Generate a question based on a cross-disciplinary theme with any number of categories"""
        try:
            categories = self.get_cross_theme_categories(theme)
            if len(categories) < 2:
                return None
            
            # Select 2-6 categories for the question (maximum flexibility)
            max_categories = min(6, len(categories))  # Cap at 6 for readability
            num_categories = random.randint(2, max_categories)
            selected_categories = random.sample(categories, num_categories)
            
            # Create a theme-specific question based on the number of categories
            question = self._create_multi_category_question(selected_categories, theme, num_categories)
            
            # Add theme-specific enhancements
            question = self._enhance_theme_question(question, theme, selected_categories)
            
            return {
                'question': question,
                'theme': theme,
                'categories': selected_categories,
                'num_categories': num_categories,
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating theme-based question: {e}")
            return None
    
    def _create_multi_category_question(self, categories, theme, num_categories):
        """Create questions for any number of categories (2-6)"""
        
        # Format category names for display
        formatted_categories = [c.replace('_', ' ').title() for c in categories]
        theme_display = theme.replace('_', ' ').title()
        
        if num_categories == 2:
            return f"How do {formatted_categories[0]} and {formatted_categories[1]} work together in {theme_display}?"
        
        elif num_categories == 3:
            return f"What synergies emerge when combining {formatted_categories[0]}, {formatted_categories[1]}, and {formatted_categories[2]} for {theme_display}?"
        
        elif num_categories == 4:
            return f"How can the integration of {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} advance {theme_display}?"
        
        elif num_categories == 5:
            return f"What innovative solutions can be developed by synthesizing {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} approaches in {theme_display}?"
        
        else:  # 6 categories
            return f"How do {', '.join(formatted_categories[:-1])} and {formatted_categories[-1]} interact to address complex challenges in {theme_display}?"
    
    def generate_flexible_theme_question(self, theme, min_categories=2, max_categories=6):
        """Generate a theme-based question with specified category range"""
        try:
            categories = self.get_cross_theme_categories(theme)
            if len(categories) < min_categories:
                return None
            
            # Select categories within the specified range
            available_max = min(max_categories, len(categories))
            if min_categories > available_max:
                min_categories = available_max
            
            num_categories = random.randint(min_categories, available_max)
            selected_categories = random.sample(categories, num_categories)
            
            # Create the question
            question = self._create_multi_category_question(selected_categories, theme, num_categories)
            question = self._enhance_theme_question(question, theme, selected_categories)
            
            return {
                'question': question,
                'theme': theme,
                'categories': selected_categories,
                'num_categories': num_categories,
                'category_range': f"{min_categories}-{max_categories}",
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating flexible theme question: {e}")
            return None
    
    def generate_synthesis_question_from_answers(self, answers, target_category):
        """Generate a cross-disciplinary question by synthesizing insights from multiple answers"""
        try:
            if not answers or len(answers) < 2:
                return None
            
            # Extract categories and insights from answers
            categories = [answer.get('category', '') for answer in answers]
            insights = [answer.get('answer_text', '') for answer in answers]
            
            # Remove duplicates and empty values
            categories = list(set([c for c in categories if c]))
            insights = [i for i in insights if i.strip()]
            
            if len(categories) < 2 or len(insights) < 2:
                return None
            
            # Create a synthesis question
            question = f"Given insights from {', '.join(c.replace('_', ' ').title() for c in categories)}, how can we apply these principles to advance {target_category.replace('_', ' ').title()}?"
            
            # Make it more specific
            question = self._enhance_synthesis_question(question, categories, target_category)
            
            return {
                'question': question,
                'source_categories': categories,
                'target_category': target_category,
                'synthesis_type': 'answer_based',
                'is_cross_disciplinary': True
            }
            
        except Exception as e:
            log.error(f"Error generating synthesis question from answers: {e}")
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
    
    def _enhance_synthesis_question(self, question, source_categories, target_category):
        """Make synthesis questions more specific"""
        enhancements = [
            f"What specific methodologies can be transferred?",
            f"How do these insights inform {target_category.replace('_', ' ')} best practices?",
            f"What new approaches emerge from this cross-pollination?",
            f"How can we measure the impact of this integration?",
            f"What barriers exist and how can we overcome them?"
        ]
        
        if random.random() < 0.6:  # 60% chance to enhance
            enhancement = random.choice(enhancements)
            question += f" {enhancement}"
        
        return question
    
    def get_cross_disciplinary_insights(self, question_data, answers):
        """Generate cross-disciplinary insights based on the question and available answers"""
        try:
            if not question_data or not answers:
                return None
            
            # Extract relevant information
            question = question_data.get('question', '')
            categories = []
            
            if 'primary_category' in question_data:
                categories.extend([question_data['primary_category'], question_data['secondary_category']])
            elif 'categories' in question_data:
                categories.extend(question_data['categories'])
            elif 'source_categories' in question_data:
                categories.extend(question_data['source_categories'])
            
            # Filter answers by relevant categories
            relevant_answers = [b for b in answers if b.get('category') in categories]
            
            if not relevant_answers:
                return None
            
            # Create synthesis prompt
            synthesis_prompt = f"""
            Question: {question}
            
            Relevant insights from different categories:
            {chr(10).join(f"- {b.get('category', 'Unknown')}: {b.get('answer_text', '')[:200]}..." for b in relevant_answers[:3])}
            
            Please provide a cross-disciplinary synthesis that:
            1. Identifies common themes across these insights
            2. Explains how they complement each other
            3. Suggests practical applications
            4. Highlights innovative opportunities
            5. Addresses potential challenges
            """
            
            # Generate synthesis using AI
            synthesis = self._generate_ai_synthesis(synthesis_prompt)
            
            return {
                'synthesis': synthesis,
                'question': question,
                'source_categories': categories,
                'relevant_answers_count': len(relevant_answers),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            log.error(f"Error generating cross-disciplinary insights: {e}")
            return None
    
    def _generate_ai_synthesis(self, prompt):
        """Generate AI-powered synthesis"""
        try:
            import requests
            
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": TEXT_MODEL,
                "prompt": f"[INST] {prompt} [/INST]",
                "temperature": 0.7,
                "max_tokens": 400,
                "top_p": 0.9,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.6
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            synthesis = result['choices'][0]['text'].strip()
            
            return synthesis
            
        except Exception as e:
            log.error(f"Error generating AI synthesis: {e}")
            return "Cross-disciplinary synthesis requires combining insights from multiple domains to create innovative solutions."

    # Research Analysis Methods (from research_explorer.py)
    
    def analyze_research_direction(self, category, current_questions, previous_insights=None):
        """Analyze and suggest research direction for a category"""
        try:
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Craft a comprehensive research analysis prompt
            prompt = f'''[INST] You are an expert architectural research analyst. Analyze the research direction for {category} based on current questions and insights.

Current Questions in {category}:
{chr(10).join(f"- {q}" for q in current_questions[:5])}

Previous Research Insights:
{previous_insights if previous_insights else "No previous insights available"}

Research Dimensions to Consider:
- Temporal: historical, contemporary, future, evolutionary
- Spatial: urban, rural, global, local, regional  
- Thematic: sustainability, technology, culture, economics, social
- Methodological: analytical, creative, experimental, theoretical, practical
- Scale: micro, meso, macro, mega
- Context: environmental, social, political, economic, cultural

Please provide:
1. Key research gaps and opportunities
2. Emerging trends and patterns
3. Cross-disciplinary connections
4. Recommended exploration directions
5. Potential breakthrough areas

Format as structured analysis: [/INST]'''
            
            payload = {
                "model": TEXT_MODEL,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.6
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    analysis = data['choices'][0]['text'].strip()
                    
                    # Store the analysis
                    insight = {
                        'category': category,
                        'timestamp': datetime.now(),
                        'analysis': analysis,
                        'questions_analyzed': len(current_questions)
                    }
                    self.research_insights.append(insight)
                    
                    return analysis
                else:
                    log.error(f"Invalid API response format for research analysis")
                    return None
            else:
                log.error(f"API error for research analysis: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            log.error(f"Error analyzing research direction for {category}: {e}")
            return None

    def discover_insights(self, categories_data):
        """Discover cross-disciplinary insights and patterns"""
        try:
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepare category data for analysis
            category_summary = []
            for category, questions in categories_data.items():
                if questions:
                    category_summary.append(f"{category}: {len(questions)} questions")
            
            prompt = f'''[INST] You are an expert architectural research analyst discovering cross-disciplinary insights.

Categories and Question Counts:
{chr(10).join(category_summary)}

Please analyze and identify:
1. Common themes across categories
2. Potential research synergies
3. Emerging architectural paradigms
4. Cross-pollination opportunities
5. Innovation hotspots

Format as structured insights: [/INST]'''
            
            payload = {
                "model": TEXT_MODEL,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 400,
                "top_p": 0.9,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.6
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    insights = data['choices'][0]['text'].strip()
                    return insights
                else:
                    log.error(f"Invalid API response format for insight discovery")
                    return None
            else:
                log.error(f"API error for insight discovery: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            log.error(f"Error discovering insights: {e}")
            return None

    def suggest_exploration_path(self, current_category, available_categories):
        """Suggest the next exploration path based on current research"""
        try:
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f'''[INST] You are an expert architectural research strategist. Suggest the optimal exploration path.

Current category: {current_category}
Available categories: {', '.join(available_categories)}

Research Dimensions:
- Temporal: historical, contemporary, future, evolutionary
- Spatial: urban, rural, global, local, regional
- Thematic: sustainability, technology, culture, economics, social
- Methodological: analytical, creative, experimental, theoretical, practical
- Scale: micro, meso, macro, mega
- Context: environmental, social, political, economic, cultural

Please suggest:
1. The next category to explore (from available list)
2. Rationale for the choice
3. Expected research synergies
4. Potential breakthrough opportunities
5. Exploration strategy

Consider:
- Cross-disciplinary connections
- Research momentum
- Innovation potential
- Knowledge gaps
- Emerging trends

Provide structured recommendation: [/INST]'''
            
            payload = {
                "model": TEXT_MODEL,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 400,
                "top_p": 0.9,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.6
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    suggestion = data['choices'][0]['text'].strip()
                    return suggestion
                else:
                    log.error(f"Invalid API response format for exploration suggestion")
                    return None
            else:
                log.error(f"API error for exploration suggestion: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            log.error(f"Error suggesting exploration path: {e}")
            return None

    def get_research_summary(self):
        """Get a summary of all research insights and exploration history"""
        summary = {
            'total_insights': len(self.research_insights),
            'total_explorations': len(self.exploration_history),
            'categories_analyzed': list(set(insight['category'] for insight in self.research_insights)),
            'latest_insight': self.research_insights[-1] if self.research_insights else None,
            'latest_exploration': self.exploration_history[-1] if self.exploration_history else None
        }
        return summary

    def generate_intelligent_theme_question(self, research_context=None, current_questions=None):
        """Generate theme question based on research analysis"""
        try:
            # Analyze current research gaps if questions provided
            if current_questions:
                analysis = self.analyze_research_direction("cross_disciplinary", current_questions)
                if analysis:
                    log.info(f"Research analysis completed: {len(analysis)} characters")
            
            # Select theme based on research context or analysis
            if research_context:
                # Filter themes based on research context
                relevant_themes = [theme for theme in self.cross_themes.keys() 
                                 if any(keyword in theme.lower() for keyword in research_context.lower().split())]
                if relevant_themes:
                    selected_theme = random.choice(relevant_themes)
                else:
                    selected_theme = random.choice(list(self.cross_themes.keys()))
            else:
                selected_theme = random.choice(list(self.cross_themes.keys()))
            
            # Generate question using the selected theme
            return self.generate_theme_based_question(selected_theme)
            
        except Exception as e:
            log.error(f"Error generating intelligent theme question: {e}")
            return self.generate_theme_based_question(random.choice(list(self.cross_themes.keys())))

    def get_category_for_question(self, question, available_categories=None):
        """Analyze a question and suggest the best category for it"""
        try:
            if not available_categories:
                available_categories = self.main_categories
            
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f'''[INST] You are an expert architectural researcher. Analyze this question and suggest the most appropriate category.

Question: {question}

Available categories: {', '.join(available_categories)}

Please select the single most appropriate category from the available list.
Consider the question's focus, scope, and primary domain.

Return only the category name: [/INST]'''
            
            payload = {
                "model": TEXT_MODEL,
                "prompt": prompt,
                "temperature": 0.3,
                "max_tokens": 50,
                "top_p": 0.9
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    suggestion = data['choices'][0]['text'].strip()
                    suggestion = suggestion.replace('"', '').replace("'", "").strip()
                    
                    if suggestion in available_categories:
                        return suggestion
                    else:
                        return random.choice(available_categories)
                else:
                    return random.choice(available_categories)
            else:
                return random.choice(available_categories)
                
        except Exception as e:
            log.error(f"Error getting category for question: {e}")
            return random.choice(available_categories)



# Convenience functions
def generate_cross_disciplinary_question(primary_category, secondary_category=None, context=None):
    """Generate a cross-disciplinary question"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_cross_disciplinary_question(primary_category, secondary_category, context)

def generate_theme_based_question(theme):
    """Generate a theme-based cross-disciplinary question"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_theme_based_question(theme)

def generate_synthesis_question_from_answers(answers, target_category):
    """Generate synthesis question from multiple answers"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_synthesis_question_from_answers(answers, target_category)

def get_cross_disciplinary_insights(question_data, answers):
    """Get cross-disciplinary insights"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.get_cross_disciplinary_insights(question_data, answers)

def generate_flexible_theme_question(theme, min_categories=2, max_categories=6):
    """Generate theme-based question with specified category range"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_flexible_theme_question(theme, min_categories, max_categories)

def generate_simple_theme_question(theme):
    """Generate theme-based question with 2-3 categories (simple combinations)"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_flexible_theme_question(theme, 2, 3)

def generate_complex_theme_question(theme):
    """Generate theme-based question with 4-6 categories (complex combinations)"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_flexible_theme_question(theme, 4, 6)

def generate_mixed_theme_question(theme):
    """Generate theme-based question with 3-5 categories (balanced combinations)"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_flexible_theme_question(theme, 3, 5)

def get_theme_counts():
    """Get counts of all theme types"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.theme_counts

def get_all_themes():
    """Get all available themes"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return list(generator.cross_themes.keys())

def get_subcategory_themes():
    """Get all subcategory-based themes"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return [theme for theme in generator.cross_themes.keys() if '_' in theme and not theme.startswith('main_') and theme != 'all_categories']

def get_main_category_themes():
    """Get all main category-based themes"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return [theme for theme in generator.cross_themes.keys() if theme.startswith('main_')]

def get_theme_categories(theme_name):
    """Get categories for a specific theme"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.cross_themes.get(theme_name, [])

# New research analysis convenience functions
def analyze_research_direction(category, current_questions, previous_insights=None):
    """Analyze research direction for a category"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.analyze_research_direction(category, current_questions, previous_insights)

def discover_cross_disciplinary_insights(categories_data):
    """Discover cross-disciplinary insights"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.discover_insights(categories_data)

def suggest_exploration_path(current_category, available_categories):
    """Suggest next exploration path"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.suggest_exploration_path(current_category, available_categories)

def get_research_summary():
    """Get research summary"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.get_research_summary()

def generate_intelligent_theme_question(research_context=None, current_questions=None):
    """Generate intelligent theme question based on research analysis"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.generate_intelligent_theme_question(research_context, current_questions)

def get_category_for_question(question, available_categories=None):
    """Get best category for a question"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.get_category_for_question(question, available_categories)

def get_all_categories():
    """Get all main categories"""
    generator = EnhancedCrossDisciplinaryGenerator()
    return generator.main_categories

def get_research_explorer():
    """Get enhanced cross-disciplinary generator instance"""
    return EnhancedCrossDisciplinaryGenerator()


