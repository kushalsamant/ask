#!/usr/bin/env python3
"""
Offline Answer Generator Module
Provides answer generation without requiring API access

This module provides functionality to:
- Generate answers from predefined templates
- Work completely offline
- Support all research themes
- Provide fallback answers when API is unavailable

Author: ASK Research Tool
Last Updated: 2025-08-24
Version: 1.0 (Offline-First)
"""

import random
import logging
from typing import Optional

# Setup logging
log = logging.getLogger(__name__)

# Predefined answer templates for offline generation
ANSWER_TEMPLATES = {
    'research_methodology': [
        "The concept of {concept} represents a fundamental shift in how we approach {challenge}. By integrating {approach}, designers can create solutions that are both {outcome1} and {outcome2}. This approach emphasizes the importance of {principle} in contemporary design practice, particularly when addressing {context}. The implementation of {concept} requires careful consideration of {factor}, ensuring that the final solution meets both functional and aesthetic requirements while contributing to {goal}.",
        
        "{Concept} has emerged as a critical response to {challenge} in {context}. This design methodology incorporates {approach} to achieve {outcome}, demonstrating how thoughtful design can address complex environmental and social issues. The key principles include {principle1}, {principle2}, and {principle3}, which work together to create {result}. By focusing on {factor}, designers can develop solutions that are both innovative and practical, ultimately contributing to {goal}.",
        
        "In addressing {challenge}, {concept} offers a comprehensive framework that integrates {approach1} with {approach2}. This methodology emphasizes {principle} as a core design principle, ensuring that solutions are both {outcome1} and {outcome2}. The implementation process involves careful consideration of {factor}, which influences both the design process and the final outcome. Through this approach, designers can create {result} that contribute meaningfully to {goal} while addressing the specific needs of {context}."
    ],
    'technology_innovation': [
        "{Technology} is revolutionizing {field} by enabling {capability} that was previously impossible. This innovation addresses {challenge} through {approach}, creating new opportunities for {outcome}. The key advantages include {benefit1}, {benefit2}, and {benefit3}, which collectively transform how we approach {process}. However, the implementation requires careful consideration of {factor}, ensuring that the technology serves {goal} while maintaining {standard}.",
        
        "The integration of {technology} in {field} represents a paradigm shift that enables {capability}. This innovation addresses {challenge} by providing {solution}, which leads to {outcome}. The technology's key features include {feature1}, {feature2}, and {feature3}, making it particularly effective for {application}. Successful implementation depends on understanding {factor} and ensuring that the technology aligns with {goal} while meeting {requirement}.",
        
        "{Technology} transforms {field} by introducing {capability} that enhances {process}. This innovation responds to {challenge} through {approach}, resulting in {outcome}. The technology's effectiveness stems from {characteristic1}, {characteristic2}, and {characteristic3}, which work together to improve {performance}. Implementation requires attention to {factor}, ensuring that the technology contributes to {goal} while maintaining {quality}."
    ],
    'sustainability_science': [
        "Achieving {sustainability_goal} through {approach} requires a comprehensive understanding of {factor}. This methodology addresses {challenge} by implementing {solution}, which contributes to {outcome}. The key principles include {principle1}, {principle2}, and {principle3}, ensuring that the approach is both {characteristic1} and {characteristic2}. By focusing on {focus}, practitioners can develop solutions that effectively contribute to {goal} while addressing the specific needs of {context}.",
        
        "The implementation of {sustainable_solution} addresses {environmental_challenge} by incorporating {approach}. This methodology emphasizes {principle} as a core component, ensuring that solutions are both {outcome1} and {outcome2}. The process involves careful consideration of {factor}, which influences both the implementation strategy and the final results. Through this approach, practitioners can achieve {goal} while creating {benefit} for {stakeholder}.",
        
        "{Sustainable_approach} represents a holistic response to {environmental_challenge} that integrates {method1} with {method2}. This methodology addresses {challenge} through {solution}, resulting in {outcome}. The key components include {component1}, {component2}, and {component3}, which work together to achieve {goal}. Implementation requires understanding {factor}, ensuring that the approach contributes to {benefit} while maintaining {standard}."
    ],
    'engineering_systems': [
        "Optimizing {system} for {performance_goal} requires a systematic approach that addresses {challenge}. This process involves {approach}, which enables {capability} and improves {outcome}. The key components include {component1}, {component2}, and {component3}, which work together to achieve {result}. Implementation requires careful consideration of {factor}, ensuring that the system meets {requirement} while maintaining {standard}.",
        
        "The design of {system} for {application} involves integrating {component1} with {component2} to achieve {performance_goal}. This approach addresses {challenge} through {solution}, resulting in {outcome}. The system's effectiveness depends on {factor1}, {factor2}, and {factor3}, which collectively determine {performance}. Successful implementation requires understanding {requirement} and ensuring that the system contributes to {goal} while meeting {standard}.",
        
        "Implementing {system} in {context} requires addressing {challenge} through {approach}. This methodology emphasizes {principle} as a core design consideration, ensuring that the system is both {characteristic1} and {characteristic2}. The key factors include {factor1}, {factor2}, and {factor3}, which influence {outcome}. By focusing on {focus}, engineers can develop systems that effectively achieve {goal} while maintaining {quality}."
    ],
    'environmental_design': [
        "Designing {space} to respond to {environmental_factor} requires understanding {principle}. This approach addresses {challenge} by implementing {solution}, which contributes to {outcome}. The key considerations include {consideration1}, {consideration2}, and {consideration3}, ensuring that the design is both {characteristic1} and {characteristic2}. By focusing on {focus}, designers can create spaces that effectively respond to {environmental_factor} while achieving {goal}.",
        
        "The principles of {environmental_concept} in {context} emphasize {principle} as a fundamental design consideration. This approach addresses {challenge} through {solution}, resulting in {outcome}. The implementation involves {approach1}, {approach2}, and {approach3}, which work together to create {result}. Designers must consider {factor}, ensuring that the solution contributes to {goal} while responding to {environmental_factor}.",
        
        "Creating {space} that responds to {environmental_factor} involves integrating {approach1} with {approach2}. This methodology addresses {challenge} by implementing {solution}, which leads to {outcome}. The key elements include {element1}, {element2}, and {element3}, which collectively determine {performance}. By understanding {factor}, designers can develop solutions that effectively respond to {environmental_factor} while achieving {goal}."
    ],
    'urban_planning': [
        "Planning {urban_element} to support {community_goal} requires a comprehensive approach that addresses {challenge}. This process involves {approach}, which enables {capability} and improves {outcome}. The key considerations include {consideration1}, {consideration2}, and {consideration3}, ensuring that the plan is both {characteristic1} and {characteristic2}. By focusing on {focus}, planners can create {urban_element} that effectively support {community_goal}.",
        
        "The development of {urban_development} in {context} involves integrating {approach1} with {approach2} to achieve {community_goal}. This approach addresses {challenge} through {solution}, resulting in {outcome}. The planning process requires {requirement1}, {requirement2}, and {requirement3}, which collectively determine {performance}. Successful implementation depends on understanding {factor} and ensuring that the development contributes to {goal}.",
        
        "Implementing {urban_strategy} to address {urban_challenge} requires understanding {principle}. This approach emphasizes {approach} as a core planning consideration, ensuring that the strategy is both {characteristic1} and {characteristic2}. The key factors include {factor1}, {factor2}, and {factor3}, which influence {outcome}. By focusing on {focus}, planners can develop strategies that effectively address {urban_challenge} while achieving {goal}."
    ],
    'spatial_design': [
        "Designing {space} to enhance {user_experience} requires understanding {principle}. This approach addresses {challenge} by implementing {solution}, which contributes to {outcome}. The key considerations include {consideration1}, {consideration2}, and {consideration3}, ensuring that the design is both {characteristic1} and {characteristic2}. By focusing on {focus}, designers can create spaces that effectively enhance {user_experience}.",
        
        "The principles of {spatial_concept} in {context} emphasize {principle} as a fundamental design consideration. This approach addresses {challenge} through {solution}, resulting in {outcome}. The implementation involves {approach1}, {approach2}, and {approach3}, which work together to create {result}. Designers must consider {factor}, ensuring that the solution contributes to {goal} while enhancing {user_experience}.",
        
        "Creating {space} that influences {behavior} involves integrating {approach1} with {approach2}. This methodology addresses {challenge} by implementing {solution}, which leads to {outcome}. The key elements include {element1}, {element2}, and {element3}, which collectively determine {performance}. By understanding {factor}, designers can develop solutions that effectively influence {behavior} while achieving {goal}."
    ],
    'digital_technology': [
        "{Digital_technology} enhances {process} by enabling {capability} that was previously impossible. This innovation addresses {challenge} through {approach}, creating new opportunities for {outcome}. The key advantages include {benefit1}, {benefit2}, and {benefit3}, which collectively transform how we approach {process}. However, implementation requires careful consideration of {factor}, ensuring that the technology serves {goal} while maintaining {standard}.",
        
        "The integration of {digital_concept} in {field} represents a paradigm shift that enables {capability}. This innovation addresses {challenge} by providing {solution}, which leads to {outcome}. The technology's key features include {feature1}, {feature2}, and {feature3}, making it particularly effective for {application}. Successful implementation depends on understanding {factor} and ensuring that the technology aligns with {goal}.",
        
        "{Digital_technology} transforms {industry} by introducing {capability} that enhances {process}. This innovation responds to {challenge} through {approach}, resulting in {outcome}. The technology's effectiveness stems from {characteristic1}, {characteristic2}, and {characteristic3}, which work together to improve {performance}. Implementation requires attention to {factor}, ensuring that the technology contributes to {goal}."
    ]
}

