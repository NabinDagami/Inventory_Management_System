# Inventory Beta - Build Complete! 🎉

## Build Summary

- **Application**: Inventory Beta - Management System
- **Version**: Beta
- **Build Mode**: Folder Mode (faster startup)
- **Build Date**: 2025-03-04
- **Executable**: `Inventory_Beta.exe`
- **Total Size**: ~112 MB

## Files Created

### Main Application

- `dist/Inventory_Beta/` - Application folder
  - `Inventory_Beta.exe` - Main executable
  - `_internal/` - Dependencies and libraries

### Installer

- `dist/install.bat` - Windows installer script

## Run the Application

### Method 1: Direct Run

```
dist/Inventory_Beta/Inventory_Beta.exe
```

### Method 2: Install

1. Run `dist/install.bat` as administrator
2. Use desktop shortcut

## Troubleshooting: If Inventory_Beta.exe Won't Open

### 1. Check Windows Defender/Antivirus

**Most common cause!** Windows may block the exe.

**Fix:**

- Right-click `Inventory_Beta.exe` → Properties
- Check "Unblock" at the bottom if present
- Click Apply → OK
- Try running again

### 2. Run as Administrator

- Right-click `Inventory_Beta.exe` → "Run as administrator"

### 3. Check Missing Dependencies

The `_internal` folder must be in the same directory as `Inventory_Beta.exe`:

```
Inventory_Beta/
├── Inventory_Beta.exe      ← Main file
└── _internal/              ← Required folder (must exist!)
    ├── assets/
    ├── customtkinter/
    └── ...
```

### 4. Check Error Logs

Look for error messages in:

- `logs/error_YYYYMMDD.log`
- `error_file.txt`

### 5. Test with Console (Debug Mode)

If you need to see error messages:

1. Open Command Prompt
2. Navigate to the folder:
   ```cmd
   cd "dist\Inventory_Beta"
   ```
3. Run the exe:
   ```cmd
   Inventory_Beta.exe
   ```
4. Look for error messages in the console

### 6. Rebuild if Needed

If nothing works, try rebuilding:

```bash
python build.py
```

## What's Included

- ✅ Centered dialogs
- ✅ Beta branding
- ✅ Error logging system
- ✅ Folder mode (faster startup)

## Build Information

- **Tool**: PyInstaller
- **Mode**: Folder (not single-file)
- **Python**: 3.x
- **UI**: CustomTkinter

---

**Build Location**: `dist/Inventory_Beta/Inventory_Beta.exe`

**Need help?** Check the logs folder for error details.
