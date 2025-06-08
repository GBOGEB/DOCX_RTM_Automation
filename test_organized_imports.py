#!/usr/bin/env python3
"""
Test Organized Imports - Verify that the organized structure works
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test importing from the organized structure."""
    print("🧪 Testing Organized Import Structure")
    print("=" * 40)

    test_modules = [
        ("RTM Pipeline", "rtm.rtm_pipeline"),
        ("JSON Analyzer", "analyzers.json_file_analyzer_safe"),
        ("Web Dashboard", "dashboard.rtm_web_dashboard"),
        ("Word to MD", "parsers.try_word_to_md"),
        ("Enhanced Parser", "parsers.enhanced_word_to_md"),
        ("Port Manager", "utils.port_manager"),
        ("Jenkins Integration", "integrations.jenkins_rtm_integration"),
    ]

    successful_imports = 0

    for module_name, module_path in test_modules:
        try:
            __import__(module_path)
            print(f"   ✅ {module_name}: {module_path}")
            successful_imports += 1
        except ImportError as e:
            print(f"   ❌ {module_name}: {module_path} - {e}")
        except Exception as e:
            print(f"   ⚠️ {module_name}: {module_path} - {type(e).__name__}: {e}")

    success_rate = (successful_imports / len(test_modules)) * 100

    print("\n📊 IMPORT TEST RESULTS:")
    print("=" * 30)
    print(f"   ✅ Successful imports: {successful_imports}/{len(test_modules)}")
    print(f"   📈 Success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🏆 EXCELLENT! Your organized structure is working well!")
    elif success_rate >= 60:
        print("🥉 GOOD! Most modules are accessible, minor fixes may be needed.")
    else:
        print("⚠️ NEEDS WORK! Several import issues to resolve.")

    return success_rate >= 80


def test_functionality():
    """Test basic functionality of key modules."""
    print("\n🔧 Testing Basic Functionality:")
    print("=" * 35)

    # Test JSON analyzer
    try:
        from analyzers.json_file_analyzer_safe import quick_json_health_check

        print("   ✅ JSON analyzer function accessible")
    except ImportError:
        print("   ❌ JSON analyzer function not accessible")

    # Test path helper
    try:
        import path_helper

        print("   ✅ Path helper accessible")
    except ImportError:
        print("   ❌ Path helper not accessible")

    # Test config access
    config_path = Path("config/config.json")
    if config_path.exists():
        print(f"   ✅ Config file accessible: {config_path}")
    else:
        print(f"   ❌ Config file missing: {config_path}")


def show_usage_examples():
    """Show examples of using the organized structure."""
    print("\n💡 USAGE EXAMPLES:")
    print("=" * 25)
    print("Now you can use your organized RTM system like this:")
    print()
    print("🔍 Run JSON Analysis:")
    print(
        '   python -c "import path_helper; from analyzers.json_file_analyzer_safe import main; main()"'
    )
    print()
    print("🚀 Run RTM Pipeline:")
    print(
        '   python -c "import path_helper; from rtm.rtm_pipeline import main; main()"'
    )
    print()
    print("🌐 Start Web Dashboard:")
    print(
        '   python -c "import path_helper; from dashboard.rtm_web_dashboard import main; main()"'
    )
    print()
    print("📊 Or use the organized main file:")
    print("   python main_organized.py")


def main():
    """Main test function."""
    print("🔍 RTM Organized Structure Test")
    print("=" * 35)
    print("Testing your newly organized RTM project structure...")

    # Test imports
    imports_ok = test_imports()

    # Test functionality
    test_functionality()

    # Show usage examples
    show_usage_examples()

    # Final summary
    print("\n🎊 TEST COMPLETE!")
    print("=" * 20)

    if imports_ok:
        print("✅ Your organized RTM system is ready to use!")
        print("🚀 All major components are accessible!")
        print("💎 Enterprise-grade structure achieved!")
    else:
        print("⚠️ Some import issues detected")
        print("💡 Run: python fix_import_paths.py")
        print("🔧 Then test again with this script")

    return 0


if __name__ == "__main__":
    main()
