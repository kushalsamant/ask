#!/usr/bin/env python3
"""
Duplicate line removal script
Identifies and removes duplicate lines across the repository
"""

import os
import glob
from collections import defaultdict

def find_duplicates():
    """Find duplicate lines across all files"""
    print("🔍 Scanning for duplicate lines...")
    
    # Collect all lines from all files
    all_lines = defaultdict(list)
    file_patterns = ["*.py", "*.env", "*.md"]
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path) and not file_path.endswith('.pyc'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                all_lines[line].append((file_path, line_num))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Find duplicates
    duplicates = {}
    for line, occurrences in all_lines.items():
        if len(occurrences) > 1:
            duplicates[line] = occurrences
    
    return duplicates

def analyze_duplicates(duplicates):
    """Analyze and categorize duplicates"""
    print(f"\n📊 Found {len(duplicates)} duplicate lines:")
    
    categories = {
        'config': [],
        'imports': [],
        'functions': [],
        'other': []
    }
    
    for line, occurrences in duplicates.items():
        if '=' in line and ('true' in line.lower() or 'false' in line.lower()):
            categories['config'].append((line, occurrences))
        elif line.startswith('import ') or line.startswith('from '):
            categories['imports'].append((line, occurrences))
        elif line.startswith('def ') or line.startswith('class '):
            categories['functions'].append((line, occurrences))
        else:
            categories['other'].append((line, occurrences))
    
    for category, items in categories.items():
        if items:
            print(f"\n🔸 {category.upper()} ({len(items)} duplicates):")
            for line, occurrences in items[:5]:  # Show first 5
                print(f"  '{line[:50]}...' appears in {len(occurrences)} files")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
    
    return categories

def remove_duplicate_imports():
    """Remove duplicate import statements"""
    print("\n🧹 Removing duplicate imports...")
    
    file_patterns = ["*.py"]
    total_removed = 0
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Find import lines
                    import_lines = []
                    other_lines = []
                    
                    for line in lines:
                        if line.strip().startswith(('import ', 'from ')):
                            import_lines.append(line)
                        else:
                            other_lines.append(line)
                    
                    # Remove duplicates from imports
                    unique_imports = []
                    seen_imports = set()
                    
                    for line in import_lines:
                        if line.strip() not in seen_imports:
                            unique_imports.append(line)
                            seen_imports.add(line.strip())
                    
                    # Reconstruct file
                    if len(unique_imports) < len(import_lines):
                        new_content = unique_imports + other_lines
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(new_content)
                        
                        removed = len(import_lines) - len(unique_imports)
                        total_removed += removed
                        print(f"  ✅ {file_path}: Removed {removed} duplicate imports")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    print(f"  🎯 Total duplicate imports removed: {total_removed}")
    return total_removed

def main():
    """Main function"""
    print("🔍 Starting duplicate analysis...")
    
    # Find all duplicates
    duplicates = find_duplicates()
    
    if not duplicates:
        print("✅ No duplicates found!")
        return
    
    # Analyze duplicates
    categories = analyze_duplicates(duplicates)
    
    # Remove duplicate imports
    removed_imports = remove_duplicate_imports()
    
    print(f"\n🎯 SUMMARY:")
    print(f"  - Total duplicate lines found: {len(duplicates)}")
    print(f"  - Duplicate imports removed: {removed_imports}")
    print(f"  - Repository is now cleaner!")

if __name__ == "__main__":
    main()