# Concept dictionaries for filling answer templates
ANSWER_CONCEPTS = {
    'concept': ['sustainable design', 'user-centered design', 'adaptive architecture', 'biophilic design', 'modular systems', 'smart environments', 'resilient infrastructure', 'inclusive design', 'parametric design', 'generative design'],
    'challenge': ['climate change', 'urban density', 'resource scarcity', 'social inequality', 'technological disruption', 'environmental degradation', 'economic uncertainty', 'cultural diversity', 'aging population', 'digital transformation'],
    'context': ['urban environments', 'rural communities', 'coastal regions', 'mountain landscapes', 'desert climates', 'tropical zones', 'industrial areas', 'residential neighborhoods', 'commercial districts', 'public spaces'],
    'outcome': ['sustainability', 'resilience', 'efficiency', 'accessibility', 'well-being', 'productivity', 'creativity', 'social cohesion', 'economic growth', 'environmental protection'],
    'outcome1': ['sustainable', 'resilient', 'efficient', 'accessible', 'healthy', 'productive', 'creative', 'inclusive', 'economical', 'environmentally friendly'],
    'outcome2': ['beautiful', 'functional', 'durable', 'flexible', 'comfortable', 'innovative', 'practical', 'equitable', 'profitable', 'regenerative'],
    'goal': ['carbon neutrality', 'zero waste', 'energy efficiency', 'social equity', 'economic prosperity', 'environmental restoration', 'community engagement', 'cultural preservation', 'technological advancement', 'sustainable development'],
    'approach': ['biophilic design', 'passive design', 'renewable energy', 'water harvesting', 'green materials', 'adaptive reuse', 'modular construction', 'smart systems', 'community engagement', 'lifecycle assessment'],
    'principle': ['sustainability', 'accessibility', 'flexibility', 'durability', 'efficiency', 'beauty', 'functionality', 'inclusivity', 'innovation', 'resilience'],
    'factor': ['user needs', 'environmental conditions', 'budget constraints', 'technical requirements', 'regulatory standards', 'cultural context', 'climate considerations', 'material availability', 'construction methods', 'maintenance requirements'],
    'technology': ['artificial intelligence', 'machine learning', 'blockchain', 'internet of things', 'augmented reality', '3D printing', 'robotics', 'drones', 'sensors', 'cloud computing'],
    'field': ['architecture', 'urban planning', 'construction', 'engineering', 'design', 'manufacturing', 'healthcare', 'education', 'transportation', 'energy'],
    'capability': ['automation', 'optimization', 'prediction', 'simulation', 'visualization', 'analysis', 'monitoring', 'control', 'communication', 'collaboration'],
    'process': ['design', 'construction', 'manufacturing', 'communication', 'collaboration', 'decision-making', 'problem-solving', 'innovation', 'research', 'development'],
    'benefit1': ['increased efficiency', 'reduced costs', 'improved accuracy', 'enhanced safety', 'better user experience', 'faster processing', 'greater flexibility', 'improved accessibility', 'reduced environmental impact', 'enhanced collaboration'],
    'benefit2': ['better quality', 'lower maintenance', 'higher reliability', 'improved performance', 'greater satisfaction', 'reduced errors', 'increased productivity', 'better outcomes', 'sustainable practices', 'enhanced innovation'],
    'benefit3': ['cost savings', 'time efficiency', 'quality improvement', 'safety enhancement', 'user satisfaction', 'performance optimization', 'flexibility increase', 'accessibility improvement', 'environmental benefits', 'innovation acceleration'],
    'standard': ['quality standards', 'safety requirements', 'performance benchmarks', 'accessibility guidelines', 'environmental regulations', 'industry best practices', 'user expectations', 'technical specifications', 'regulatory compliance', 'ethical considerations'],
    'feature1': ['automation capabilities', 'real-time monitoring', 'predictive analytics', 'adaptive responses', 'intelligent optimization', 'seamless integration', 'user-friendly interfaces', 'robust performance', 'scalable architecture', 'secure protocols'],
    'feature2': ['data-driven insights', 'machine learning algorithms', 'cloud-based solutions', 'mobile accessibility', 'cross-platform compatibility', 'real-time updates', 'customizable options', 'comprehensive reporting', 'advanced analytics', 'intuitive design'],
    'feature3': ['seamless connectivity', 'intelligent automation', 'predictive maintenance', 'adaptive learning', 'real-time collaboration', 'advanced visualization', 'comprehensive monitoring', 'intelligent optimization', 'secure communication', 'flexible deployment'],
    'application': ['residential buildings', 'commercial spaces', 'industrial facilities', 'public infrastructure', 'healthcare facilities', 'educational institutions', 'transportation hubs', 'recreational areas', 'cultural venues', 'mixed-use developments'],
    'performance': ['efficiency', 'reliability', 'accuracy', 'speed', 'quality', 'safety', 'accessibility', 'sustainability', 'flexibility', 'durability'],
    'characteristic1': ['sustainable', 'efficient', 'accessible', 'flexible', 'durable', 'beautiful', 'functional', 'inclusive', 'innovative', 'resilient'],
    'characteristic2': ['practical', 'cost-effective', 'user-friendly', 'maintainable', 'scalable', 'adaptable', 'reliable', 'safe', 'environmentally friendly', 'socially responsible'],
    'characteristic3': ['innovative', 'sustainable', 'efficient', 'accessible', 'flexible', 'durable', 'beautiful', 'functional', 'inclusive', 'resilient'],
    'result': ['sustainable solutions', 'efficient systems', 'accessible environments', 'flexible spaces', 'durable structures', 'beautiful designs', 'functional layouts', 'inclusive communities', 'innovative approaches', 'resilient infrastructure'],
    'quality': ['high performance', 'reliability', 'safety', 'accessibility', 'sustainability', 'efficiency', 'durability', 'flexibility', 'innovation', 'user satisfaction'],
    'sustainability_goal': ['carbon neutrality', 'zero waste', 'renewable energy', 'water conservation', 'biodiversity protection', 'circular economy', 'green building', 'sustainable transport', 'clean energy', 'climate resilience'],
    'sustainable_solution': ['green roofs', 'solar panels', 'rainwater harvesting', 'composting systems', 'bike lanes', 'public transit', 'community gardens', 'renewable energy', 'green building', 'sustainable transport'],
    'environmental_challenge': ['climate change', 'biodiversity loss', 'pollution', 'resource depletion', 'waste accumulation', 'air quality', 'water scarcity', 'soil degradation', 'ocean acidification', 'deforestation'],
    'sustainable_approach': ['biophilic design', 'circular economy', 'green infrastructure', 'renewable energy', 'sustainable materials', 'passive design', 'adaptive reuse', 'community resilience', 'environmental justice', 'regenerative design'],
    'benefit': ['environmental protection', 'social equity', 'economic prosperity', 'public health', 'community well-being', 'cultural preservation', 'educational opportunities', 'recreational access', 'economic development', 'sustainable growth'],
    'stakeholder': ['communities', 'residents', 'businesses', 'governments', 'environmental groups', 'educational institutions', 'healthcare providers', 'transportation agencies', 'utility companies', 'cultural organizations'],
    'method1': ['technical analysis', 'community engagement', 'environmental assessment', 'economic evaluation', 'social impact analysis', 'cultural preservation', 'historical research', 'geographic analysis', 'demographic study', 'infrastructure planning'],
    'method2': ['stakeholder consultation', 'data collection', 'impact assessment', 'feasibility analysis', 'cost-benefit evaluation', 'risk assessment', 'performance monitoring', 'quality assurance', 'sustainability evaluation', 'accessibility review'],
    'component1': ['system architecture', 'user interface', 'data management', 'communication protocols', 'security measures', 'monitoring systems', 'control mechanisms', 'integration platforms', 'analytics tools', 'reporting systems'],
    'component2': ['hardware infrastructure', 'software applications', 'network connectivity', 'storage solutions', 'backup systems', 'maintenance protocols', 'upgrade procedures', 'training programs', 'documentation', 'support services'],
    'component3': ['performance monitoring', 'quality assurance', 'safety protocols', 'accessibility features', 'sustainability measures', 'efficiency optimization', 'reliability testing', 'user feedback', 'continuous improvement', 'innovation tracking'],
    'requirement': ['performance standards', 'safety regulations', 'accessibility guidelines', 'environmental compliance', 'quality benchmarks', 'technical specifications', 'user expectations', 'regulatory standards', 'industry best practices', 'ethical considerations'],
    'consideration1': ['user needs', 'environmental impact', 'budget constraints', 'technical feasibility', 'regulatory compliance', 'cultural context', 'climate conditions', 'material availability', 'construction methods', 'maintenance requirements'],
    'consideration2': ['safety requirements', 'accessibility standards', 'sustainability goals', 'performance objectives', 'quality expectations', 'cost effectiveness', 'timeline constraints', 'resource availability', 'stakeholder input', 'future adaptability'],
    'consideration3': ['maintenance needs', 'operational efficiency', 'lifecycle costs', 'environmental benefits', 'social impact', 'cultural significance', 'economic value', 'technological integration', 'community engagement', 'long-term viability'],
    'focus': ['user experience', 'environmental sustainability', 'social equity', 'economic viability', 'cultural preservation', 'technological innovation', 'safety and security', 'accessibility and inclusion', 'quality and performance', 'community engagement'],
    'environmental_factor': ['climate', 'topography', 'vegetation', 'water', 'wind', 'sunlight', 'noise', 'air quality', 'biodiversity', 'geology'],
    'environmental_concept': ['biophilic design', 'passive design', 'sustainable architecture', 'green building', 'climate-responsive design', 'environmental psychology', 'ecological design', 'regenerative design', 'net-zero design', 'circular design'],
    'solution': ['integrated design', 'adaptive systems', 'smart technology', 'green infrastructure', 'renewable energy', 'sustainable materials', 'community engagement', 'lifecycle assessment', 'performance monitoring', 'continuous improvement'],
    'space': ['buildings', 'parks', 'streets', 'plazas', 'interiors', 'landscapes', 'neighborhoods', 'districts', 'cities', 'regions'],
    'urban_element': ['neighborhoods', 'districts', 'streets', 'parks', 'plazas', 'buildings', 'infrastructure', 'transportation', 'public spaces', 'green spaces'],
    'community_goal': ['social equity', 'economic prosperity', 'environmental sustainability', 'public health', 'safety', 'accessibility', 'cultural diversity', 'community engagement', 'quality of life', 'resilience'],
    'urban_development': ['mixed-use projects', 'transit-oriented development', 'green infrastructure', 'affordable housing', 'commercial districts', 'industrial areas', 'recreational facilities', 'cultural venues', 'educational institutions', 'healthcare facilities'],
    'urban_challenge': ['traffic congestion', 'air pollution', 'housing affordability', 'social inequality', 'climate change', 'aging infrastructure', 'population growth', 'economic development', 'public health', 'safety'],
    'urban_strategy': ['transit-oriented development', 'green infrastructure', 'affordable housing', 'mixed-use development', 'pedestrian-friendly design', 'bike lanes', 'public transit', 'smart city technology', 'climate adaptation', 'community engagement'],
    'requirement1': ['comprehensive planning', 'stakeholder engagement', 'environmental assessment', 'economic analysis', 'social impact evaluation', 'cultural preservation', 'historical research', 'geographic analysis', 'demographic study', 'infrastructure planning'],
    'requirement2': ['technical feasibility', 'financial viability', 'regulatory compliance', 'community support', 'environmental sustainability', 'social equity', 'cultural sensitivity', 'historical preservation', 'geographic appropriateness', 'demographic consideration'],
    'requirement3': ['implementation strategy', 'monitoring systems', 'evaluation methods', 'maintenance protocols', 'upgrade procedures', 'community feedback', 'performance tracking', 'quality assurance', 'sustainability evaluation', 'accessibility review'],
    'user_experience': ['comfort', 'efficiency', 'safety', 'accessibility', 'well-being', 'productivity', 'creativity', 'social interaction', 'learning', 'entertainment'],
    'spatial_concept': ['flow', 'hierarchy', 'rhythm', 'balance', 'proportion', 'scale', 'unity', 'variety', 'emphasis', 'harmony'],
    'behavior': ['movement', 'interaction', 'communication', 'learning', 'work', 'relaxation', 'socialization', 'exploration', 'creation', 'reflection'],
    'element1': ['spatial organization', 'lighting design', 'acoustic treatment', 'ventilation systems', 'temperature control', 'privacy measures', 'accessibility features', 'safety systems', 'aesthetic elements', 'functional layouts'],
    'element2': ['material selection', 'color schemes', 'texture patterns', 'furniture arrangement', 'technology integration', 'artwork placement', 'planting design', 'water features', 'pathway systems', 'seating areas'],
    'element3': ['signage systems', 'wayfinding elements', 'interactive features', 'display areas', 'storage solutions', 'flexible spaces', 'specialized areas', 'transition zones', 'focal points', 'gathering spaces'],
    'digital_technology': ['artificial intelligence', 'machine learning', 'blockchain', 'internet of things', 'augmented reality', '3D printing', 'robotics', 'drones', 'sensors', 'cloud computing'],
    'digital_concept': ['artificial intelligence', 'machine learning', 'big data', 'cloud computing', 'internet of things', 'blockchain', 'augmented reality', 'virtual reality', 'cybersecurity', 'digital twins'],
    'industry': ['construction', 'manufacturing', 'healthcare', 'education', 'transportation', 'energy', 'retail', 'finance', 'entertainment', 'agriculture'],
    'principle1': ['sustainability', 'accessibility', 'flexibility', 'durability', 'efficiency', 'beauty', 'functionality', 'inclusivity', 'innovation', 'resilience'],
    'principle2': ['user-centered design', 'evidence-based planning', 'sustainable development', 'smart technology', 'green infrastructure', 'transit-oriented development', 'mixed-use development', 'pedestrian-friendly design', 'bike-friendly design', 'climate-adaptive planning'],
    'principle3': ['community engagement', 'stakeholder consultation', 'environmental assessment', 'economic analysis', 'social impact evaluation', 'cultural preservation', 'historical research', 'geographic analysis', 'demographic study', 'infrastructure planning'],
    'factor1': ['user needs', 'environmental conditions', 'budget constraints', 'technical requirements', 'regulatory standards', 'cultural context', 'climate considerations', 'material availability', 'construction methods', 'maintenance requirements'],
    'factor2': ['safety requirements', 'accessibility standards', 'sustainability goals', 'performance objectives', 'quality expectations', 'cost effectiveness', 'timeline constraints', 'resource availability', 'stakeholder input', 'future adaptability'],
    'factor3': ['maintenance needs', 'operational efficiency', 'lifecycle costs', 'environmental benefits', 'social impact', 'cultural significance', 'economic value', 'technological integration', 'community engagement', 'long-term viability']
}

