#!/bin/bash
# dflux_InteractiveAnalyzer - macOS/Linux 설치 스크립트
# 이 스크립트는 macOS와 Linux에서 프로그램을 설치합니다.

echo "========================================"
echo "dflux_InteractiveAnalyzer 설치 중..."
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

# pip 설치 확인
if ! command -v pip3 &> /dev/null; then
    echo "pip3가 설치되어 있지 않습니다. 설치를 시도합니다..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip -y
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "pip3를 수동으로 설치해주세요."
        exit 1
    fi
fi

# 가상환경 생성 (선택사항)
read -p "가상환경을 생성하시겠습니까? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "오류: 가상환경 생성에 실패했습니다."
        exit 1
    fi
    echo "가상환경이 생성되었습니다."
    echo "활성화하려면: source venv/bin/activate"
fi

# 의존성 설치
echo "의존성을 설치합니다..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "오류: 의존성 설치에 실패했습니다."
    exit 1
fi

# 개발 모드 설치 (선택사항)
read -p "개발 모드로 설치하시겠습니까? (y/n): " install_dev
if [[ $install_dev =~ ^[Yy]$ ]]; then
    echo "개발 모드로 설치합니다..."
    pip3 install -e .
    if [ $? -ne 0 ]; then
        echo "경고: 개발 모드 설치에 실패했습니다."
    else
        echo "개발 모드 설치가 완료되었습니다."
    fi
fi

echo ""
echo "========================================"
echo "설치가 완료되었습니다!"
echo "========================================"
echo ""
echo "실행 방법:"
echo "1. ./run.sh 실행"
echo "2. 또는 python3 main.py"
echo ""
echo "가상환경을 사용하는 경우:"
echo "1. source venv/bin/activate"
echo "2. python3 main.py"
echo ""

