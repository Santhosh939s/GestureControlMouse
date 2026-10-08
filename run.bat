@echo off
title Hand Gesture Mouse Control
echo Starting Hand Gesture Mouse Control...

:: Try Python 3.10 first (which has full camera access permissions)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" main.py
    goto end
)

:: Try py -3.10
py -3.10 main.py 2>nul
if %errorlevel% equ 0 goto end

:: Fallback to default python
python main.py

:end
pause
