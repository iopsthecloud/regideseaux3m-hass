#!/usr/bin/env python3
"""
Build a HACS-compatible ZIP file for the integration.

This script creates a ZIP file that can be manually installed
in Home Assistant via HACS or by copying to custom_components/.

Usage:
    python scripts/build_hacs_zip.py
    
    # Or with custom version
    python scripts/build_hacs_zip.py --version 0.3.0
"""

import argparse
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
COMPONENT_DIR = PROJECT_DIR / "custom_components" / "regiedeseauxmpl"
BUILD_DIR = PROJECT_DIR / "build"
DIST_DIR = PROJECT_DIR / "dist"


def get_version() -> str:
    """Get version from manifest.json."""
    import json
    manifest_path = COMPONENT_DIR / "manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest.get("version", "0.0.0")


def build_zip(version: str | None = None) -> Path:
    """Build the ZIP file."""
    if version is None:
        version = get_version()
    
    # Clean build directory
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy component to build directory
    dest_dir = BUILD_DIR / "regiedeseauxmpl"
    shutil.copytree(COMPONENT_DIR, dest_dir)
    
    # Remove unnecessary files from the build
    unnecessary_files = [
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "*.md",  # Keep only if needed for HACS
    ]
    
    for pattern in unnecessary_files:
        for path in dest_dir.rglob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    
    # Create ZIP file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"regiedeseauxmpl-{version}-{timestamp}.zip"
    zip_path = DIST_DIR / zip_filename
    
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dest_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dest_dir)
                zipf.write(file_path, arcname)
    
    return zip_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build HACS ZIP for Régie des Eaux Montpellier"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Version to use (default: from manifest.json)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up build directory"
    )
    
    args = parser.parse_args()
    
    print(f"📦 Building HACS ZIP file...")
    print(f"   Component dir: {COMPONENT_DIR}")
    
    # Build ZIP
    zip_path = build_zip(args.version)
    
    print(f"✅ ZIP created: {zip_path}")
    print(f"   Size: {zip_path.stat().st_size / 1024:.1f} KB")
    
    if not args.no_cleanup:
        print(f"🧹 Cleaning up build directory...")
        shutil.rmtree(BUILD_DIR)
    
    print(f"\n🎉 Build complete!")
    print(f"   You can now:")
    print(f"   - Install manually: copy to custom_components/")
    print(f"   - Or upload to GitHub releases")


if __name__ == "__main__":
    main()
