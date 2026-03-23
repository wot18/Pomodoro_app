@echo off
echo ===========================================
echo Pomodoro Timer
echo ===========================================
echo.

REM Activate existing virtual environment
call conda activate gptac_venv
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment 'gptac_venv'
    echo Please check if conda is installed correctly
    pause
    exit /b 1
)

REM Run the program
echo Starting Pomodoro Timer...
python main.py

REM Pause to check for errors
if %errorlevel% neq 0 (
    echo.
    echo Program error occurred, please check error messages above
    pause
)
