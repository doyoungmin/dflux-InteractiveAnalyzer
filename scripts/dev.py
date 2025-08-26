#!/usr/bin/env python3
"""
개발용 스크립트
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent


def run_linting():
    """코드 린팅 실행"""
    print("🔍 코드 린팅 실행...")
    
    # flake8 실행
    try:
        subprocess.run([
            sys.executable, "-m", "flake8", 
            "src/", "main.py", "setup.py", "interactive_visualizer.py", "base_visualizer.py",
            "--max-line-length=100",
            "--ignore=E203,W503"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ flake8 통과")
    except subprocess.CalledProcessError:
        print("❌ flake8 오류 발견")
        return False
    except FileNotFoundError:
        print("⚠️ flake8이 설치되지 않았습니다.")
        return True
    
    return True


def run_type_checking():
    """타입 체킹 실행"""
    print("🔍 타입 체킹 실행...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "mypy", 
            "src/touch_analyzer/",
            "--ignore-missing-imports"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ mypy 통과")
    except subprocess.CalledProcessError:
        print("❌ mypy 오류 발견")
        return False
    except FileNotFoundError:
        print("⚠️ mypy가 설치되지 않았습니다.")
        return True
    
    return True


def run_tests():
    """테스트 실행"""
    print("🧪 테스트 실행...")
    print("⚠️ 현재 테스트 파일이 없습니다. 기본 import 테스트만 수행합니다.")
    
    try:
        # 기본 import 테스트
        subprocess.run([
            sys.executable, "-c", 
            "import interactive_visualizer; import base_visualizer; print('✅ 기본 import 테스트 통과')"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ 기본 테스트 통과")
    except subprocess.CalledProcessError:
        print("❌ 기본 테스트 실패")
        return False
    
    return True


def format_code():
    """코드 포맷팅"""
    print("🎨 코드 포맷팅...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "black", 
            "src/", "main.py", "setup.py", "scripts/", "interactive_visualizer.py", "base_visualizer.py",
            "--line-length=100"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ 코드 포맷팅 완료")
    except subprocess.CalledProcessError:
        print("❌ 코드 포맷팅 실패")
        return False
    except FileNotFoundError:
        print("⚠️ black이 설치되지 않았습니다.")
        return True
    
    return True


def install_dev_deps():
    """개발 의존성 설치"""
    print("📦 개발 의존성 설치...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-e", ".[dev,monitoring]"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ 개발 의존성 설치 완료")
    except subprocess.CalledProcessError:
        print("❌ 개발 의존성 설치 실패")
        return False
    
    return True


def build_package():
    """패키지 빌드"""
    print("📦 패키지 빌드...")
    
    try:
        subprocess.run([
            sys.executable, "setup.py", "sdist", "bdist_wheel"
        ], cwd=PROJECT_ROOT, check=True)
        print("✅ 패키지 빌드 완료")
    except subprocess.CalledProcessError:
        print("❌ 패키지 빌드 실패")
        return False
    
    return True


def clean():
    """빌드 아티팩트 정리"""
    print("🧹 정리 작업...")
    
    import shutil
    
    # 정리할 디렉토리/파일 목록
    cleanup_targets = [
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "dist", 
        PROJECT_ROOT / "src" / "touch_data_analyzer.egg-info",
        PROJECT_ROOT / ".pytest_cache",
        PROJECT_ROOT / "htmlcov",
        PROJECT_ROOT / ".mypy_cache",
        PROJECT_ROOT / ".coverage"
    ]
    
    for target in cleanup_targets:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            print(f"  🗑️ 삭제: {target.name}")
    
    print("✅ 정리 완료")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="개발 도구")
    parser.add_argument("command", choices=[
        "lint", "type", "test", "format", "install", "build", "clean", "all"
    ], help="실행할 명령")
    
    args = parser.parse_args()
    
    if args.command == "lint":
        return run_linting()
    elif args.command == "type":
        return run_type_checking()
    elif args.command == "test":
        return run_tests()
    elif args.command == "format":
        return format_code()
    elif args.command == "install":
        return install_dev_deps()
    elif args.command == "build":
        return build_package()
    elif args.command == "clean":
        clean()
        return True
    elif args.command == "all":
        success = True
        success &= format_code()
        success &= run_linting()
        success &= run_type_checking()
        success &= run_tests()
        success &= build_package()
        
        if success:
            print("🎉 모든 작업 완료!")
        else:
            print("❌ 일부 작업 실패")
        
        return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
