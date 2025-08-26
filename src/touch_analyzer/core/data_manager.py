"""
데이터 관리 모듈 - 최적화된 버전
CSV 파일 로딩, 데이터 검증, 변환 등을 담당
"""

import os
import glob
from typing import List, Optional, Dict, Set, Tuple, Any
import pandas as pd
import logging
import gc

from .cache_manager import CacheManager
from .config import Config
from ..utils.memory_utils import optimize_dataframe_memory

logger = logging.getLogger(__name__)


class DataManager:
    """최적화된 터치 데이터 관리 클래스"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_manager = CacheManager(config.max_cache_size)
        self.data: Dict[str, pd.DataFrame] = {}
        self._file_metadata_cache = {}  # 파일 메타데이터 캐시
        
    def get_user_list(self) -> List[str]:
        """
        사용자 목록을 반환 (캐시 최적화)
        
        Returns:
            List[str]: 정렬된 사용자 이름 목록
        """
        cache_key = "user_list"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        users = []
        data_folder = self.config.data_dir
        
        if not os.path.exists(data_folder):
            return users
            
        try:
            for item in os.listdir(data_folder):
                item_path = os.path.join(data_folder, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    users.append(item)
            
            users = sorted(users)
            self.cache_manager.put(cache_key, users)
            return users
        except Exception as e:
            logger.error(f"사용자 목록 조회 실패: {str(e)}")
            return []
    
    def get_max_task_count(self) -> int:
        """
        사용 가능한 최대 task 수를 반환 (최적화된 버전)
        
        Returns:
            int: 최대 task 수
        """
        cache_key = "max_task_count"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        max_tasks = 0
        data_folder = self.config.data_dir
        
        if not os.path.exists(data_folder):
            return 0
            
        try:
            user_folders = []
            for item in os.listdir(data_folder):
                item_path = os.path.join(data_folder, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    user_folders.append(item)
            
            if not user_folders:
                # 루트 레벨에 CSV 파일이 있는 경우
                csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
                max_tasks = len(csv_files)
            else:
                # 사용자별 폴더에서 최대 task 수 계산
                for user_folder in user_folders:
                    user_path = os.path.join(data_folder, user_folder)
                    csv_files = glob.glob(os.path.join(user_path, "*.csv"))
                    sorted_files = self._sort_files_by_time(csv_files)
                    max_tasks = max(max_tasks, len(sorted_files))
            
            self.cache_manager.put(cache_key, max_tasks)
            return max_tasks
        except Exception as e:
            logger.error(f"최대 task 수 조회 실패: {str(e)}")
            return 0
    
    def _extract_time_from_filename(self, filename: str) -> str:
        """
        파일명에서 시간 정보 추출 (마지막 6자리 숫자)
        
        Args:
            filename: 파일명
            
        Returns:
            str: 시간 정보 (6자리 숫자)
        """
        basename = os.path.basename(filename)
        # 파일명에서 마지막 6자리 숫자 추출
        # 예: ks_drag_0803-121820.csv -> 121820
        parts = basename.split('-')
        if len(parts) > 1:
            time_part = parts[-1].split('.')[0]  # .csv 제거
            if len(time_part) == 6 and time_part.isdigit():
                return time_part
        return "000000"  # 기본값
    
    def _sort_files_by_time(self, file_list: List[str]) -> List[str]:
        """
        파일들을 시간순으로 정렬 (마지막 6자리 숫자 기준)
        
        Args:
            file_list: 파일 경로 목록
            
        Returns:
            List[str]: 정렬된 파일 경로 목록
        """
        return sorted(file_list, key=self._extract_time_from_filename)
    
    def get_task_files_for_users(self, task_num: int, users: List[str]) -> List[str]:
        """
        특정 사용자들의 task 번호에 해당하는 파일들을 반환 (최적화된 버전)
        
        Args:
            task_num: task 번호
            users: 사용자 목록
            
        Returns:
            List[str]: 파일 경로 목록
        """
        cache_key = f"task_files_{task_num}_{'_'.join(sorted(users))}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        file_paths = []
        data_folder = self.config.data_dir
        
        try:
            for user in users:
                user_folder = os.path.join(data_folder, user)
                if os.path.exists(user_folder):
                    csv_files = glob.glob(os.path.join(user_folder, "*.csv"))
                    sorted_files = self._sort_files_by_time(csv_files)
                    
                    # task_num에 해당하는 파일 선택 (1-based indexing)
                    if 1 <= task_num <= len(sorted_files):
                        file_paths.append(sorted_files[task_num - 1])
            
            self.cache_manager.put(cache_key, file_paths)
            return file_paths
        except Exception as e:
            logger.error(f"task 파일 조회 실패: {str(e)}")
            return []
    
    def load_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        단일 파일 로드 (최적화된 버전)
        
        Args:
            file_path: 파일 경로
            
        Returns:
            Optional[pd.DataFrame]: 로드된 데이터프레임 또는 None
        """
        if not os.path.exists(file_path):
            logger.warning(f"파일이 존재하지 않습니다: {file_path}")
            return None
        
        try:
            # 파일 메타데이터 캐시 확인
            file_stat = os.stat(file_path)
            cache_key = f"file_{file_path}_{file_stat.st_mtime}"
            
            cached_df = self.cache_manager.get(cache_key)
            if cached_df is not None:
                logger.debug(f"캐시에서 파일 로드: {file_path}")
                return cached_df.copy()
            
            # 파일 로드
            logger.debug(f"파일 로드 시작: {file_path}")
            df = pd.read_csv(file_path)
            
            # 데이터 검증
            required_columns = self.config.required_columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.warning(f"필수 컬럼이 누락되었습니다: {missing_columns}")
                return None
            
            # 데이터 최적화
            df = self._optimize_dataframe(df)
            
            # 캐시에 저장
            self.cache_manager.put(cache_key, df.copy())
            
            logger.debug(f"파일 로드 완료: {file_path} ({len(df)} 행)")
            return df
            
        except Exception as e:
            logger.error(f"파일 로드 실패: {file_path}, 오류: {str(e)}")
            return None
    
    def load_and_combine_data(self, file_paths: List[str]) -> Optional[pd.DataFrame]:
        """
        여러 파일을 로드하고 합치는 공통 로직 (메모리 최적화)
        
        Args:
            file_paths: 파일 경로 목록
            
        Returns:
            Optional[pd.DataFrame]: 합쳐진 데이터프레임 또는 None
        """
        if not file_paths:
            return None
        
        try:
            # 캐시 키 생성
            cache_key = f"combined_{'_'.join(sorted(file_paths))}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug("캐시에서 결합 데이터 로드")
                return cached_result.copy()
            
            # 파일들 로드
            dataframes = []
            for file_path in file_paths:
                df = self.load_file(file_path)
                if df is not None:
                    dataframes.append(df)
            
            if not dataframes:
                logger.warning("로드할 수 있는 파일이 없습니다.")
                return None
            
            # 데이터프레임 결합
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # 결합된 데이터 최적화
            combined_df = self._optimize_dataframe(combined_df)
            
            # 캐시에 저장
            self.cache_manager.put(cache_key, combined_df.copy())
            
            logger.info(f"데이터 결합 완료: {len(combined_df)} 행")
            return combined_df
            
        except Exception as e:
            logger.error(f"데이터 결합 실패: {str(e)}")
            return None
        finally:
            # 메모리 정리
            gc.collect()
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터프레임 메모리 최적화 (향상된 버전)
        
        Args:
            df: 원본 데이터프레임
            
        Returns:
            pd.DataFrame: 최적화된 데이터프레임
        """
        try:
            # 필요한 컬럼만 선택
            required_columns = self.config.required_columns
            available_columns = [col for col in required_columns if col in df.columns]
            df = df[available_columns].copy()
            
            # 데이터 타입 최적화
            if 'Time(ms)' in df.columns:
                df['Time(ms)'] = pd.to_numeric(df['Time(ms)'], errors='coerce', downcast='integer')
            
            if 'TouchX' in df.columns:
                df['TouchX'] = pd.to_numeric(df['TouchX'], errors='coerce', downcast='float')
            
            if 'TouchY' in df.columns:
                df['TouchY'] = pd.to_numeric(df['TouchY'], errors='coerce', downcast='float')
            
            # Layer Name 컬럼 최적화
            if 'Layer Name' in df.columns:
                df['Layer Name'] = df['Layer Name'].astype('category')
            
            # NaN 값 제거
            numeric_columns = ['Time(ms)', 'TouchX', 'TouchY']
            available_numeric = [col for col in numeric_columns if col in df.columns]
            if available_numeric:
                df = df.dropna(subset=available_numeric)
            
            # 추가 메모리 최적화
            df = optimize_dataframe_memory(df)
            
            return df
            
        except Exception as e:
            logger.warning(f"데이터프레임 최적화 실패: {str(e)}")
            return df
    
    def clear_cache(self) -> None:
        """캐시 클리어"""
        self.cache_manager.clear()
        self._file_metadata_cache.clear()
        gc.collect()
        logger.info("데이터 매니저 캐시 클리어 완료")
    
    def get_cache_info(self) -> Dict[str, int]:
        """캐시 정보 반환"""
        return {
            'size': self.cache_manager.size(),
            'max_size': self.cache_manager.max_size,
            'metadata_cache_size': len(self._file_metadata_cache)
        }
    
    def get_user_file_count(self, user: str) -> int:
        """
        특정 사용자의 CSV 파일 개수 반환 (캐시 최적화)
        
        Args:
            user: 사용자 이름
            
        Returns:
            int: CSV 파일 개수
        """
        cache_key = f"user_file_count_{user}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            user_folder = os.path.join(self.config.data_dir, user)
            if os.path.exists(user_folder):
                file_count = len([f for f in os.listdir(user_folder) if f.endswith('.csv')])
                self.cache_manager.put(cache_key, file_count)
                return file_count
            return 0
        except Exception as e:
            logger.error(f"사용자 파일 개수 조회 실패: {str(e)}")
            return 0
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        파일 정보 반환 (메타데이터)
        
        Args:
            file_path: 파일 경로
            
        Returns:
            Dict[str, Any]: 파일 정보
        """
        if file_path in self._file_metadata_cache:
            return self._file_metadata_cache[file_path]
        
        try:
            if not os.path.exists(file_path):
                return {}
            
            file_stat = os.stat(file_path)
            info = {
                'size_bytes': file_stat.st_size,
                'modified_time': file_stat.st_mtime,
                'exists': True
            }
            
            # 파일 내용 미리보기 (첫 몇 행)
            try:
                df_preview = pd.read_csv(file_path, nrows=5)
                info['columns'] = list(df_preview.columns)
                info['preview_rows'] = len(df_preview)
            except Exception:
                info['columns'] = []
                info['preview_rows'] = 0
            
            self._file_metadata_cache[file_path] = info
            return info
            
        except Exception as e:
            logger.error(f"파일 정보 조회 실패: {str(e)}")
            return {}
    
    def cleanup_resources(self) -> None:
        """리소스 정리"""
        self.clear_cache()
        self.data.clear()
        gc.collect()
        logger.info("데이터 매니저 리소스 정리 완료")
