#!/usr/bin/env python3
"""
dflux_InteractiveAnalyzer - 설치 테스트 스크립트
이 스크립트는 필요한 라이브러리들이 올바르게 설치되었는지 확인합니다.
"""

import sys
import os

def test_imports():
    """필요한 라이브러리 import 테스트"""
    print("=== 라이브러리 설치 확인 ===")
    
    # 핵심 라이브러리 테스트
    libraries = [
        ('tkinter', 'GUI 프레임워크'),
        ('numpy', '수치 계산'),
        ('pandas', '데이터 처리'),
        ('matplotlib', '시각화'),
        ('PIL', '이미지 처리'),
        ('psutil', '시스템 모니터링'),
    ]
    
    failed_imports = []
    
    for lib_name, description in libraries:
        try:
            if lib_name == 'tkinter':
                import tkinter
            elif lib_name == 'PIL':
                from PIL import Image
            else:
                __import__(lib_name)
            print(f"✅ {lib_name} - {description}")
        except ImportError as e:
            print(f"❌ {lib_name} - {description} (오류: {e})")
            failed_imports.append(lib_name)
    
    return failed_imports

def test_project_modules():
    """프로젝트 모듈 테스트"""
    print("\n=== 프로젝트 모듈 확인 ===")
    
    # 현재 디렉토리를 Python 경로에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'src'))
    
    modules = [
        ('src.touch_analyzer.core.config', '설정 관리'),
        ('src.touch_analyzer.utils.logging_utils', '로깅 유틸리티'),
        ('src.touch_analyzer.utils.memory_utils', '메모리 관리'),
        ('src.touch_analyzer.utils.path_manager', '경로 관리'),
        ('base_visualizer', '기본 시각화'),
        ('interactive_visualizer', '인터랙티브 시각화'),
    ]
    
    failed_modules = []
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError as e:
            print(f"❌ {module_name} - {description} (오류: {e})")
            failed_modules.append(module_name)
    
    return failed_modules

def test_config():
    """설정 파일 테스트"""
    print("\n=== 설정 파일 확인 ===")
    
    try:
        from config.settings import get_config
        config = get_config()
        print("✅ 설정 파일 로드 성공")
        print(f"   - 윈도우 크기: {config.get('window', {}).get('width', 'N/A')}x{config.get('window', {}).get('height', 'N/A')}")
        print(f"   - 메모리 임계값: {config.get('performance', {}).get('memory_threshold_mb', 'N/A')}MB")
        return []
    except Exception as e:
        print(f"❌ 설정 파일 로드 실패 (오류: {e})")
        return ['config']

def main():
    """메인 테스트 함수"""
    print("dflux_InteractiveAnalyzer 설치 테스트")
    print("=" * 50)
    
    # Python 버전 확인
    python_version = sys.version_info
    print(f"Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        return False
    else:
        print("✅ Python 버전 확인 완료")
    
    # 라이브러리 테스트
    failed_libs = test_imports()
    
    # 프로젝트 모듈 테스트
    failed_modules = test_project_modules()
    
    # 설정 테스트
    failed_config = test_config()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약:")
    
    if not failed_libs and not failed_modules and not failed_config:
        print("✅ 모든 테스트 통과!")
        print("\n프로그램을 실행할 수 있습니다:")
        print("- Windows: run.bat 또는 python main.py")
        print("- macOS/Linux: ./run.sh 또는 python3 main.py")
        return True
    else:
        print("❌ 일부 테스트 실패")
        
        if failed_libs:
            print(f"\n실패한 라이브러리: {', '.join(failed_libs)}")
            print("해결 방법: pip install -r requirements.txt")
        
        if failed_modules:
            print(f"\n실패한 모듈: {', '.join(failed_modules)}")
            print("해결 방법: 프로젝트 파일이 올바른 위치에 있는지 확인")
        
        if failed_config:
            print(f"\n실패한 설정: {', '.join(failed_config)}")
            print("해결 방법: config 폴더와 파일이 올바른 위치에 있는지 확인")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

