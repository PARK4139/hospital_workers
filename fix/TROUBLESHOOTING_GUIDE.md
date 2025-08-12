# PK System Python Module Import Troubleshooting Guide

## Problem
```
ModuleNotFoundError: No module named 'pkg_py'
```

## Root Cause
The Python script is trying to import from `pkg_py` but Python can't find this module because:
1. The working directory is incorrect
2. The Python path doesn't include the necessary directories
3. The module structure is not properly set up

## Solutions

### Solution 1: Use the Fixed Batch File (Recommended)
1. Copy `run_pk_system.bat` to your `pk_system` directory
2. Run the batch file from the `pk_system` directory
3. This will automatically set the correct working directory and Python path

### Solution 2: Manual Python Path Setup
1. Navigate to the `pk_system` directory:
   ```cmd
   cd C:\Users\pk\Downloads\pk_system
   ```

2. Set the PYTHONPATH environment variable:
   ```cmd
   set PYTHONPATH=%CD%;%PYTHONPATH%
   ```

3. Run the original script:
   ```cmd
   python pkg_py\functions_split\ensure_pk_system_enabled.py
   ```

### Solution 3: Use the Fixed Python Script
1. Replace the original `ensure_pk_system_enabled.py` with `ensure_pk_system_enabled_fixed.py`
2. The fixed script automatically handles path setup

### Solution 4: Check Directory Structure
Ensure your `pk_system` directory has this structure:
```
pk_system/
├── pkg_py/
│   └── functions_split/
│       ├── ensure_pk_system_enabled.py
│       └── ensure_guided_not_prepared_yet.py
└── pkg_windows/
    └── ensure_pk_system_enabled.cmd
```

## Verification Steps

1. **Check if pkg_py exists:**
   ```cmd
   dir C:\Users\pk\Downloads\pk_system\pkg_py
   ```

2. **Check Python path:**
   ```python
   import sys
   for path in sys.path:
       print(path)
   ```

3. **Test import manually:**
   ```python
   import sys
   sys.path.append(r"C:\Users\pk\Downloads\pk_system")
   from pkg_py.functions_split.ensure_guided_not_prepared_yet import ensure_guided_not_prepared_yet
   ```

## Common Issues and Fixes

### Issue 1: Wrong Working Directory
- **Symptom**: "No module named 'pkg_py'" error
- **Fix**: Run from the `pk_system` directory, not from `pkg_windows`

### Issue 2: Missing __init__.py Files
- **Symptom**: Import errors even with correct path
- **Fix**: Ensure `pkg_py` and `functions_split` directories have `__init__.py` files

### Issue 3: Python Version Mismatch
- **Symptom**: Module not found despite correct path
- **Fix**: Ensure you're using the correct Python version and virtual environment

## Quick Fix Commands

```cmd
REM Navigate to correct directory
cd C:\Users\pk\Downloads\pk_system

REM Set Python path
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Run the script
python pkg_py\functions_split\ensure_pk_system_enabled.py
```

## Next Steps
After fixing the import issue, the script should run successfully. If you encounter other errors, they will be related to the actual functionality rather than module imports.
