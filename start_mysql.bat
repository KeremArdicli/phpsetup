@echo off
setlocal

set MYSQLD="C:\mysql\bin\mysqld.exe"
set DATA_DIR="D:\mysql_data"

:: Kill existing MySQL processes forcefully
taskkill /F /IM mysqld.exe >nul 2>&1
:: Give it a moment to terminate gracefully
timeout /t 1 >nul 2>&1

:: Remove any lingering mysqld.pid file to ensure a clean start
:: The PID file is usually in the data directory
del "%DATA_DIR%\mysqld.pid" >nul 2>&1

:: Start MySQL in a completely detached and hidden way
:: 'start ""' ensures a new process and handles paths with spaces.
:: '> NUL 2>&1' redirects all standard output and error to the NUL device,
:: preventing a console window from appearing and staying open.
echo Starting MySQL...
start /min /b "" %MYSQLD% --datadir=%DATA_DIR% > NUL 2>&1

exit /b