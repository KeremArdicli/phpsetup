@echo off
setlocal enabledelayedexpansion

:: Configure these paths
set APACHE_DIR=C:\Apache24
set PHP_BASE=C:\PHP

:: Default PHP version (this will be overridden by the argument from VBScript)
set PHP_VERSION=php81
set CONF_FILE_DIR=%APACHE_DIR%\conf\httpd_%PHP_VERSION%.conf

:: Parse command line arguments
if not "%~1"=="" (
    set PHP_VERSION=%~1
    set PHP_VERSION=!PHP_VERSION:--=!
    set CONF_FILE_DIR=%APACHE_DIR%\conf\httpd_!PHP_VERSION!.conf
)

:: Set PHP path
set PHP_PATH=%PHP_BASE%\!PHP_VERSION!

:: Verify paths
if not exist "%APACHE_DIR%\bin\httpd.exe" (
    echo Error: Apache not found at %APACHE_DIR%\bin\httpd.exe
    exit /b 1
)

if not exist "!PHP_PATH!" (
    echo Error: PHP folder "!PHP_PATH!" not found
    echo Available versions:
    dir /b "%PHP_BASE%\php*" | find "php"
    exit /b 1
)

:: Kill existing Apache processes (ensure clean start before attempting to start a new one)
taskkill /f /im httpd.exe >nul 2>&1
:: Give it a moment to terminate gracefully
timeout /t 1 >nul 2>&1
:: Remove pid file if it exists from a previous crash, to prevent issues
del "%APACHE_DIR%\logs\httpd.pid" >nul 2>&1

:: Check if version-specific config exists, otherwise create it
if not exist "!CONF_FILE_DIR!" (
    echo Creating new configuration for !PHP_VERSION!...
    (
        echo LoadModule php_module "!PHP_PATH!\php8apache2_4.dll"
        echo PHPIniDir "!PHP_PATH!"
        echo AddHandler application/x-httpd-php .php
        type "%APACHE_DIR%\conf\httpd.conf"
    ) > "!CONF_FILE_DIR!"
)

:: Start Apache in a minimized, separate command prompt window
echo Starting Apache with PHP !PHP_VERSION!...
echo Using config: !CONF_FILE_DIR!
start "Apache Server" /min cmd /c ""%APACHE_DIR%\bin\httpd.exe" -k start -n "Apache24" -f "!CONF_FILE_DIR!""

:: Exit the batch script immediately after starting Apache
exit /b
