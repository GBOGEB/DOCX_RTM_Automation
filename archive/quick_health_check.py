#!/usr/bin/env python3
"""
Quick Health Check - Standalone diagnostic tool for RTM pipeline
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_directories():
    """Check required directories"""
    print_header("DIRECTORY CHECK")

    required_dirs = ["input", "output", "temp_processing", "logs"]
    status = {"good": 0, "missing": 0, "errors": []}

    for dir_name in required_dirs:
        try:
            if os.path.exists(dir_name):
                file_count = len([f for f in os.listdir(dir_name)
                                if os.path.isfile(os.path.join(dir_name, f))])
                print(f"✅ {dir_name:15} - {file_count} files")
                status["good"] += 1
            else:
                print(f"❌ {dir_name:15} - MISSING")
                status["missing"] += 1
        except Exception as e:
            print(f"⚠️  {dir_name:15} - ERROR: {e}")
            status["errors"].append(f"{dir_name}: {e}")

    return status

def check_files():
    """Check for important files"""
    print_header("FILE CHECK")

    important_files = [
        "setup_and_run_pipeline.py",
        "debug_console.py",
        "word_markdown_pipeline_fixed.py",
        "debug_config.json"
    ]

    status = {"found": 0, "missing": 0}

    for filename in important_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename:30} - {size:,} bytes")
            status["found"] += 1
        else:
            print(f"❌ {filename:30} - MISSING")
            status["missing"] += 1

    return status

def check_python_environment():
    """Check Python environment"""
    print_header("PYTHON ENVIRONMENT")

    print(f"✅ Python Version: {sys.version}")
    print(f"✅ Platform: {sys.platform}")
    print(f"✅ Working Directory: {os.getcwd()}")

    # Check for important modules
    modules_to_check = [
        "json", "os", "sys", "pathlib", "datetime",
        "logging", "traceback"
    ]

    missing_modules = []
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✅ Module {module:15} - Available")
        except ImportError:
            print(f"❌ Module {module:15} - MISSING")
            missing_modules.append(module)

    # Check optional modules
    optional_modules = ["psutil", "docx", "markdown"]
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ Optional {module:10} - Available")
        except ImportError:
            print(f"⚠️  Optional {module:10} - Not installed (non-critical)")

    return {"missing_critical": missing_modules}

def check_input_files():
    """Check input files"""
    print_header("INPUT FILES CHECK")

    input_dir = Path("input")
    if not input_dir.exists():
        print("❌ Input directory does not exist")
        return {"count": 0, "types": {}}

    files = list(input_dir.glob("*"))
    if not files:
        print("⚠️  No files found in input directory")
        return {"count": 0, "types": {}}

    file_types = {}
    for file_path in files:
        if file_path.is_file():
            ext = file_path.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            size = file_path.stat().st_size
            print(f"📄 {file_path.name:25} - {size:,} bytes")

    print(f"\n📊 File type summary:")
    for ext, count in file_types.items():
        print(f"   {ext or '(no extension)':10} - {count} files")

    return {"count": len(files), "types": file_types}

def generate_quick_report():
    """Generate a quick diagnostic report"""
    print_header("QUICK DIAGNOSTIC REPORT")

    report = {
        "timestamp": datetime.now().isoformat(),
        "directories": check_directories(),
        "files": check_files(),
        "python": check_python_environment(),
        "input_files": check_input_files()
    }

    # Summary
    print_header("SUMMARY")

    total_issues = 0

    # Directory issues
    dir_issues = report["directories"]["missing"] + len(report["directories"]["errors"])
    if dir_issues > 0:
        print(f"⚠️  Directory Issues: {dir_issues}")
        total_issues += dir_issues
    else:
        print("✅ Directories: All good")

    # File issues
    if report["files"]["missing"] > 0:
        print(f"⚠️  Missing Files: {report['files']['missing']}")
        total_issues += report["files"]["missing"]
    else:
        print("✅ Files: All good")

    # Python issues
    if report["python"]["missing_critical"]:
        print(f"❌ Missing Critical Modules: {len(report['python']['missing_critical'])}")
        total_issues += len(report["python"]["missing_critical"])
    else:
        print("✅ Python Environment: All good")

    # Input files
    if report["input_files"]["count"] == 0:
        print("⚠️  Input Files: None found (add files to process)")
        total_issues += 1
    else:
        print(f"✅ Input Files: {report['input_files']['count']} files ready")

    print(f"\n🎯 Total Issues Found: {total_issues}")

    if total_issues == 0:
        print("🎉 System is ready to run RTM pipeline!")
    else:
        print("🔧 Please address the issues above before running the pipeline")

    # Save report
    os.makedirs("logs", exist_ok=True)
    report_file = f"logs/quick_health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return report

def main():
    """Main function"""
    print("🏥 RTM Quick Health Check")
    print("=" * 60)
    print("This tool performs a quick diagnostic of your RTM system")

    try:
        report = generate_quick_report()
        return 0 if not any([
            report["directories"]["missing"],
            report["directories"]["errors"],
            report["files"]["missing"],
            report["python"]["missing_critical"]
        ]) else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
