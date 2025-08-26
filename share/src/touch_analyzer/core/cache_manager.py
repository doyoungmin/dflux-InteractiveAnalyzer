"""
캐시 관리 모듈 - 최적화된 버전
LRU 방식의 메모리 캐시 관리
"""

import time
import logging
from typing import Optional, Dict, Any, Tuple
from collections import OrderedDict
import gc

logger = logging.getLogger(__name__)


class CacheManager:
    """최적화된 LRU 캐시 매니저"""
    
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        """
        캐시 매니저 초기화
        
        Args:
            max_size: 최대 캐시 크기
            ttl_seconds: 캐시 항목의 수명 (초)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._access_count: Dict[str, int] = {}
        self._total_hits = 0
        self._total_misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 조회 (TTL 및 접근 통계 포함)
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[Any]: 캐시된 값 또는 None
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            current_time = time.time()
            
            # TTL 확인
            if current_time - timestamp > self.ttl_seconds:
                # 만료된 항목 제거
                del self._cache[key]
                if key in self._access_count:
                    del self._access_count[key]
                logger.debug(f"캐시 만료: {key}")
                self._total_misses += 1
                return None
            
            # LRU: 사용된 항목을 맨 뒤로 이동
            self._cache.move_to_end(key)
            self._access_count[key] = self._access_count.get(key, 0) + 1
            self._total_hits += 1
            
            logger.debug(f"캐시 히트: {key}")
            return value
        
        self._total_misses += 1
        logger.debug(f"캐시 미스: {key}")
        return None
    
    def put(self, key: str, value: Any) -> None:
        """
        캐시에 값 저장 (메모리 최적화 포함)
        
        Args:
            key: 캐시 키
            value: 저장할 값
        """
        current_time = time.time()
        
        if key in self._cache:
            # 기존 키 업데이트
            self._cache.pop(key)
            logger.debug(f"캐시 업데이트: {key}")
        elif len(self._cache) >= self.max_size:
            # 캐시 크기 초과 시 가장 오래된 항목 제거
            oldest_key, _ = self._cache.popitem(last=False)
            if oldest_key in self._access_count:
                del self._access_count[oldest_key]
            logger.debug(f"캐시 제거 (LRU): {oldest_key}")
        
        # 메모리 사용량이 큰 객체는 복사본 저장
        if hasattr(value, 'copy'):
            try:
                cached_value = value.copy()
            except Exception:
                cached_value = value
        else:
            cached_value = value
        
        self._cache[key] = (cached_value, current_time)
        self._access_count[key] = 0
        logger.debug(f"캐시 저장: {key}")
    
    def clear(self) -> None:
        """캐시 전체 클리어"""
        cache_size = len(self._cache)
        self._cache.clear()
        self._access_count.clear()
        self._total_hits = 0
        self._total_misses = 0
        gc.collect()  # 가비지 컬렉션 강제 실행
        logger.info(f"캐시 클리어 완료: {cache_size}개 항목 제거")
    
    def size(self) -> int:
        """현재 캐시 크기 반환"""
        return len(self._cache)
    
    def is_full(self) -> bool:
        """캐시가 가득 찼는지 확인"""
        return len(self._cache) >= self.max_size
    
    def get_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 정보 반환
        
        Returns:
            Dict[str, Any]: 캐시 통계 정보
        """
        total_requests = self._total_hits + self._total_misses
        hit_rate = (self._total_hits / total_requests * 100) if total_requests > 0 else 0
        
        # 가장 자주 접근된 항목들
        top_accessed = sorted(
            self._access_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'total_hits': self._total_hits,
            'total_misses': self._total_misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds,
            'top_accessed': top_accessed
        }
    
    def cleanup_expired(self) -> int:
        """
        만료된 캐시 항목들을 정리
        
        Returns:
            int: 정리된 항목 수
        """
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp) in self._cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            if key in self._access_count:
                del self._access_count[key]
        
        if expired_keys:
            logger.debug(f"만료된 캐시 항목 정리: {len(expired_keys)}개")
        
        return len(expired_keys)
    
    def get_memory_usage_estimate(self) -> int:
        """
        캐시 메모리 사용량 추정 (바이트)
        
        Returns:
            int: 추정 메모리 사용량 (바이트)
        """
        total_size = 0
        
        for key, (value, timestamp) in self._cache.items():
            # 키 크기
            total_size += len(key.encode('utf-8'))
            
            # 값 크기 추정
            if hasattr(value, '__sizeof__'):
                total_size += value.__sizeof__()
            elif hasattr(value, 'memory_usage'):
                # pandas DataFrame의 경우
                total_size += value.memory_usage(deep=True).sum()
            else:
                # 기본 추정
                total_size += 1000  # 기본 1KB 추정
        
        return total_size
    
    def optimize_memory(self, target_size_mb: float = 100.0) -> None:
        """
        메모리 사용량 최적화
        
        Args:
            target_size_mb: 목표 메모리 크기 (MB)
        """
        current_memory_mb = self.get_memory_usage_estimate() / 1024 / 1024
        
        if current_memory_mb > target_size_mb:
            # 메모리 사용량이 목표를 초과한 경우
            items_to_remove = int(len(self._cache) * 0.3)  # 30% 제거
            
            # 가장 오래된 항목들 제거
            for _ in range(items_to_remove):
                if self._cache:
                    oldest_key, _ = self._cache.popitem(last=False)
                    if oldest_key in self._access_count:
                        del self._access_count[oldest_key]
            
            gc.collect()  # 가비지 컬렉션 강제 실행
            logger.info(f"메모리 최적화 완료: {items_to_remove}개 항목 제거")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        상세 캐시 정보 반환
        
        Returns:
            Dict[str, Any]: 상세 캐시 정보
        """
        stats = self.get_stats()
        stats.update({
            'memory_usage_mb': self.get_memory_usage_estimate() / 1024 / 1024,
            'expired_items': self.cleanup_expired()
        })
        return stats
