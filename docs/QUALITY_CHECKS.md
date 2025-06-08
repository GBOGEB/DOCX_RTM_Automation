# Code Quality Check Options

Choose the right quality check for your needs:

## 🚀 Light Check (`quality_check_light.py`)
**Best for: Quick development feedback**
- ⚡ **Speed**: ~5-10 seconds
- 🎯 **Focus**: Critical syntax errors only
- 📋 **Scope**: Core files only
- 💡 **Use when**: Before commits, quick validation

```bash
python quality_check_light.py
```

## ⚡ Quick Check (`quick_quality_check.py`)
**Best for: Regular development**
- ⚡ **Speed**: ~30-60 seconds
- 🎯 **Focus**: Important issues + project structure
- 📋 **Scope**: Key files + basic structure
- 💡 **Use when**: Daily development, CI/CD

```bash
python quick_quality_check.py
```

## 🔄 Heavy Check (`quality_check_heavy.py`)
**Best for: Comprehensive analysis**
- ⚡ **Speed**: ~2-5 minutes
- 🎯 **Focus**: Complete analysis + reporting
- 📋 **Scope**: All files + detailed metrics
- 💡 **Use when**: Release preparation, code reviews

```bash
python quality_check_heavy.py
```

## 🏢 Enterprise Check (`run_code_quality_checks.py`)
**Best for: Production systems**
- ⚡ **Speed**: ~5-10 minutes
- 🎯 **Focus**: Enterprise-grade analysis
- 📋 **Scope**: Full project + compliance
- 💡 **Use when**: Production deployments, audits

```bash
python run_code_quality_checks.py --checks all
```

## Quick Reference

| Check | Time | Files | Issues Caught | Report Detail |
|-------|------|-------|---------------|---------------|
| Light | 5-10s | Core only | Critical only | Minimal |
| Quick | 30-60s | Key files | Important | Basic |
| Heavy | 2-5m | All files | Comprehensive | Detailed |
| Enterprise | 5-10m | All + deps | Everything | Full |

Choose based on your current development phase and time constraints!
