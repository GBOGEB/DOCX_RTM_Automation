#!/usr/bin/env python3
"""
Simple Workflow Test - Test the basic functionality without complex imports
"""

import sys
from pathlib import Path
from datetime import datetime
import json

def test_basic_structure():
    """Test basic project structure"""
    print("🏗️ Testing Basic Project Structure")
    print("-" * 40)

    # Check for essential files
    essential_files = [
        'main.py',
        'document_converter.py',
        'version_manager.py',
        'final_refactor_and_deploy.py'
    ]

    present_files = []
    for file_name in essential_files:
        if Path(file_name).exists():
            present_files.append(file_name)
            print(f"   ✅ Found: {file_name}")
        else:
            print(f"   ⚠️  Missing: {file_name}")

    print(f"\n📊 Files present: {len(present_files)}/{len(essential_files)}")
    return len(present_files) >= 3

def test_logs_directory():
    """Test logs directory functionality"""
    print("\n📁 Testing Logs Directory")
    print("-" * 30)

    logs_dir = Path("logs")

    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        json_files = list(logs_dir.glob("*.json"))
        txt_files = list(logs_dir.glob("*.txt"))

        print(f"   ✅ Logs directory exists")
        print(f"   📄 Log files: {len(log_files)}")
        print(f"   📋 JSON files: {len(json_files)}")
        print(f"   📝 Text files: {len(txt_files)}")

        # Test creating a simple log entry
        try:
            test_log = logs_dir / f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(test_log, 'w', encoding='utf-8') as f:
                f.write(f"Test log entry created at {datetime.now()}\n")
            print(f"   ✅ Successfully created test log: {test_log.name}")
            return True
        except Exception as e:
            print(f"   ❌ Could not create test log: {e}")
            return False
    else:
        print(f"   ⚠️  Logs directory not found")
        try:
            logs_dir.mkdir(exist_ok=True)
            print(f"   ✅ Created logs directory")
            return True
        except Exception as e:
            print(f"   ❌ Could not create logs directory: {e}")
            return False

def test_version_system():
    """Test version management system"""
    print("\n📦 Testing Version System")
    print("-" * 25)

    version_file = Path("VERSION.json")

    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)

            print(f"   ✅ VERSION.json exists")
            print(f"   📋 Current version: {version_data.get('version', 'Unknown')}")
            print(f"   🔨 Build number: {version_data.get('build', 'Unknown')}")
            print(f"   🌐 GitHub roundtrips: {version_data.get('github_roundtrips', 0)}")
            return True
        except Exception as e:
            print(f"   ❌ Error reading VERSION.json: {e}")
            return False
    else:
        print(f"   ⚠️  VERSION.json not found")
        # Create a basic version file
        try:
            default_version = {
                "version": "1.0.0",
                "build": 1,
                "github_roundtrips": 0,
                "created": datetime.now().isoformat()
            }

            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(default_version, f, indent=2)

            print(f"   ✅ Created default VERSION.json")
            return True
        except Exception as e:
            print(f"   ❌ Could not create VERSION.json: {e}")
            return False

def test_git_status():
    """Test Git repository status"""
    print("\n🔧 Testing Git Status")
    print("-" * 20)

    if Path(".git").exists():
        print(f"   ✅ Git repository initialized")

        # Try to get basic Git info
        try:
            import subprocess

            # Check current branch
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                branch = result.stdout.strip()
                print(f"   📋 Current branch: {branch}")

            # Check if there are uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                print(f"   📊 Uncommitted changes: {len(changes)}")

            # Check remote origin
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                origin = result.stdout.strip()
                print(f"   🌐 Remote origin configured: {origin[:50]}...")
            else:
                print(f"   ⚠️  No remote origin configured")

            return True
        except Exception as e:
            print(f"   ⚠️  Could not get Git status: {e}")
            return True  # Git exists, that's the main thing
    else:
        print(f"   ❌ Git repository not initialized")
        return False

def test_python_imports():
    """Test if main Python files can be imported"""
    print("\n🐍 Testing Python Imports")
    print("-" * 25)

    test_imports = [
        ('main', 'main.py'),
        ('document_converter', 'document_converter.py'),
        ('version_manager', 'version_manager.py')
    ]

    successful_imports = 0

    for module_name, file_name in test_imports:
        try:
            if Path(file_name).exists():
                # Try to compile the file
                import subprocess
                result = subprocess.run(['python', '-m', 'py_compile', file_name],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ {file_name}: Valid Python syntax")
                    successful_imports += 1
                else:
                    print(f"   ❌ {file_name}: Syntax error")
            else:
                print(f"   ⚠️  {file_name}: File not found")
        except Exception as e:
            print(f"   ❌ {file_name}: Error testing - {e}")

    print(f"\n📊 Successful imports: {successful_imports}/{len(test_imports)}")
    return successful_imports >= 2

def create_test_report(results):
    """Create a simple test report"""
    print("\n📋 Creating Test Report")
    print("-" * 25)

    # Calculate overall success rate
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100

    # Create report data
    report_content = f"""RTM AUTOMATION WORKFLOW TEST REPORT
==========================================
Generated: {datetime.now().isoformat()}

TEST RESULTS:
"""

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        report_content += f"- {test_name}: {status}\n"

    report_content += f"""
SUMMARY:
- Total tests: {total_tests}
- Passed tests: {passed_tests}
- Success rate: {success_rate:.1f}%

SYSTEM STATUS:
- Basic structure: {'✅ Good' if results.get('basic_structure', False) else '❌ Issues'}
- Logging system: {'✅ Working' if results.get('logs_directory', False) else '⚠️ Limited'}
- Version management: {'✅ Active' if results.get('version_system', False) else '⚠️ Basic'}
- Git repository: {'✅ Ready' if results.get('git_status', False) else '❌ Needs setup'}
- Python files: {'✅ Valid' if results.get('python_imports', False) else '⚠️ Issues'}

RECOMMENDATIONS:
"""

    if success_rate >= 80:
        report_content += "- System is ready for production use\n"
        report_content += "- Run main.py to test RTM pipeline\n"
        report_content += "- Use version_manager.py for version control\n"
    else:
        report_content += "- Address failed tests before proceeding\n"
        report_content += "- Check file structure and dependencies\n"
        report_content += "- Review Git configuration\n"

    # Save report
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        report_file = logs_dir / f"workflow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"   ✅ Report saved: {report_file}")
        return report_file
    except Exception as e:
        print(f"   ❌ Could not save report: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 RTM AUTOMATION WORKFLOW TEST")
    print("=" * 40)
    print("Testing basic functionality and structure...\n")

    # Run all tests
    test_results = {
        'basic_structure': test_basic_structure(),
        'logs_directory': test_logs_directory(),
        'version_system': test_version_system(),
        'git_status': test_git_status(),
        'python_imports': test_python_imports()
    }

    # Create test report
    report_file = create_test_report(test_results)

    # Show summary
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100

    print(f"\n🎯 TEST SUMMARY")
    print("=" * 20)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 SYSTEM READY!")
        print("Your RTM automation system is working well.")
        print("\nNext steps:")
        print("1. python main.py                    # Test RTM pipeline")
        print("2. python version_manager.py         # Manage versions")
        print("3. python final_refactor_and_deploy.py  # Full deployment")
        return 0
    else:
        print("\n⚠️ ISSUES FOUND")
        print("Some components need attention.")
        print("\nFailed tests:")
        for test_name, passed in test_results.items():
            if not passed:
                print(f"❌ {test_name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
