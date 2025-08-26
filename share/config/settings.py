"""
dflux_InteractiveAnalyzer - 설정 파일
모든 하드코딩된 설정값들을 중앙 집중 관리 - 최적화된 버전
"""

import os
from pathlib import Path

# 중앙집중식 경로 관리를 통한 기본 경로 설정
try:
    from src.touch_analyzer.utils.path_manager import path_manager
    
    # PathManager를 통한 경로 설정
    BASE_DIR = path_manager.project_root
    DATA_DIR = path_manager.data_dir
    OUTPUT_DIR = path_manager.output_dir
    BACKGROUND_IMAGES_DIR = path_manager.background_images_dir
    BACKUP_DIR = path_manager.backup_dir
except ImportError:
    # 백업용 직접 경로 설정 (PathManager를 사용할 수 없는 경우)
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data_log"
    OUTPUT_DIR = BASE_DIR / "data_results"
    BACKGROUND_IMAGES_DIR = BASE_DIR / "data_bg"
    BACKUP_DIR = BASE_DIR / "backup"

# 화면 설정
SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 850

# UI 설정
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MAIN_WINDOW_TITLE = "dflux_InteractiveAnalyzer"

# 데이터 처리 설정
REQUIRED_COLUMNS = ['Time(ms)', 'TouchX', 'TouchY', 'Layer Name']
MAX_CACHE_SIZE = 15  # 캐시 크기 증가
MEMORY_MONITOR_INTERVAL = 3000  # 모니터링 간격 단축 (3초)

# 시각화 설정
DEFAULT_HEATMAP_BINS_X = 50
DEFAULT_HEATMAP_BINS_Y = 20
MIN_HEATMAP_BINS_X = 20
MIN_HEATMAP_BINS_Y = 10
MAX_HEATMAP_BINS_X = 50
MAX_HEATMAP_BINS_Y = 20

# 파일 형식 설정
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
DEFAULT_OUTPUT_FORMAT = 'png'
DEFAULT_DPI = 300

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 성능 설정 (최적화된 버전)
DATA_DENSITY_THRESHOLD = 800  # 적응적 bins 조정 기준 감소
BINS_MULTIPLIER_X = 8  # 배수 감소
BINS_MULTIPLIER_Y = 3  # 배수 감소
MEMORY_THRESHOLD_MB = 800.0  # 메모리 임계값 설정
CACHE_TTL_SECONDS = 1800  # 캐시 수명 30분

# UI 텍스트
UI_MESSAGES = {
    'welcome': "🚀 시작하기: ① 사용자 선택 → ② Task 선택 → ③ 탭에서 분석 결과 확인",
    'no_data': "표시할 데이터가 없습니다.",
    'data_loaded': "📊 데이터 로드 완료!",
    'memory_insufficient': "메모리가 부족합니다. 더 적은 양의 데이터를 선택해주세요.",
    'file_not_found': "파일을 찾을 수 없습니다.",
    'all_users': "모든사용자",
    'no_selection': "선택안됨",
    'optimization_active': "최적화 모드 활성화",
    'cache_cleared': "캐시가 정리되었습니다."
}

# 색상 테마
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'success': '#F18F01',
    'warning': '#C73E1D',
    'background': '#FFFFFF',
    'text': '#333333',
    'optimized': '#28A745'  # 최적화 상태 표시용
}

# 성능 최적화 설정
PERFORMANCE_OPTIONS = {
    'enable_lazy_loading': True,  # 지연 로딩 활성화
    'enable_adaptive_bins': True,  # 적응적 bins 활성화
    'enable_memory_monitoring': True,  # 메모리 모니터링 활성화
    'enable_cache_optimization': True,  # 캐시 최적화 활성화
    'max_concurrent_loads': 3,  # 최대 동시 로드 수
    'chunk_size': 10000,  # 청크 단위 처리 크기
}

def get_config():
    """설정 딕셔너리 반환 - 최적화된 버전"""
    return {
        'paths': {
            'data_dir': str(DATA_DIR),
            'output_dir': str(OUTPUT_DIR),
            'background_images_dir': str(BACKGROUND_IMAGES_DIR),
            'backup_dir': str(BACKUP_DIR)
        },
        'screen': {
            'width': SCREEN_WIDTH,
            'height': SCREEN_HEIGHT
        },
        'ui': {
            'window_width': WINDOW_WIDTH,
            'window_height': WINDOW_HEIGHT,
            'title': MAIN_WINDOW_TITLE,
            'messages': UI_MESSAGES,
            'colors': COLORS
        },
        'data': {
            'required_columns': REQUIRED_COLUMNS,
            'max_cache_size': MAX_CACHE_SIZE,
            'memory_monitor_interval': MEMORY_MONITOR_INTERVAL,
            'cache_ttl_seconds': CACHE_TTL_SECONDS
        },
        'visualization': {
            'heatmap': {
                'default_bins_x': DEFAULT_HEATMAP_BINS_X,
                'default_bins_y': DEFAULT_HEATMAP_BINS_Y,
                'min_bins_x': MIN_HEATMAP_BINS_X,
                'min_bins_y': MIN_HEATMAP_BINS_Y,
                'max_bins_x': MAX_HEATMAP_BINS_X,
                'max_bins_y': MAX_HEATMAP_BINS_Y
            },
            'output': {
                'format': DEFAULT_OUTPUT_FORMAT,
                'dpi': DEFAULT_DPI
            }
        },
        'performance': {
            'data_density_threshold': DATA_DENSITY_THRESHOLD,
            'bins_multiplier_x': BINS_MULTIPLIER_X,
            'bins_multiplier_y': BINS_MULTIPLIER_Y,
            'memory_threshold_mb': MEMORY_THRESHOLD_MB,
            'options': PERFORMANCE_OPTIONS
        },
        'logging': {
            'level': LOG_LEVEL,
            'format': LOG_FORMAT
        }
    }
