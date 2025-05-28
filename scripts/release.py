#!/usr/bin/env python3
"""
Release script for Memra SDK
Builds and uploads the package to PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ {description} failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"✅ {description} completed")
    return result.stdout

def clean_build_artifacts():
    """Clean up build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove build directories
    for dir_name in ['build', 'dist', 'memra.egg-info']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"   Removed {pycache_path}")
    
    print("✅ Build artifacts cleaned")

def run_tests():
    """Run tests before release"""
    print("🧪 Running tests...")
    
    # Check if pytest is available
    try:
        subprocess.run(['pytest', '--version'], check=True, capture_output=True)
        run_command('pytest tests/', 'Running pytest')
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  pytest not found, skipping tests")
    
    # Run basic import test
    run_command('python -c "import memra; print(f\'Memra SDK version: {memra.__version__ if hasattr(memra, \"__version__\") else \"unknown\"}\')"', 'Testing basic import')

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Install build dependencies
    run_command('pip install build twine', 'Installing build tools')
    
    # Build the package
    run_command('python -m build', 'Building wheel and source distribution')
    
    # Check the package
    run_command('twine check dist/*', 'Checking package')

def upload_package(test=False):
    """Upload package to PyPI"""
    if test:
        print("🚀 Uploading to Test PyPI...")
        run_command('twine upload --repository testpypi dist/*', 'Uploading to Test PyPI')
        print("📍 Package uploaded to Test PyPI: https://test.pypi.org/project/memra/")
    else:
        print("🚀 Uploading to PyPI...")
        run_command('twine upload dist/*', 'Uploading to PyPI')
        print("📍 Package uploaded to PyPI: https://pypi.org/project/memra/")

def main():
    """Main release process"""
    print("🎯 Memra SDK Release Process")
    print("=" * 40)
    
    # Parse arguments
    test_release = '--test' in sys.argv
    skip_tests = '--skip-tests' in sys.argv
    
    if test_release:
        print("🧪 Test release mode enabled")
    
    # Ensure we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ setup.py not found. Please run from the project root.")
        sys.exit(1)
    
    try:
        # Clean up
        clean_build_artifacts()
        
        # Run tests
        if not skip_tests:
            run_tests()
        else:
            print("⚠️  Skipping tests")
        
        # Build package
        build_package()
        
        # Upload package
        upload_package(test=test_release)
        
        print("\n🎉 Release completed successfully!")
        
        if test_release:
            print("\n📋 Next steps:")
            print("1. Test the package: pip install -i https://test.pypi.org/simple/ memra")
            print("2. If everything works, run: python scripts/release.py")
        else:
            print("\n📋 Package is now available on PyPI!")
            print("Install with: pip install memra")
        
    except KeyboardInterrupt:
        print("\n❌ Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Release failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 