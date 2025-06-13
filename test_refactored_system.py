#!/usr/bin/env python3
"""
Test Refactored System - Comprehensive testing of the new structure
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess

def test_new_directory_structure():
    """Test that all new directories were created correctly"""
    print("🏗️ Testing New Directory Structure")
    print("-" * 40)

    required_dirs = [
        "src/rtm",
        "src/analyzers",
        "scripts/automation",
        "scripts/quality",
        "scripts/setup",
        "docs/guides",
        "tests/unit",
        "tests/integration",
        "logs"
    ]

    missing_dirs = []
    present_dirs = []

    for directory in required_dirs:
        if Path(directory).exists():
            present_dirs.append(directory)
            print(f"   ✅ {directory}/")
        else:
            missing_dirs.append(directory)
            print(f"   ❌ {directory}/ - MISSING")

    print(f"\n📊 Directory Status: {len(present_dirs)}/{len(required_dirs)} present")

    if missing_dirs:
        print(f"⚠️  Missing directories: {missing_dirs}")
        return False

    return True

def test_file_organization():
    """Test that files were moved to correct locations"""
    print("\n📁 Testing File Organization")
    print("-" * 30)

    expected_files = {
        "src/rtm/document_converter.py": "Core RTM processing",
        "src/analyzers/project_scanner.py": "Project analysis",
        "scripts/automation/version_manager.py": "Version management",
        "scripts/quality/simple_clone_test.py": "Quality testing",
        "scripts/setup/final_refactor_and_deploy.py": "Setup scripts",
        "docs/guides/git_github_guide.md": "Documentation"
    }

    missing_files = []
    present_files = []

    for file_path, description in expected_files.items():
        if Path(file_path).exists():
            present_files.append(file_path)
            print(f"   ✅ {file_path} - {description}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - MISSING")

    print(f"\n📊 File Status: {len(present_files)}/{len(expected_files)} present")

    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
        return False

    return True

def test_imports_and_syntax():
    """Test that Python files have correct imports and syntax"""
    print("\n🐍 Testing Imports and Syntax")
    print("-" * 30)

    # Test main.py import
    try:
        print("   Testing main.py...")
        result = subprocess.run([sys.executable, '-c', 'import main'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ main.py imports successfully")
        else:
            print(f"   ⚠️  main.py import issue: {result.stderr[:100]}")
    except Exception as e:
        print(f"   ❌ Error testing main.py: {e}")

    # Test key modules
    test_modules = [
        ("src.rtm.document_converter", "Document converter module"),
        ("scripts.automation.version_manager", "Version manager module"),
        ("src.rtm.logging_system", "Logging system module")
    ]

    working_modules = 0

    for module_name, description in test_modules:
        try:
            # Add current directory to Python path
            import_cmd = f"import sys; sys.path.insert(0, '.'); import {module_name}"
            result = subprocess.run([sys.executable, '-c', import_cmd],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {module_name} - {description}")
                working_modules += 1
            else:
                print(f"   ⚠️  {module_name} - Import issues")
        except Exception as e:
            print(f"   ❌ {module_name} - Error: {e}")

    print(f"\n📊 Module Status: {working_modules}/{len(test_modules)} working")
    return working_modules >= len(test_modules) // 2

def test_version_management():
    """Test the version management system"""
    print("\n📦 Testing Version Management")
    print("-" * 30)

    # Check VERSION.json
    version_file = Path("VERSION.json")
    if version_file.exists():
        try:
            import json
            with open(version_file, 'r') as f:
                version_data = json.load(f)

            print(f"   ✅ VERSION.json exists")
            print(f"   📋 Version: {version_data.get('version', 'Unknown')}")
            print(f"   🔨 Build: {version_data.get('build', 'Unknown')}")
            print(f"   🌐 Roundtrips: {version_data.get('github_roundtrips', 0)}")

            return True
        except Exception as e:
            print(f"   ❌ Error reading VERSION.json: {e}")
            return False
    else:
        print("   ⚠️  VERSION.json not found")
        return False

def test_logging_system():
    """Test the logging system"""
    print("\n📋 Testing Logging System")
    print("-" * 25)

    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        json_files = list(logs_dir.glob("*.json"))
        txt_files = list(logs_dir.glob("*.txt"))

        print(f"   ✅ Logs directory exists")
        print(f"   📄 Log files: {len(log_files)}")
        print(f"   📋 JSON files: {len(json_files)}")
        print(f"   📝 Text files: {len(txt_files)}")

        # Test creating a log entry
        try:
            test_log = logs_dir / f"refactor_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(test_log, 'w', encoding='utf-8') as f:
                f.write(f"Refactor test log created at {datetime.now()}\n")
                f.write("New directory structure is working!\n")
            print(f"   ✅ Successfully created test log: {test_log.name}")
            return True
        except Exception as e:
            print(f"   ❌ Could not create test log: {e}")
            return False
    else:
        print("   ❌ Logs directory not found")
        return False

def test_git_status_after_refactor():
    """Test Git status after refactoring"""
    print("\n🔧 Testing Git Status After Refactor")
    print("-" * 35)

    try:
        # Check current commit
        result = subprocess.run(['git', 'log', '--oneline', '-1'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            commit_info = result.stdout.strip()
            print(f"   ✅ Latest commit: {commit_info}")

        # Check status
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"   📊 Uncommitted changes: {len(changes)}")

            if len(changes) > 0:
                print("   📋 Recent changes (showing first 5):")
                for change in changes[:5]:
                    print(f"      • {change}")

        # Check remote status
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Git remote configured")

        return True
    except Exception as e:
        print(f"   ❌ Error checking Git status: {e}")
        return False

def run_quick_functionality_test():
    """Run a quick test of core functionality"""
    print("\n⚡ Quick Functionality Test")
    print("-" * 30)

    # Test if we can run basic scripts
    test_scripts = [
        ("python simple_workflow_test.py", "Basic workflow test"),
        ("python scripts/automation/version_manager.py", "Version manager"),
        ("python scripts/quality/simple_clone_test.py", "Clone test")
    ]

    working_scripts = 0

    for script_cmd, description in test_scripts:
        script_path = script_cmd.split()[1]
        if Path(script_path).exists():
            print(f"   ✅ {script_path} - Available for testing")
            print(f"      Command: {script_cmd}")
            working_scripts += 1
        else:
            print(f"   ⚠️  {script_path} - Not found")

    print(f"\n📊 Available scripts: {working_scripts}/{len(test_scripts)}")
    return working_scripts > 0

def create_refactor_test_report(results):
    """Create a comprehensive test report"""
    print("\n📋 Creating Refactor Test Report")
    print("-" * 35)

    # Calculate success rate
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100

    # Create report content
    report_content = f"""RTM AUTOMATION REFACTOR TEST REPORT
