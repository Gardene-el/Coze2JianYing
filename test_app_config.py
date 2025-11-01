#!/usr/bin/env python3
"""
Test to verify the application configuration is correct
"""
import subprocess
import sys


def test_entry_point_exists():
    """Test that the entry point command is installed"""
    print("=== Testing entry point exists ===")
    result = subprocess.run(
        ["which", "coze-2-jianying"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Entry point exists at: {result.stdout.strip()}")
        return True
    else:
        print("❌ Entry point not found")
        return False


def test_no_packages_exported():
    """Test that the package doesn't export unnecessary packages"""
    print("\n=== Testing package structure ===")
    
    # Try to import the package
    try:
        import coze_2_jianying
        print("❌ Package 'coze_2_jianying' should not be importable (application config)")
        return False
    except ImportError:
        print("✅ Package 'coze_2_jianying' is not importable (correct for application)")
        return True


def test_setup_file_structure():
    """Test that setup.py has correct structure for application"""
    print("\n=== Testing setup.py structure ===")
    
    with open("setup.py", "r") as f:
        content = f.read()
    
    # Check that find_packages is not imported
    if "find_packages" in content:
        print("❌ find_packages should not be used in application config")
        return False
    
    print("✅ find_packages not used")
    
    # Check that packages parameter is not present
    if "packages=" in content:
        print("❌ packages parameter should not be present in application config")
        return False
    
    print("✅ packages parameter not present")
    
    # Check that entry_points exists
    if "entry_points" not in content:
        print("❌ entry_points should be present")
        return False
    
    print("✅ entry_points present")
    
    # Check that the entry point points to src.main:main
    if "src.main:main" not in content:
        print("❌ entry point should point to src.main:main")
        return False
    
    print("✅ Entry point correctly configured")
    
    return True


def test_intended_audience():
    """Test that the classifier is correct for an application"""
    print("\n=== Testing classifiers ===")
    
    with open("setup.py", "r") as f:
        content = f.read()
    
    if "Intended Audience :: End Users/Desktop" in content:
        print("✅ Intended Audience correctly set to End Users/Desktop")
        return True
    else:
        print("❌ Intended Audience should be 'End Users/Desktop' for applications")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Application Configuration")
    print("=" * 60)
    
    results = []
    results.append(test_entry_point_exists())
    results.append(test_no_packages_exported())
    results.append(test_setup_file_structure())
    results.append(test_intended_audience())
    
    print("\n" + "=" * 60)
    print(f"Test Summary: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    sys.exit(0 if all(results) else 1)
