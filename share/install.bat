@echo off
REM dflux_InteractiveAnalyzer - Windows 설치 스크립트
REM 이 스크립트는 Windows에서 프로그램을 설치합니다.

echo ========================================
echo dflux_InteractiveAnalyzer 설치 중...
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

echo Python 설치 확인 완료

REM 가상환경 생성 (선택사항)
set /p create_venv="가상환경을 생성하시겠습니까? (y/n): "
if /i "%create_venv%"=="y" (
    echo 가상환경을 생성합니다...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 오류: 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo 가상환경이 생성되었습니다.
    echo 활성화하려면: venv\Scripts\activate.bat
)

REM 의존성 설치
echo 의존성을 설치합니다...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 오류: 의존성 설치에 실패했습니다.
    pause
    exit /b 1
)

REM 개발 모드 설치 (선택사항)
set /p install_dev="개발 모드로 설치하시겠습니까? (y/n): "
if /i "%install_dev%"=="y" (
    echo 개발 모드로 설치합니다...
    pip install -e .
    if %errorlevel% neq 0 (
        echo 경고: 개발 모드 설치에 실패했습니다.
    ) else (
        echo 개발 모드 설치가 완료되었습니다.
    )
)

echo.
echo ========================================
echo 설치가 완료되었습니다!
echo ========================================
echo.
echo 실행 방법:
echo 1. run.bat 실행
echo 2. 또는 python main.py
echo.
echo 가상환경을 사용하는 경우:
echo 1. venv\Scripts\activate.bat
echo 2. python main.py
echo.
pause

