#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 배포 파일 생성 스크립트
dflux_InteractiveAnalyzer의 배포 패키지를 윈도우용과 맥용으로 구분하여 자동으로 생성합니다.
"""

import os
import shutil
import sys
import platform
from datetime import datetime
import zipfile

def create_deployment_package():
    """윈도우용과 맥용 배포 패키지를 각각 생성합니다."""
    
    # 현재 작업 디렉토리 확인
    current_dir = os.getcwd()
    print(f"📍 현재 작업 디렉토리: {current_dir}")
    
    # 프로젝트 루트 디렉토리 확인
    if not os.path.exists("interactive_visualizer.py"):
        print("❌ 프로젝트 루트 디렉토리에서 실행해주세요.")
        print("   interactive_visualizer.py 파일이 현재 디렉토리에 있어야 합니다.")
        return False
    
    # 배포 폴더명 생성 (날짜 포함)
    timestamp = datetime.now().strftime("%m%d")
    
    # 윈도우용과 맥용 폴더 생성
    windows_folder = f"share_{timestamp}_Windows"
    mac_folder = f"share_{timestamp}_macOS"
    
    print(f"🚀 윈도우용 배포 폴더 생성: {windows_folder}")
    print(f"🚀 맥용 배포 폴더 생성: {mac_folder}")
    
    # 기존 배포 폴더가 있으면 삭제
    for folder in [windows_folder, mac_folder]:
        if os.path.exists(folder):
            print(f"🗑️  기존 {folder} 폴더 삭제 중...")
            shutil.rmtree(folder)
    
    # 윈도우용 배포 패키지 생성
    print("\n🪟 윈도우용 배포 패키지 생성 중...")
    if not create_platform_specific_package(windows_folder, "windows"):
        return False
    
    # 맥용 배포 패키지 생성
    print("\n🍎 맥용 배포 패키지 생성 중...")
    if not create_platform_specific_package(mac_folder, "macos"):
        return False
    
    # ZIP 파일 생성
    print("\n📦 ZIP 파일 생성 중...")
    create_platform_zip_packages(windows_folder, mac_folder, timestamp)
    
    print(f"\n🎉 모든 배포 패키지 생성 완료!")
    print(f"🪟 윈도우용: {windows_folder}/")
    print(f"🍎 맥용: {mac_folder}/")
    print(f"📊 윈도우용 크기: {get_folder_size(windows_folder):.1f} MB")
    print(f"📊 맥용 크기: {get_folder_size(mac_folder):.1f} MB")
    
    return True

def create_platform_specific_package(deployment_folder, platform_type):
    """플랫폼별 배포 패키지를 생성합니다."""
    
    # 배포 폴더 생성
    os.makedirs(deployment_folder, exist_ok=True)
    
    # 복사할 파일 및 폴더 목록
    files_to_copy = [
        "main.py",
        "interactive_visualizer.py", 
        "base_visualizer.py",
        "requirements.txt",
        "setup.py",
        "README.md",
        "ARCHITECTURE.md"
    ]
    
    folders_to_copy = [
        "config",
        "src", 
        "docs"
    ]
    
    # 빈 폴더로 생성할 폴더 목록
    empty_folders_to_create = [
        "data_log",
        "data_bg"
    ]
    
    # 파일 복사
    print("📁 핵심 파일 복사 중...")
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, deployment_folder)
            print(f"   ✅ {file_name}")
        else:
            print(f"   ⚠️  {file_name} (파일 없음)")
    
    # 폴더 복사
    print("📂 폴더 복사 중...")
    for folder_name in folders_to_copy:
        if os.path.exists(folder_name):
            shutil.copytree(folder_name, os.path.join(deployment_folder, folder_name))
            print(f"   ✅ {folder_name}/")
        else:
            print(f"   ⚠️  {folder_name}/ (폴더 없음)")
    
    # 빈 폴더 생성
    print("📁 빈 폴더 생성 중...")
    for folder_name in empty_folders_to_create:
        empty_folder_path = os.path.join(deployment_folder, folder_name)
        os.makedirs(empty_folder_path, exist_ok=True)
        print(f"   ✅ {folder_name}/ (빈 폴더)")
    
    # 플랫폼별 최적화된 main.py 생성
    print("🔧 플랫폼별 최적화된 main.py 생성 중...")
    create_platform_optimized_main(deployment_folder, platform_type)
    
    # 플랫폼별 설치 및 실행 스크립트 생성
    print("📜 플랫폼별 설치/실행 스크립트 생성 중...")
    create_platform_install_scripts(deployment_folder, platform_type)
    
    # 플랫폼별 배포 가이드 생성
    print("📖 플랫폼별 배포 가이드 생성 중...")
    create_platform_deployment_guide(deployment_folder, platform_type)
    
    return True

def create_platform_optimized_main(deployment_folder, platform_type):
    """플랫폼별 최적화된 main.py를 생성합니다."""
    
    if platform_type == "windows":
        main_content = create_windows_main_content()
    else:
        main_content = create_macos_main_content()
    
    with open(os.path.join(deployment_folder, "main.py"), "w", encoding="utf-8") as f:
        f.write(main_content)

def create_windows_main_content():
    """윈도우용 main.py 내용을 생성합니다."""
    
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dflux_InteractiveAnalyzer - 메인 실행 파일 (Windows용)
배포용으로 최적화됨 - 원본 구조 반영
"""

