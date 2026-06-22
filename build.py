#!/usr/bin/env python3
"""
Build script for creating Windows executable using PyInstaller
and preparing installer assets.

Usage:
    python build.py              # Full build (clean + pyinstaller + installer prep)

Prerequisites:
    pip install pyinstaller
    (Optional) Inno Setup 6+ from https://jrsoftware.org/isdl.php
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
    
    # PyInstaller command (find it in venv or system)
    pyinstaller_exe = shutil.which('pyinstaller')
    if pyinstaller_exe is None:
        pyinstaller_exe = [sys.executable, '-m', 'PyInstaller']
    else:
        pyinstaller_exe = [pyinstaller_exe]
    
    # Find python-barcode fonts for PyInstaller bundling
    barcode_fonts_arg = None
    try:
        import barcode
        barcode_dir = os.path.dirname(barcode.__file__)
        fonts_dir = os.path.join(barcode_dir, 'fonts')
        if os.path.isdir(fonts_dir):
            barcode_fonts_arg = f'--add-data={fonts_dir};barcode/fonts'
    except Exception:
        pass

    cmd = pyinstaller_exe + [
        # '--onefile',                  # Create single executable (disabled for folder mode)
        '--windowed',                   # Remove console window (no console shown)
        '--noconsole',                  # Extra flag to ensure no console
        '--name=Inventory_Beta',        # Executable name
        '--icon=assets/icons/app_icon.ico',  # App icon (multi-res with alpha)
        '--add-data=assets;assets',     # Include assets folder
        '--add-data=data;data',         # Include data folder (if exists)
    ]
    if barcode_fonts_arg:
        cmd.append(barcode_fonts_arg)
    cmd += [
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
        ('assets/icons/app_icon.ico', 'assets/icons/app_icon.ico'),
        ('assets/icons/app_icon_light.png', 'assets/icons/app_icon_light.png'),
        ('assets/icons/app_icon_light.ico', 'assets/icons/app_icon_light.ico'),
        ('assets/icons/app_icon_dark.png', 'assets/icons/app_icon_dark.png'),
        ('assets/icons/app_icon_dark.ico', 'assets/icons/app_icon_dark.ico'),
        ('assets/logo.svg', 'assets/logo.svg'),
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_path / dst
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src} -> {dst}")

def create_ico():
    """Generate all icon sets from source JPEGs using PIL, with transparent backgrounds."""
    from PIL import Image
    import numpy as np
    icons_dir = Path('assets/icons')
    icons_dir.mkdir(parents=True, exist_ok=True)
    sizes_ico = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
    size_png = (64, 64)

    def make_transparent(img_path, is_dark_bg=False):
        """Open image and convert background to transparent."""
        img = Image.open(img_path).convert('RGBA')
        arr = np.array(img)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        if is_dark_bg:
            mask = (r < 40) & (g < 40) & (b < 40)
        else:
            mask = (r > 220) & (g > 220) & (b > 220)
        arr[:,:,3] = np.where(mask, 0, 255)
        return Image.fromarray(arr)

    sources = {
        'light': ('logo/app_logo.jpeg', 'app_icon_light', False),
        'dark':  ('logo/black_logo.jpeg', 'app_icon_dark', True),
    }

    for theme, (src_rel, stem, is_dark) in sources.items():
        src = Path(src_rel)
        if not src.exists():
            print(f"WARNING: {src} not found, skipping {theme} icons")
            continue
        transparent = make_transparent(src, is_dark_bg=is_dark)
        # PNG
        png_path = icons_dir / f'{stem}.png'
        transparent.resize(size_png, Image.LANCZOS).save(png_path)
        print(f"Created {png_path}")
        # ICO (with alpha)
        ico_path = icons_dir / f'{stem}.ico'
        transparent.save(ico_path, format='ICO', sizes=sizes_ico)
        print(f"Created {ico_path}")

    # Default app_icon = light variant (app_logo)
    light_png = icons_dir / 'app_icon_light.png'
    if light_png.exists():
        shutil.copy(light_png, icons_dir / 'app_icon.png')
        print(f"Copied app_icon_light.png -> app_icon.png")
    light_ico = icons_dir / 'app_icon_light.ico'
    if light_ico.exists():
        shutil.copy(light_ico, icons_dir / 'app_icon.ico')
        print(f"Copied app_icon_light.ico -> app_icon.ico")

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
        try:
            create_ico()
            print("Created app_icon.ico for installer")
        except Exception as e:
            print(f"Skipping ICO creation (non-critical): {e}")
        
        copy_required_files()
        
        print("\n" + "=" * 50)
        print("BUILD COMPLETE!")
        print("=" * 50)
        print("Files created:")
        print("- dist/Inventory_Beta/Inventory_Beta.exe (Main executable)")
        print("\nOption 1 — Quick install (no extra tools):")
        print("  Right-click install.bat > Run as administrator")
        print("\nOption 2 — Professional installer:")
        print("  1. Download Inno Setup 6 from https://jrsoftware.org/isdl.php")
        print("  2. Right-click installer.iss > Compile")
        print("\nOption 3 — Portable (just run the exe):")
        print("  - Double-click dist/Inventory_Beta/Inventory_Beta.exe")
        print("  - Or copy the whole dist/Inventory_Beta folder to any PC")
    else:
        print("\nBuild failed! Check the error messages above.")

if __name__ == "__main__":
    main()
