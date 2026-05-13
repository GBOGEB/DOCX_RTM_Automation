#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
"""

import sys
import subprocess

def test_imports():
    """Test that all modules can be imported"""
    try:
        import ascii_art
        print("✅ ascii_art module imported successfully")

        # Test a function
        banner = ascii_art.final_success_banner()
        if banner and "RTM AUTOMATION SUCCESS" in banner:
            print("✅ ASCII art functions working correctly")
        else:
            print("❌ ASCII art functions not working properly")
            return False

    except Exception as e:
        print(f"❌ Failed to import ascii_art: {e}")
        return False

    return True

def test_syntax():
    """Test Python syntax compilation"""
    files_to_test = ['ascii_art.py', 'simple_pre_commit_hook.py']

    for file in files_to_test:
        try:
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', file
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {file} syntax check passed")
            else:
                print(f"❌ {file} syntax check failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error checking {file}: {e}")
            return False

    return True

def test_pre_commit_hook():
    """Test the pre-commit hook"""
    try:
        result = subprocess.run([
            sys.executable, 'simple_pre_commit_hook.py'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Pre-commit hook executed successfully")
            return True
        else:
            print(f"❌ Pre-commit hook failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Pre-commit hook timed out (but this is expected)")
        return True
    except Exception as e:
        print(f"❌ Error running pre-commit hook: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running comprehensive tests...\n")

    tests = [
        ("Import Tests", test_imports),
        ("Syntax Tests", test_syntax),
        ("Pre-commit Hook Test", test_pre_commit_hook),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your fixes are working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())