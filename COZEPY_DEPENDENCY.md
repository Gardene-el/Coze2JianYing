# cozepy Dependency Addition

## Overview
This document describes the addition of `cozepy` as a project dependency.

## What is cozepy?
`cozepy` is the official Python SDK for the Coze platform, developed by ByteDance. It provides programmatic access to Coze's APIs and services.

- **Package Name**: cozepy
- **Version Required**: >=0.20.0
- **PyPI**: https://pypi.org/project/cozepy/
- **License**: MIT

## Installation

### For Users
Install all project dependencies including cozepy:
```bash
pip install -r requirements.txt
```

### For Developers
If you're working with the source code:
```bash
# Install in development mode
pip install -e .

# Or install dependencies separately
pip install cozepy>=0.20.0
```

## Usage
The cozepy package provides access to Coze platform features. Example usage:

```python
import cozepy

# Your Coze integration code here
```

## Testing
To verify cozepy is correctly installed:
```bash
python test_cozepy_import.py
```

This test will:
1. Verify cozepy is listed in requirements.txt
2. Test that cozepy can be imported successfully
3. Display available modules and version information

## Dependencies
cozepy requires the following dependencies (automatically installed):
- pydantic (>=2.5.0, <3.0.0)
- authlib (>=1.2.0, <2.0.0)
- httpx (version depends on Python version)
- typing-extensions (>=4.3.0, <5.0.0)
- distro (>=1.9.0, <2.0.0)
- websockets (version depends on Python version)

## Integration
The cozepy dependency is automatically included when:
- Installing via `pip install -r requirements.txt`
- Installing the package via `pip install -e .` (uses setup.py)
- Building with PyInstaller (reads from requirements.txt)

## Notes
- This addition doesn't modify any existing functionality
- The dependency is positioned logically in requirements.txt after pyJianYingDraft
- setup.py automatically includes it since it reads from requirements.txt
