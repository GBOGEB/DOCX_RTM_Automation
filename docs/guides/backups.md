# Backup Cleanup

To manage backup files and prevent them from consuming excessive disk space, use the provided Python-based cleanup script, `scripts/cleanup_backups.py`. This script offers granular control over backup retention.

```bash
# Example: Keep the last 7 daily, 4 weekly, and 2 monthly backups
python scripts/cleanup_backups.py --daily 7 --weekly 4 --monthly 2

# Example: Perform a dry run to see which files would be deleted
python scripts/cleanup_backups.py --daily 7 --weekly 4 --monthly 2 --dry-run

# Example: Run with settings from a specific configuration file
python scripts/cleanup_backups.py --config /path/to/your/cleanup_config.ini
```

This script helps you maintain a history of backups according to defined policies (e.g., daily, weekly, monthly) while managing disk space effectively. Refer to the script's help option (`python scripts/cleanup_backups.py --help`) for all available commands and options.