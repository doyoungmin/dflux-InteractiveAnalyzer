"""
dflux_InteractiveAnalyzer - 핵심 베이스 클래스
단일 Interactive 버전을 위한 최적화된 기능 제공
"""

import os
import sys
import glob
from typing import Optional, Dict, Set, List, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image

from src.touch_analyzer.utils.path_manager import path_manager, get_resource_path
from src.touch_analyzer.core.data_manager import DataManager
from src.touch_analyzer.core.config import Config


# 한글 폰트 설정 (간소화)
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class BaseVisualizer:
    """터치 데이터 Interactive 시각화를 위한 최적화된 베이스 클래스"""
    
    def __init__(self, root: tk.Tk, title: str = "dflux_InteractiveAnalyzer") -> None:
        """
        베이스 시각화 클래스 초기화
        
        Args:
            root: Tkinter 루트 윈도우
            title: 윈도우 제목
        """
        self.root = root
        self.root.title(title)
        self.root.geometry("1200x800")
        
        # 설정 및 데이터 관리자 초기화
        self.config = Config.default()
        self.data_manager = DataManager(self.config)
        
        # 데이터 저장소
        self.data: Dict[str, pd.DataFrame] = {}
        self.filtered_data: Optional[pd.DataFrame] = None
        self.background_image_path: str = ""
        
        # 사용자 및 task 선택 관리
        self.selected_users = set()
        self.user_buttons = {}
        self.task_buttons = {}
        self.background_buttons = {}  # 배경 이미지 버튼들
        self.selected_files = set()
        
        # 화면 크기 설정
        self.screen_width = 3840
        self.screen_height = 850
        
        # 탭 관련
        self.tab_buttons = {}
        self.tab_contents = {}
        self.current_tab = None
    
    def get_user_list(self) -> List[str]:
        """사용자 목록을 반환"""
        return self.data_manager.get_user_list()
    
    def get_max_task_count(self) -> int:
        """사용 가능한 최대 task 수를 반환"""
        return self.data_manager.get_max_task_count()
    
    def get_task_files_for_users(self, task_num, users):
        """특정 사용자들의 task 번호에 해당하는 파일들을 반환"""
        return self.data_manager.get_task_files_for_users(task_num, users)
    
    def load_and_combine_data(self) -> Optional[pd.DataFrame]:
        """선택된 파일들의 데이터를 로드하고 합치는 공통 로직 (메모리 최적화)"""
        if not self.selected_files:
            return None
        
        file_paths = list(self.selected_files)
        return self.data_manager.load_and_combine_data(file_paths)
    
    def create_user_buttons(self, parent):
        """사용자 선택 버튼들 생성"""
        users = self.get_user_list()
        
        # "모든 사용자" 토글 버튼 추가
        all_users_btn = ttk.Button(parent, text="모든 사용자", 
                                  command=self.toggle_all_users)
        all_users_btn.pack(side=tk.LEFT, padx=2, pady=2)
        all_users_btn.user_name = "all_users"
        self.user_buttons["all_users"] = all_users_btn
        
        # 구분선 추가
        separator = ttk.Separator(parent, orient='vertical')
        separator.pack(side=tk.LEFT, fill='y', padx=5, pady=2)
        
        # 사용자 버튼들 생성 (데이터 상태 포함)
        for user in users:
            # 사용자별 파일 개수 확인
            file_count = self.data_manager.get_user_file_count(user)
            
            if file_count > 0:
                text = f"{user} ({file_count})"
                state = "normal"
            else:
                text = f"{user} (None)"
                state = "disabled"
            
            btn = ttk.Button(parent, text=text, state=state,
                           command=lambda u=user: self.toggle_user(u))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            btn.user_name = user
            self.user_buttons[user] = btn
    
    def toggle_all_users(self):
        """모든 사용자 선택/해제 토글"""
        users = self.get_user_list()
        all_selected = all(user in self.selected_users for user in users)
        
        if all_selected:
            self.selected_users.clear()
            for user in users:
                if user in self.user_buttons:
                    try:
                        self.user_buttons[user].configure(style='TButton')
                    except tk.TclError:
                        continue
            try:
                self.user_buttons["all_users"].configure(style='TButton')
            except tk.TclError:
                pass
        else:
            self.selected_users.update(users)
            for user in users:
                if user in self.user_buttons:
                    try:
                        self.user_buttons[user].configure(style='SelectedData.TButton')
                    except tk.TclError:
                        continue
            try:
                self.user_buttons["all_users"].configure(style='SelectedData.TButton')
            except tk.TclError:
                pass
        
        self.update_selected_files()
    
    def toggle_user(self, user_name):
        """사용자 선택/해제 토글"""
        if user_name in self.selected_users:
            self.selected_users.discard(user_name)
            try:
                self.user_buttons[user_name].configure(style='TButton')
            except tk.TclError:
                pass
        else:
            self.selected_users.add(user_name)
            try:
                self.user_buttons[user_name].configure(style='SelectedData.TButton')
            except tk.TclError:
                pass
        
        self.update_all_users_button()
        self.update_selected_files()
    
    def update_all_users_button(self):
        """모든 사용자 버튼의 상태를 업데이트"""
        users = self.get_user_list()
        all_selected = all(user in self.selected_users for user in users)
        
        try:
            if all_selected:
                self.user_buttons["all_users"].configure(style='SelectedData.TButton')
            else:
                self.user_buttons["all_users"].configure(style='TButton')
        except tk.TclError:
            pass
    
    def create_task_buttons(self, parent):
        """Task 선택 버튼들 생성"""
        max_tasks = self.get_max_task_count()
        
        for i in range(1, max_tasks + 1):
            btn = ttk.Button(parent, text=f"Task {i}", 
                           command=lambda task_num=i: self.select_task(task_num))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            btn.task_num = i
            self.task_buttons[i] = btn
    
    def select_task(self, task_num):
        """특정 task 번호의 선택된 사용자들의 파일들을 선택"""
        selected_users = list(self.selected_users)
        
        if not selected_users:
            if hasattr(self, 'info_label'):
                self.info_label.config(text="사용자를 먼저 선택해주세요.")
            self.selected_files.clear()
            self.filtered_data = None
            return
        
        task_files = self.get_task_files_for_users(task_num, selected_users)
        self.selected_files.clear()
        
        for file_path in task_files:
            self.selected_files.add(file_path)
        
        # Task 버튼 스타일 업데이트
        for btn_task_num, btn in self.task_buttons.items():
            try:
                if btn_task_num == task_num:
                    btn.configure(style='SelectedData.TButton')
                else:
                    btn.configure(style='TButton')
            except tk.TclError:
                # 버튼이 이미 삭제된 경우 무시
                continue
        
        self.show_all_data()
    
    def update_selected_files(self):
        """선택된 사용자들에 따라 파일들을 업데이트"""
        selected_tasks = set()
        for task_num, btn in self.task_buttons.items():
            try:
                if btn.cget('style') == 'SelectedData.TButton':
                    selected_tasks.add(task_num)
            except tk.TclError:
                # 버튼이 이미 삭제된 경우 무시
                continue
        
        selected_users = list(self.selected_users)
        
        if not selected_users:
            self.selected_files.clear()
            self.filtered_data = None
            if hasattr(self, 'info_label'):
                self.info_label.config(text="사용자를 선택해주세요.")
            return
        
        self.selected_files.clear()
        for task_num in selected_tasks:
            task_files = self.get_task_files_for_users(task_num, selected_users)
            for file_path in task_files:
                self.selected_files.add(file_path)
        
        if not self.selected_files:
            if hasattr(self, 'info_label'):
                self.info_label.config(text="선택된 사용자의 Task를 선택해주세요.")
            self.filtered_data = None
            return
        
        self.show_all_data()
    
    def show_all_data(self):
        """전체 데이터 표시"""
        if not self.selected_files:
            if hasattr(self, 'info_label'):
                self.info_label.config(text="사용자와 Task를 선택하세요.")
            return
        
        combined_data = self.load_and_combine_data()
        if combined_data is None:
            if hasattr(self, 'info_label'):
                self.info_label.config(text="선택된 파일에서 데이터를 읽을 수 없습니다.")
            return
        
        self.filtered_data = combined_data
        total_points = len(combined_data)
        
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"전체 데이터 표시: {total_points}개 이벤트")
        
        self.update_current_visualization()
    
    def create_background_buttons(self):
        """배경 이미지 버튼들 생성"""
        bg_dir = get_resource_path("background_images")
        
        if not hasattr(self, 'bg_content_frame'):
            return
        
        if not os.path.exists(bg_dir):
            none_btn = ttk.Button(self.bg_content_frame, text="배경 없음")
            none_btn.pack(padx=2, pady=1, anchor=tk.W)
            none_btn.bind('<Button-1>', lambda e: self.select_background_image(""))
            none_btn.file_path = ""
            self.background_image_path = ""
            return
        
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(bg_dir, ext)))
        
        image_files.sort(key=lambda x: os.path.basename(x))
        
        # None 옵션 추가
        none_btn = ttk.Button(self.bg_content_frame, text="배경 없음", width=24)
        none_btn.pack(padx=2, pady=1, anchor=tk.W, fill=tk.X)
        none_btn.bind('<Button-1>', lambda e: self.select_background_image(""))
        none_btn.file_path = ""
        self.background_buttons[""] = none_btn
        
        # 이미지 파일들에 대한 버튼 생성
        for file_path in image_files:
            filename = os.path.basename(file_path)
            # 파일명에서 확장자 제거
            display_name = os.path.splitext(filename)[0]
            btn = ttk.Button(self.bg_content_frame, text=display_name, width=24)
            btn.pack(padx=2, pady=1, anchor=tk.W, fill=tk.X)
            btn.bind('<Button-1>', lambda e, f=file_path: self.select_background_image(f))
            btn.file_path = file_path
            self.background_buttons[file_path] = btn
        
        # 기본으로 "배경 없음" 선택 상태로 설정
        self.background_image_path = ""
        if "" in self.background_buttons:
            self.background_buttons[""].configure(style='SelectedBg.TButton')
    
    def select_background_image(self, image_path):
        """배경 이미지 선택"""
        self.background_image_path = image_path
        
        # 모든 배경 버튼 스타일 초기화
        self.update_background_button_styles()
        
        # 선택된 버튼 스타일 변경
        if image_path in self.background_buttons:
            selected_btn = self.background_buttons[image_path]
            selected_btn.configure(style='SelectedBg.TButton')
        
        # 상태 업데이트
        if hasattr(self, 'update_status'):
            if image_path == "":
                self.update_status("배경 이미지 제거됨")
            else:
                filename = os.path.basename(image_path)
                self.update_status(f"배경 이미지 선택: {filename}")
        elif hasattr(self, 'info_label'):
            if image_path == "":
                self.info_label.config(text="배경 이미지가 제거되었습니다.")
            else:
                self.info_label.config(text=f"배경 이미지가 선택되었습니다: {os.path.basename(image_path)}")
        
        self.update_current_visualization()
    
    def update_background_button_styles(self):
        """배경 이미지 버튼 스타일 업데이트"""
        for btn in self.background_buttons.values():
            btn.configure(style='TButton')  # 기본 스타일로 초기화
    
    def switch_tab(self, tab_name):
        """탭 전환"""
        self.current_tab = tab_name
        self.show_tab_content(tab_name)
        self.update_current_visualization()
    
    def show_tab_content(self, tab_name):
        """지정된 탭 콘텐츠를 표시"""
        if not hasattr(self, 'tab_contents') or not self.tab_contents:
            return
            
        for name, frame in self.tab_contents.items():
            frame.pack_forget()
        
        if tab_name in self.tab_contents:
            self.tab_contents[tab_name].pack(fill=tk.BOTH, expand=True)
        elif self.tab_contents:
            first_tab_name = next(iter(self.tab_contents))
            self.tab_contents[first_tab_name].pack(fill=tk.BOTH, expand=True)
            self.current_tab = first_tab_name
    
    # 추상 메서드들 - 하위 클래스에서 구현해야 함
    def update_current_visualization(self):
        """현재 탭의 시각화를 업데이트 (하위 클래스에서 구현)"""
        pass
    
    def setup_ui(self):
        """UI 설정 (하위 클래스에서 구현)"""
        pass
    
    def clear_cache(self) -> None:
        """캐시 클리어"""
        self.data_manager.clear_cache()
