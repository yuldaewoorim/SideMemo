@echo off
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean --windowed --name SideMemo sidememo.py
