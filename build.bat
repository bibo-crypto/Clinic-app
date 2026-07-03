@echo off
:: ── Keep the window open no matter what happens ──────────────────────────────
if not "%CLINIC_BUILD_RUNNING%"=="1" (
    set CLINIC_BUILD_RUNNING=1
    cmd /k ""%~f0""
    exit /b
)

:: ── Always run from the script's own folder ───────────────────────────────────
cd /d "%~dp0"

cls
echo.
echo  ============================================================
echo    Clinic Management System  -  Build Script
echo  ============================================================
echo.

:: ── STEP 1: Find Python ───────────────────────────────────────────────────────
echo  [1/5] Searching for Python...

set PYTHON=python
python --version >nul 2>&1
if errorlevel 1 (
    set PYTHON=py
    py --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  [ERROR] Python not found!
        echo  Install Python 3.10+ from https://python.org
        echo  Tick "Add Python to PATH" during install.
        echo.
        goto :end
    )
)

for /f "tokens=*" %%V in ('%PYTHON% --version 2^>^&1') do echo  [OK] %%V
echo.

:: ── STEP 2: Create virtual environment ───────────────────────────────────────
echo  [2/5] Creating virtual environment...

if exist "venv\Scripts\activate.bat" (
    echo  [OK] venv already exists.
    goto :do_activate
)

%PYTHON% -m venv venv
if exist "venv\Scripts\activate.bat" (
    echo  [OK] venv created successfully.
    goto :do_activate
)

echo  [WARN] venv failed - will use system Python instead.
goto :do_install

:do_activate
call venv\Scripts\activate.bat
set PYTHON=python
echo  [OK] venv activated.

:do_install
echo.

:: ── STEP 3: Install packages ──────────────────────────────────────────────────
echo  [3/5] Installing packages...
echo        (first run takes 5-10 minutes, please wait)
echo.

%PYTHON% -m pip install --upgrade pip --quiet --no-warn-script-location
%PYTHON% -m pip install -r requirements.txt --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [ERROR] Package install failed.
    echo  Check internet connection or disable antivirus temporarily.
    goto :end
)

%PYTHON% -m pip install pyinstaller --quiet --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [ERROR] PyInstaller install failed.
    goto :end
)
echo.
echo  [OK] All packages installed.
echo.

:: ── STEP 4: Icon check ────────────────────────────────────────────────────────
echo  [4/5] Checking icon.ico...
if exist "icon.ico" (
    echo  [OK] icon.ico found.
) else (
    echo  [WARN] icon.ico not found - building with no icon.
)
echo.

:: ── STEP 5: Build ─────────────────────────────────────────────────────────────
echo  [5/5] Building EXE with PyInstaller...
echo        Please wait...
echo.

if exist "build" rmdir /s /q build
if exist "dist"  rmdir /s /q dist

%PYTHON% -m PyInstaller main.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed!
    echo  Try: right-click build.bat -> Run as Administrator
    echo  Or:  disable Avast and retry.
    goto :end
)

echo.
echo  ============================================================
echo    BUILD SUCCESSFUL!
echo  ============================================================
echo.
echo    EXE : dist\ClinicSystem\ClinicSystem.exe
echo.
echo    To make installer:
echo    Open installer.iss in Inno Setup then click Compile
echo    Output: output\ClinicSetup.exe
echo  ============================================================

:end
echo.
echo  Press any key to close...
pause > nul
