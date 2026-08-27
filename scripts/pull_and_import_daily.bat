@echo off
setlocal
set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

set "WINSCP=C:\Program Files (x86)\WinSCP\WinSCP.com"
if not exist "%WINSCP%" set "WINSCP=C:\Program Files\WinSCP\WinSCP.com"

if not exist "%WINSCP%" (
    echo Khong tim thay WinSCP.com. Kiem tra duong dan cai dat WinSCP. >> "%~dp0pull_log.txt"
    exit /b 1
)

echo ==== %date% %time% ==== >> "%~dp0pull_log.txt"
"%WINSCP%" /script="%~dp0pull_sanluong_chitiet.txt" /log="%~dp0pull_log.txt"

python manage.py import_daily_production >> "%~dp0pull_log.txt" 2>&1

endlocal
