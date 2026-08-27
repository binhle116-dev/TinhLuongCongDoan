@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Khong tim thay Python. Hay cai tai https://www.python.org/downloads/ (tick "Add python.exe to PATH").
  pause
  exit /b 1
)
python -c "import django, waitress, import_export, pandas, openpyxl" 2>nul
if errorlevel 1 (
  echo Dang cai dat thu vien can thiet...
  python -m pip install -r requirements.txt
)
python manage.py migrate
python serve.py
pause
