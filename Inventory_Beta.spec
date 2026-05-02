# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('assets', 'assets'), ('data', 'data')],
    hiddenimports=['customtkinter', 'matplotlib', 'PIL', 'reportlab', 'openpyxl', 'babel', 'tkcalendar', 'src', 'src.models.database', 'src.models', 'src.views.dashboard', 'src.views.inventory', 'src.views.sales', 'src.views.purchases', 'src.views.customers', 'src.views.suppliers', 'src.views.statements', 'src.views.reports', 'src.views.settings', 'src.views.payment_dialog', 'src.utils.logger', 'src.utils.simple_table_styles', 'src.utils.format_utils', 'src.utils.export_manager', 'src.utils.sku_generator', 'src.modules.sales', 'src.modules'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Inventory_Beta',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\app_icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Inventory_Beta',
)
