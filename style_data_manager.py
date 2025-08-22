#!/usr/bin/env python3
"""
Style Data Management Module
Handles architectural style data, characteristics, and base style definitions
"""

import os
import logging
import csv
from datetime import datetime, timedelta
from collections import defaultdict

# Setup logging
log = logging.getLogger(__name__)

class StyleDataManager:
    """Manages architectural style data and characteristics"""

    def __init__(self):
        self.base_styles = {
            'architecture': [
                'Modern', 'Contemporary', 'Classical', 'Minimalist', 'Brutalist', 'Art Deco', 'Gothic', 'Renaissance',
                'Baroque', 'Neoclassical', 'Victorian', 'Bauhaus', 'International Style', 'Postmodern', 'Deconstructivist',
                'High-Tech', 'Organic', 'Sustainable', 'Parametric', 'Biomimetic', 'Futuristic', 'Vernacular', 'Regional',
                'Tropical', 'Mediterranean', 'Scandinavian', 'Japanese', 'Chinese', 'Islamic', 'African'
            ],
            'construction': [
                'Industrial', 'Modern', 'Sustainable', 'Innovative', 'Prefabricated', 'Modular', 'Steel Frame', 'Concrete',
                'Timber Frame', 'Masonry', 'Glass and Steel', 'Composite', '3D Printed', 'Robotic', 'Smart Construction',
                'Green Building', 'Passive House', 'Net Zero', 'Circular Economy', 'Biomimetic', 'Adaptive', 'Resilient',
                'Disaster Resistant', 'Seismic', 'Hurricane Resistant', 'Fire Resistant', 'Acoustic', 'Thermal', 'Structural', 'Geotechnical'
            ],
            'design': [
                'Contemporary', 'Modern', 'Minimalist', 'Eclectic', 'Scandinavian', 'Japanese', 'Industrial', 'Bohemian',
                'Mid-Century Modern', 'Art Nouveau', 'Art Deco', 'Victorian', 'Rustic', 'Coastal', 'Urban', 'Tropical',
                'Mediterranean', 'Moroccan', 'Asian', 'Nordic', 'Industrial Chic', 'Vintage', 'Retro', 'Futuristic',
                'Sustainable', 'Biophilic', 'Wellness', 'Smart Design', 'Universal', 'Inclusive'
            ],
            'engineering': [
                'Modern', 'Industrial', 'Technical', 'Innovative', 'Structural', 'Mechanical', 'Electrical', 'Civil',
                'Environmental', 'Transportation', 'Geotechnical', 'Hydraulic', 'Aerospace', 'Biomedical', 'Robotics',
                'Automation', 'Smart Systems', 'IoT', 'AI-Integrated', 'Sustainable', 'Resilient', 'Adaptive', 'Modular',
                'Prefabricated', '3D Printed', 'Digital Twin', 'BIM', 'Parametric', 'Computational', 'Generative'
            ],
            'interiors': [
                'Contemporary', 'Modern', 'Minimalist', 'Luxury', 'Scandinavian', 'Japanese', 'Industrial', 'Bohemian',
                'Mid-Century Modern', 'Art Deco', 'Victorian', 'Rustic', 'Coastal', 'Urban', 'Tropical', 'Mediterranean',
                'Moroccan', 'Asian', 'Nordic', 'Industrial Chic', 'Vintage', 'Retro', 'Futuristic', 'Sustainable',
                'Biophilic', 'Wellness', 'Smart Home', 'Universal Design', 'Inclusive', 'Accessible'
            ],
            'marketing': [
                'Modern', 'Contemporary', 'Professional', 'Creative', 'Digital', 'Social Media', 'Brand Identity',
                'Visual Communication', 'Typography', 'Color Psychology', 'User Experience', 'Interactive', 'Immersive',
                'Storytelling', 'Content Marketing', 'Influencer', 'Viral', 'Authentic', 'Transparent', 'Sustainable',
                'Socially Conscious', 'Inclusive', 'Diverse', 'Accessible', 'Mobile-First', 'Omnichannel', 'Data-Driven',
                'Personalized', 'Experiential', 'Emotional', 'Memorable'
            ],
            'planning': [
                'Modern', 'Sustainable', 'Urban', 'Contemporary', 'Smart City', 'Green Infrastructure', 'Transit-Oriented',
                'Mixed-Use', 'Walkable', 'Bike-Friendly', 'Resilient', 'Adaptive', 'Inclusive', 'Equitable', 'Accessible',
                'Healthy', 'Wellness', 'Biophilic', 'Circular', 'Regenerative', 'Carbon Neutral', 'Zero Waste',
                'Community-Centered', 'Participatory', 'Data-Driven', 'Digital Twin', '15-Minute City', 'Garden City',
                'New Urbanism', 'Traditional Neighborhood'
            ],
            'urbanism': [
                'Modern', 'Sustainable', 'Urban', 'Contemporary', 'Smart City', 'Green Infrastructure', 'Transit-Oriented',
                'Mixed-Use', 'Walkable', 'Bike-Friendly', 'Resilient', 'Adaptive', 'Inclusive', 'Equitable', 'Accessible',
                'Healthy', 'Wellness', 'Biophilic', 'Circular', 'Regenerative', 'Carbon Neutral', 'Zero Waste',
                'Community-Centered', 'Participatory', 'Data-Driven', 'Digital Twin', '15-Minute City', 'Garden City',
                'New Urbanism', 'Traditional Neighborhood'
            ]
        }

        self.style_characteristics = {
            'Modern': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high'},
            'Classical': {'period': 'traditional', 'complexity': 'high', 'innovation': 'low'},
            'Sustainable': {'period': 'contemporary', 'complexity': 'medium', 'innovation': 'high'},
            'Minimalist': {'period': 'contemporary', 'complexity': 'low', 'innovation': 'medium'},
            'Brutalist': {'period': 'modern', 'complexity': 'high', 'innovation': 'medium'},
            'Futuristic': {'period': 'contemporary', 'complexity': 'high', 'innovation': 'very_high'},
            'Vernacular': {'period': 'traditional', 'complexity': 'low', 'innovation': 'low'},
            'Parametric': {'period': 'contemporary', 'complexity': 'very_high', 'innovation': 'very_high'}
        }

        self.style_trends = defaultdict(list)

        # Load style history if exists
        self.load_style_history()

    def load_style_history(self):
        """Load style usage history from CSV for trend analysis"""
        try:
            log_csv_file = os.getenv('LOG_CSV_FILE', 'log.csv')
            if os.path.exists(log_csv_file):
                with open(log_csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('style') and row.get('category'):
                            timestamp = row.get('created_timestamp', '')
                            self.style_trends[row['category']].append({
                                'style': row['style'],
                                'timestamp': timestamp,
                                'question': row.get('question', '')
                            })
                log.info(f"Loaded style history: {sum(len(trends) for trends in self.style_trends.values())} entries")
        except Exception as e:
            log.warning(f"Could not load style history: {e}")

    def get_base_styles_for_category(self, category):
        """Get base styles for a specific category"""
        return self.base_styles.get(category, [])

    def get_style_characteristics(self, style):
        """Get characteristics of a given style"""
        return self.style_characteristics.get(style, {
            'period': 'contemporary', 
            'complexity': 'medium', 
            'innovation': 'medium'
        })

    def get_all_categories(self):
        """Get all available categories"""
        return list(self.base_styles.keys())

    def get_style_trends_data(self, category):
        """Get style trends data for a category"""
        return self.style_trends.get(category, [])

    def add_style_usage(self, category, style, question, timestamp=None):
        """Add a style usage entry to trends"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.style_trends[category].append({
            'style': style,
            'timestamp': timestamp,
            'question': question
        })

# Global instance
style_data_manager = StyleDataManager()

# Convenience functions
def get_base_styles_for_category(category):
    """Get base styles for a specific category"""
    return style_data_manager.get_base_styles_for_category(category)

def get_style_characteristics(style):
    """Get characteristics of a given style"""
    return style_data_manager.get_style_characteristics(style)

def get_all_categories():
    """Get all available categories"""
    return style_data_manager.get_all_categories()
