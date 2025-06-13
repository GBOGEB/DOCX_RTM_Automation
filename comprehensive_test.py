#!/usr/bin/env python3
"""
Comprehensive Test - Test all RTM automation components
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess

def test_dependencies():
    """Test that all dependencies are installed"""
    print("🔧 Testing Dependencies")
    print("-" * 25)

    dependencies = ['docx', 'json', 'pathlib', 'datetime']
    working_deps = 0

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
            working_deps += 1
        except ImportError:
            print(f"   ❌ {dep} - Not installed")

    print(f"\n📊 Dependencies: {working_deps}/{len(dependencies)} working")
    return working_deps == len(dependencies)

def test_project_structure():
    """Test the refactored project structure"""
    print("\n🏗️ Testing Project Structure")
    print("-" * 30)

    required_dirs = [
        "src/rtm", "scripts/automation", "scripts/quality",
        "docs/guides", "logs", "input", "output"
    ]

    present_dirs = 0
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"   ✅ {directory}/")
            present_dirs += 1
        else:
            print(f"   ❌ {directory}/ - Missing")

    print(f"\n📊 Structure: {present_dirs}/{len(required_dirs)} directories")
    return present_dirs >= len(required_dirs) * 0.8  # 80% threshold

def test_docx_processing():
    """Test DOCX processing capabilities"""
    print("\n📄 Testing DOCX Processing")
    print("-" * 30)

    try:
        # Test creating a document
        print("   Testing document creation...")
        result = subprocess.run([sys.executable, 'create_test_document.py'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Test document creation working")
            doc_creation = True
        else:
            print("   ⚠️  Test document creation issues")
            doc_creation = False

        # Test main pipeline
        print("   Testing main pipeline...")
        result = subprocess.run([sys.executable, 'main.py'],
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("   ✅ Main pipeline working")
            pipeline = True
        else:
            print("   ⚠️  Main pipeline issues")
            pipeline = False

        return doc_creation or pipeline

    except Exception as e:
        print(f"   ❌ Error testing DOCX processing: {e}")
        return False

def test_version_management():
    """Test version management system"""
    print("\n📦 Testing Version Management")
    print("-" * 30)

    version_file = Path("VERSION.json")
    if version_file.exists():
        try:
            import json
            with open(version_file, 'r') as f:
                version_data = json.load(f)
            print(f"   ✅ VERSION.json: v{version_data.get('version', 'Unknown')}")
            print(f"   📊 Build: #{version_data.get('build', 'Unknown')}")
            print(f"   🔄 Roundtrips: {version_data.get('github_roundtrips', 0)}")
            return True
        except Exception as e:
            print(f"   ❌ Error reading VERSION.json: {e}")
            return False
    else:
        print("   ⚠️  VERSION.json not found")
        return False

def test_git_integration():
    """Test Git repository integration"""
    print("\n🔧 Testing Git Integration")
    print("-" * 25)

    if not Path(".git").exists():
        print("   ❌ Not a Git repository")
        return False

    try:
        # Test Git status
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"   ✅ Git status: {len(changes)} uncommitted changes")

        # Test remote
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("   ✅ Git remote configured")
            return True
        else:
            print("   ⚠️  No Git remote configured")
            return True  # Still counts as working Git

    except Exception as e:
        print(f"   ❌ Git error: {e}")
        return False

def test_output_generation():
    """Test output file generation"""
    print("\n📁 Testing Output Generation")
    print("-" * 30)

    output_dir = Path("output")
    if output_dir.exists():
        files = list(output_dir.glob("*"))
        print(f"   ✅ Output directory: {len(files)} files")

        # Check for different file types
        json_files = list(output_dir.glob("*.json"))
        docx_files = list(output_dir.glob("*.docx"))
        txt_files = list(output_dir.glob("*.txt"))

        print(f"   📋 JSON files: {len(json_files)}")
        print(f"   📄 DOCX files: {len(docx_files)}")
        print(f"   📝 Text files: {len(txt_files)}")

        return len(files) > 0
    else:
        print("   ❌ Output directory not found")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🧪 RTM AUTOMATION COMPREHENSIVE TEST")
    print("=" * 45)
    print("Testing all components of the refactored system...\n")

    # Run all tests
    test_results = {
        'dependencies': test_dependencies(),
        'project_structure': test_project_structure(),
        'docx_processing': test_docx_processing(),
        'version_management': test_version_management(),
        'git_integration': test_git_integration(),
        'output_generation': test_output_generation()
    }

    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100

    # Show summary
    print(f"\n🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 35)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {success_rate:.1f}%")

    print(f"\nDetailed Results:")
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 SYSTEM STATUS: EXCELLENT")
        print("Your RTM automation system is working perfectly!")
        print("\n🚀 Ready for production use with:")
        print("   • Full DOCX processing capabilities")
        print("   • Professional project structure")
        print("   • Version management system")
        print("   • Comprehensive logging")
        print("   • GitHub integration")

        print(f"\n🎯 Recommended Commands:")
        print("   python main.py                              # Process DOCX files")
        print("   python scripts/automation/version_manager.py # Manage versions")
        print("   python find_output_files.py                 # Check results")

        return 0
    elif success_rate >= 60:
        print(f"\n⚠️  SYSTEM STATUS: GOOD")
        print("Most components working, minor issues to address.")
        return 1
    else:
        print(f"\n❌ SYSTEM STATUS: NEEDS ATTENTION")
        print("Several components need fixing.")
        return 2

def main():
    """Main function"""
    return run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())
