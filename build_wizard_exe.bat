@echo off
REM Bulldawg AI Install Wizard - PyInstaller build script
REM Run this on a Windows machine with Python installed.

echo Building BulldawgAI_InstallWizard.exe ...
python -m pip install --upgrade pyinstaller
python -m PyInstaller --onefile --windowed --name BulldogAI_InstallWizard bulldog_install_wizard.py

if exist dist\BulldogAI_InstallWizard.exe (
    echo.
    echo SUCCESS: dist\BulldogAI_InstallWizard.exe
    echo.
    echo SHA-256:
    certutil -hashfile dist\BulldogAI_InstallWizard.exe SHA256
    echo.
    echo Copy the EXE to the target laptop (USB, Google Drive, or GitHub Release).
    echo Expect a SmartScreen warning on first run (unsigned).
) else (
    echo BUILD FAILED
    exit /b 1
)
pause
