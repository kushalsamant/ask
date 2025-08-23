import os
import logging
import random
import requests
from style_data_manager import get_base_styles_for_category
            from style_data_manager import get_style_characteristics
#!/usr/bin/env python3
"""
Style AI Generator Module
Handles AI-powered architectural style generation and suggestions
"""


# Setup logging
log = logging.getLogger(__name__)

# Environment variables
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
TEXT_MODEL = os.getenv('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))

class StyleAIGenerator:
    """AI-powered architectural style generator"""

    def __init__(self):
        self.context_weights = {
            'question_complexity': 0.3,
            'category_specificity': 0.4,
            'trend_popularity': 0.2,
            'innovation_factor': 0.1
        }

    def get_ai_generated_style_suggestion(self, theme, question, context=None):
        """Generate AI-powered style suggestions based on question and context"""
        try:
            url = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1') + '/chat/completions'
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }

            system_prompt = """You are an expert architectural style consultant. Analyze the given architectural question and suggest the most appropriate architectural style(s) that would best represent or complement the concept being explored."""

            context_info = f"Context: {context}" if context else ""

            prompt = f"""Question: {question}
            theme: {theme}
            {context_info}

            Based on this architectural question, suggest 3-5 most appropriate architectural styles from this list:
            {', '.join(get_base_styles_for_category(theme))}

            Consider:
            - How the style relates to the question's theme
            - Contemporary relevance
            - Visual impact and representation
            - Innovation potential

            Return only the style names, separated by commas:"""

            payload = {
                "model": TEXT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 100,
                "top_p": 0.9
            }

            response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    suggestions = data['choices'][0]['message']['content'].strip()
                    # Parse suggestions
                    suggested_styles = [s.strip() for s in suggestions.split(',')]
                    # Filter to valid styles
                    valid_styles = [s for s in suggested_styles if s in get_base_styles_for_category(theme)]
                    return valid_styles[:3]  # Return top 3 suggestions
                else:
                    log.warning("Invalid API response for style suggestions")
                    return []
            else:
                log.error(f"API error generating style suggestions: {response.status_code}")
                return []

        except Exception as e:
            log.error(f"Error generating AI style suggestions: {e}")
            return []

    def create_dynamic_style_combination(self, theme, base_style, question_context=None):
        """Create dynamic style combinations based on context and trends"""
        try:
            
            # Get base style characteristics
            style_characteristics = get_style_characteristics(base_style)

            # Find complementary styles
            complementary_styles = self.find_complementary_styles(theme, base_style)

            # Create combination
            if complementary_styles:
                combined_style = f"{base_style}-{random.choice(complementary_styles)}"

                # Add context-specific modifiers
                if question_context:
                    context_modifier = self.get_context_modifier(question_context)
                    if context_modifier:
                        combined_style = f"{combined_style}-{context_modifier}"

                return combined_style
            else:
                return base_style

        except Exception as e:
            log.error(f"Error creating dynamic style combination: {e}")
            return base_style

    def find_complementary_styles(self, theme, base_style):
        """Find styles that complement the base style"""
        
        base_characteristics = get_style_characteristics(base_style)
        available_styles = get_base_styles_for_category(theme)

        complementary = []
        for style in available_styles:
            if style != base_style:
                style_char = get_style_characteristics(style)

                # Check for complementary characteristics
                if (base_characteristics['period'] != style_char['period'] or
                    base_characteristics['complexity'] != style_char['complexity']):
                    complementary.append(style)

        return complementary[:3]  # Return top 3 complementary styles

    def get_context_modifier(self, question_context):
        """Get context-specific style modifiers"""
        modifiers = {
            'sustainable': 'Eco',
            'technology': 'Tech',
            'community': 'Social',
            'innovation': 'Innovative',
            'traditional': 'Heritage',
            'urban': 'Urban',
            'rural': 'Rural',
            'coastal': 'Coastal',
            'mountain': 'Alpine',
            'desert': 'Arid'
        }

        question_lower = question_context.lower()
        for key, modifier in modifiers.items():
            if key in question_lower:
                return modifier
        return None

    def get_style_variations(self, theme, base_style, count=3):
        """Generate style variations for a given base style"""
        try:
            
            variations = []
            base_characteristics = get_style_characteristics(base_style)

            for _ in range(count):
                # Create variation based on characteristics
                if base_characteristics['innovation'] == 'very_high':
                    variation = f"Next-Gen {base_style}"
                elif base_characteristics['period'] == 'traditional':
                    variation = f"Contemporary {base_style}"
                elif base_characteristics['complexity'] == 'high':
                    variation = f"Simplified {base_style}"
                else:
                    variation = f"Enhanced {base_style}"

                variations.append(variation)

            return variations

        except Exception as e:
            log.error(f"Error generating style variations: {e}")
            return [base_style] * count

# Global instance
style_ai_generator = StyleAIGenerator()

# Convenience functions
def get_ai_generated_style_suggestion(theme, question, context=None):
    """Get AI-generated style suggestions"""
    return style_ai_generator.get_ai_generated_style_suggestion(theme, question, context)

def create_dynamic_style_combination(theme, base_style, question_context=None):
    """Create dynamic style combinations"""
    return style_ai_generator.create_dynamic_style_combination(theme, base_style, question_context)

def get_style_variations(theme, base_style, count=3):
    """Generate style variations"""
    return style_ai_generator.get_style_variations(theme, base_style, count)
