"""
설정 관리 모듈
애플리케이션 설정을 중앙 집중 관리
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# 중앙집중식 경로 관리 임포트
try:
    from ..utils.path_manager import path_manager
    PATH_MANAGER_AVAILABLE = True
except ImportError:
    PATH_MANAGER_AVAILABLE = False


@dataclass
class Config:
    """애플리케이션 설정 클래스"""
    
    # 경로 설정
    base_dir: Path
    data_dir: str
    output_dir: str
    background_images_dir: str
    backup_dir: str
    
    # 화면 설정
    screen_width: int = 3840
    screen_height: int = 850
    
    # UI 설정
    window_width: int = 1400
    window_height: int = 900
    window_title: str = "터치 데이터 시각화 도구 - Interactive"
    
    # 데이터 처리 설정
    required_columns: List[str] = None
    max_cache_size: int = 10
    memory_monitor_interval: int = 5000
    
    # 시각화 설정
    default_heatmap_bins_x: int = 50
    default_heatmap_bins_y: int = 20
    min_heatmap_bins_x: int = 20
    min_heatmap_bins_y: int = 10
    max_heatmap_bins_x: int = 50
    max_heatmap_bins_y: int = 20
    
    # 파일 형식 설정
    default_output_format: str = 'png'
    default_dpi: int = 300
    
    # 성능 설정
    data_density_threshold: int = 1000
    bins_multiplier_x: int = 10
    bins_multiplier_y: int = 4
    
    # UI 메시지
    ui_messages: Dict[str, str] = None
    
    def __post_init__(self):
        """초기화 후 기본값 설정"""
        if self.required_columns is None:
            self.required_columns = ['Time(ms)', 'TouchX', 'TouchY', 'Layer Name']
        
        if self.ui_messages is None:
            self.ui_messages = {
                'welcome': "🚀 시작하기: ① 사용자 선택 → ② Task 선택 → ③ 탭에서 분석 결과 확인",
                'no_data': "표시할 데이터가 없습니다.",
                'data_loaded': "📊 데이터 로드 완료!",
                'memory_insufficient': "메모리가 부족합니다. 더 적은 양의 데이터를 선택해주세요.",
                'file_not_found': "파일을 찾을 수 없습니다.",
                'all_users': "모든사용자",
                'no_selection': "선택안됨"
            }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """딕셔너리에서 Config 객체 생성 (PathManager 활용)"""
        if PATH_MANAGER_AVAILABLE:
            # PathManager를 통한 기본값 설정
            base_dir = path_manager.project_root
            default_data_dir = path_manager.get_data_dir_str()
            default_output_dir = path_manager.get_output_dir_str()
            default_bg_dir = path_manager.get_background_images_dir_str()
            default_backup_dir = path_manager.get_backup_dir_str()
        else:
            # 백업용 직접 경로 설정
            base_dir = Path(__file__).parent.parent.parent.parent
            default_data_dir = str(base_dir / "data_log")
            default_output_dir = str(base_dir / "data_results")
            default_bg_dir = str(base_dir / "data_bg")
            default_backup_dir = str(base_dir / "backup")
        
        return cls(
            base_dir=base_dir,
            data_dir=config_dict.get('paths', {}).get('data_dir', default_data_dir),
            output_dir=config_dict.get('paths', {}).get('output_dir', default_output_dir),
            background_images_dir=config_dict.get('paths', {}).get('background_images_dir', default_bg_dir),
            backup_dir=config_dict.get('paths', {}).get('backup_dir', default_backup_dir),
            screen_width=config_dict.get('screen', {}).get('width', 3840),
            screen_height=config_dict.get('screen', {}).get('height', 850),
            window_width=config_dict.get('ui', {}).get('window_width', 1400),
            window_height=config_dict.get('ui', {}).get('window_height', 900),
            window_title=config_dict.get('ui', {}).get('title', "dflux_InteractiveAnalyzer"),
            required_columns=config_dict.get('data', {}).get('required_columns', ['Time(ms)', 'TouchX', 'TouchY', 'Layer Name']),
            max_cache_size=config_dict.get('data', {}).get('max_cache_size', 10),
            memory_monitor_interval=config_dict.get('data', {}).get('memory_monitor_interval', 5000),
            default_heatmap_bins_x=config_dict.get('visualization', {}).get('heatmap', {}).get('default_bins_x', 50),
            default_heatmap_bins_y=config_dict.get('visualization', {}).get('heatmap', {}).get('default_bins_y', 20),
            min_heatmap_bins_x=config_dict.get('visualization', {}).get('heatmap', {}).get('min_bins_x', 20),
            min_heatmap_bins_y=config_dict.get('visualization', {}).get('heatmap', {}).get('min_bins_y', 10),
            max_heatmap_bins_x=config_dict.get('visualization', {}).get('heatmap', {}).get('max_bins_x', 50),
            max_heatmap_bins_y=config_dict.get('visualization', {}).get('heatmap', {}).get('max_bins_y', 20),
            default_output_format=config_dict.get('visualization', {}).get('output', {}).get('format', 'png'),
            default_dpi=config_dict.get('visualization', {}).get('output', {}).get('dpi', 300),
            data_density_threshold=config_dict.get('performance', {}).get('data_density_threshold', 1000),
            bins_multiplier_x=config_dict.get('performance', {}).get('bins_multiplier_x', 10),
            bins_multiplier_y=config_dict.get('performance', {}).get('bins_multiplier_y', 4),
            ui_messages=config_dict.get('ui', {}).get('messages', {})
        )
    
    @classmethod
    def default(cls) -> 'Config':
        """기본 설정으로 Config 객체 생성 (PathManager 활용)"""
        if PATH_MANAGER_AVAILABLE:
            # PathManager를 통한 경로 설정
            return cls(
                base_dir=path_manager.project_root,
                data_dir=path_manager.get_data_dir_str(),
                output_dir=path_manager.get_output_dir_str(),
                background_images_dir=path_manager.get_background_images_dir_str(),
                backup_dir=path_manager.get_backup_dir_str()
            )
        else:
            # 백업용 직접 경로 설정
            base_dir = Path(__file__).parent.parent.parent.parent
            return cls(
                base_dir=base_dir,
                data_dir=str(base_dir / "data_log"),
                output_dir=str(base_dir / "data_results"),
                background_images_dir=str(base_dir / "data_bg"),
                backup_dir=str(base_dir / "backup")
            )
    
    def ensure_directories(self) -> None:
        """필요한 디렉토리들 생성"""
        directories = [
            self.output_dir,
            self.backup_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_adaptive_bins(self, data_count: int) -> tuple[int, int]:
        """
        데이터 수에 따른 적응적 bins 크기 계산
        
        Args:
            data_count: 데이터 포인트 수
            
        Returns:
            tuple[int, int]: (bins_x, bins_y)
        """
        data_density = data_count // self.data_density_threshold + 1
        bins_x = min(self.max_heatmap_bins_x, 
                    max(self.min_heatmap_bins_x, data_density * self.bins_multiplier_x))
        bins_y = min(self.max_heatmap_bins_y, 
                    max(self.min_heatmap_bins_y, data_density * self.bins_multiplier_y))
        
        return bins_x, bins_y
