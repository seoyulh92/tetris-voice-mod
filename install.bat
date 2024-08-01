@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Ensuring pip is installed...
python -m ensurepip --upgrade

echo Installing required packages...
pip install --upgrade pip
pip install tkinter pynput SpeechRecognition python-Levenshtein

echo Installation complete.
pause
