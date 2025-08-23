#!/usr/bin/env python3
"""
Code optimization script
Identifies unnecessary lines that can be skipped or removed
"""

import os
import glob
import re

def analyze_file(file_path):
    """Analyze a single file for optimization opportunities"""
    print(f"Analyzing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        issues = {
            'unused_imports': [],
            'commented_code': [],
            'empty_lines': 0,
            'redundant_comments': [],
            'hardcoded_values': [],
            'debug_prints': []
        }
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Count empty lines
            if not line:
                issues['empty_lines'] += 1
            
            # Find commented code (not docstrings)
            elif line.startswith('#') and any(keyword in line.lower() for keyword in ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ']):
                issues['commented_code'].append((line_num, line))
            
            # Find debug prints
            elif 'print(' in line and any(debug_word in line.lower() for debug_word in ['debug', 'temp', 'test', 'xxx']):
                issues['debug_prints'].append((line_num, line))
            
            # Find hardcoded values (simple heuristic)
            elif '=' in line and any(hardcoded in line for hardcoded in ['/path/', '/tmp/', 'localhost', '127.0.0.1']):
                issues['hardcoded_values'].append((line_num, line))
        
        # Check for unused imports (simple heuristic)
        import_lines = [i for i, line in enumerate(lines) if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) > 5:  # Flag files with many imports
            issues['unused_imports'] = import_lines
        
        return issues
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def main():
    """Main function"""
    print("🔍 Starting code optimization analysis...")
    
    file_patterns = ["*.py"]
    total_files = 0
    total_issues = 0
    
    summary = {
        'unused_imports': 0,
        'commented_code': 0,
        'empty_lines': 0,
        'debug_prints': 0,
        'hardcoded_values': 0
    }
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path) and not file_path.endswith('.pyc'):
                total_files += 1
                issues = analyze_file(file_path)
                
                if issues:
                    file_issues = 0
                    
                    if issues['unused_imports']:
                        print(f"  ⚠️  {len(issues['unused_imports'])} potential unused imports")
                        summary['unused_imports'] += len(issues['unused_imports'])
                        file_issues += len(issues['unused_imports'])
                    
                    if issues['commented_code']:
                        print(f"  🗑️  {len(issues['commented_code'])} commented code blocks")
                        summary['commented_code'] += len(issues['commented_code'])
                        file_issues += len(issues['commented_code'])
                    
                    if issues['empty_lines'] > 10:
                        print(f"  📝 {issues['empty_lines']} empty lines (consider cleanup)")
                        summary['empty_lines'] += issues['empty_lines']
                        file_issues += 1
                    
                    if issues['debug_prints']:
                        print(f"  🐛 {len(issues['debug_prints'])} debug print statements")
                        summary['debug_prints'] += len(issues['debug_prints'])
                        file_issues += len(issues['debug_prints'])
                    
                    if issues['hardcoded_values']:
                        print(f"  🔧 {len(issues['hardcoded_values'])} potential hardcoded values")
                        summary['hardcoded_values'] += len(issues['hardcoded_values'])
                        file_issues += len(issues['hardcoded_values'])
                    
                    if file_issues > 0:
                        total_issues += file_issues
                    else:
                        print(f"  ✅ Clean file")
    
    print(f"\n🎯 OPTIMIZATION SUMMARY:")
    print(f"  - Files analyzed: {total_files}")
    print(f"  - Total optimization opportunities: {total_issues}")
    print(f"  - Unused imports: {summary['unused_imports']}")
    print(f"  - Commented code: {summary['commented_code']}")
    print(f"  - Excessive empty lines: {summary['empty_lines']}")
    print(f"  - Debug prints: {summary['debug_prints']}")
    print(f"  - Hardcoded values: {summary['hardcoded_values']}")
    
    if total_issues > 0:
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"  - Remove {summary['commented_code']} commented code blocks")
        print(f"  - Clean up {summary['debug_prints']} debug statements")
        print(f"  - Review {summary['unused_imports']} import statements")
        print(f"  - Consider environment variables for {summary['hardcoded_values']} hardcoded values")
    else:
        print(f"\n✅ Repository is well-optimized!")

if __name__ == "__main__":
    main()
