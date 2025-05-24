# Be careful with this command - it deletes ALL .bak files
find . -name "*.bak" -type f -delete


## Backup Cleanup

Backup files accumulate over time. While you can manually delete them as shown above, this removes ALL backups without discrimination.

For a safer approach, use the provided cleanup script that will preserve the most recent backups:

```bash
python scripts/cleanup_backups.py --keep-recent 5
```

This command keeps your 5 most recent backup files and removes older ones, helping you maintain history while managing disk space.