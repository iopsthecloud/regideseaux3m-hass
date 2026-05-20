#!/usr/bin/env python3
"""
Setup development environment using uv.

This script creates an isolated Python environment with all dependencies
using uv (https://github.com/astral-sh/uv).

Usage:
    # Setup the environment (first time)
    python scripts/setup_dev_env.py
    
    # Or use the Makefile commands:
    make setup
    make test
    make run
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
UV = "uv"


def run_command(cmd, cwd=None, check=True):
    """Run a shell command."""
    print(f"🔄 {cmd}")
    try:
        subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or PROJECT_DIR,
            check=check,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False


def check_uv_installed():
    """Check if uv is installed."""
    try:
        result = subprocess.run(
            [UV, "--version"],
            capture_output=True,
            text=True,
        )
        print(f"✅ uv {result.stdout.strip()} is installed")
        return True
    except FileNotFoundError:
        print("❌ uv is not installed")
        print("\nTo install uv:")
        print("    curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("\nOr on macOS:")
        print("    brew install uv")
        return False


def setup_environment():
    """Setup the development environment."""
    print("\n" + "="*60)
    print("Setting up Régie des Eaux development environment")
    print("="*60 + "\n")
    
    if not check_uv_installed():
        sys.exit(1)
    
    # Check Python version
    print("\n🐍 Checking Python version...")
    run_command("python --version")
    
    # Create virtual environment with uv
    print("\n📦 Creating virtual environment with uv...")
    run_command(f"{UV} venv --python-preference only-managed")
    
    # Install dependencies
    print("\n📥 Installing dependencies...")
    run_command(f"{UV} pip install -e '.'")
    run_command(f"{UV} pip install -e '. [dev]'")
    
    # Verify installation
    print("\n✅ Verifying installation...")
    run_command("python -c \"from custom_components.regiedeseauxmpl.api import RegieDesEauxAPI; print('✓ API module OK')\"")
    run_command("python -c \"from standalone import SimpleRegieAPI; print('✓ Standalone wrapper OK')\"")
    
    print("\n" + "="*60)
    print("Development environment setup complete! ✅")
    print("="*60)
    print("\nTo activate the environment:")
    print(f"    source {PROJECT_DIR / '.venv' / 'bin' / 'activate'}")
    print("\nTo run tests:")
    print("    make test")
    print("\nTo run the standalone CLI:")
    print("    REGIE_USERNAME=your@email REGIE_PASSWORD=your_pass python test_standalone.py")


def run_tests():
    """Run the test suite."""
    print("\n" + "="*60)
    print("Running tests")
    print("="*60 + "\n")
    
    # Run pytest
    result = run_command(
        f"{UV} pip install pytest pytest-asyncio && {UV} run pytest tests/ -v --tb=short",
        check=False
    )
    
    if result:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


def run_standalone():
    """Run the standalone test."""
    username = os.getenv("REGIE_USERNAME")
    password = os.getenv("REGIE_PASSWORD")
    
    if not username or not password:
        print("❌ REGIE_USERNAME and REGIE_PASSWORD environment variables required")
        print("\nSet them first:")
        print("    export REGIE_USERNAME=your@email.com")
        print("    export REGIE_PASSWORD=your_password")
        sys.exit(1)
    
    run_command("python test_standalone.py --full --verbose")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("    python scripts/setup_dev_env.py setup   # Setup environment")
        print("    python scripts/setup_dev_env.py test    # Run tests")
        print("    python scripts/setup_dev_env.py run     # Run standalone test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_environment()
    elif command == "test":
        run_tests()
    elif command == "run":
        run_standalone()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