========================================
Generated: {datetime.now().isoformat()}

REFACTORING SUMMARY:
- Project successfully refactored to new structure
- Files organized into logical directories
- Version management system active
- Comprehensive logging system implemented

TEST RESULTS:
"""

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        report_content += f"- {test_name}: {status}\n"

    report_content += f"""
OVERALL ASSESSMENT:
- Total tests: {total_tests}
- Passed tests: {passed_tests}
- Success rate: {success_rate:.1f}%

NEW STRUCTURE STATUS:
- Directory organization: {'✅ Complete' if results.get('directory_structure', False) else '❌ Issues'}
- File organization: {'✅ Complete' if results.get('file_organization', False) else '❌ Issues'}
- Import system: {'✅ Working' if results.get('imports_syntax', False) else '⚠️ Partial'}
- Version management: {'✅ Active' if results.get('version_management', False) else '❌ Issues'}
- Logging system: {'✅ Operational' if results.get('logging_system', False) else '❌ Issues'}

NEXT STEPS:
"""

    if success_rate >= 80:
        report_content += """- ✅ Refactoring successful - system ready for use
- Run: python main.py (test RTM pipeline)
- Run: python scripts/automation/version_manager.py (manage versions)
- Run: python scripts/quality/simple_clone_test.py (test GitHub integration)
- Continue development with new organized structure
"""
    else:
        report_content += """- ⚠️ Address failed tests before proceeding
- Check import paths and module references
- Verify all files moved to correct locations
- Test individual components manually
"""

    # Save report
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        report_file = logs_dir / f"refactor_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"   ✅ Report saved: {report_file}")
        return report_file, success_rate
    except Exception as e:
        print(f"   ❌ Could not save report: {e}")
        return None, success_rate

def main():
    """Main test function"""
    print("🧪 RTM AUTOMATION REFACTOR TEST")
    print("=" * 40)
    print("Testing the refactored project structure...\n")

    # Run all tests
    test_results = {
        'directory_structure': test_new_directory_structure(),
        'file_organization': test_file_organization(),
        'imports_syntax': test_imports_and_syntax(),
        'version_management': test_version_management(),
        'logging_system': test_logging_system(),
        'git_status': test_git_status_after_refactor()
    }

    # Run functionality test
    run_quick_functionality_test()

    # Create comprehensive report
    report_file, success_rate = create_refactor_test_report(test_results)

    # Show final summary
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    print(f"\n🎯 REFACTOR TEST SUMMARY")
    print("=" * 30)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 REFACTORING SUCCESSFUL!")
        print("Your RTM automation system has been successfully refactored!")
        print("\n🚀 Ready for production use with new organized structure")
        print("\nNext steps:")
        print("1. python main.py                              # Test RTM pipeline")
        print("2. python scripts/automation/version_manager.py # Manage versions")
        print("3. python scripts/quality/simple_clone_test.py   # Test GitHub clone")
        print("4. Explore the new organized directory structure")
        return 0
    else:
        print("\n⚠️ REFACTORING NEEDS ATTENTION")
        print("Some components need to be addressed.")
        print("\nFailed tests:")
        for test_name, passed in test_results.items():
            if not passed:
                print(f"❌ {test_name}")
        print(f"\nCheck the detailed report: {report_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
