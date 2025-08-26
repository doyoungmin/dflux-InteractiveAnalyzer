#!/usr/bin/env python3
"""
dflux_InteractiveAnalyzer - 메인 진입점 (독립 실행 버전)
모듈화된 구조로 재구성된 버전 - 최적화된 버전
"""

import sys
import os
import gc

# 현재 스크립트의 디렉토리를 기준으로 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

import tkinter as tk
from src.touch_analyzer.core.config import Config
from src.touch_analyzer.utils.logging_utils import setup_logger
from src.touch_analyzer.utils.memory_utils import MemoryMonitor, full_memory_cleanup
from src.touch_analyzer.utils.path_manager import path_manager

# 설정 로드
try:
    from config.settings import get_config
    config_dict = get_config()
    config = Config.from_dict(config_dict)
except ImportError:
    # 기본 설정 사용
    config = Config.default()

# 로거 설정
logger = setup_logger('TouchAnalyzer', level=config_dict.get('logging', {}).get('level', 'INFO'))


def initialize_application():
    """애플리케이션 초기화"""
    logger.info("dflux_InteractiveAnalyzer 초기화 시작")
    
    # 필요한 디렉토리 생성
    config.ensure_directories()
    
    # 메모리 모니터 초기화
    memory_monitor = MemoryMonitor(
        enable_monitoring=True, 
        threshold_mb=config_dict.get('performance', {}).get('memory_threshold_mb', 1000.0)
    )
    memory_monitor.log_memory_usage("프로그램 시작")
    
    return memory_monitor


def create_main_window():
    """메인 윈도우 생성"""
    root = tk.Tk()
    root.title(config.window_title)
    root.geometry(f"{config.window_width}x{config.window_height}")
    
    # 윈도우 아이콘 설정 (선택사항)
    try:
        # 아이콘 파일이 있는 경우 설정
        icon_path = os.path.join(current_dir, 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass  # 아이콘 설정 실패는 무시
    
    return root


def create_application(root, memory_monitor):
    """애플리케이션 인스턴스 생성"""
    try:
        # 구 방식 임포트 (점진적 마이그레이션)
        from interactive_visualizer import InteractiveVisualizer
        app = InteractiveVisualizer(root)
        
        # 메모리 모니터링 설정
        if hasattr(app, '_setup_memory_monitoring'):
            app._setup_memory_monitoring()
        
        return app
    except Exception as e:
        logger.error(f"애플리케이션 생성 실패: {str(e)}")
        raise


def setup_cleanup_handler(root, app, memory_monitor):
    """정리 핸들러 설정"""
    def on_closing():
        """프로그램 종료 시 리소스 정리"""
        try:
            logger.info("프로그램 종료 시작")
            memory_monitor.log_memory_usage("종료 전")
            
            # 애플리케이션 리소스 정리
            if hasattr(app, 'cleanup_resources'):
                app.cleanup_resources()
            
            # 데이터 매니저 정리
            if hasattr(app, 'data_manager'):
                app.data_manager.cleanup_resources()
            
            # 전체 메모리 정리
            full_memory_cleanup()
            
            memory_monitor.log_memory_usage("정리 후")
            logger.info("리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"종료 시 오류: {str(e)}")
        finally:
            root.destroy()
    
    # 창 닫기 이벤트 바인딩
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Ctrl+C 핸들러 (Unix 시스템)
    def signal_handler(signum, frame):
        logger.info("시그널 수신, 프로그램 종료")
        on_closing()
    
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
    except ImportError:
        pass  # Windows에서는 signal 모듈이 제한적


def run_application(root):
    """애플리케이션 실행"""
    try:
        logger.info("GUI 시작")
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("사용자에 의한 중단")
    except Exception as e:
        logger.error(f"GUI 실행 중 오류: {str(e)}")
        raise


def main():
    """메인 함수 - 최적화된 버전"""
    memory_monitor = None
    root = None
    app = None
    
    try:
        # 애플리케이션 초기화
        memory_monitor = initialize_application()
        
        # 메인 윈도우 생성
        root = create_main_window()
        
        # 애플리케이션 생성
        app = create_application(root, memory_monitor)
        
        # 정리 핸들러 설정
        setup_cleanup_handler(root, app, memory_monitor)
        
        # 애플리케이션 실행
        run_application(root)
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {str(e)}")
        raise
    finally:
        # 최종 정리
        try:
            if memory_monitor:
                memory_monitor.log_memory_usage("프로그램 종료")
            
            # 강제 메모리 정리
            gc.collect()
            
            logger.info("dflux_InteractiveAnalyzer 종료")
        except Exception as e:
            logger.error(f"종료 시 최종 정리 실패: {str(e)}")


if __name__ == "__main__":
    main()
