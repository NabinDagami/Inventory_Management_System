#!/usr/bin/env python3
"""
Build script for creating Windows executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    folders_to_clean = ['build', 'dist', '__pycache__']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        os.remove(spec_file)
        print(f"Removed {spec_file}")

def create_executable():
    """Create executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Create single executable
        '--windowed',                   # Remove console window
        '--name=InventoryPro',          # Executable name
        '--icon=assets/icons/app_icon.png',  # App icon
        '--add-data=assets;assets',     # Include assets folder
        '--add-data=data;data',         # Include data folder (if exists)
        '--hidden-import=customtkinter',
        '--hidden-import=matplotlib',
        '--hidden-import=PIL',
        '--hidden-import=reportlab',
        '--hidden-import=openpyxl',
        '--hidden-import=babel',
        '--hidden-import=tkcalendar',
        '--clean',                      # Clean cache
        'main.py'
    ]
    
    print("Building executable...")
    print("Command:", ' '.join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Check if executable was created
        exe_path = Path('dist/InventoryPro.exe')
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"Executable created: {exe_path}")
            print(f"Size: {size:.1f} MB")
            
            # Copy required files to dist folder
            copy_required_files()
            
            return True
        else:
            print("ERROR: Executable not found in dist folder")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def copy_required_files():
    """Copy required files to the dist folder"""
    dist_path = Path('dist')
    
    # Create necessary folders
    folders_to_create = ['assets/icons', 'data', 'reports']
    for folder in folders_to_create:
        (dist_path / folder).mkdir(parents=True, exist_ok=True)
    
    # Copy files
    files_to_copy = [
        ('README.md', 'README.md'),
        ('requirements.txt', 'requirements.txt'),
        ('assets/icons/app_icon.png', 'assets/icons/app_icon.png'),
        ('assets/logo.svg', 'assets/logo.svg'),
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_path / dst
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src} -> {dst}")

def create_installer_script():
    """Create a simple installer script"""
    installer_script = '''@echo off
echo Installing Inventory Pro...
echo.

REM Create application directory
if not exist "%PROGRAMFILES%\\InventoryPro" (
    mkdir "%PROGRAMFILES%\\InventoryPro"
)

REM Copy files
copy "InventoryPro.exe" "%PROGRAMFILES%\\InventoryPro\\"
xcopy "assets" "%PROGRAMFILES%\\InventoryPro\\assets\\" /E /I /Q
xcopy "data" "%PROGRAMFILES%\\InventoryPro\\data\\" /E /I /Q 2>nul
xcopy "reports" "%PROGRAMFILES%\\InventoryPro\\reports\\" /E /I /Q 2>nul

REM Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\shortcut.vbs"
echo sLinkFile = "%USERPROFILE%\\Desktop\\Inventory Pro.lnk" >> "%TEMP%\\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\shortcut.vbs"
echo oLink.TargetPath = "%PROGRAMFILES%\\InventoryPro\\InventoryPro.exe" >> "%TEMP%\\shortcut.vbs"
echo oLink.WorkingDirectory = "%PROGRAMFILES%\\InventoryPro" >> "%TEMP%\\shortcut.vbs"
echo oLink.IconLocation = "%PROGRAMFILES%\\InventoryPro\\assets\\icons\\app_icon.png" >> "%TEMP%\\shortcut.vbs"
echo oLink.Description = "Inventory Pro - Professional Inventory Management" >> "%TEMP%\\shortcut.vbs"
echo oLink.Save >> "%TEMP%\\shortcut.vbs"
cscript "%TEMP%\\shortcut.vbs" /nologo
del "%TEMP%\\shortcut.vbs"

echo.
echo Installation complete!
echo Desktop shortcut created.
echo.
pause
'''
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_script)
    
    print("Created installer script: dist/install.bat")

def main():
    """Main build process"""
    print("=" * 50)
    print("Inventory Pro - Build Script")
    print("=" * 50)
    
    # Check if we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("WARNING: Not running in virtual environment")
        print("It's recommended to run this in the virtual environment")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Clean previous builds
    clean_build()
    
    # Create executable
    if create_executable():
        # Create installer script
        create_installer_script()
        
        print("\n" + "=" * 50)
        print("BUILD COMPLETE!")
        print("=" * 50)
        print("Files created:")
        print("- dist/InventoryPro.exe (Main executable)")
        print("- dist/install.bat (Installer script)")
        print("- dist/assets/ (Application assets)")
        print("\nTo install:")
        print("1. Run 'install.bat' as administrator")
        print("2. Or copy files manually to desired location")
        print("\nTo run:")
        print("- Double-click InventoryPro.exe")
        print("- Or use the desktop shortcut after installation")
    else:
        print("\nBuild failed! Check the error messages above.")

if __name__ == "__main__":
    main()
