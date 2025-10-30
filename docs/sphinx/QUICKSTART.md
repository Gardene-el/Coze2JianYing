# Sphinx-Markdown-Builder Quick Start Guide

## Overview

The project now includes Sphinx documentation with markdown-builder support. This allows you to automatically generate API documentation from Python docstrings in Markdown format.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- sphinx>=7.0.0
- sphinx-rtd-theme>=1.3.0
- sphinx-autodoc-typehints>=1.24.0
- sphinx-markdown-builder>=0.6.5

### 2. Build Documentation

Navigate to the Sphinx documentation directory:

```bash
cd docs/sphinx
```

Build Markdown documentation:

```bash
# Linux/macOS
make markdown

# Windows
make.bat markdown
```

Build HTML documentation (optional):

```bash
# Linux/macOS
make html

# Windows
make.bat html
```

### 3. View Generated Documentation

The generated documentation will be in:
- **Markdown**: `docs/sphinx/build/markdown/`
- **HTML**: `docs/sphinx/build/html/`

### 4. Available Make Commands

```bash
make markdown  # Generate Markdown documentation
make html      # Generate HTML documentation  
make clean     # Clean build directory
make help      # Show all available commands
```

## Documentation Structure

```
docs/sphinx/
├── README.md              # Detailed documentation guide
├── Makefile              # Build automation (Linux/macOS)
├── make.bat              # Build automation (Windows)
├── source/               # Source files
│   ├── conf.py          # Sphinx configuration
│   ├── index.rst        # Main entry point
│   └── modules/         # Module documentation
│       ├── coze_plugin.rst
│       └── src.rst
└── build/               # Generated documentation (gitignored)
    ├── markdown/        # Markdown output
    └── html/            # HTML output
```

## Adding Documentation to Your Code

To have your code appear in the generated documentation, use proper docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

Both Google-style and NumPy-style docstrings are supported.

## Further Information

For more detailed information, see [docs/sphinx/README.md](docs/sphinx/README.md).
