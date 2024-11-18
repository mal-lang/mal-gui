"""Utilities for loading files"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

def image_path(filename):
    """From a filename, return the absolute path of the image"""
    return str(PACKAGE_DIR / "images" / filename)
