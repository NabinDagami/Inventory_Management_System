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
        # '--onefile',                  # Create single executable (disabled for folder mode)
        '--windowed',                   # Remove console window (no console shown)
        '--noconsole',                  # Extra flag to ensure no console
        '--name=Inventory_Beta',        # Executable name
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
        '--hidden-import=src',
        '--hidden-import=src.models.database',
        '--hidden-import=src.models',
        '--hidden-import=src.views.dashboard',
        '--hidden-import=src.views.inventory',
        '--hidden-import=src.views.sales',
        '--hidden-import=src.views.purchases',
        '--hidden-import=src.views.customers',
        '--hidden-import=src.views.suppliers',
        '--hidden-import=src.views.statements',
        '--hidden-import=src.views.reports',
        '--hidden-import=src.views.settings',
        '--hidden-import=src.views.payment_dialog',
        '--hidden-import=src.utils.logger',
        '--hidden-import=src.utils.simple_table_styles',
        '--hidden-import=src.utils.format_utils',
        '--hidden-import=src.utils.export_manager',
        '--hidden-import=src.utils.sku_generator',
        '--hidden-import=src.modules.sales',
        '--hidden-import=src.modules',
        '--paths=src',                  # Add src to Python path
        '--clean',                      # Clean cache
        'main.py'
    ]
    
    print("Building executable...")
    print("Command:", ' '.join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Check if executable was created (folder mode creates dist/Inventory_Beta/Inventory_Beta.exe)
        exe_path = Path('dist/Inventory_Beta/Inventory_Beta.exe')
        if exe_path.exists():
            # Calculate total folder size
            total_size = sum(f.stat().st_size for f in Path('dist/Inventory_Beta').rglob('*') if f.is_file())
            total_size_mb = total_size / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Total folder size: {total_size_mb:.1f} MB")
            
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
echo Installing Inventory Beta...
echo.

REM Create application directory
if not exist "%PROGRAMFILES%\\Inventory_Beta" (
    mkdir "%PROGRAMFILES%\\Inventory_Beta"
)

REM Copy files
xcopy "Inventory_Beta" "%PROGRAMFILES%\\Inventory_Beta\\" /E /I /Q

REM Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\shortcut.vbs"
echo sLinkFile = "%USERPROFILE%\\Desktop\\Inventory Beta.lnk" >> "%TEMP%\\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\shortcut.vbs"
echo oLink.TargetPath = "%PROGRAMFILES%\\Inventory_Beta\\Inventory_Beta.exe" >> "%TEMP%\\shortcut.vbs"
echo oLink.WorkingDirectory = "%PROGRAMFILES%\\Inventory_Beta" >> "%TEMP%\\shortcut.vbs"
echo oLink.IconLocation = "%PROGRAMFILES%\\Inventory_Beta\\_internal\\assets\\icons\\app_icon.png" >> "%TEMP%\\shortcut.vbs"
echo oLink.Description = "Inventory Beta - Inventory Management System" >> "%TEMP%\\shortcut.vbs"
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
    print("Inventory Beta - Build Script")
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
        print("- dist/Inventory_Beta/Inventory_Beta.exe (Main executable)")
        print("- dist/install.bat (Installer script)")
        print("\nTo install:")
        print("1. Run 'install.bat' as administrator")
        print("2. Or copy files manually to desired location")
        print("\nTo run:")
        print("- Run: dist/Inventory_Beta/Inventory_Beta.exe")
        print("- Or use the desktop shortcut after installation")
    else:
        print("\nBuild failed! Check the error messages above.")

if __name__ == "__main__":
    main()
