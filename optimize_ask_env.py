#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASK Environment File Optimizer
Removes duplicates, improves structure, and optimizes configuration
"""

import os
import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class ASKEnvOptimizer:
    """Optimize the ask.env configuration file"""
    
    def __init__(self, input_file: str = 'ask.env', output_file: str = 'ask.env.optimized'):
        self.input_file = input_file
        self.output_file = output_file
        self.sections = []
        self.variables = {}
        self.duplicates = []
        
    def load_and_analyze(self):
        """Load and analyze the environment file"""
        print(f"🔍 Analyzing {self.input_file}...")
        
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file {self.input_file} not found")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse sections and variables
        current_section = "GENERAL"
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.startswith('#') and '=' in line and 'CONFIGURATION' in line.upper():
                current_section = line.replace('#', '').replace('=', '').strip()
                if current_section not in self.sections:
                    self.sections.append(current_section)
            
            # Parse variable definitions
            elif line and not line.startswith('#') and '=' in line:
                # Split on first '=' and handle comments
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Remove inline comments
                if '#' in value:
                    value = value.split('#')[0].strip()
                
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Check for duplicates
                if key in self.variables:
                    self.duplicates.append(key)
                    print(f"⚠️  Found duplicate: {key}")
                else:
                    self.variables[key] = {
                        'value': value,
                        'section': current_section,
                        'original_line': line
                    }
        
        print(f"📊 Analysis complete:")
        print(f"   - Total variables: {len(self.variables)}")
        print(f"   - Duplicates found: {len(self.duplicates)}")
        print(f"   - Sections: {len(self.sections)}")
    
    def identify_duplicates(self) -> Dict[str, List[str]]:
        """Identify and categorize duplicates"""
        duplicate_groups = defaultdict(list)
        
        for duplicate in self.duplicates:
            # Categorize duplicates
            if 'MARGIN' in duplicate:
                duplicate_groups['MARGIN'].append(duplicate)
            elif 'TOC_' in duplicate:
                duplicate_groups['TOC'].append(duplicate)
            elif 'IMAGE_' in duplicate:
                duplicate_groups['IMAGE'].append(duplicate)
            elif 'LOG_' in duplicate:
                duplicate_groups['LOG'].append(duplicate)
            elif 'OUTPUT_' in duplicate:
                duplicate_groups['OUTPUT'].append(duplicate)
            elif 'QA_' in duplicate:
                duplicate_groups['QA'].append(duplicate)
            else:
                duplicate_groups['OTHER'].append(duplicate)
        
        return dict(duplicate_groups)
    
    def resolve_duplicates(self) -> Dict[str, str]:
        """Resolve duplicate variables by keeping the most appropriate one"""
        resolution_rules = {
            'MARGIN_BOTTOM': 'IMAGE_MARGIN_BOTTOM',  # Keep image-specific version
            'TOC_QUESTION_PREVIEW_LENGTH': 'IMAGE_TOC_QUESTION_PREVIEW_LENGTH',  # Keep image-specific version
            'IMAGE_TEXT_WRAP_WIDTH_ANSWER': 'TEXT_WRAP_WIDTH_ANSWER',  # Keep general version
            'IMAGE_TEXT_WRAP_WIDTH_OVERLAY': 'TEXT_WRAP_WIDTH_OVERLAY',  # Keep general version
            'IMAGE_FONT_SIZE_FOOTER': 'FONT_SIZE_FOOTER',  # Keep general version
            'LOG_QUESTION_DISPLAY_LENGTH': 'QUESTION_DISPLAY_LENGTH',  # Keep general version
            'QA_PAIRS_PER_VOLUME': 'VOLUME_QA_PAIRS',  # Keep volume-specific version
            'OUTPUT_DIR': 'IMAGES_DIR'  # Keep images-specific version
        }
        
        resolved_variables = {}
        removed_variables = []
        
        for key, value_info in self.variables.items():
            if key in self.duplicates:
                # Check if we have a resolution rule
                if key in resolution_rules:
                    resolved_key = resolution_rules[key]
                    if resolved_key in self.variables:
                        # Keep the resolved version, remove this one
                        removed_variables.append(key)
                        print(f"🔄 Resolved duplicate: {key} -> {resolved_key}")
                        continue
                    else:
                        # Rename this variable to the resolved key
                        resolved_variables[resolved_key] = value_info
                        removed_variables.append(key)
                        print(f"🔄 Renamed duplicate: {key} -> {resolved_key}")
                        continue
                else:
                    # For other duplicates, keep the first occurrence
                    if key not in resolved_variables:
                        resolved_variables[key] = value_info
                    else:
                        removed_variables.append(key)
                        print(f"🗑️  Removed duplicate: {key}")
            else:
                resolved_variables[key] = value_info
        
        print(f"✅ Resolved {len(removed_variables)} duplicate variables")
        return resolved_variables
    
    def optimize_structure(self, variables: Dict[str, dict]) -> str:
        """Create optimized environment file structure"""
        print("🏗️  Creating optimized structure...")
        
        # Define section order
        section_order = [
            "API CONFIGURATION",
            "AI MODEL CONFIGURATION", 
            "API TIMEOUT AND RATE LIMITING",
            "TEXT GENERATION CONFIGURATION",
            "IMAGE GENERATION CONFIGURATION",
            "IMAGE GENERATION FEATURES",
            "TABLE OF CONTENTS FEATURES",
            "TOC TEMPLATES",
            "INDIVIDUAL IMAGE SETTINGS",
            "PAGE AND LAYOUT SETTINGS",
            "TYPOGRAPHY SETTINGS",
            "COLOR SETTINGS",
            "SPACING SETTINGS",
            "MARGIN SETTINGS",
            "COVER GENERATION SETTINGS",
            "LOGGING FEATURES",
            "PROGRESS TRACKING FEATURES",
            "ERROR HANDLING FEATURES",
            "VOLUME CONFIGURATION",
            "OUTPUT DIRECTORY CONFIGURATION",
            "TOC CONTENT SETTINGS",
            "COMPILATION SETTINGS",
            "TIMING AND PERFORMANCE",
            "OUTPUT FORMATS",
            "QUALITY CONTROL",
            "BACKUP AND RECOVERY",
            "NOTIFICATIONS",
            "DEBUGGING",
            "IMAGE TEXT OVERLAY CONFIGURATION",
            "FONT CONFIGURATION",
            "DIRECTORY CONFIGURATION",
            "QUESTION GENERATION CONFIGURATION",
            "CHAINED QUESTION FLOW CONFIGURATION",
            "STYLE GENERATION CONFIGURATION",
            "RESEARCH EXPLORER CONFIGURATION",
            "DATA MANAGEMENT CONFIGURATION",
            "MODE-SPECIFIC CONFIGURATION",
            "SEQUENTIAL NUMBERING CONFIGURATION",
            "TOC Grouping Configuration",
            "TOC Content Configuration",
            "Individual IMAGE Configuration",
            "IMAGE Page Configuration",
            "LOGGING CONFIGURATION",
            "Individual IMAGE Logging Configuration",
            "Progress Tracking Configuration",
            "Error Handling Configuration",
            "COVER GENERATION CONFIGURATION",
            "TOC BACKGROUND CONFIGURATION",
            "VOLUME CONFIGURATION",
            "SYSTEM PROMPTS CONFIGURATION",
            "TEST CONFIGURATION",
            "OUTPUT DIRECTORY CONFIGURATION",
            "Cross-Disciplinary Generation Settings",
            "Question Management Settings",
            "Style Management Settings",
            "CPU Image Generation Settings",
            "GPU Image Generation Settings"
        ]
        
        # Group variables by section
        section_variables = defaultdict(list)
        for key, value_info in variables.items():
            section = value_info['section']
            section_variables[section].append((key, value_info))
        
        # Build optimized content
        optimized_content = []
        optimized_content.append("# =============================================================================")
        optimized_content.append("")
        optimized_content.append("# ASK: Daily Research - Optimized Configuration")
        optimized_content.append("")
        optimized_content.append("# =============================================================================")
        optimized_content.append("")
        
        # Add sections in order
        for section in section_order:
            if section in section_variables:
                optimized_content.append(f"# {section}")
                optimized_content.append("# =============================================================================")
                optimized_content.append("")
                
                # Add variables for this section
                for key, value_info in sorted(section_variables[section]):
                    value = value_info['value']
                    optimized_content.append(f"{key}={value}")
                
                optimized_content.append("")
        
        # Add any remaining sections
        for section in section_variables:
            if section not in section_order:
                optimized_content.append(f"# {section}")
                optimized_content.append("# =============================================================================")
                optimized_content.append("")
                
                for key, value_info in sorted(section_variables[section]):
                    value = value_info['value']
                    optimized_content.append(f"{key}={value}")
                
                optimized_content.append("")
        
        return '\n'.join(optimized_content)
    
    def create_backup(self):
        """Create a backup of the original file"""
        backup_file = f"{self.input_file}.backup"
        if not os.path.exists(backup_file):
            import shutil
            shutil.copy2(self.input_file, backup_file)
            print(f"💾 Created backup: {backup_file}")
    
    def optimize(self):
        """Run the complete optimization process"""
        print("🚀 Starting ASK Environment Optimization...")
        print("=" * 60)
        
        # Load and analyze
        self.load_and_analyze()
        
        # Create backup
        self.create_backup()
        
        # Identify duplicates
        duplicate_groups = self.identify_duplicates()
        print("\n📋 Duplicate Analysis:")
        for category, duplicates in duplicate_groups.items():
            if duplicates:
                print(f"   {category}: {', '.join(duplicates)}")
        
        # Resolve duplicates
        resolved_variables = self.resolve_duplicates()
        
        # Create optimized structure
        optimized_content = self.optimize_structure(resolved_variables)
        
        # Write optimized file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        # Calculate improvements
        original_size = os.path.getsize(self.input_file)
        optimized_size = os.path.getsize(self.output_file)
        size_reduction = ((original_size - optimized_size) / original_size) * 100
        
        print("\n✅ Optimization Complete!")
        print("=" * 60)
        print(f"📁 Original file: {self.input_file} ({original_size:,} bytes)")
        print(f"📁 Optimized file: {self.output_file} ({optimized_size:,} bytes)")
        print(f"📉 Size reduction: {size_reduction:.1f}%")
        print(f"🔧 Variables optimized: {len(self.duplicates)}")
        print(f"📊 Total variables: {len(resolved_variables)}")
        
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'size_reduction': size_reduction,
            'duplicates_resolved': len(self.duplicates),
            'total_variables': len(resolved_variables)
        }

def main():
    """Main optimization function"""
    optimizer = ASKEnvOptimizer()
    results = optimizer.optimize()
    
    print("\n🎯 Next Steps:")
    print("1. Review the optimized file: ask.env.optimized")
    print("2. Test the optimized configuration")
    print("3. Replace the original file if satisfied")
    print("4. Run the testing suite to verify improvements")

if __name__ == "__main__":
    main()
