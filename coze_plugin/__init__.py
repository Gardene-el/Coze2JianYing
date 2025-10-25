"""
Coze Plugin Subproject

This subproject contains the Coze platform plugin tools and the core assistant functionality.
It includes:
- tools/: Coze tool function handlers
- main.py: Core assistant classes and main entry point
"""

__version__ = "0.1.0"

# Import core functionality
try:
    from .main import CozeJianYingAssistant, main
    __all__ = ["CozeJianYingAssistant", "main"]
except ImportError:
    # If dependencies are not available, just pass
    __all__ = []
