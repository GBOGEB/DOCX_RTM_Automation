# Sample Files Guide

This guide provides information about sample files used in the DOCX_RTM_Automation pipeline and how to manage them effectively.

## Overview

The automation pipeline generates various files during its operation. These files can accumulate over time and may need periodic cleanup while preserving important data.

## Sample Files Directory Structure

```text
/samples/
    ├── input/
    │   ├── requirements/
    │   └── specifications/
    ├── output/
    │   ├── reports/
    │   └── matrices/
    └── backups/
            ├── daily/
            └── weekly/
```

## Backup Management

Backups are automatically generated during pipeline runs. To prevent excessive disk usage, you should periodically clean up old backup files.

### Using the Cleanup Script

We provide a Python-based cleanup utility script (`scripts/cleanup_backups.py`) that intelligently preserves the most recent backups while removing older ones:

```bash
# Run cleanup using default settings (often defined in a config file or script defaults)
python scripts/cleanup_backups.py

# Specify custom retention periods
python scripts/cleanup_backups.py --daily 10 --weekly 6 --monthly 2

# Dry run (shows what would be deleted without actually removing files)
python scripts/cleanup_backups.py --dry-run

# Use a specific configuration file
python scripts/cleanup_backups.py --config /path/to/custom_cleanup_config.ini
```

### Cleanup Configuration

You can customize the cleanup behavior by modifying a configuration file (e.g., `cleanup_config.ini` or `config/cleanup.ini`) used by the `cleanup_backups.py` script. The script should be designed to look for this file in a predefined location or allow specifying it via a command-line argument.

Example `cleanup_config.ini`:
```ini
# Sample cleanup_config.ini
[General]
BACKUP_DIR="/samples/backups" # Or an absolute path

[Retention]
RETAIN_DAILY=7
RETAIN_WEEKLY=4
RETAIN_MONTHLY=3
# Set to 0 to disable a specific retention period, e.g., RETAIN_MONTHLY=0
```

### Listing Markdown Files

To list all markdown files in the directory and its subdirectories, use the following command:

```bash
find . -name "*.md"
```

## Best Practices

1. Run the cleanup script regularly as part of your maintenance routine
2. Always verify important backups before running cleanup
3. Consider increasing retention periods before major system changes
4. Use the `--dry-run` option to preview changes before actual deletion

For more information on backup strategies, refer to the [Backup and Recovery](backup_recovery.md) guide.