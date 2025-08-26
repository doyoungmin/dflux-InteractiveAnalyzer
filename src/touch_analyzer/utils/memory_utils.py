"""
메모리 관리 유틸리티 - 최적화된 버전
"""

import os
import gc
import logging
from typing import Optional, Dict, Any
import weakref

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """최적화된 메모리 사용량 모니터링 클래스"""
    
    def __init__(self, enable_monitoring: bool = True, threshold_mb: float = 1000.0):
        """
        메모리 모니터 초기화
        
        Args:
            enable_monitoring: 모니터링 활성화 여부
            threshold_mb: 메모리 임계값 (MB)
        """
        self.enable_monitoring = enable_monitoring
        self.threshold_mb = threshold_mb
        self._psutil_available = False
        self._memory_history = []
        self._max_history_size = 10
        
        if self.enable_monitoring:
            try:
                import psutil
                self._psutil_available = True
                self._process = psutil.Process(os.getpid())
            except ImportError:
                logger.debug("psutil이 설치되지 않아 메모리 모니터링을 비활성화합니다.")
    
    def get_memory_usage(self) -> Optional[float]:
        """
        현재 메모리 사용량 반환 (MB)
        
        Returns:
            Optional[float]: 메모리 사용량 (MB) 또는 None
        """
        if not self._psutil_available:
            return None
        
        try:
            import psutil
            memory_info = self._process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # 메모리 히스토리 업데이트
            self._memory_history.append(memory_mb)
            if len(self._memory_history) > self._max_history_size:
                self._memory_history.pop(0)
            
            return memory_mb
        except Exception:
            return None
    
    def get_memory_percent(self) -> Optional[float]:
        """
        메모리 사용율 반환 (%)
        
        Returns:
            Optional[float]: 메모리 사용율 (%) 또는 None
        """
        if not self._psutil_available:
            return None
        
        try:
            return self._process.memory_percent()
        except Exception:
            return None
    
    def get_system_memory_info(self) -> Optional[Dict[str, float]]:
        """
        시스템 메모리 정보 반환
        
        Returns:
            Optional[Dict[str, float]]: 시스템 메모리 정보 또는 None
        """
        if not self._psutil_available:
            return None
        
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / 1024 / 1024 / 1024,
                'available_gb': memory.available / 1024 / 1024 / 1024,
                'used_gb': memory.used / 1024 / 1024 / 1024,
                'percent': memory.percent
            }
        except Exception:
            return None
    
    def log_memory_usage(self, context: str = ""):
        """
        메모리 사용량 로깅
        
        Args:
            context: 로그 컨텍스트
        """
        if not self.enable_monitoring:
            return
        
        memory_mb = self.get_memory_usage()
        if memory_mb is not None:
            context_str = f" ({context})" if context else ""
            logger.debug(f"메모리 사용량{context_str}: {memory_mb:.1f} MB")
            
            # 임계값 초과 시 경고
            if memory_mb > self.threshold_mb:
                logger.warning(f"메모리 사용량이 임계값({self.threshold_mb:.1f} MB)을 초과했습니다: {memory_mb:.1f} MB")
    
    def check_memory_threshold(self, threshold_mb: float = None) -> bool:
        """
        메모리 사용량이 임계값을 초과했는지 확인
        
        Args:
            threshold_mb: 임계값 (MB), None이면 기본값 사용
            
        Returns:
            bool: 임계값 초과 여부
        """
        if threshold_mb is None:
            threshold_mb = self.threshold_mb
            
        memory_mb = self.get_memory_usage()
        if memory_mb is None:
            return False
        
        return memory_mb > threshold_mb
    
    def get_memory_trend(self) -> Optional[Dict[str, float]]:
        """
        메모리 사용량 트렌드 분석
        
        Returns:
            Optional[Dict[str, float]]: 메모리 트렌드 정보
        """
        if len(self._memory_history) < 2:
            return None
        
        current = self._memory_history[-1]
        previous = self._memory_history[-2]
        change = current - previous
        change_percent = (change / previous * 100) if previous > 0 else 0
        
        return {
            'current_mb': current,
            'change_mb': change,
            'change_percent': change_percent,
            'trend': 'increasing' if change > 0 else 'decreasing' if change < 0 else 'stable'
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        메모리 통계 정보 반환
        
        Returns:
            Dict[str, Any]: 메모리 통계 정보
        """
        stats = {
            'monitoring_enabled': self.enable_monitoring,
            'psutil_available': self._psutil_available,
            'threshold_mb': self.threshold_mb
        }
        
        if self._psutil_available:
            stats.update({
                'process_memory_mb': self.get_memory_usage(),
                'process_memory_percent': self.get_memory_percent(),
                'system_memory': self.get_system_memory_info(),
                'memory_trend': self.get_memory_trend()
            })
        
        return stats


def cleanup_matplotlib_memory():
    """matplotlib 메모리 정리 - 최적화된 버전"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        
        # 모든 figure 닫기
        plt.close('all')
        
        # matplotlib 백엔드 정리
        if hasattr(matplotlib, 'backends'):
            for backend in dir(matplotlib.backends):
                if hasattr(matplotlib.backends, backend):
                    backend_obj = getattr(matplotlib.backends, backend)
                    if hasattr(backend_obj, 'FigureCanvas'):
                        canvas_class = backend_obj.FigureCanvas
                        if hasattr(canvas_class, '_cleanup'):
                            canvas_class._cleanup()
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        logger.debug("matplotlib 메모리 정리 완료")
    except Exception as e:
        logger.warning(f"matplotlib 메모리 정리 실패: {str(e)}")


def cleanup_pandas_memory():
    """pandas 메모리 정리 - 최적화된 버전"""
    try:
        import pandas as pd
        
        # pandas 내부 캐시 정리
        if hasattr(pd, '_libs'):
            for lib_name in dir(pd._libs):
                lib_obj = getattr(pd._libs, lib_name)
                if hasattr(lib_obj, 'clear_cache'):
                    lib_obj.clear_cache()
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        logger.debug("pandas 메모리 정리 완료")
    except Exception as e:
        logger.warning(f"pandas 메모리 정리 실패: {str(e)}")


def cleanup_tkinter_memory():
    """tkinter 메모리 정리"""
    try:
        import tkinter as tk
        
        # 모든 tkinter 윈도우 정리
        for widget in tk.Tk().winfo_children():
            widget.destroy()
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        logger.debug("tkinter 메모리 정리 완료")
    except Exception as e:
        logger.warning(f"tkinter 메모리 정리 실패: {str(e)}")


def full_memory_cleanup():
    """전체 메모리 정리 - 최적화된 버전"""
    logger.info("전체 메모리 정리 시작")
    
    # 각 모듈별 메모리 정리
    cleanup_matplotlib_memory()
    cleanup_pandas_memory()
    cleanup_tkinter_memory()
    
    # 최종 가비지 컬렉션
    collected = gc.collect()
    logger.info(f"가비지 컬렉션 완료: {collected}개 객체 정리됨")
    
    # 메모리 사용량 확인
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"정리 후 메모리 사용량: {memory_mb:.1f} MB")
    except ImportError:
        pass


def optimize_dataframe_memory(df):
    """
    데이터프레임 메모리 최적화
    
    Args:
        df: pandas DataFrame
        
    Returns:
        pandas DataFrame: 최적화된 DataFrame
    """
    try:
        import pandas as pd
        
        # 데이터 타입 최적화
        for col in df.columns:
            if df[col].dtype == 'object':
                # 문자열 컬럼 최적화
                if df[col].nunique() / len(df) < 0.5:  # 카테고리형으로 변환 가능한 경우
                    df[col] = df[col].astype('category')
            elif df[col].dtype in ['int64', 'float64']:
                # 수치형 컬럼 최적화
                if df[col].dtype == 'int64':
                    df[col] = pd.to_numeric(df[col], downcast='integer')
                else:
                    df[col] = pd.to_numeric(df[col], downcast='float')
        
        logger.debug("데이터프레임 메모리 최적화 완료")
        return df
    except Exception as e:
        logger.warning(f"데이터프레임 메모리 최적화 실패: {str(e)}")
        return df
