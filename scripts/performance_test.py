#!/usr/bin/env python3
"""
성능 테스트 스크립트
dflux_InteractiveAnalyzer의 최적화 효과를 측정
"""

import os
import sys
import time
import psutil
import logging
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.touch_analyzer.core.config import Config
from src.touch_analyzer.core.data_manager import DataManager
from src.touch_analyzer.utils.memory_utils import MemoryMonitor, optimize_dataframe_memory
from src.touch_analyzer.core.cache_manager import CacheManager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PerformanceTester:
    """성능 테스트 클래스"""
    
    def __init__(self):
        self.config = Config.default()
        self.memory_monitor = MemoryMonitor(enable_monitoring=True)
        self.data_manager = DataManager(self.config)
        self.cache_manager = CacheManager(max_size=15)
        
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        logger.info("=== 메모리 사용량 테스트 시작 ===")
        
        initial_memory = self.memory_monitor.get_memory_usage()
        logger.info(f"초기 메모리 사용량: {initial_memory:.1f} MB")
        
        # 데이터 로드 테스트
        test_files = self._get_test_files()
        if not test_files:
            logger.warning("테스트 파일이 없습니다.")
            return
        
        start_time = time.time()
        combined_data = self.data_manager.load_and_combine_data(test_files[:3])
        load_time = time.time() - start_time
        
        if combined_data is not None:
            memory_after_load = self.memory_monitor.get_memory_usage()
            memory_increase = memory_after_load - initial_memory if initial_memory else 0
            
            logger.info(f"데이터 로드 시간: {load_time:.2f}초")
            logger.info(f"로드 후 메모리: {memory_after_load:.1f} MB")
            logger.info(f"메모리 증가량: {memory_increase:.1f} MB")
            logger.info(f"데이터 크기: {len(combined_data)} 행")
            
            # 메모리 정리 테스트
            self.data_manager.clear_cache()
            memory_after_cleanup = self.memory_monitor.get_memory_usage()
            cleanup_reduction = memory_after_load - memory_after_cleanup if memory_after_load else 0
            
            logger.info(f"정리 후 메모리: {memory_after_cleanup:.1f} MB")
            logger.info(f"정리로 인한 감소: {cleanup_reduction:.1f} MB")
    
    def test_cache_performance(self):
        """캐시 성능 테스트"""
        logger.info("=== 캐시 성능 테스트 시작 ===")
        
        # 캐시 저장 테스트
        test_data = {"test_key": "test_value"}
        
        start_time = time.time()
        for i in range(100):
            self.cache_manager.put(f"key_{i}", test_data)
        put_time = time.time() - start_time
        
        # 캐시 조회 테스트
        start_time = time.time()
        for i in range(100):
            self.cache_manager.get(f"key_{i}")
        get_time = time.time() - start_time
        
        # 캐시 통계
        stats = self.cache_manager.get_stats()
        
        logger.info(f"캐시 저장 시간 (100회): {put_time:.4f}초")
        logger.info(f"캐시 조회 시간 (100회): {get_time:.4f}초")
        logger.info(f"캐시 히트율: {stats['hit_rate']:.1f}%")
        logger.info(f"캐시 크기: {stats['size']}/{stats['max_size']}")
    
    def test_data_optimization(self):
        """데이터 최적화 테스트"""
        logger.info("=== 데이터 최적화 테스트 시작 ===")
        
        import pandas as pd
        import numpy as np
        
        # 테스트 데이터 생성
        test_data = pd.DataFrame({
            'Time(ms)': np.random.randint(0, 10000, 10000),
            'TouchX': np.random.uniform(0, 3840, 10000),
            'TouchY': np.random.uniform(0, 850, 10000),
            'Layer Name': np.random.choice(['Button1', 'Button2', 'Slider'], 10000)
        })
        
        # 최적화 전 메모리 사용량
        memory_before = test_data.memory_usage(deep=True).sum() / 1024 / 1024
        
        # 최적화 적용
        start_time = time.time()
        optimized_data = optimize_dataframe_memory(test_data)
        optimization_time = time.time() - start_time
        
        # 최적화 후 메모리 사용량
        memory_after = optimized_data.memory_usage(deep=True).sum() / 1024 / 1024
        memory_reduction = memory_before - memory_after
        
        logger.info(f"최적화 전 메모리: {memory_before:.2f} MB")
        logger.info(f"최적화 후 메모리: {memory_after:.2f} MB")
        logger.info(f"메모리 감소량: {memory_reduction:.2f} MB ({memory_reduction/memory_before*100:.1f}%)")
        logger.info(f"최적화 시간: {optimization_time:.4f}초")
    
    def test_file_loading_performance(self):
        """파일 로딩 성능 테스트"""
        logger.info("=== 파일 로딩 성능 테스트 시작 ===")
        
        test_files = self._get_test_files()
        if not test_files:
            logger.warning("테스트 파일이 없습니다.")
            return
        
        # 개별 파일 로딩 테스트
        for i, file_path in enumerate(test_files[:3]):
            logger.info(f"파일 {i+1} 로딩 테스트: {os.path.basename(file_path)}")
            
            start_time = time.time()
            df = self.data_manager.load_file(file_path)
            load_time = time.time() - start_time
            
            if df is not None:
                memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
                logger.info(f"  로딩 시간: {load_time:.2f}초")
                logger.info(f"  데이터 크기: {len(df)} 행")
                logger.info(f"  메모리 사용량: {memory_usage:.2f} MB")
            else:
                logger.warning(f"  파일 로딩 실패")
    
    def _get_test_files(self):
        """테스트용 파일 목록 반환"""
        data_dir = self.config.data_dir
        test_files = []
        
        if os.path.exists(data_dir):
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.csv'):
                        test_files.append(os.path.join(root, file))
        
        return test_files[:5]  # 최대 5개 파일만 테스트
    
    def run_all_tests(self):
        """모든 성능 테스트 실행"""
        logger.info("🚀 dflux_InteractiveAnalyzer 성능 테스트 시작")
        
        try:
            self.test_memory_usage()
            print()
            
            self.test_cache_performance()
            print()
            
            self.test_data_optimization()
            print()
            
            self.test_file_loading_performance()
            print()
            
            logger.info("✅ 모든 성능 테스트 완료")
            
        except Exception as e:
            logger.error(f"성능 테스트 중 오류 발생: {str(e)}")


def main():
    """메인 함수"""
    tester = PerformanceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
