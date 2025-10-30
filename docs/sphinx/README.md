# Sphinx Documentation for Coze2JianYing

This directory contains Sphinx configuration for generating API documentation from the project's source code.

## Overview

This Sphinx configuration uses `sphinx-markdown-builder` to generate Markdown format documentation instead of HTML. This allows the generated API documentation to be easily integrated with the existing Markdown documentation in the `docs/` directory.

## Prerequisites

Make sure you have installed all required dependencies:

```bash
pip install -r ../../requirements.txt
```

The key documentation dependencies are:
- `sphinx>=7.0.0`
- `sphinx-rtd-theme>=1.3.0`
- `sphinx-autodoc-typehints>=1.24.0`
- `sphinx-markdown-builder>=0.6.5`

## Building Documentation

### Using Make (Linux/macOS)

```bash
# Build Markdown documentation
make markdown

# Build HTML documentation (if needed)
make html

# Clean build directory
make clean
```

### Using make.bat (Windows)

```cmd
# Build Markdown documentation
make.bat markdown

# Build HTML documentation (if needed)
make.bat html

# Clean build directory
make.bat clean
```

### Direct Sphinx Command

```bash
# Build Markdown
sphinx-build -b markdown source build/markdown

# Build HTML
sphinx-build -b html source build/html
```

## Output Location

- **Markdown output**: `build/markdown/`
- **HTML output**: `build/html/`

## Configuration

The main configuration file is `source/conf.py`, which includes:

- **Project Information**: Project name, version, author
- **Extensions**: 
  - `sphinx.ext.autodoc` - Automatic documentation from docstrings
  - `sphinx.ext.napoleon` - Support for Google and NumPy style docstrings
  - `sphinx.ext.viewcode` - Add links to source code
  - `sphinx_autodoc_typehints` - Support for type hints
  - `sphinx_markdown_builder` - Generate Markdown output
- **Autodoc Options**: Configured to include members, special methods, and type hints
- **Napoleon Settings**: Configured for both Google and NumPy style docstrings

## Structure

```
docs/sphinx/
├── Makefile           # Build automation for Linux/macOS
├── make.bat          # Build automation for Windows
├── README.md         # This file
├── source/           # Source files for documentation
│   ├── conf.py      # Sphinx configuration
│   ├── index.rst    # Main documentation entry point
│   └── modules/     # Module-specific documentation
│       ├── coze_plugin.rst  # Coze Plugin API docs
│       └── src.rst          # Draft Generator API docs
└── build/           # Generated documentation (gitignored)
    ├── markdown/    # Markdown output
    └── html/        # HTML output
```

## Customization

### Adding New Modules

To document a new module:

1. Create a new `.rst` file in `source/modules/`
2. Use `automodule` directives to include the module
3. Add the new file to the `toctree` in `source/index.rst`

Example:

```rst
New Module
==========

.. automodule:: your_module_name
   :members:
   :undoc-members:
   :show-inheritance:
```

### Modifying Configuration

Edit `source/conf.py` to:
- Change theme or appearance
- Add/remove extensions
- Modify autodoc behavior
- Adjust Napoleon settings for docstring parsing

## Docstring Style

The configuration supports both Google and NumPy style docstrings. Example:

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

## Continuous Integration

Consider adding documentation building to your CI/CD pipeline:

```yaml
# Example GitHub Actions step
- name: Build Documentation
  run: |
    cd docs/sphinx
    make markdown
```

## Troubleshooting

### Import Errors

If Sphinx cannot import your modules:
- Ensure the project root is in `sys.path` (already configured in `conf.py`)
- Check that all dependencies are installed
- Verify Python can import the modules directly

### Missing Documentation

If documentation is not being generated:
- Check that modules have proper docstrings
- Verify the module paths in `.rst` files are correct
- Use `sphinx-build -v` for verbose output

### Markdown Output Issues

If markdown output is not as expected:
- Verify `sphinx-markdown-builder` is installed
- Check the `markdown_uri_doc_suffix` setting in `conf.py`
- Review the builder's documentation for limitations

## Further Reading

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [sphinx-markdown-builder](https://github.com/clayrisser/sphinx-markdown-builder)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Autodoc Extension](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
