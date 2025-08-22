#!/usr/bin/env python3
"""
Style Trend Analyzer Module
Handles style usage trend analysis and reporting
"""

import os
import logging
from datetime import datetime, timedelta
from collections import Counter
from style_data_manager import style_data_manager, get_base_styles_for_category

# Setup logging
log = logging.getLogger(__name__)

class StyleTrendAnalyzer:
    """Analyzes style usage trends and generates reports"""

    def __init__(self):
        pass

    def analyze_style_trends(self, category, timeframe_days=30):
        """Analyze style usage trends for a category"""
        try:
            style_trends_data = style_data_manager.get_style_trends_data(category)
            if not style_trends_data:
                return {}

            # Filter by timeframe
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            recent_styles = []

            for entry in style_trends_data:
                try:
                    if entry['timestamp']:
                        entry_date = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                        if entry_date >= cutoff_date:
                            recent_styles.append(entry['style'])
                except:
                    continue

            # Count style usage
            style_counts = Counter(recent_styles)

            # Calculate trends
            trends = {
                'most_popular': style_counts.most_common(5),
                'trending_up': self.identify_trending_styles(category, style_counts),
                'underutilized': self.identify_underutilized_styles(category, style_counts),
                'total_usage': len(recent_styles)
            }

            return trends

        except Exception as e:
            log.error(f"Error analyzing style trends: {e}")
            return {}

    def identify_trending_styles(self, category, style_counts):
        """Identify styles that are trending upward"""
        # Simple trending logic - styles used more than average
        if not style_counts:
            return []

        avg_usage = sum(style_counts.values()) / len(style_counts)
        trending = [style for style, count in style_counts.items() if count > avg_usage * 1.5]
        return trending[:3]

    def identify_underutilized_styles(self, category, style_counts):
        """Identify styles that are underutilized"""
        all_styles = set(get_base_styles_for_category(category))
        used_styles = set(style_counts.keys())
        underutilized = all_styles - used_styles
        return list(underutilized)[:5]

    def get_style_report(self, category):
        """Generate comprehensive style analysis report"""
        try:
            trends = self.analyze_style_trends(category)

            report = {
                'category': category,
                'total_styles': len(get_base_styles_for_category(category)),
                'recent_usage': trends.get('total_usage', 0),
                'most_popular': trends.get('most_popular', []),
                'trending_up': trends.get('trending_up', []),
                'underutilized': trends.get('underutilized', []),
                'recommendations': self.generate_style_recommendations(category, trends)
            }

            return report

        except Exception as e:
            log.error(f"Error generating style report: {e}")
            return {}

    def generate_style_recommendations(self, category, trends):
        """Generate style recommendations based on trends"""
        recommendations = []

        # Recommend underutilized styles
        if trends.get('underutilized'):
            recommendations.append(f"Consider using underutilized styles: {', '.join(trends['underutilized'][:3])}")

        # Recommend trending styles
        if trends.get('trending_up'):
            recommendations.append(f"Trending styles to explore: {', '.join(trends['trending_up'])}")

        # Recommend style combinations
        if trends.get('most_popular'):
            popular_style = trends['most_popular'][0][0]
            recommendations.append(f"Try combining {popular_style} with complementary styles")

        return recommendations

    def get_style_usage_statistics(self, category, timeframe_days=30):
        """Get detailed style usage statistics"""
        try:
            trends = self.analyze_style_trends(category, timeframe_days)
            
            stats = {
                'category': category,
                'timeframe_days': timeframe_days,
                'total_usage': trends.get('total_usage', 0),
                'unique_styles_used': len(set([style for style, _ in trends.get('most_popular', [])])),
                'most_popular_style': trends.get('most_popular', [{}])[0][0] if trends.get('most_popular') else None,
                'most_popular_count': trends.get('most_popular', [{}])[0][1] if trends.get('most_popular') else 0,
                'trending_styles_count': len(trends.get('trending_up', [])),
                'underutilized_styles_count': len(trends.get('underutilized', []))
            }
            
            return stats

        except Exception as e:
            log.error(f"Error getting style usage statistics: {e}")
            return {}

    def compare_categories_trends(self, categories, timeframe_days=30):
        """Compare style trends across multiple categories"""
        try:
            comparison = {}
            
            for category in categories:
                trends = self.analyze_style_trends(category, timeframe_days)
                comparison[category] = {
                    'total_usage': trends.get('total_usage', 0),
                    'most_popular': trends.get('most_popular', []),
                    'trending_up': trends.get('trending_up', []),
                    'underutilized': trends.get('underutilized', [])
                }
            
            return comparison

        except Exception as e:
            log.error(f"Error comparing categories trends: {e}")
            return {}

# Global instance
style_trend_analyzer = StyleTrendAnalyzer()

# Convenience functions
def analyze_style_trends(category, timeframe_days=30):
    """Analyze style trends for a category"""
    return style_trend_analyzer.analyze_style_trends(category, timeframe_days)

def get_style_report(category):
    """Get comprehensive style report"""
    return style_trend_analyzer.get_style_report(category)

def get_style_usage_statistics(category, timeframe_days=30):
    """Get detailed style usage statistics"""
    return style_trend_analyzer.get_style_usage_statistics(category, timeframe_days)

def compare_categories_trends(categories, timeframe_days=30):
    """Compare style trends across multiple categories"""
    return style_trend_analyzer.compare_categories_trends(categories, timeframe_days)
