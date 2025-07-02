@echo off
setlocal

taskkill /F /IM mysqld.exe >nul 2>&1
timeout /t 1 >nul 2>&1

exit /b