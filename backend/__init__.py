"""
backend package initialization
"""

import os
from pathlib import Path

# Package root directory
PACKAGE_ROOT = Path(__file__).parent

# Ensure required directories exist
for folder in ['uploads', 'models', 'logs']:
    (PACKAGE_ROOT / folder).mkdir(exist_ok=True)

# Version information
__version__ = "1.0.0"

# Import key components for easier access
from .core.detection import CheatingDetector
from .services.file_service import FileService

__all__ = ['CheatingDetector', 'FileService']