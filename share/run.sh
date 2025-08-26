#!/bin/bash
# dflux_InteractiveAnalyzer - macOS/Linux 실행 스크립트
# 이 스크립트는 macOS와 Linux에서 프로그램을 실행합니다.

echo "========================================"
echo "dflux_InteractiveAnalyzer 실행 중..."
echo "========================================"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python3가 설치되어 있지 않습니다."
    echo "Python 3.8 이상을 설치해주세요."
    echo "macOS: brew install python3"
    echo "Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

# Python 버전 확인
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "오류: Python 3.8 이상이 필요합니다. 현재 버전: $python_version"
    exit 1
fi

echo "Python 버전 확인: $python_version"

# 가상환경 확인 (선택사항)
if [ -f "venv/bin/activate" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
fi

# 의존성 설치 확인
echo "의존성 확인 중..."
if ! python3 -c "import pandas" &> /dev/null; then
    echo "의존성을 설치합니다..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "오류: 의존성 설치에 실패했습니다."
        exit 1
    fi
fi

# 프로그램 실행
echo "프로그램을 시작합니다..."
python3 main.py

# 오류 발생 시 대기
if [ $? -ne 0 ]; then
    echo ""
    echo "프로그램 실행 중 오류가 발생했습니다."
    echo "오류 코드: $?"
    read -p "계속하려면 Enter를 누르세요..."
fi

echo ""
echo "프로그램이 종료되었습니다."

