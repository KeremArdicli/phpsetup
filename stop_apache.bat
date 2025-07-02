@echo off
setlocal enabledelayedexpansion

:: Configure these paths
set APACHE_DIR=C:\Apache24

:: Kill existing Apache
taskkill /f /im httpd.exe >nul 2>&1
cmd /c ""%APACHE_DIR%\bin\httpd.exe" -k stop -n "Apache24""
del "C:\Apache24\logs\httpd.pid" >nul 2>&1

exit