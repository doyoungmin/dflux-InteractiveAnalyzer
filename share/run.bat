@echo off
REM dflux_InteractiveAnalyzer - Windows 실행 스크립트
REM 이 스크립트는 Windows에서 프로그램을 실행합니다.

echo ========================================
echo dflux_InteractiveAnalyzer 실행 중...
echo ========================================

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 오류: Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 가상환경 확인 (선택사항)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
)

REM 의존성 설치 확인
echo 의존성 확인 중...
pip show pandas >nul 2>&1
if %errorlevel% neq 0 (
    echo 의존성을 설치합니다...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 오류: 의존성 설치에 실패했습니다.
        pause
        exit /b 1
    )
)

REM 프로그램 실행
echo 프로그램을 시작합니다...
python main.py

REM 오류 발생 시 대기
if %errorlevel% neq 0 (
    echo.
    echo 프로그램 실행 중 오류가 발생했습니다.
    echo 오류 코드: %errorlevel%
    pause
)

echo.
echo 프로그램이 종료되었습니다.
pause

