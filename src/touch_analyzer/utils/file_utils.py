"""
파일 관련 유틸리티 함수들
"""

import os
import sys
from pathlib import Path
from typing import List


def get_resource_path(relative_path: str) -> str:
    """
    PyInstaller 환경에서 리소스 경로를 올바르게 가져오는 함수
    
    Args:
        relative_path: 상대 경로
        
    Returns:
        str: 절대 경로
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def ensure_directory(path: str) -> None:
    """
    디렉토리가 존재하지 않으면 생성
    
    Args:
        path: 디렉토리 경로
    """
    os.makedirs(path, exist_ok=True)


def get_supported_image_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    지원되는 이미지 파일 목록 반환
    
    Args:
        directory: 검색할 디렉토리
        extensions: 지원되는 확장자 목록
        
    Returns:
        List[str]: 이미지 파일 경로 목록
    """
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    
    image_files = []
    
    if not os.path.exists(directory):
        return image_files
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                image_files.append(file_path)
    
    return sorted(image_files)


def generate_unique_filename(directory: str, base_filename: str) -> str:
    """
    중복되지 않는 파일명 생성
    
    Args:
        directory: 저장할 디렉토리
        base_filename: 기본 파일명
        
    Returns:
        str: 고유한 파일명
    """
    if not os.path.exists(os.path.join(directory, base_filename)):
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1


def get_file_size_mb(file_path: str) -> float:
    """
    파일 크기를 MB 단위로 반환
    
    Args:
        file_path: 파일 경로
        
    Returns:
        float: 파일 크기 (MB)
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def cleanup_old_files(directory: str, max_files: int = 100) -> None:
    """
    오래된 파일들 정리 (최대 파일 수 제한)
    
    Args:
        directory: 정리할 디렉토리
        max_files: 최대 파일 수
    """
    if not os.path.exists(directory):
        return
    
    files = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            files.append((file_path, os.path.getmtime(file_path)))
    
    # 수정 시간으로 정렬 (오래된 것부터)
    files.sort(key=lambda x: x[1])
    
    # 최대 파일 수 초과 시 오래된 파일들 삭제
    if len(files) > max_files:
        files_to_delete = files[:-max_files]
        for file_path, _ in files_to_delete:
            try:
                os.remove(file_path)
            except OSError:
                pass
