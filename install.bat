@echo off
REM Python 3 설치
echo 다운로드 및 Python 3 설치를 시작합니다.

REM Python 설치 파일 다운로드 (64-bit Python 3.11.x)
curl -o python-installer.exe https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe

REM 설치 파일 실행
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

REM pip가 최신 버전인지 확인 및 업그레이드
python -m pip install --upgrade pip

REM 필요한 패키지 설치
echo 패키지 설치를 시작합니다.
pip install pillow SpeechRecognition python-levenshtein pynput

REM 작업 완료
echo 모든 작업이 완료되었습니다.
pause
