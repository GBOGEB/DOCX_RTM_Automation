#!/usr/bin/env python3
"""
Fix remaining syntax errors in files that still fail Black formatting
"""

import os


def fix_debug_full_pipeline():
    """Fix syntax errors in debug_full_pipeline.py files"""
    paths = [
        "scripts/debug_full_pipeline.py",
        "DOCX_RTM_Automation/scripts/debug_full_pipeline.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue

        print(f"Fixing {path}...")
        try:
            # Read the file content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for missing line numbers
            if "<line number missing in source>" in content:
                # Completely replace the problematic line
                lines = content.splitlines()
                fixed_lines = []

                for _i, line in enumerate(lines):  # Mark i as unused
                    if 'logging.debug("Pipeline execution")' in line:
                        # Replace with a complete, working version of the line
                        fixed_lines.append(
                            '        logging.debug("Pipeline execution")'
                        )
                    else:
                        fixed_lines.append(line)

                content = "\n".join(fixed_lines)

            # Write the fixed content back to the file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Finished fixing {path}")

        except IOError as e:
            print(f"IOError fixing {path}: {e}")
        except Exception as e:
            print(f"Error fixing {path}: {e}")
            # Add more specific error handling if needed
