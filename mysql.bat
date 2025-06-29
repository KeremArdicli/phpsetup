@echo off
setlocal

set MYSQLD="C:\mysql\bin\mysqld.exe"
set DATA_DIR="D:\mysql_data"

:: Kill existing MySQL
taskkill /F /IM mysqld.exe >nul 2>&1

:: Start MySQL
echo Starting MySQL...
%MYSQLD% --datadir=%DATA_DIR% --console

echo MySQL started in console mode.
echo Keep this window open while MySQL is running.
pause