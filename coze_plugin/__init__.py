"""
Coze Plugin Subproject

This subproject contains the Coze platform plugin tools and the core assistant functionality.
It includes:
- tools/: Coze tool function handlers
- coze_jianying_assistant/: Core assistant classes and utilities
"""

__version__ = "0.1.0"

# Import from coze_jianying_assistant for backward compatibility
try:
    from .coze_jianying_assistant import CozeJianYingAssistant, main
    __all__ = ["CozeJianYingAssistant", "main"]
except ImportError:
    # If coze_jianying_assistant is not available, just pass
    __all__ = []
