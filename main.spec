# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Clinic Management System
# Build command:  pyinstaller main.spec  (always via build.bat)

import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

# ── Collect everything for each package (data + binaries + hidden imports) ────
datas    = []
binaries = []
hiddenimports = []

# customtkinter — assets, themes, fonts
ctk_d, ctk_b, ctk_h = collect_all("customtkinter")
datas    += ctk_d
binaries += ctk_b
hiddenimports += ctk_h

# SQLAlchemy — must use collect_all; collect_submodules alone misses importers
sa_d, sa_b, sa_h = collect_all("sqlalchemy")
datas    += sa_d
binaries += sa_b
hiddenimports += sa_h

# reportlab
rl_d, rl_b, rl_h = collect_all("reportlab")
datas    += rl_d
binaries += rl_b
hiddenimports += rl_h

# Pillow
pil_d, pil_b, pil_h = collect_all("PIL")
datas    += pil_d
binaries += pil_b
hiddenimports += pil_h

# openpyxl
xl_d, xl_b, xl_h = collect_all("openpyxl")
datas    += xl_d
binaries += xl_b
hiddenimports += xl_h

# Application language files and assets
datas += [
    ("languages", "languages"),
    ("assets",    "assets"),
]

# Extra hidden imports that dynamic loaders can miss
hiddenimports += [
    # SQLAlchemy SQLite dialect (critical — this was the missing piece)
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.pysqlite",
    "sqlalchemy.dialects.sqlite.base",
    "sqlalchemy.dialects.sqlite.json",
    "sqlalchemy.orm",
    "sqlalchemy.orm.decl_api",
    "sqlalchemy.ext.declarative",
    "sqlalchemy.sql.default_comparator",
    "sqlalchemy.pool.impl",
    # greenlet — required by SQLAlchemy async internals
    "greenlet",
    # bcrypt
    "bcrypt",
    # openpyxl extras
    "openpyxl.styles.alignment",
    "openpyxl.styles.fills",
    "openpyxl.styles.fonts",
    "openpyxl.utils.dataframe",
    # reportlab extras
    "reportlab.lib.pagesizes",
    "reportlab.lib.colors",
    "reportlab.lib.styles",
    "reportlab.lib.units",
    "reportlab.platypus",
    "reportlab.platypus.tables",
    "reportlab.pdfgen.canvas",
]

# ── Analysis ───────────────────────────────────────────────────────────────────
a = Analysis(
    ["main.py"],
    pathex=[os.path.abspath(".")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "scipy", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE ────────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ClinicSystem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico",
)

# ── COLLECT (onedir → dist\ClinicSystem\) ─────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ClinicSystem",
)
