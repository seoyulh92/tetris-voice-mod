
@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing required packages...
pip install tkinter pynput SpeechRecognition python-Levenshtein

echo Installation complete.
pause
