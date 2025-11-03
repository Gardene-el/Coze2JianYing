#!/usr/bin/env python3
"""
Test to verify cozepy package can be imported correctly.
This test validates that the cozepy dependency is properly added to the project.
"""

def test_cozepy_import():
    """Test that cozepy can be imported"""
    print("=== Testing cozepy Import ===")
    
    try:
        import cozepy
        print("✅ Successfully imported cozepy")
        
        # Check if the package has expected attributes
        if hasattr(cozepy, '__version__'):
            print(f"   Version: {cozepy.__version__}")
        
        # Try to access some common components if they exist
        common_modules = ['auth', 'client', 'models', 'exceptions']
        available_modules = []
        for module_name in common_modules:
            if hasattr(cozepy, module_name):
                available_modules.append(module_name)
        
        if available_modules:
            print(f"   Available modules: {', '.join(available_modules)}")
        
        print("✅ cozepy import test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import cozepy: {e}")
        print("   Note: Run 'pip install -r requirements.txt' to install cozepy")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import test: {e}")
        return False


def test_requirements_includes_cozepy():
    """Test that requirements.txt includes cozepy"""
    print("\n=== Testing requirements.txt ===")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        if 'cozepy' in requirements:
            print("✅ cozepy is listed in requirements.txt")
            
            # Extract the cozepy line
            for line in requirements.split('\n'):
                if 'cozepy' in line and not line.strip().startswith('#'):
                    print(f"   Entry: {line.strip()}")
            
            return True
        else:
            print("❌ cozepy is not found in requirements.txt")
            return False
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


if __name__ == "__main__":
    print("Testing cozepy dependency addition\n")
    
    results = []
    
    # Test requirements.txt first (doesn't require package installation)
    results.append(test_requirements_includes_cozepy())
    
    # Test import (requires package installation)
    results.append(test_cozepy_import())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed! cozepy dependency has been successfully added.")
    else:
        print("\n⚠️  Some tests failed. If import test failed, install dependencies with:")
        print("   pip install -r requirements.txt")
