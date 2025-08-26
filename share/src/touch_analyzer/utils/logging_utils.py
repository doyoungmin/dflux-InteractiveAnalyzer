"""
로깅 유틸리티
"""

import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logger(
    name: str = __name__,
    level: str = "INFO",
    log_format: str = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        level: 로그 레벨
        log_format: 로그 형식
        log_file: 로그 파일 경로 (선택사항)
        
    Returns:
        logging.Logger: 설정된 로거
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포매터 생성
    formatter = logging.Formatter(log_format)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (선택사항)
    if log_file:
        # 로그 디렉토리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_log_level_from_string(level_str: str) -> int:
    """
    문자열에서 로그 레벨 변환
    
    Args:
        level_str: 로그 레벨 문자열
        
    Returns:
        int: 로그 레벨
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return level_map.get(level_str.upper(), logging.INFO)


def log_function_call(func):
    """
    함수 호출 로깅 데코레이터
    
    Args:
        func: 데코레이트할 함수
        
    Returns:
        function: 래핑된 함수
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"함수 호출: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"함수 완료: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"함수 오류: {func.__name__} - {str(e)}")
            raise
    
    return wrapper


def log_execution_time(func):
    """
    함수 실행 시간 로깅 데코레이터
    
    Args:
        func: 데코레이트할 함수
        
    Returns:
        function: 래핑된 함수
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"함수 실행 시간: {func.__name__} - {execution_time:.3f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"함수 오류 (실행 시간: {execution_time:.3f}초): {func.__name__} - {str(e)}")
            raise
    
    return wrapper


class LoggingContext:
    """로깅 컨텍스트 매니저"""
    
    def __init__(self, logger: logging.Logger, message: str, level: int = logging.INFO):
        """
        로깅 컨텍스트 초기화
        
        Args:
            logger: 로거 객체
            message: 로그 메시지
            level: 로그 레벨
        """
        self.logger = logger
        self.message = message
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.log(self.level, f"시작: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.log(self.level, f"완료: {self.message} (소요시간: {duration:.3f}초)")
        else:
            self.logger.error(f"오류: {self.message} (소요시간: {duration:.3f}초) - {exc_val}")
        
        return False
