#!/usr/bin/env python3
"""
Hybrid Cross-Disciplinary Chained Content Example
Demonstrates how cross-disciplinary and chained content work together
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('ask.env')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(name)s:%(levelname)s:%(message)s')
log = logging.getLogger(__name__)

def demonstrate_hybrid_mode():
    """Demonstrate the hybrid cross-disciplinary chained content generation"""
    
    print("🎯 HYBRID CROSS-DISCIPLINARY CHAINED CONTENT GENERATION")
    print("=" * 60)
    print()
    
    print("📋 What This Does:")
    print("1. Starts with cross-disciplinary questions that connect multiple architectural themes")
    print("2. Chains deeper questions that explore the intersection progressively")
    print("3. Creates a logical flow from broad concepts to specific applications")
    print()
    
    print("🔄 Example Flow:")
    print()
    print("Theme: 'sustainability_technology'")
    print("Chain Length: 3 questions")
    print()
    print("Question 1 (Cross-Disciplinary):")
    print("  'How do Architectural Design and Construction Technology work together")
    print("   in sustainable building?'")
    print()
    print("Answer 1:")
    print("  'The integration involves early collaboration, BIM coordination,")
    print("   and material selection that considers both design aesthetics and")
    print("   construction efficiency...'")
    print()
    print("Question 2 (Chained):")
    print("  'What specific BIM coordination strategies optimize the design-")
    print("   construction interface for sustainability?'")
    print()
    print("Answer 2:")
    print("  'BIM coordination requires standardized protocols, clash detection,")
    print("   and real-time collaboration between design and construction teams...'")
    print()
    print("Question 3 (Chained):")
    print("  'How can real-time collaboration tools enhance sustainable material")
    print("   selection during the construction phase?'")
    print()
    print("Answer 3:")
    print("  'Real-time tools enable instant feedback on material availability,")
    print("   cost, environmental impact, and supply chain sustainability...'")
    print()
    
    print("🎨 Benefits of Hybrid Mode:")
    print("✅ Combines breadth (cross-disciplinary) with depth (chained)")
    print("✅ Creates progressive learning paths")
    print("✅ Explores intersections between architectural fields")
    print("✅ Builds comprehensive understanding of complex topics")
    print("✅ Generates innovative insights at theme boundaries")
    print()
    
    print("🚀 How to Use:")
    print("python main.py hybrid")
    print()
    print("Configuration (in ask.env):")
    print("HYBRID_THEME_COUNT=2      # Number of themes to explore")
    print("HYBRID_CHAIN_LENGTH=3     # Questions per chain")
    print()
    
    print("📊 Expected Output:")
    print("• 2 themes × 3 questions = 6 total Q&A pairs")
    print("• Each theme gets its own chain of connected questions")
    print("• Questions progress from broad to specific")
    print("• Images generated for each Q&A pair")
    print("• All content logged and organized by chain")
    print()
    
    print("🎯 Perfect For:")
    print("• Educational content that builds progressively")
    print("• Research exploration of complex topics")
    print("• Innovation discovery at theme intersections")
    print("• Comprehensive coverage of architectural themes")
    print("• Creating connected content series")
    print()

def show_available_themes():
    """Show available cross-disciplinary themes"""
    
    print("🎨 AVAILABLE CROSS-DISCIPLINARY THEMES")
    print("=" * 40)
    print()
    
    try:
        from research_theme_system import get_all_themes
        themes = get_all_themes()
        
        print(f"Total themes available: {len(themes)}")
        print()
        
        # Group themes by type
        main_themes = [t for t in themes if t.startswith('main_')]
        sub_themes = [t for t in themes if '_' in t and not t.startswith('main_') and t != 'all_categories']
        
        print("🏗️  Main Theme Themes:")
        for theme in main_themes[:5]:  # Show first 5
            print(f"  • {theme.replace('main_', '').replace('_', ' ').title()}")
        if len(main_themes) > 5:
            print(f"  • ... and {len(main_themes) - 5} more")
        print()
        
        print("🔗 Subcategory Themes:")
        for theme in sub_themes[:10]:  # Show first 10
            print(f"  • {theme.replace('_', ' ').title()}")
        if len(sub_themes) > 10:
            print(f"  • ... and {len(sub_themes) - 10} more")
        print()
        
        print("💡 Example Theme Combinations:")
        print("  • sustainability_technology")
        print("  • urban_design_innovation")
        print("  • construction_digital")
        print("  • interior_engineering")
        print("  • planning_technology")
        print()
        
    except Exception as e:
        print(f"❌ Error loading themes: {e}")
        print("Make sure research_theme_system.py is available")

if __name__ == "__main__":
    demonstrate_hybrid_mode()
    show_available_themes()
    
    print("🎉 Ready to generate hybrid content!")
    print("Run: python main.py hybrid")