import os
import sys
import gc
import platform

# Windows 환경 확인
if platform.system() != "Windows":
    print("⚠️  이 버전은 Windows용입니다. macOS/Linux용을 사용해주세요.")
    sys.exit(1)

# 소스 경로 추가 (배포용)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import messagebox

# 배포용으로 간소화된 import
try:
    from src.touch_analyzer.core.config import Config
    from src.touch_analyzer.utils.logging_utils import setup_logger
    from src.touch_analyzer.utils.memory_utils import MemoryMonitor, full_memory_cleanup
    from src.touch_analyzer.utils.path_manager import path_manager
except ImportError:
    # src 모듈이 없는 경우 기본 클래스들 정의
    class Config:
        def __init__(self):
            self.window_title = "dflux_InteractiveAnalyzer (Windows)"
            self.window_width = 1200
            self.window_height = 800
        
        @classmethod
        def default(cls):
            return cls()
        
        @classmethod
        def from_dict(cls, config_dict):
            return cls()
        
        def ensure_directories(self):
            pass
    
    def setup_logger(name, level='INFO'):
        import logging
        logging.basicConfig(level=getattr(logging, level.upper()))
        return logging.getLogger(name)
    
    class MemoryMonitor:
        def __init__(self, enable_monitoring=True, threshold_mb=1000.0):
            self.enable_monitoring = enable_monitoring
            self.threshold_mb = threshold_mb
        
        def log_memory_usage(self, message):
            pass
    
    def full_memory_cleanup():
        pass
    
    class path_manager:
        @staticmethod
        def get_data_dir():
            return os.path.join(os.path.dirname(__file__), 'data')

# 설정 로드
try:
    from config.settings import get_config
    config_dict = get_config()
except ImportError:
    try:
        from config import settings
        config_dict = settings.get_config()
    except ImportError:
        config_dict = {}

def initialize_application():
    """애플리케이션 초기화"""
    print("🚀 Windows용 dflux_InteractiveAnalyzer 초기화 시작")
    
    # 메모리 정리
    gc.collect()
    
    # 로거 설정
    logger = setup_logger("dflux_InteractiveAnalyzer")
    logger.info("Windows용 애플리케이션 초기화 시작")
    
    # 설정 로드
    config = Config.from_dict(config_dict)
    config.ensure_directories()
    
    # 메모리 모니터 설정
    memory_monitor = MemoryMonitor(
        enable_monitoring=True, 
        threshold_mb=config_dict.get('performance', {}).get('memory_threshold_mb', 1000.0)
    )
    memory_monitor.log_memory_usage("Windows용 애플리케이션 초기화")
    
    return config, memory_monitor, logger

def create_main_window(config):
    """메인 윈도우 생성"""
    root = tk.Tk()
    root.title(config.window_title)
    root.geometry(f"{config.window_width}x{config.window_height}")
    
    # Windows 스타일 적용
    try:
        root.state('zoomed')  # Windows에서 전체화면
    except:
        pass
    
    # 윈도우 아이콘 설정 (선택사항)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass  # 아이콘 설정 실패는 무시
    
    return root

