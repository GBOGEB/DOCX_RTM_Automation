#!/usr/bin/env python3
"""
Unicode Safe Output Utilities
"""

import sys

def safe_print(text, **kwargs):
    """Print text with Unicode fallbacks."""
    replacements = {
        '🎉': '[SUCCESS]', '✅': '[OK]', '❌': '[ERROR]', '⚠️': '[WARNING]',
        '🔧': '[FIX]', '📁': '[DIR]', '📄': '[FILE]', '🚀': '[LAUNCH]',
        '💡': '[TIP]', '🔍': '[SEARCH]', '📊': '[REPORT]', '🎯': '[TARGET]',
        '•': '*', '→': '->', '←': '<-', '═': '=', '─': '-',
        'Ô£à': '[COMPLETE]', '­ƒôé': '[CHECK]', 'ÔÇó': '*'
    }

    # Apply replacements
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)

    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # Fallback to ASCII-only
        text = text.encode('ascii', 'replace').decode('ascii')
        print(text, **kwargs)

def safe_header(title, width=50):
    """Print a safe header."""
    safe_print("=" * width)
    safe_print(title.center(width))
    safe_print("=" * width)

def safe_success(message):
    """Print success message safely."""
    safe_print(f"[SUCCESS] {message}")

def safe_error(message):
    """Print error message safely."""
    safe_print(f"[ERROR] {message}")

def safe_info(message):
    """Print info message safely."""
    safe_print(f"[INFO] {message}")