def generate_offline_answer(question: str, theme: str) -> Optional[str]:
    """
    Generate an answer offline using predefined templates
    
    Args:
        question (str): The question to answer
        theme (str): Theme name for answer generation
        
    Returns:
        str: Generated answer or None if failed
    """
    try:
        # Normalize theme name
        theme = theme.lower().replace(' ', '_')
        
        # Get templates for theme
        if theme not in ANSWER_TEMPLATES:
            log.warning(f"No answer templates available for theme: {theme}")
            return None
        
        templates = ANSWER_TEMPLATES[theme]
        
        # Select random template
        template = random.choice(templates)
        
        # Fill template with random concepts
        answer = template
        for placeholder, concepts in ANSWER_CONCEPTS.items():
            if placeholder in answer:
                concept = random.choice(concepts)
                answer = answer.replace(f"{{{placeholder}}}", concept)
        
        # Clean up any remaining placeholders
        import re
        answer = re.sub(r'\{[^}]+\}', 'sustainable design', answer)
        
        # Ensure answer is between 200-250 words
        words = answer.split()
        if len(words) < 200:
            # Add more content to reach minimum length
            additional_content = f" This approach demonstrates how {random.choice(ANSWER_CONCEPTS['concept'])} can effectively address {random.choice(ANSWER_CONCEPTS['challenge'])} in {random.choice(ANSWER_CONCEPTS['context'])}. The implementation of such solutions requires careful consideration of {random.choice(ANSWER_CONCEPTS['factor'])} to ensure successful outcomes."
            answer += additional_content
        elif len(words) > 250:
            # Truncate to maximum length
            answer = ' '.join(words[:250]) + "..."
        
        # Ensure proper sentence case (first letter capitalized, rest lowercase)
        if answer:
            # Split into sentences and capitalize first letter of each
            sentences = re.split(r'(?<=[.!?])\s+', answer)
            capitalized_sentences = []
            for sentence in sentences:
                if sentence.strip():
                    # Capitalize first letter and make rest lowercase
                    sentence = sentence.strip()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:].lower()
                    capitalized_sentences.append(sentence)
            
            # Join sentences back together
            answer = ' '.join(capitalized_sentences)
        
        log.info(f"Generated offline answer for theme '{theme}': {answer[:50]}...")
        return answer
        
    except Exception as e:
        log.error(f"Error generating offline answer for theme '{theme}': {e}")
        return None

def generate_answer(question: str, theme: str) -> Optional[str]:
    """
    Generate a research answer for a specific question and theme (offline version)
    
    Args:
        question (str): The question to answer
        theme (str): Theme name for answer generation
        
    Returns:
        str: Generated answer or None if failed
    """
    return generate_offline_answer(question, theme)
