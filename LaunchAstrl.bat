@echo off
title Astrl Launcher

:: 1. Close any running CPU-only Ollama instances to apply GPU settings
taskkill /F /IM ollama.exe 2>NUL

:: 2. Start Ollama with the AMD GPU override flag via PowerShell
echo Starting Ollama background engine with GPU acceleration...
powershell -Command "$env:HSA_OVERRIDE_GFX_VERSION='11.0.2'; Start-Process ollama -ArgumentList 'serve'"
timeout /t 4 /nobreak >NUL

:: 3. Launch the app using the virtual environment
echo Booting Astrl...
".\venv\Scripts\python.exe" main.py

exit