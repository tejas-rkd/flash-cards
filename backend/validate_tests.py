#!/usr/bin/env python3
"""
Simple test runner to validate the test setup.
This script can be run to quickly check if all tests are working.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 Flashcard Backend Test Validation")
    print("=" * 50)
    
    # Set PYTHONPATH
    current_dir = Path(__file__).parent.absolute()
    os.environ['PYTHONPATH'] = str(current_dir)
    
    # List of commands to run
    test_commands = [
        ("python -m pytest --version", "Check pytest installation"),
        ("python -c 'import app.main; print(\"App imports successfully\")'", "Check app imports"),
        ("python -m pytest tests/ --collect-only -q", "Test discovery"),
        ("python -m pytest tests/test_models.py -v", "Model tests"),
        ("python -m pytest tests/test_config.py -v", "Configuration tests"),
        ("python -m pytest tests/test_flashcard_service.py::test_create_flashcard_success -v", "Single service test"),
        ("python -m pytest tests/ -k 'test_root_endpoint' -v", "API endpoint test"),
        ("python -m pytest tests/ -m unit --tb=short", "Unit tests"),
        ("python -m pytest tests/ --tb=short", "All tests"),
    ]
    
    # Track results
    passed = 0
    total = len(test_commands)
    
    # Run each command
    for command, description in test_commands:
        if run_command(command, description):
            passed += 1
        else:
            # If a critical test fails, we might want to stop
            if "All tests" in description:
                print("\n⚠️ Some tests failed. Check the output above for details.")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Validation Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validation checks passed! The test setup is working correctly.")
        return 0
    else:
        print("⚠️ Some validation checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
