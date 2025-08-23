#!/usr/bin/env python3
"""
Systematic terminology fix script
Replaces all theme/theme inconsistencies across the repository
"""

import os
import re
import glob

def fix_file(file_path):
    """Fix terminology in a single file"""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes = 0
    
    # Replace _THEMES_ with _THEMES_
    old_content = content
    content = re.sub(r'_THEMES_', '_THEMES_', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced _THEMES_ with _THEMES_")
    
    # Replace _THEME_ with _THEME_
    old_content = content
    content = re.sub(r'_THEME_', '_THEME_', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced _THEME_ with _THEME_")
    
    # Replace 'theme' with 'theme' (case sensitive)
    old_content = content
    content = re.sub(r'\bcategory\b', 'theme', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced 'theme' with 'theme'")
    
    # Replace 'themes' with 'themes' (case sensitive)
    old_content = content
    content = re.sub(r'\bcategories\b', 'themes', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced 'themes' with 'themes'")
    
    # Replace 'Theme' with 'Theme' (capitalized)
    old_content = content
    content = re.sub(r'\bCategory\b', 'Theme', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced 'Theme' with 'Theme'")
    
    # Replace 'Themes' with 'Themes' (capitalized)
    old_content = content
    content = re.sub(r'\bCategories\b', 'Themes', content)
    if content != old_content:
        changes += 1
        print(f"  - Replaced 'Themes' with 'Themes'")
    
    if changes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed {changes} terminology issues")
    else:
        print(f"  ✅ No changes needed")
    
    return changes

def main():
    """Main function to process all files"""
    print("🔍 Starting systematic terminology fix...")
    
    # Get all Python and environment files
    file_patterns = [
        "*.py",
        "*.env",
        "*.md",
        "*.txt"
    ]
    
    total_files = 0
    total_changes = 0
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path):
                total_files += 1
                changes = fix_file(file_path)
                total_changes += changes
    
    print(f"\n🎯 SUMMARY:")
    print(f"  - Files processed: {total_files}")
    print(f"  - Total terminology fixes: {total_changes}")
    print(f"  - Repository terminology is now consistent!")

if __name__ == "__main__":
    main()