def create_application(root, memory_monitor, logger):
    """애플리케이션 인스턴스 생성"""
    try:
        # 대시보드 표시
        from interactive_visualizer import InteractiveVisualizer
        app = InteractiveVisualizer(root)
        
        # 메모리 모니터링 설정
        if hasattr(app, '_setup_memory_monitoring'):
            app._setup_memory_monitoring()
        
        return app
    except Exception as e:
        logger.error(f"애플리케이션 생성 실패: {str(e)}")
        raise

def setup_cleanup_handler(root, app, memory_monitor, logger):
    """정리 핸들러 설정"""
    def on_closing():
        """프로그램 종료 시 리소스 정리"""
        try:
            logger.info("Windows용 프로그램 종료 시작")
            memory_monitor.log_memory_usage("종료 전")
            
            # 애플리케이션 리소스 정리
            if hasattr(app, 'cleanup_resources'):
                app.cleanup_resources()
            
            # 데이터 매니저 정리
            if hasattr(app, 'data_manager'):
                app.data_manager.cleanup_resources()
            
            # 메모리 정리
            full_memory_cleanup()
            memory_monitor.log_memory_usage("종료 후")
            
            logger.info("Windows용 프로그램 종료 완료")
            root.destroy()
            
        except Exception as e:
            logger.error(f"종료 중 오류 발생: {str(e)}")
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

