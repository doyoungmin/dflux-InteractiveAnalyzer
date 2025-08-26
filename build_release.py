#!/usr/bin/env python3
"""
dflux_InteractiveAnalyzer v1.0 배포용 실행파일 생성 스크립트
개발자가 아닌 사용자도 쉽게 사용할 수 있도록 자동화된 빌드 프로세스
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """필요한 의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    try:
        import pyinstaller
        print("✅ PyInstaller 설치됨")
    except ImportError:
        print("❌ PyInstaller가 설치되지 않음")
        print("설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 설치 완료")
    
    # 기타 필요한 패키지들 확인
    required_packages = ['pandas', 'matplotlib', 'numpy', 'PIL']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 설치됨")
        except ImportError:
            print(f"❌ {package} 설치되지 않음")
            return False
    
    return True

def create_spec_file():
    """PyInstaller spec 파일 생성"""
    print("📝 spec 파일 생성 중...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
        ('data_log', 'data_log'),
        ('data_results', 'data_results'),
        ('data_bg', 'data_bg'),
        ('docs', 'docs'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'pandas',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'logging',
        'pathlib',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'unittest',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dflux_InteractiveAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('dflux_InteractiveAnalyzer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ spec 파일 생성 완료")

def build_executable():
    """실행파일 빌드"""
    print("🔨 실행파일 빌드 중...")
    
    # 기존 빌드 폴더 정리
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller 실행
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "dflux_InteractiveAnalyzer.spec"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 실행파일 빌드 완료")
        return True
    else:
        print("❌ 빌드 실패")
        print("오류:", result.stderr)
        return False

def create_release_package():
    """배포 패키지 생성"""
    print("📦 배포 패키지 생성 중...")
    
    # 버전 정보
    version = "v1.0"
    app_name = "dflux_InteractiveAnalyzer"
    release_folder = f"{app_name}_{version}"
    
    # 기존 릴리즈 폴더 정리
    if os.path.exists(release_folder):
        shutil.rmtree(release_folder)
    
    # 릴리즈 폴더 생성
    os.makedirs(release_folder)
    
    # 실행파일 복사
    if platform.system() == "Darwin":  # macOS
        source = "dist/dflux_InteractiveAnalyzer"
        if os.path.exists(source):
            shutil.copy2(source, release_folder)
            print("✅ macOS 실행파일 복사 완료")
    elif platform.system() == "Windows":
        source = "dist/dflux_InteractiveAnalyzer.exe"
        if os.path.exists(source):
            shutil.copy2(source, release_folder)
            print("✅ Windows 실행파일 복사 완료")
    else:  # Linux
        source = "dist/dflux_InteractiveAnalyzer"
        if os.path.exists(source):
            shutil.copy2(source, release_folder)
            print("✅ Linux 실행파일 복사 완료")
    
    # 필요한 폴더들 복사
    folders_to_copy = ['data_log', 'data_results', 'config', 'data_bg']
    for folder in folders_to_copy:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(release_folder, folder))
            print(f"✅ {folder} 폴더 복사 완료")
    
    # README 파일 복사
    if os.path.exists('README.md'):
        shutil.copy2('README.md', release_folder)
        print("✅ README.md 복사 완료")
    
    # 사용법 안내 파일 생성
    create_usage_guide(release_folder)
    
    print(f"✅ 배포 패키지 생성 완료: {release_folder}")
    return release_folder

def create_usage_guide(release_folder):
    """사용법 안내 파일 생성"""
    guide_content = """# dflux_InteractiveAnalyzer v1.0 사용법

## 🚀 실행 방법

### Windows 사용자
1. `dflux_InteractiveAnalyzer.exe` 파일을 더블클릭하세요
2. 프로그램이 자동으로 시작됩니다

### macOS 사용자
1. `dflux_InteractiveAnalyzer` 파일을 더블클릭하세요
2. 보안 경고가 나타나면 "열기"를 클릭하세요

### Linux 사용자
1. 터미널에서 `./dflux_InteractiveAnalyzer` 명령어를 실행하세요
2. 또는 파일을 더블클릭하세요

## 📁 폴더 구조

- `data_log/`: 분석할 데이터 파일들이 저장된 폴더
- `data_results/`: 분석 결과가 저장되는 폴더
- `data_bg/`: 프로그램에서 사용하는 배경 이미지 파일들
- `config/`: 프로그램 설정 파일들

## 🔧 문제 해결

### 프로그램이 실행되지 않는 경우
1. 운영체제가 지원되는지 확인하세요 (Windows 10+, macOS 10.14+, Linux)
2. 바이러스 백신 프로그램이 실행을 차단할 수 있습니다
3. 관리자 권한으로 실행해보세요

### 데이터가 보이지 않는 경우
1. `data_log/` 폴더에 CSV 파일들이 있는지 확인하세요
2. 파일 형식이 올바른지 확인하세요

## 📞 지원

문제가 발생하면 개발팀에 문의하세요.

---
dflux_InteractiveAnalyzer v1.0
"""
    
    with open(os.path.join(release_folder, '사용법.txt'), 'w', encoding='utf-8') as f:
        f.write(guide_content)

def main():
    """메인 함수"""
    print("🚀 dflux_InteractiveAnalyzer v1.0 배포 패키지 생성 시작")
    print("=" * 50)
    
    # 1. 의존성 확인
    if not check_dependencies():
        print("❌ 의존성 확인 실패")
        return False
    
    # 2. spec 파일 생성
    create_spec_file()
    
    # 3. 실행파일 빌드
    if not build_executable():
        print("❌ 빌드 실패")
        return False
    
    # 4. 배포 패키지 생성
    release_folder = create_release_package()
    
    print("=" * 50)
    print(f"🎉 배포 패키지 생성 완료!")
    print(f"📁 생성된 폴더: {release_folder}")
    print(f"📤 이 폴더를 그대로 공유하면 됩니다!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()
