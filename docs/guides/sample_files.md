# Sample Files Guide

This guide provides information about sample files used in the DOCX_RTM_Automation pipeline and how to manage them effectively.

## Overview

The automation pipeline generates various files during its operation. These files can accumulate over time and may need periodic cleanup while preserving important data.

## Sample Files Directory Structure

```
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

We provide a cleanup utility script that intelligently preserves the most recent backups while removing older ones:

```bash
# Run the basic cleanup (keeps last 7 daily backups and last 4 weekly backups)
./scripts/cleanup.sh

# Specify custom retention periods
./scripts/cleanup.sh --daily 10 --weekly 6

# Dry run (shows what would be deleted without actually removing files)
./scripts/cleanup.sh --dry-run
```

### Cleanup Configuration

You can customize the cleanup behavior by modifying the `cleanup.config` file:

```ini
# Sample cleanup.config
BACKUP_DIR="/path/to/backups"
RETAIN_DAILY=7
RETAIN_WEEKLY=4
RETAIN_MONTHLY=3
```

## Best Practices

1. Run the cleanup script regularly as part of your maintenance routine
2. Always verify important backups before running cleanup
3. Consider increasing retention periods before major system changes
4. Use the `--dry-run` option to preview changes before actual deletion

For more information on backup strategies, refer to the [Backup and Recovery](backup_recovery.md) guide.