# 메인 애플리케이션 실행
def main():
    try:
        # 애플리케이션 초기화
        config, memory_monitor, logger = initialize_application()
        
        # 메인 윈도우 생성
        root = create_main_window(config)
        
        # 애플리케이션 생성
        app = create_application(root, memory_monitor, logger)
        
        # 정리 핸들러 설정
        setup_cleanup_handler(root, app, memory_monitor, logger)
        
        # 메모리 정리
        full_memory_cleanup()
        
        # 메인 루프 시작
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Windows용 애플리케이션 실행 중 오류가 발생했습니다:\\n{str(e)}"
        print(f"❌ {error_msg}")
        
        # GUI 오류 표시
        try:
            root = tk.Tk()
            root.withdraw()  # 메인 윈도우 숨기기
            messagebox.showerror("오류", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

def create_macos_main_content():
    """맥용 main.py 내용을 생성합니다."""
    
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dflux_InteractiveAnalyzer - 메인 실행 파일 (macOS용)
배포용으로 최적화됨 - 원본 구조 반영
"""

import os
import sys
import gc
import platform

# macOS 환경 확인
if platform.system() != "Darwin":
    print("⚠️  이 버전은 macOS용입니다. Windows/Linux용을 사용해주세요.")
    sys.exit(1)

# 소스 경로 추가 (배포용)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import messagebox

# 배포용으로 간소화된 import
try:
    from src.touch_analyzer.core.config import Config
    from src.touch_analyzer.utils.logging_utils import setup_logger
    from src.touch_analyzer.utils.memory_utils import MemoryMonitor, full_memory_cleanup
    from src.touch_analyzer.utils.path_manager import path_manager
except ImportError:
    # src 모듈이 없는 경우 기본 클래스들 정의
    class Config:
        def __init__(self):
            self.window_title = "dflux_InteractiveAnalyzer (macOS)"
            self.window_width = 1200
            self.window_height = 800
        
        @classmethod
        def default(cls):
            return cls()
        
        @classmethod
        def from_dict(cls, config_dict):
            return cls()
        
        def ensure_directories(self):
            pass
    
    def setup_logger(name, level='INFO'):
        import logging
        logging.basicConfig(level=getattr(logging, level.upper()))
        return logging.getLogger(name)
    
    class MemoryMonitor:
        def __init__(self, enable_monitoring=True, threshold_mb=1000.0):
            self.enable_monitoring = enable_monitoring
            self.threshold_mb = threshold_mb
        
        def log_memory_usage(self, message):
            pass
    
    def full_memory_cleanup():
        pass
    
    class path_manager:
        @staticmethod
        def get_data_dir():
            return os.path.join(os.path.dirname(__file__), 'data')

# 설정 로드
try:
    from config.settings import get_config
    config_dict = get_config()
except ImportError:
    try:
        from config import settings
        config_dict = settings.get_config()
    except ImportError:
        config_dict = {}

def initialize_application():
    """애플리케이션 초기화"""
    print("🚀 macOS용 dflux_InteractiveAnalyzer 초기화 시작")
    
    # 메모리 정리
    gc.collect()
    
    # 로거 설정
    logger = setup_logger("dflux_InteractiveAnalyzer")
    logger.info("macOS용 애플리케이션 초기화 시작")
    
    # 설정 로드
    config = Config.from_dict(config_dict)
    config.ensure_directories()
    
    # 메모리 모니터 설정
    memory_monitor = MemoryMonitor(
        enable_monitoring=True, 
        threshold_mb=config_dict.get('performance', {}).get('memory_threshold_mb', 1000.0)
    )
    memory_monitor.log_memory_usage("macOS용 애플리케이션 초기화")
    
    return config, memory_monitor, logger

def create_main_window(config):
    """메인 윈도우 생성"""
    root = tk.Tk()
    root.title(config.window_title)
    root.geometry(f"{config.window_width}x{config.window_height}")
    
    # macOS 스타일 적용
    try:
        # macOS에서 메뉴바 통합
        root.createcommand('tk::mac::Quit', root.quit)
        root.createcommand('tk::mac::OnHide', root.withdraw)
    except:
        pass
    
    # 윈도우 아이콘 설정 (선택사항)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass  # 아이콘 설정 실패는 무시
    
    return root

def create_application(root, memory_monitor, logger):
    """애플리케이션 인스턴스 생성"""
    try:
        # 대시보드 표시
        from interactive_visualizer import InteractiveVisualizer
        app = InteractiveVisualizer(root)
        
        # 메모리 모니터링 설정
        if hasattr(app, '_setup_memory_monitoring'):
            app._setup_memory_monitoring()
        
        return app
    except Exception as e:
        logger.error(f"애플리케이션 생성 실패: {str(e)}")
        raise

def setup_cleanup_handler(root, app, memory_monitor, logger):
    """정리 핸들러 설정"""
    def on_closing():
        """프로그램 종료 시 리소스 정리"""
        try:
            logger.info("macOS용 프로그램 종료 시작")
            memory_monitor.log_memory_usage("종료 전")
            
            # 애플리케이션 리소스 정리
            if hasattr(app, 'cleanup_resources'):
                app.cleanup_resources()
            
            # 데이터 매니저 정리
            if hasattr(app, 'data_manager'):
                app.data_manager.cleanup_resources()
            
            # 메모리 정리
            full_memory_cleanup()
            memory_monitor.log_memory_usage("종료 후")
            
            logger.info("macOS용 프로그램 종료 완료")
            root.destroy()
            
        except Exception as e:
            logger.error(f"종료 중 오류 발생: {str(e)}")
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

# 메인 애플리케이션 실행
def main():
    try:
        # 애플리케이션 초기화
        config, memory_monitor, logger = initialize_application()
        
        # 메인 윈도우 생성
        root = create_main_window(config)
        
        # 애플리케이션 생성
        app = create_application(root, memory_monitor, logger)
        
        # 정리 핸들러 설정
        setup_cleanup_handler(root, app, memory_monitor, logger)
        
        # 메모리 정리
        full_memory_cleanup()
        
        # 메인 루프 시작
        root.mainloop()
        
    except Exception as e:
        error_msg = f"macOS용 애플리케이션 실행 중 오류가 발생했습니다:\\n{str(e)}"
        print(f"❌ {error_msg}")
        
        # GUI 오류 표시
        try:
            root = tk.Tk()
            root.withdraw()  # 메인 윈도우 숨기기
            messagebox.showerror("오류", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

def create_platform_install_scripts(deployment_folder, platform_type):
    """플랫폼별 설치 및 실행 스크립트를 생성합니다."""
    
    if platform_type == "windows":
        create_windows_scripts(deployment_folder)
    else:
        create_macos_scripts(deployment_folder)

def create_windows_scripts(deployment_folder):
    """윈도우용 스크립트를 생성합니다."""
    
    # install.bat 생성
    install_bat = '''@echo off
chcp 65001 >nul
echo ========================================
echo   dflux_InteractiveAnalyzer 설치 스크립트
echo            Windows 전용 버전
echo ========================================
echo.
echo Python 가상환경을 생성하고 필요한 패키지를 설치합니다.
echo.

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    Python 3.8 이상을 먼저 설치해주세요.
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python 버전:
python --version
echo.

REM 가상환경 생성
echo 🔧 Python 가상환경 생성 중...
python -m venv touch_analyzer_env

if errorlevel 1 (
    echo ❌ 가상환경 생성에 실패했습니다.
    echo    관리자 권한으로 실행해보세요.
    pause
    exit /b 1
)

echo ✅ 가상환경 생성 완료
echo.

REM 가상환경 활성화
echo 🚀 가상환경 활성화 중...
call touch_analyzer_env\\Scripts\\activate.bat

if errorlevel 1 (
    echo ❌ 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

echo ✅ 가상환경 활성화 완료
echo.

REM pip 업그레이드
echo ⬆️  pip 업그레이드 중...
python -m pip install --upgrade pip

REM 필요한 패키지 설치
echo 📦 필요한 패키지 설치 중...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 패키지 설치에 실패했습니다.
    echo    인터넷 연결을 확인하고 다시 시도해보세요.
    pause
    exit /b 1
)

echo ✅ 모든 패키지 설치 완료!
echo.
echo 🎉 Windows용 설치가 완료되었습니다!
echo 이제 run.bat을 실행하여 애플리케이션을 시작할 수 있습니다.
echo.
pause
'''
    
    # run.bat 생성
    run_bat = '''@echo off
chcp 65001 >nul
echo ========================================
echo   dflux_InteractiveAnalyzer 실행 스크립트
echo            Windows 전용 버전
echo ========================================
echo.

REM 가상환경이 존재하는지 확인
if not exist "touch_analyzer_env" (
    echo ❌ 가상환경이 존재하지 않습니다.
    echo    먼저 install.bat을 실행해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 가상환경 확인됨
echo.

REM 가상환경 활성화
echo 🚀 가상환경 활성화 중...
call touch_analyzer_env\\Scripts\\activate.bat

if errorlevel 1 (
    echo ❌ 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

echo ✅ 가상환경 활성화 완료
echo.

REM 메모리 정리
echo 🧹 메모리 정리 중...
python -c "import gc; gc.collect()"

REM 애플리케이션 실행
echo 🚀 Windows용 애플리케이션 시작 중...
python main.py

REM 실행 완료 후 메모리 정리
echo 🧹 메모리 정리 중...
python -c "import gc; gc.collect()"

echo ✅ 애플리케이션 종료
echo.
pause
'''
    
    # 스크립트 파일 생성
    with open(os.path.join(deployment_folder, "install.bat"), "w", encoding="utf-8") as f:
        f.write(install_bat)
    
    with open(os.path.join(deployment_folder, "run.bat"), "w", encoding="utf-8") as f:
        f.write(run_bat)

def create_macos_scripts(deployment_folder):
    """맥용 스크립트를 생성합니다."""
    
    # install.sh 생성
    install_sh = '''#!/bin/bash

echo "========================================"
echo "  dflux_InteractiveAnalyzer 설치 스크립트"
echo "           macOS 전용 버전"
echo "========================================"
echo ""

echo "Python 가상환경을 생성하고 필요한 패키지를 설치합니다."
echo ""

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo "   Python 3.8 이상을 먼저 설치해주세요."
    echo "   https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "✅ Python3 버전: $(python3 --version)"
echo ""

# 가상환경 생성
echo "🔧 Python 가상환경 생성 중..."
python3 -m venv touch_analyzer_env

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성에 실패했습니다."
    echo "   권한 문제일 수 있습니다. sudo를 사용해보세요."
    exit 1
fi

echo "✅ 가상환경 생성 완료"
echo ""

# 가상환경 활성화
echo "🚀 가상환경 활성화 중..."
source touch_analyzer_env/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화에 실패했습니다."
    exit 1
fi

echo "✅ 가상환경 활성화 완료"
echo ""

# pip 업그레이드
echo "⬆️  pip 업그레이드 중..."
pip install --upgrade pip

# 필요한 패키지 설치
echo "📦 필요한 패키지 설치 중..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치에 실패했습니다."
    echo "   인터넷 연결을 확인하고 다시 시도해보세요."
    exit 1
fi

echo "✅ 모든 패키지 설치 완료!"
echo ""
echo "🎉 macOS용 설치가 완료되었습니다!"
echo "이제 ./run.sh를 실행하여 애플리케이션을 시작할 수 있습니다."
echo ""
'''
    
    # run.sh 생성
    run_sh = '''#!/bin/bash

echo "========================================"
echo "  dflux_InteractiveAnalyzer 실행 스크립트"
echo "           macOS 전용 버전"
echo "========================================"
echo ""

# 가상환경이 존재하는지 확인
if [ ! -d "touch_analyzer_env" ]; then
    echo "❌ 가상환경이 존재하지 않습니다."
    echo "   먼저 ./install.sh를 실행해주세요."
    echo ""
    exit 1
fi

echo "✅ 가상환경 확인됨"
echo ""

# 가상환경 활성화
echo "🚀 가상환경 활성화 중..."
source touch_analyzer_env/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화에 실패했습니다."
    exit 1
fi

echo "✅ 가상환경 활성화 완료"
echo ""

# 메모리 정리
echo "🧹 메모리 정리 중..."
python3 -c "import gc; gc.collect()"

# 애플리케이션 실행
echo "🚀 macOS용 애플리케이션 시작 중..."
python3 main.py

# 실행 완료 후 메모리 정리
echo "🧹 메모리 정리 중..."
python3 -c "import gc; gc.collect()"

echo "✅ 애플리케이션 종료"
echo ""
'''
    
    # 스크립트 파일 생성
    with open(os.path.join(deployment_folder, "install.sh"), "w", encoding="utf-8") as f:
        f.write(install_sh)
    
    with open(os.path.join(deployment_folder, "run.sh"), "w", encoding="utf-8") as f:
        f.write(run_sh)
    
    # 실행 권한 부여
    os.chmod(os.path.join(deployment_folder, "install.sh"), 0o755)
    os.chmod(os.path.join(deployment_folder, "run.sh"), 0o755)

def create_platform_deployment_guide(deployment_folder, platform_type):
    """플랫폼별 배포 가이드를 생성합니다."""
    
    if platform_type == "windows":
        guide_content = create_windows_guide_content()
        guide_filename = "Windows_배포_가이드.md"
    else:
        guide_content = create_macos_guide_content()
        guide_filename = "macOS_배포_가이드.md"
    
    with open(os.path.join(deployment_folder, guide_filename), "w", encoding="utf-8") as f:
        f.write(guide_content)

def create_windows_guide_content():
    """윈도우용 배포 가이드 내용을 생성합니다."""
    
    return '''# 🪟 dflux_InteractiveAnalyzer Windows 전용 배포 가이드

## 📋 시스템 요구사항

### 필수 요구사항
- **운영체제**: Windows 10 (버전 1903) 이상
- **Python**: 3.8 이상
- **메모리**: 최소 4GB RAM (권장 8GB+)
- **저장공간**: 최소 2GB 여유 공간
- **아키텍처**: x64 (64비트)

### 권장 사양
- **운영체제**: Windows 11
- **Python**: 3.9 - 3.11
- **메모리**: 8GB+ RAM
- **저장공간**: 5GB+ 여유 공간

---

## 🛠️ 설치 방법

### 1단계: Python 설치 확인
```cmd
python --version
```

**Python 3.8 이상이 설치되어 있어야 합니다.**

### 2단계: 설치 스크립트 실행
```cmd
# 관리자 권한으로 명령 프롬프트 실행 후
install.bat
```

### 3단계: 설치 완료 확인
- `touch_analyzer_env` 폴더가 생성되었는지 확인
- 오류 메시지가 없는지 확인

---

## 🚀 실행 방법

```cmd
run.bat
```

---

## 📁 폴더 구조

```
share_MMDD_Windows/
├── main.py                          # Windows 전용 메인 실행 파일
├── interactive_visualizer.py        # 핵심 시각화 모듈
├── base_visualizer.py              # 기본 시각화 클래스
├── requirements.txt                 # Python 패키지 의존성
├── setup.py                        # 설치 설정
├── README.md                       # 프로젝트 설명서
├── ARCHITECTURE.md                 # 아키텍처 문서
├── install.bat                     # Windows 설치 스크립트
├── run.bat                         # Windows 실행 스크립트
├── Windows_배포_가이드.md           # Windows 전용 가이드
├── config/                         # 설정 파일들
├── src/                            # 소스 코드
├── docs/                           # 문서
├── data_log/                       # 데이터 로그 저장 폴더 (빈 폴더)
└── data_bg/                        # 배경 이미지 저장 폴더 (빈 폴더)
```

---

## 🔑 Windows 전용 기능

### 🪟 Windows UI 최적화
- **전체화면 지원**: `state('zoomed')` 사용으로 Windows 전체화면
- **Windows 스타일**: Windows 네이티브 UI 요소 활용
- **고해상도 지원**: DPI 인식 및 스케일링 지원

### ⚡ 성능 최적화
- **Windows 메모리 관리**: Windows 전용 메모리 정리
- **프로세스 최적화**: Windows 환경에 최적화된 실행

---

## 🚨 Windows 전용 문제 해결

### 일반적인 문제들

#### 1. Python 가상환경 오류
```cmd
# 가상환경 재생성
rmdir /s touch_analyzer_env
install.bat
```

#### 2. 권한 오류
- **관리자 권한으로 실행**: 명령 프롬프트를 관리자 권한으로 실행
- **UAC 설정 확인**: 사용자 계정 컨트롤 설정 확인

#### 3. Python 경로 문제
```cmd
# Python 경로 확인
where python
# 환경 변수 PATH에 Python 경로 추가
```

#### 4. 가상환경 활성화 오류
```cmd
# 수동 활성화
touch_analyzer_env\\Scripts\\activate.bat
```

---

## 📞 Windows 전용 지원

### 문제 발생 시
1. **이벤트 뷰어 확인**: Windows 이벤트 로그에서 오류 확인
2. **관리자 권한**: 관리자 권한으로 재실행
3. **Python 재설치**: Python을 완전히 제거 후 재설치

### 추가 도움
- Windows 버전 및 빌드 번호 확인
- Python 설치 경로 및 환경 변수 확인
- 바이러스 백신 프로그램 일시 비활성화

---

## 🔄 업데이트

### 새 버전 설치
1. 기존 폴더 백업
2. 새 Windows용 배포 패키지 다운로드
3. `install.bat` 재실행

---

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

---

**🎉 Windows용 설치 및 실행이 완료되었습니다!**

이제 `run.bat`을 실행하여 애플리케이션을 시작할 수 있습니다.
'''

def create_macos_guide_content():
    """맥용 배포 가이드 내용을 생성합니다."""
    
    return '''# 🍎 dflux_InteractiveAnalyzer macOS 전용 배포 가이드

## 📋 시스템 요구사항

### 필수 요구사항
- **운영체제**: macOS 10.14 (Mojave) 이상
- **Python**: 3.8 이상
- **메모리**: 최소 4GB RAM (권장 8GB+)
- **저장공간**: 최소 2GB 여유 공간
- **아키텍처**: Intel 또는 Apple Silicon (M1/M2)

### 권장 사양
- **운영체제**: macOS 12 (Monterey) 이상
- **Python**: 3.9 - 3.11
- **메모리**: 8GB+ RAM
- **저장공간**: 5GB+ 여유 공간

---

## 🛠️ 설치 방법

### 1단계: Python 설치 확인
```bash
python3 --version
```

**Python 3.8 이상이 설치되어 있어야 합니다.**

### 2단계: 설치 스크립트 실행
```bash
# 터미널에서
chmod +x install.sh
./install.sh
```

### 3단계: 설치 완료 확인
- `touch_analyzer_env` 폴더가 생성되었는지 확인
- 오류 메시지가 없는지 확인

---

## 🚀 실행 방법

```bash
chmod +x run.sh
./run.sh
```

---

## 📁 폴더 구조

```
share_MMDD_macOS/
├── main.py                          # macOS 전용 메인 실행 파일
├── interactive_visualizer.py        # 핵심 시각화 모듈
├── base_visualizer.py              # 기본 시각화 클래스
├── requirements.txt                 # Python 패키지 의존성
├── setup.py                        # 설치 설정
├── README.md                       # 프로젝트 설명서
├── ARCHITECTURE.md                 # 아키텍처 문서
├── install.sh                      # macOS 설치 스크립트
├── run.sh                          # macOS 실행 스크립트
├── macOS_배포_가이드.md             # macOS 전용 가이드
├── config/                         # 설정 파일들
├── src/                            # 소스 코드
├── docs/                           # 문서
├── data_log/                       # 데이터 로그 저장 폴더 (빈 폴더)
└── data_bg/                        # 배경 이미지 저장 폴더 (빈 폴더)
```

---

## 🔑 macOS 전용 기능

### 🍎 macOS UI 최적화
- **메뉴바 통합**: macOS 네이티브 메뉴바와 통합
- **macOS 스타일**: macOS 네이티브 UI 요소 활용
- **Retina 디스플레이**: 고해상도 디스플레이 지원

### ⚡ 성능 최적화
- **macOS 메모리 관리**: macOS 전용 메모리 정리
- **프로세스 최적화**: macOS 환경에 최적화된 실행

---

## 🚨 macOS 전용 문제 해결

### 일반적인 문제들

#### 1. Python 가상환경 오류
```bash
# 가상환경 재생성
rm -rf touch_analyzer_env
./install.sh
```

#### 2. 권한 오류
```bash
# 실행 권한 부여
chmod +x *.sh
```

#### 3. Python 경로 문제
```bash
# Python 경로 확인
which python3
# Homebrew 사용 시
brew install python3
```

#### 4. 가상환경 활성화 오류
```bash
# 수동 활성화
source touch_analyzer_env/bin/activate
```

---

## 📞 macOS 전용 지원

### 문제 발생 시
1. **시스템 로그 확인**: Console.app에서 오류 확인
2. **권한 확인**: 보안 및 개인정보 보호 설정 확인
3. **Python 재설치**: Homebrew를 통한 Python 재설치

### 추가 도움
- macOS 버전 및 빌드 번호 확인
- Python 설치 경로 및 환경 변수 확인
- Gatekeeper 및 보안 설정 확인

---

## 🔄 업데이트

### 새 버전 설치
1. 기존 폴더 백업
2. 새 macOS용 배포 패키지 다운로드
3. `./install.sh` 재실행

---

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

---

**🎉 macOS용 설치 및 실행이 완료되었습니다!**

이제 `./run.sh`를 실행하여 애플리케이션을 시작할 수 있습니다.
'''

def create_platform_zip_packages(windows_folder, mac_folder, timestamp):
    """플랫폼별 ZIP 압축 파일을 생성합니다."""
    
    # 윈도우용 ZIP 생성
    windows_zip = f"{windows_folder}.zip"
    print(f"📦 윈도우용 ZIP 생성: {windows_zip}")
    create_zip_package(windows_folder, windows_zip)
    
    # 맥용 ZIP 생성
    mac_zip = f"{mac_folder}.zip"
    print(f"📦 맥용 ZIP 생성: {mac_zip}")
    create_zip_package(mac_folder, mac_zip)

def create_zip_package(deployment_folder, zip_filename):
    """ZIP 압축 파일을 생성합니다."""
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_folder)
                zipf.write(file_path, arcname)

def get_folder_size(folder_path):
    """폴더 크기를 MB 단위로 반환합니다."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size / (1024 * 1024)  # MB로 변환

def main():
    """메인 함수"""
    print("🚀 dflux_InteractiveAnalyzer 자동 배포 패키지 생성기")
    print("🪟 Windows용과 🍎 macOS용을 각각 생성합니다")
    print("=" * 70)
    
    try:
        success = create_deployment_package()
        if success:
            print("\n🎯 **모든 플랫폼용 배포 준비 완료!**")
            print("🪟 Windows용과 🍎 macOS용 폴더가 각각 생성되었습니다.")
            print("각 플랫폼에 맞는 폴더를 배포하거나 ZIP 파일을 전달할 수 있습니다.")
        else:
            print("\n❌ 배포 패키지 생성에 실패했습니다.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
