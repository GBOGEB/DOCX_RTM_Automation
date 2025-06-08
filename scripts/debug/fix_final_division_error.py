#!/usr/bin/env python3
"""
Fix the final division by zero error in enhanced_requirement_parser.py
"""

from pathlib import Path
import re

def fix_division_by_zero_comprehensive():
    """Comprehensively fix all division by zero errors."""
    file_path = Path("enhanced_requirement_parser.py")

    if not file_path.exists():
        print("enhanced_requirement_parser.py not found")
        return

    print("🔧 Comprehensively fixing division by zero errors...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix all instances of division by total_requirements
    # Pattern 1: implemented_requirements*100/total_requirements
    content = re.sub(
        r'implemented_requirements\*100/total_requirements',
        r'(implemented_requirements*100/total_requirements if total_requirements > 0 else 0)',
        content
    )

    # Pattern 2: Any division by total_requirements in f-strings
    content = re.sub(
        r'(\w+)\*100/total_requirements\.1f',
        r'(\1*100/total_requirements if total_requirements > 0 else 0):.1f',
        content
    )

    # Pattern 3: Simple division by total_requirements
    content = re.sub(
        r'/total_requirements',
        r'/(total_requirements if total_requirements > 0 else 1)',
        content
    )

    # Pattern 4: Fix the specific problematic line
    content = content.replace(
        'f"- **Implemented Requirements**: {implemented_requirements} ({implemented_requirements*100/total_requirements:.1f}% if total > 0)\\n"',
        'f"- **Implemented Requirements**: {implemented_requirements} ({(implemented_requirements*100/total_requirements if total_requirements > 0 else 0):.1f}%)\\n"'
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("   ✅ Comprehensively fixed division by zero errors")

if __name__ == "__main__":
    fix_division_by_zero_comprehensive()
