@echo off
REM Quick start script for image processor
REM Usage: run_processor.bat "path\to\images" [/f]
REM  /f flag generates Excel file

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Image Processor - Quick Start
    echo.
    echo Usage: run_processor.bat "path\to\images" [/f]
    echo.
    echo Arguments:
    echo   path\to\images  - Directory containing images to process
    echo   /f              - (Optional) Generate Excel metadata file
    echo.
    echo Examples:
    echo   run_processor.bat "ShatkahonEU\Punjabi"
    echo   run_processor.bat "ShatkahonEU\Punjabi" /f
    exit /b 1
)

set IMAGE_PATH=%~1
set EXCEL_FLAG=

if "%~2"=="/f" (
    set EXCEL_FLAG=-f
)

echo Processing images from: %IMAGE_PATH%
python image_processor.py "%IMAGE_PATH%" %EXCEL_FLAG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Processing complete! Check the 'processed' folder for results.
    if not "%EXCEL_FLAG%"=="" (
        echo Excel file has been generated in the image directory.
    )
) else (
    echo.
    echo An error occurred during processing.
    exit /b 1
)

pause
