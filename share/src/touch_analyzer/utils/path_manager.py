"""
dflux_InteractiveAnalyzer 경로 관리를 위한 중앙집중식 유틸리티 모듈

이 모듈은 애플리케이션에서 사용하는 모든 경로를 중앙에서 관리하여
하드코딩된 경로 참조를 방지하고 유지보수성을 향상시킵니다.
"""

import os
from pathlib import Path
from typing import Optional


class PathManager:
    """애플리케이션 경로 관리 클래스"""
    
    _instance: Optional['PathManager'] = None
    
    def __new__(cls) -> 'PathManager':
        """싱글톤 패턴으로 인스턴스 생성"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """PathManager 초기화"""
        if hasattr(self, '_initialized'):
            return
        
        # 기본 프로젝트 루트 경로 설정
        try:
            # __file__이 정의된 경우 (정상 import)
            self._project_root = Path(__file__).parent.parent.parent.parent
        except NameError:
            # exec()로 실행된 경우 현재 작업 디렉토리 사용
            self._project_root = Path.cwd()
        self._initialized = True
    
    @property
    def project_root(self) -> Path:
        """프로젝트 루트 경로"""
        return self._project_root
    
    @property
    def data_dir(self) -> Path:
        """데이터 폴더 경로 (data_log)"""
        return self._project_root / "data_log"
    
    @property
    def output_dir(self) -> Path:
        """출력 결과 폴더 경로 (data_results)"""
        return self._project_root / "data_results"
    
    @property
    def background_images_dir(self) -> Path:
        """배경 이미지 폴더 경로 (data_bg)"""
        return self._project_root / "data_bg"
    
    @property
    def backup_dir(self) -> Path:
        """백업 폴더 경로 (backup)"""
        return self._project_root / "backup"
    
    @property
    def config_dir(self) -> Path:
        """설정 폴더 경로 (config)"""
        return self._project_root / "config"
    
    @property
    def src_dir(self) -> Path:
        """소스 폴더 경로 (src)"""
        return self._project_root / "src"
    
    # 문자열 경로 반환 메서드들 (기존 코드 호환성을 위해)
    def get_data_dir_str(self) -> str:
        """데이터 폴더 경로를 문자열로 반환"""
        return str(self.data_dir)
    
    def get_output_dir_str(self) -> str:
        """출력 결과 폴더 경로를 문자열로 반환"""
        return str(self.output_dir)
    
    def get_background_images_dir_str(self) -> str:
        """배경 이미지 폴더 경로를 문자열로 반환"""
        return str(self.background_images_dir)
    
    def get_backup_dir_str(self) -> str:
        """백업 폴더 경로를 문자열로 반환"""
        return str(self.backup_dir)
    
    # 디렉토리 생성 유틸리티 메서드들
    def ensure_data_dir(self) -> str:
        """데이터 폴더가 존재하지 않으면 생성하고 경로 반환"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return str(self.data_dir)
    
    def ensure_output_dir(self) -> str:
        """출력 폴더가 존재하지 않으면 생성하고 경로 반환"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return str(self.output_dir)
    
    def ensure_background_images_dir(self) -> str:
        """배경 이미지 폴더가 존재하지 않으면 생성하고 경로 반환"""
        self.background_images_dir.mkdir(parents=True, exist_ok=True)
        return str(self.background_images_dir)
    
    def ensure_backup_dir(self) -> str:
        """백업 폴더가 존재하지 않으면 생성하고 경로 반환"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        return str(self.backup_dir)
    
    # 편의 메서드들
    def get_user_data_dir(self, username: str) -> Path:
        """특정 사용자의 데이터 폴더 경로"""
        return self.data_dir / username
    
    def get_user_data_dir_str(self, username: str) -> str:
        """특정 사용자의 데이터 폴더 경로를 문자열로 반환"""
        return str(self.get_user_data_dir(username))
    
    def ensure_user_data_dir(self, username: str) -> str:
        """특정 사용자의 데이터 폴더가 존재하지 않으면 생성하고 경로 반환"""
        user_dir = self.get_user_data_dir(username)
        user_dir.mkdir(parents=True, exist_ok=True)
        return str(user_dir)
    
    def list_users(self) -> list[str]:
        """데이터 폴더에서 사용자 목록 반환"""
        if not self.data_dir.exists():
            return []
        
        users = []
        for item in self.data_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                users.append(item.name)
        return sorted(users)
    
    def list_background_images(self) -> list[str]:
        """배경 이미지 파일 목록 반환"""
        if not self.background_images_dir.exists():
            return []
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        images = []
        
        for item in self.background_images_dir.iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                images.append(item.name)
        
        return sorted(images)
    
    def get_background_image_path(self, filename: str) -> Path:
        """특정 배경 이미지의 전체 경로 반환"""
        return self.background_images_dir / filename
    
    def get_background_image_path_str(self, filename: str) -> str:
        """특정 배경 이미지의 전체 경로를 문자열로 반환"""
        return str(self.get_background_image_path(filename))


# 전역 인스턴스 (싱글톤)
path_manager = PathManager()


# 편의 함수들 (기존 코드 호환성을 위한 래퍼 함수들)
def get_data_dir() -> str:
    """데이터 폴더 경로 반환"""
    return path_manager.get_data_dir_str()


def get_output_dir() -> str:
    """출력 폴더 경로 반환"""
    return path_manager.get_output_dir_str()


def get_background_images_dir() -> str:
    """배경 이미지 폴더 경로 반환"""
    return path_manager.get_background_images_dir_str()


def ensure_output_dir() -> str:
    """출력 폴더가 존재하지 않으면 생성하고 경로 반환"""
    return path_manager.ensure_output_dir()


def ensure_data_dir() -> str:
    """데이터 폴더가 존재하지 않으면 생성하고 경로 반환"""
    return path_manager.ensure_data_dir()


def ensure_background_images_dir() -> str:
    """배경 이미지 폴더가 존재하지 않으면 생성하고 경로 반환"""
    return path_manager.ensure_background_images_dir()


# 기존 get_resource_path 함수 호환성 유지
def get_resource_path(relative_path: str) -> str:
    """
    리소스 경로 반환 (기존 코드 호환성 유지)
    
    Args:
        relative_path: 상대 경로 (예: "background_images", "data_bg", "data_log", "output_results", "data_results")
    
    Returns:
        str: 절대 경로
    """
    if relative_path == "background_images" or relative_path == "data_bg":
        return path_manager.get_background_images_dir_str()
    elif relative_path == "data_log":
        return path_manager.get_data_dir_str()
    elif relative_path == "output_results" or relative_path == "data_results":
        return path_manager.get_output_dir_str()
    elif relative_path == "backup":
        return path_manager.get_backup_dir_str()
    else:
        # 기본적으로 프로젝트 루트 기준 상대 경로
        return str(path_manager.project_root / relative_path)
