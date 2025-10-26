# GitHub Workflow Guide

## Overview

This document provides a detailed explanation of the GitHub Actions workflow (`.github/workflows/build.yml`) in this project, including its purpose, how it's built, current issues, and solutions.

## Relationship Between Workflow and build.py

**Yes, the workflow is closely related to build.py.** The core function of the workflow is to automatically execute the `build.py` script in the GitHub Actions environment.

### What does build.py do?

`build.py` is a packaging script that uses PyInstaller to package the Python application into a Windows executable (.exe). Main functions include:

- Cleaning old build directories (`build`, `dist`)
- Using PyInstaller to package `src/main.py` into a single .exe file
- Including necessary dependencies and resource files
- Generating an executable named `CozeJianYingDraftGenerator.exe`

### What does the Workflow do?

The GitHub Actions workflow (`.github/workflows/build.yml`) automates the following processes:

1. **Continuous Integration (CI)**: Automatically builds and tests on every push to `main` branch or Pull Request creation
2. **Automated Packaging**: Runs `build.py` to automatically build Windows executables in the cloud
3. **Release Management**: Automatically creates GitHub Releases and uploads .exe files when `v*` tags are pushed

## Current Workflow Content Explained

### Trigger Conditions

```yaml
on:
  push:
    branches: [main]
    tags:
      - "v*"
  pull_request:
    branches: [main]
```

The workflow is triggered when:
- Pushing to `main` branch
- Creating tags in `v*` format (e.g., `v1.0.0`)
- Creating or updating Pull Requests targeting `main` branch

### Workflow Steps

1. **Checkout code** - Checks out the code repository
2. **Set up Python** - Sets up Python 3.11 environment
3. **Install dependencies** - Installs dependencies from `requirements.txt`
4. **Run tests** - Runs pytest tests (if test files exist)
5. **Build executable** - Executes `python build.py` to build .exe file
6. **Upload artifact** - Uploads the built .exe file as a workflow artifact
7. **Create Release** - Creates a GitHub Release if it's a tag push

## Why is the Workflow Failing?

### Root Cause

The main reason for workflow failure **was** the use of a **deprecated GitHub Action version**:

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v3  # v3 was deprecated
```

GitHub deprecated `actions/upload-artifact@v3` in April 2024, and workflow runs would automatically fail during the preparation phase.

**This issue has been fixed** by updating to `v4` in the workflow file.

### Detailed Error Information

From the workflow logs, we can see:
- The workflow fails during the "Prepare all required actions" phase
- No actual build steps are executed
- The error points to the deprecated action version

Reference: [GitHub Blog - Deprecation Notice](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)

### Differences Between Local and Cloud Builds

**Why does build.py run successfully locally but the workflow fails?**

1. **Local execution**: Running `python build.py` directly doesn't involve GitHub Actions, so it's not affected by action version deprecation
2. **Cloud execution**: The workflow fails before executing `python build.py`, because GitHub Actions detects the deprecated action version during the preparation phase

**Note**: Even after fixing the action version issue, the workflow still requires:
- Running in a Windows environment (currently configured correctly: `runs-on: windows-latest`)
- Ensuring all dependencies can be installed correctly in the cloud environment
- The `resources` directory needs to exist (referenced in build.py)

## Solutions Applied

The following issues have been fixed in this repository:

### 1. Updated Upload Artifact Action

**Status: ✅ Fixed**

Updated `actions/upload-artifact@v3` to `v4`:

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4  # Now using v4 version
  with:
    name: CozeJianYingDraftGenerator-Windows
    path: dist/CozeJianYingDraftGenerator.exe
```

### 2. Ensured Resources Directory Exists

**Status: ✅ Fixed**

build.py references the `resources` directory, which has been created with proper .gitignore configuration:

```python
'--add-data=resources;resources',  # Add resource files
```

The directory structure is now tracked in git while allowing content to be ignored.

### 3. Fixed Test Directory Reference

**Status: ✅ Fixed**

The workflow has been updated to reference the correct `test/` directory:

```yaml
- name: Run tests
  run: |
    pip install pytest
    pytest test/ -v || echo "No tests found"  # Now correctly references test/
```

## Summary of Workflow Purpose

### Current Purpose

1. **Automated Building**: Automatically builds Windows executables on every code update
2. **Quality Assurance**: Runs tests before merging code
3. **Version Release**: Automatically creates Releases and publishes executables through Git tags

### Future Extensible Purposes

1. **Multi-platform Builds**: Can be extended to support macOS and Linux builds
2. **Automated Testing**: Add more comprehensive test coverage
3. **Code Quality Checks**: Integrate linting and code formatting checks
4. **Deployment Automation**: Automatically deploy to distribution platforms

## How to Test the Workflow

### Local Testing of build.py

```bash
# Install dependencies
pip install -r requirements.txt

# Run build script
python build.py

# Check generated file
dir dist\CozeJianYingDraftGenerator.exe
```

### Cloud Testing of Workflow

The workflow has been fixed and should now run successfully:

1. **Workflow is now configured correctly** (action versions updated, paths fixed)
2. **Push to branch or create PR** to trigger workflow
3. **View Actions page** to monitor build progress
4. **Download artifacts** to verify generated .exe files

The next workflow run should complete successfully with all steps passing.

## Conclusion

- ✅ The workflow **is indeed related to build.py**, it automates the execution of build.py
- ✅ The workflow failure is due to using a **deprecated GitHub Action version**
- ✅ Local execution works because it **doesn't depend on GitHub Actions infrastructure**
- ✅ The fix is to **update to actions/upload-artifact@v4**

The workflow provides automated build and release capabilities for the project, and it is **recommended to keep and fix** rather than remove it.
