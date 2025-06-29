@echo off
setlocal enabledelayedexpansion

:: Configure these paths
set APACHE_DIR=C:\Apache24
set PHP_BASE=C:\PHP

:: Default PHP version
set PHP_VERSION=php82
set CONF_FILE_DIR=%APACHE_DIR%\conf\httpd_%PHP_VERSION%.conf

:: Parse command line arguments
if not "%~1"=="" (
    set PHP_VERSION=%~1
    set PHP_VERSION=!PHP_VERSION:--=!
    set CONF_FILE_DIR=%APACHE_DIR%\conf\httpd_%PHP_VERSION%.conf
)

:: Set PHP path
set PHP_PATH=%PHP_BASE%\!PHP_VERSION!

:: Verify paths
if not exist "%APACHE_DIR%\bin\httpd.exe" (
    echo Error: Apache not found at %APACHE_DIR%\bin\httpd.exe
    pause
    exit /b 1
)

if not exist "!PHP_PATH!" (
    echo Error: PHP folder "!PHP_PATH!" not found
    echo Available versions:
    dir /b "%PHP_BASE%\php*" | find "php"
    pause
    exit /b 1
)

:: Kill existing Apache
taskkill /f /im httpd.exe >nul 2>&1

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

:: Start Apache
echo Starting Apache with PHP !PHP_VERSION!...
echo Using config: !CONF_FILE_DIR!
start "Apache Server" cmd /c ""%APACHE_DIR%\bin\httpd.exe" -X -f "!CONF_FILE_DIR!""

:: Verify
timeout /t 3 >nul
tasklist /fi "imagename eq httpd.exe" >nul
if errorlevel 1 (
    echo Failed to start Apache
    echo Check %APACHE_DIR%\logs\error.log
    echo Last errors:
    type "%APACHE_DIR%\logs\error.log" | findstr /i error
) else (
    echo Apache started successfully
    echo PHP Version: !PHP_VERSION!
    echo URL: http://localhost
    echo.
    echo Running PHP:
    "!PHP_PATH!\php.exe" -r "echo phpversion();"
)

pause