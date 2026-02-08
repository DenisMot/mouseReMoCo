@echo off
REM mouseReMoCo launcher script for Windows
REM Activates the mouseremoco conda environment and starts the app
REM Can be run from any directory

REM Repository location - CHANGE THIS to your mouseReMoCo repository path
set REPO_DIR=C:\path\to\your\mouseReMoCo

REM Get the directory where this script is located (data will be saved here)
setlocal enabledelayedexpansion
set WORK_DIR=%~dp0
set WORK_DIR=%WORK_DIR:~0,-1%

REM Path to the Python app entry point
set APP_PATH=%REPO_DIR%\python\main.py

cls
echo.
echo ================================================
echo         mouseReMoCo Launcher
echo ================================================
echo.
echo Repository: %REPO_DIR%
echo Data folder: %WORK_DIR%
echo.

REM Check if the app file exists
if not exist "%APP_PATH%" (
    echo X Error: Repository not found at %REPO_DIR%
    echo Please edit this script and update REPO_DIR to the correct path
    echo.
    pause
    exit /b 1
)

echo + Found main.py
echo.

REM Initialize conda
echo Initializing conda...
call conda.bat shell.cmd hook > nul 2>&1

REM Check if mouseremoco environment exists
conda env list | findstr /R "^mouseremoco" > nul
if errorlevel 1 (
    echo X Error: 'mouseremoco' conda environment not found
    echo.
    echo Please create it first by running:
    echo   cd %SCRIPT_DIR%\python
    echo   conda env create -f environment.yml
    echo.
    pause
    exit /b 1
)

echo + Found conda environment: mouseremoco
echo.
echo Launching application...
echo ================================================
echo.

REM Change to work directory and run the app
cd /d "%WORK_DIR%"
call conda activate mouseremoco
python "%APP_PATH%"

echo.
echo ================================================

REM Archive data files with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a-%%b)
set TIMESTAMP=%mydate%_%mytime%

if exist "data.csv" (
    copy "data.csv" "data_%TIMESTAMP%.csv" > nul
    echo + Archived: data_%TIMESTAMP%.csv
)
if exist "marker.csv" (
    copy "marker.csv" "marker_%TIMESTAMP%.csv" > nul
    echo + Archived: marker_%TIMESTAMP%.csv
)

echo ================================================
echo Application closed
echo Data folder: %WORK_DIR%
echo ================================================
echo.
pause
endlocal
