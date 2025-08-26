"""
dflux_InteractiveAnalyzer - 통합 Interactive 버전
단일 버전으로 통합하여 최적화된 성능과 기능 제공
"""

import os
import sys
import logging
from typing import Optional, Dict, Set, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image, ImageTk

from base_visualizer import BaseVisualizer
from src.touch_analyzer.utils.path_manager import path_manager, ensure_output_dir


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class RangeSlider(ttk.Frame):
    """간소화된 범위 슬라이더 - HWK 이벤트 표시 기능 포함"""
    
    def __init__(self, parent, from_=0, to=100, start_value=0, end_value=100, 
                 command=None, hwk_events=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.from_ = from_
        self.to = to
        self.start_value = start_value
        self.end_value = end_value
        self.command = command
        self.dragging = None
        self.hwk_events = hwk_events or []
        self.tooltip = None  # 툴팁 창 초기화
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, pady=5)
        
        # 슬라이더 중앙 상단의 시간 표시 제거 (타이틀 옆 시간 표시로 대체됨)
        
        # 슬라이더 컨테이너
        slider_container = ttk.Frame(main_frame)
        slider_container.pack(fill=tk.X, padx=10)
        
        # Canvas 기반 슬라이더
        self.canvas = tk.Canvas(slider_container, height=45, bg='#f8fafc', 
                               highlightthickness=0)
        self.canvas.pack(fill=tk.X, expand=True)
        
        # 마우스 이벤트 바인딩
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # 슬라이더 변수
        self.start_var = tk.DoubleVar(value=self.start_value)
        self.end_var = tk.DoubleVar(value=self.end_value)
        
        # 초기 그리기
        self.draw_slider()
        self.update_range_label()
        
        # 부모 컨테이너 크기 변화 감지
        self.bind('<Configure>', self.on_container_resize)
        
    def draw_slider(self):
        """슬라이더 그리기"""
        self.canvas.delete("all")
        
        # 캔버스 크기 업데이트 강제 실행
        self.canvas.update_idletasks()
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            # 부모 프레임의 폭을 기반으로 추정
            parent_width = self.winfo_width()
            if parent_width > 1:
                canvas_width = parent_width - 20  # 패딩 고려
            else:
                canvas_width = 300
        
        canvas_height = 45
        
        # 색상 설정
        track_color = '#e2e8f0'
        active_color = '#3b82f6'
        handle_color = '#ffffff'
        handle_border = '#cbd5e1'
        hwk_color = '#a855f7'  # 자주색으로 HWK 이벤트 통일
        
        # 트랙 그리기
        bar_y = 25
        bar_height = 4
        
        # 배경 트랙
        self.canvas.create_rectangle(5, bar_y - bar_height//2, 
                                   canvas_width - 5, bar_y + bar_height//2,
                                   fill=track_color, outline=track_color)
        
        # 활성 트랙
        start_pos = 5 + (self.start_var.get() - self.from_) / (self.to - self.from_) * (canvas_width - 10)
        end_pos = 5 + (self.end_var.get() - self.from_) / (self.to - self.from_) * (canvas_width - 10)
        
        if end_pos > start_pos:
            self.canvas.create_rectangle(start_pos, bar_y - bar_height//2,
                                       end_pos, bar_y + bar_height//2,
                                       fill=active_color, outline=active_color)
        
        # 이벤트 표시 (HWK 및 플리킹)
        for event in self.hwk_events:
            event_time = event['time']
            event_type = event['type']
            
            if self.to > self.from_:
                event_pos = 5 + (event_time - self.from_) / (self.to - self.from_) * (canvas_width - 10)
                event_pos = max(5, min(canvas_width - 5, event_pos))
                
                # 이벤트 타입에 따른 색상 결정
                if 'SWIPE' in event_type:
                    event_color = '#06b6d4'  # 시안블루로 플리킹 이벤트 통일
                else:
                    event_color = '#a855f7'  # 자주색으로 HWK 이벤트 통일
                
                # 이벤트 선 그리기
                self.canvas.create_line(event_pos, 5, event_pos, 20, 
                                      fill=event_color, width=2)
                
                # 이니셜 표시 (툴팁 이벤트 포함)
                initial = self.get_hwk_initial(event_type)
                text_id = self.canvas.create_text(event_pos, 40, text=initial, 
                                                font=('Arial', 7), fill=event_color)
                
                # 이벤트 툴팁을 위한 마우스 이벤트 바인딩
                self.canvas.tag_bind(text_id, '<Enter>', 
                                   lambda e, time=event_time: self.show_hwk_tooltip(e, time))
                self.canvas.tag_bind(text_id, '<Leave>', self.hide_hwk_tooltip)
        
        # 핸들 그리기
        handle_radius = 8
        
        self.start_handle = self.canvas.create_oval(
            start_pos - handle_radius, bar_y - handle_radius,
            start_pos + handle_radius, bar_y + handle_radius,
            fill=handle_color, outline=handle_border, width=1, tags="start_handle"
        )
        
        self.end_handle = self.canvas.create_oval(
            end_pos - handle_radius, bar_y - handle_radius,
            end_pos + handle_radius, bar_y + handle_radius,
            fill=handle_color, outline=handle_border, width=1, tags="end_handle"
        )
    
    def on_mouse_down(self, event):
        """마우스 클릭 이벤트"""
        start_handle_bbox = self.canvas.bbox("start_handle")
        end_handle_bbox = self.canvas.bbox("end_handle")
        
        if start_handle_bbox:
            start_handle_x = (start_handle_bbox[0] + start_handle_bbox[2]) / 2
            if abs(event.x - start_handle_x) < 12:
                self.dragging = 'start'
                return
        
        if end_handle_bbox:
            end_handle_x = (end_handle_bbox[0] + end_handle_bbox[2]) / 2
            if abs(event.x - end_handle_x) < 12:
                self.dragging = 'end'
                return
    
    def on_mouse_drag(self, event):
        """마우스 드래그 이벤트"""
        if not self.dragging:
            return
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            return
        
        x_pos = max(5, min(canvas_width - 5, event.x))
        value = self.from_ + (x_pos - 5) / (canvas_width - 10) * (self.to - self.from_)
        
        if self.dragging == 'start':
            if value > self.end_var.get():
                value = self.end_var.get()
            self.start_var.set(value)
        elif self.dragging == 'end':
            if value < self.start_var.get():
                value = self.start_var.get()
            self.end_var.set(value)
        
        self.draw_slider()
        self.update_range_label()
        
        if self.command:
            self.command()
    
    def on_mouse_up(self, event):
        """마우스 릴리즈 이벤트"""
        self.dragging = None
    
    def update_range_label(self):
        """시간 범위 라벨 업데이트 (제거됨 - 타이틀 옆 시간 표시로 대체)"""
        # 슬라이더 중앙 상단 시간 표시 제거됨
        # 대신 타이틀 옆의 time_range_display가 시간을 표시함
        pass
    
    def get_values(self):
        """현재 값들을 반환"""
        return self.start_var.get(), self.end_var.get()
    
    def get_hwk_initial(self, event_type):
        """이벤트 타입에 따른 이니셜 반환"""
        initials = {
            'HWK_boost': 'b',
            'HWK_magma': 'm', 
            'HWK_drive': 'd',
            'SWIPE_UP': '↑',
            'SWIPE_DOWN': '↓',
            'SWIPE_LEFT': '←',
            'SWIPE_RIGHT': '→',
            'SWIPE_UNKNOWN': '↔'
        }
        return initials.get(event_type, '?')
    
    def set_hwk_events(self, events):
        """HWK 이벤트 설정"""
        self.hwk_events = events
        self.draw_slider()
    
    def set_range(self, from_, to):
        """슬라이더 범위 설정"""
        self.from_ = from_
        self.to = to
        
        start_val = self.start_var.get()
        end_val = self.end_var.get()
        
        if start_val < from_:
            self.start_var.set(from_)
        if end_val > to:
            self.end_var.set(to)
        
        self.draw_slider()
        self.update_range_label()
    
    def show_hwk_tooltip(self, event, time_sec, event_type=None):
        """이벤트 툴팁 표시"""
        # 시간을 mm:ss 형식으로 변환
        minutes = int(time_sec // 60)
        seconds = int(time_sec % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        # 이벤트 타입에 따른 텍스트 설정
        if event_type and event_type.startswith('SWIPE'):
            event_text = f"플리킹: {event_type}"
        elif event_type and event_type.startswith('HWK'):
            event_text = f"HWK: {event_type}"
        else:
            event_text = time_text
        
        # 툴팁 창 생성
        self.tooltip = tk.Toplevel(self.canvas)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.configure(bg='black')
        
        # 툴팁 라벨
        tooltip_label = tk.Label(self.tooltip, text=event_text, 
                               bg='black', fg='white',
                               font=('Arial', 8), padx=5, pady=2)
        tooltip_label.pack()
        
        # 툴팁 위치 설정 (마우스 위치 기준)
        x = event.x_root + 10
        y = event.y_root - 25
        self.tooltip.geometry(f"+{x}+{y}")
    
    def hide_hwk_tooltip(self, event=None):
        """HWK 이벤트 툴팁 숨김"""
        if hasattr(self, 'tooltip') and self.tooltip:
            try:
                self.tooltip.destroy()
                self.tooltip = None
            except:
                pass
    
    def on_container_resize(self, event=None):
        """컨테이너 크기 변화 시 슬라이더 재그리기"""
        # 크기 변화가 실제로 있을 때만 재그리기
        if hasattr(self, '_last_width'):
            if abs(event.width - self._last_width) > 5:  # 5픽셀 이상 변화 시에만
                self._last_width = event.width
                self.after(50, self.draw_slider)  # 지연 실행으로 성능 최적화
        else:
            self._last_width = event.width


class InteractiveVisualizer(BaseVisualizer):
    """최적화된 Interactive 터치 데이터 시각화 도구 - 성능 및 안정성 강화"""
    
    def __init__(self, root):
        super().__init__(root, "dflux_InteractiveAnalyzer")
        self.root.geometry("1400x900")
        
        logger.info("dflux_InteractiveAnalyzer 초기화 시작")
        
        try:
            # UI 상태 변수 초기화
            self.start_time_var = tk.DoubleVar(value=0)
            self.end_time_var = tk.DoubleVar(value=100000)
            self.user_var = tk.StringVar()
            self.task_var = tk.IntVar(value=1)
            self.layer_filter_var = tk.StringVar(value="전체")
            
            # 데이터 관리 변수 초기화
            self.current_data = None
            self.current_task_files = []
            
            # matplotlib 객체 초기화
            self.fig = None
            self.canvas = None
            self.ax = None
            

            
            # UI 설정
            self.setup_styles()
            self.setup_ui()
            
            # 배경 이미지 로딩
            self.create_background_buttons()
            
            # 초기 상태 설정 및 사용자 가이드
            if hasattr(self, 'info_label'):
                self.info_label.config(
                    text="🚀 시작하기: ① 사용자 선택 → ② Task 선택 → ③ 탭에서 분석 결과 확인",
                    font=('Arial', 9, 'bold')
                )
            
            # 창 크기 변경 이벤트 바인딩
            self.root.bind('<Configure>', self.on_window_resize)
            
            # 키보드 단축키 설정
            self.setup_keyboard_shortcuts()
            
            # 메모리 사용량 모니터링 (개발용)
            if logger.level == logging.DEBUG:
                self._setup_memory_monitoring()
            
            logger.info("dflux_InteractiveAnalyzer 초기화 완료")
            
        except Exception as e:
            logger.error(f"초기화 중 오류 발생: {str(e)}")
            messagebox.showerror("초기화 오류", f"프로그램 초기화 중 오류가 발생했습니다: {str(e)}")
            raise
    
    def setup_styles(self):
        """UI 스타일 설정"""
        style = ttk.Style()
        
        try:
            style.theme_use('clam')
        except Exception as e:
            logger.warning(f"테마 설정 실패, 기본 테마 사용: {e}")
        
        # 기본 버튼 스타일
        style.configure('TButton', 
                      background='#f8fafc', 
                      foreground='#1e293b',
                      font=('Arial', 9),
                      padding=(6, 3),
                      relief='raised',
                      borderwidth=1,
                      focuscolor='none')
        
        style.map('TButton',
                 background=[('pressed', '#e2e8f0'), ('active', '#f1f5f9')],
                 foreground=[('pressed', '#1e293b'), ('active', '#1e293b')],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])
        
        # 선택된 버튼 스타일
        style.configure('SelectedData.TButton',
                      background='#3b82f6',
                      foreground='white',
                      font=('Arial', 9),
                      padding=(6, 3),
                      relief='raised',
                      borderwidth=1,
                      focuscolor='none')
        
        style.map('SelectedData.TButton',
                 background=[('pressed', '#2563eb'), ('active', '#1d4ed8')],
                 foreground=[('pressed', 'white'), ('active', 'white')],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])
        
        # 선택된 배경 이미지 버튼 스타일
        style.configure('SelectedBg.TButton',
                      background='#10b981',  # 초록색 배경
                      foreground='white',
                      font=('Arial', 9),
                      padding=(6, 3),
                      relief='raised',
                      borderwidth=2,
                      focuscolor='none')
        
        style.map('SelectedBg.TButton',
                 background=[('pressed', '#059669'), ('active', '#047857')],
                 foreground=[('pressed', 'white'), ('active', 'white')],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])
        
        # 강조 버튼 스타일 (필터 영역용)
        style.configure('Accent.TButton',
                      background='#2563eb',  # 파란색 배경
                      foreground='white',
                      font=('Arial', 9, 'bold'),
                      padding=(8, 4),
                      relief='raised',
                      borderwidth=1,
                      focuscolor='none')
        
        style.map('Accent.TButton',
                 background=[('pressed', '#1d4ed8'), ('active', '#1e40af')],
                 foreground=[('pressed', 'white'), ('active', 'white')],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])
        
        # 저장 버튼 스타일 (레몬색 강조)
        style.configure('Save.TButton',
                      background='#fde047',  # 레몬색 배경
                      foreground='#1e293b',  # 어두운 텍스트
                      font=('Arial', 9, 'bold'),
                      padding=(8, 4),
                      relief='raised',
                      borderwidth=2,
                      focuscolor='none')
        
        style.map('Save.TButton',
                 background=[('pressed', '#facc15'), ('active', '#fde047')],
                 foreground=[('pressed', '#1e293b'), ('active', '#1e293b')],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])
    
    def on_window_resize(self, event=None):
        """창 크기 변경 시 업데이트"""
        # 슬라이더 재그리기 (폭 변화에 대응)
        if hasattr(self, 'time_range_slider'):
            self.root.after(100, self.time_range_slider.draw_slider)
    
    def setup_ui(self):
        """UI 설정"""
        # 사용자 선택 영역 (스크롤 가능)
        user_main_frame = ttk.Frame(self.root)
        user_main_frame.pack(side="top", fill="x", padx=5, pady=2)
        
        # 사용자 라벨
        user_label = ttk.Label(user_main_frame, text="사용자 선택:", font=('Arial', 9, 'bold'))
        user_label.pack(side="left", padx=(0, 10))
        
        # 스크롤 가능한 사용자 프레임
        user_scroll_frame = tk.Frame(user_main_frame, bg='white', relief='sunken', bd=1)
        user_scroll_frame.pack(side="left", fill="x", expand=True)
        
        user_canvas = tk.Canvas(user_scroll_frame, height=40, bg='white', 
                               highlightthickness=0)
        user_scrollbar = ttk.Scrollbar(user_scroll_frame, orient="horizontal", 
                                      command=user_canvas.xview)
        user_scrollable_frame = ttk.Frame(user_canvas)
        
        user_scrollable_frame.bind(
            "<Configure>",
            lambda e: user_canvas.configure(scrollregion=user_canvas.bbox("all"))
        )
        
        user_canvas.create_window((0, 0), window=user_scrollable_frame, anchor="nw")
        user_canvas.configure(xscrollcommand=user_scrollbar.set)
        
        user_canvas.pack(side="top", fill="both", expand=True)
        user_scrollbar.pack(side="bottom", fill="x")
        
        # 마우스 휠 스크롤 지원
        def _on_user_mousewheel(event):
            user_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        user_canvas.bind("<MouseWheel>", _on_user_mousewheel)
        
        self.create_user_buttons(user_scrollable_frame)
        
        # Task 선택 영역 (스크롤 가능)
        task_main_frame = ttk.Frame(self.root)
        task_main_frame.pack(side="top", fill="x", padx=5, pady=2)
        
        # Task 라벨
        task_label = ttk.Label(task_main_frame, text="Task 선택:", font=('Arial', 9, 'bold'))
        task_label.pack(side="left", padx=(0, 10))
        
        # 스크롤 가능한 Task 프레임
        task_scroll_frame = tk.Frame(task_main_frame, bg='white', relief='sunken', bd=1)
        task_scroll_frame.pack(side="left", fill="x", expand=True)
        
        task_canvas = tk.Canvas(task_scroll_frame, height=40, bg='white', 
                               highlightthickness=0)
        task_scrollbar = ttk.Scrollbar(task_scroll_frame, orient="horizontal", 
                                      command=task_canvas.xview)
        task_scrollable_frame = ttk.Frame(task_canvas)
        
        task_scrollable_frame.bind(
            "<Configure>",
            lambda e: task_canvas.configure(scrollregion=task_canvas.bbox("all"))
        )
        
        task_canvas.create_window((0, 0), window=task_scrollable_frame, anchor="nw")
        task_canvas.configure(xscrollcommand=task_scrollbar.set)
        
        task_canvas.pack(side="top", fill="both", expand=True)
        task_scrollbar.pack(side="bottom", fill="x")
        
        # 마우스 휠 스크롤 지원
        def _on_task_mousewheel(event):
            task_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        task_canvas.bind("<MouseWheel>", _on_task_mousewheel)
        
        self.create_task_buttons(task_scrollable_frame)
        
        # 구분선
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill="x", pady=5)
        
        # 메인 컨텐츠 영역
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 배경 이미지 선택 영역 (왼쪽, 스크롤 가능)
        bg_main_frame = ttk.Frame(content_frame)
        bg_main_frame.pack(side="left", fill="y", padx=1, pady=1)
        
        # 배경 이미지 라벨
        bg_label = ttk.Label(bg_main_frame, text="배경 이미지:", font=('Arial', 9, 'bold'))
        bg_label.pack(pady=(0, 5))
        
        # 스크롤 가능한 배경 이미지 프레임
        bg_scroll_frame = tk.Frame(bg_main_frame, bg='white', relief='sunken', bd=1)
        bg_scroll_frame.pack(fill="both", expand=True)
        
        bg_canvas = tk.Canvas(bg_scroll_frame, width=200, bg='white', 
                             highlightthickness=0)
        bg_scrollbar = ttk.Scrollbar(bg_scroll_frame, orient="vertical", 
                                    command=bg_canvas.yview)
        self.bg_content_frame = ttk.Frame(bg_canvas)
        
        self.bg_content_frame.bind(
            "<Configure>",
            lambda e: bg_canvas.configure(scrollregion=bg_canvas.bbox("all"))
        )
        
        bg_canvas.create_window((0, 0), window=self.bg_content_frame, anchor="nw")
        bg_canvas.configure(yscrollcommand=bg_scrollbar.set)
        
        bg_canvas.pack(side="left", fill="both", expand=True)
        bg_scrollbar.pack(side="right", fill="y")
        
        # 마우스 휠 스크롤 지원
        def _on_bg_mousewheel(event):
            bg_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        bg_canvas.bind("<MouseWheel>", _on_bg_mousewheel)
        
        # 구분선
        panel_separator = ttk.Separator(content_frame, orient='vertical')
        panel_separator.pack(side="left", fill="y", padx=5)
        
        # 시각화 영역 (오른쪽)
        self.setup_right_panel(content_frame)
    
    def setup_right_panel(self, parent):
        """오른쪽 패널 설정"""
        # 필터링 설정 영역 - 단순화된 구조
        filter_container = ttk.Frame(parent)
        filter_container.pack(fill=tk.X, padx=15, pady=(0, 20))
        
        # 좌측 영역 (시간 필터 + 레이어 필터)
        left_section = ttk.Frame(filter_container)
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # 우측 영역 (전체 데이터 버튼 + 시스템 메시지)
        right_section = ttk.Frame(filter_container)
        right_section.pack(side=tk.RIGHT, fill=tk.Y)
        right_section.configure(width=400)
        right_section.pack_propagate(False)
        
        # === 좌측 영역 구성 ===
        
        # 좌측 상단: 시간 필터
        time_section = ttk.Frame(left_section)
        time_section.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        
        # 시간 범위 라벨과 현재 설정 시간을 함께 표시하는 프레임
        time_title_frame = ttk.Frame(time_section)
        time_title_frame.pack(fill=tk.X, pady=(0, 8))
        
        time_status_label = ttk.Label(time_title_frame, text="시간 범위:", 
                                     font=('Arial', 9), foreground='#64748b')
        time_status_label.pack(side=tk.LEFT)
        
        # 현재 설정된 시간 범위 표시 라벨
        self.time_range_display = ttk.Label(time_title_frame, text="00:00 ~ 00:00", 
                                          font=('Arial', 9, 'bold'), foreground='#059669')
        self.time_range_display.pack(side=tk.LEFT, padx=(8, 0))
        
        # 시간 범위 슬라이더
        self.time_range_slider = RangeSlider(time_section, from_=0, to=100, 
                                           command=self.on_time_range_change)
        self.time_range_slider.pack(fill=tk.X, pady=(0, 5))
        
        # 슬라이더 초기 크기 설정
        self.root.after(100, lambda: self.time_range_slider.draw_slider())
        
        # 좌측 하단: 레이어 필터
        layer_section = ttk.Frame(left_section)
        layer_section.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 레이어 필터 설명 (제외 필터로 변경)
        layer_help = ttk.Label(layer_section, text="제외할 이벤트 키워드: (예: hwk, btn, swipe - 콤마로 구분)", 
                              font=('Arial', 9), foreground='#64748b')
        layer_help.pack(anchor=tk.W, pady=(0, 5))
        
        # 레이어 필터 입력과 X 버튼을 위한 프레임
        layer_input_frame = ttk.Frame(layer_section)
        layer_input_frame.pack(fill=tk.X, pady=(0, 8))
        
        # 레이어 필터 입력
        self.layer_filter = ttk.Entry(layer_input_frame, font=('Arial', 10), 
                                     style='TEntry')
        self.layer_filter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.layer_filter.bind('<KeyRelease>', lambda e: self.apply_filter_auto())
        
        # X 아이콘 버튼 (필터 초기화)
        clear_filter_btn = ttk.Button(layer_input_frame, text="✖", width=3,
                                     command=self.clear_filters)
        clear_filter_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # === 우측 영역 구성 ===
        
        # 우측 상단: 필터링 리셋 버튼 (고정 높이)
        button_section = ttk.Frame(right_section)
        button_section.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        button_section.configure(height=40)  # 고정 높이 설정
        button_section.pack_propagate(False)  # 자식 위젯에 의한 크기 변화 방지
        
        self.show_all_button = ttk.Button(button_section, text="🔄 필터링 리셋", 
                                         style='Accent.TButton',
                                         command=self.show_all_data)
        self.show_all_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 우측 하단: 시스템 메시지 (고정 높이)
        info_section = ttk.Frame(right_section)
        info_section.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        info_section.configure(height=120)  # 고정 높이 설정
        info_section.pack_propagate(False)  # 자식 위젯에 의한 크기 변화 방지
        
        # 시스템 메시지 라벨 (높이 축소)
        self.info_label = ttk.Label(info_section, text="사용자와 Task를 선택하고 필터를 적용해주세요.", 
                                   background="#f1f5f9", foreground="#475569",
                                   font=('Arial', 9), padding=(8, 6), anchor=tk.NW,
                                   borderwidth=1, relief='solid', wraplength=240,
                                   justify=tk.LEFT)
        self.info_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 구분선
        viz_separator = ttk.Separator(parent, orient='horizontal')
        viz_separator.pack(fill=tk.X, pady=(15, 10))
        
        # 시각화 탭들
        self.create_visualization_tabs(parent)
    

    
    def create_visualization_tabs(self, parent):
        """시각화 탭 생성"""
        # 탭 컨테이너
        tab_container = ttk.Frame(parent)
        tab_container.pack(fill=tk.BOTH, expand=True)
        
        # 탭 버튼 프레임
        tab_button_frame = ttk.Frame(tab_container)
        tab_button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 탭 버튼들
        self.tab_buttons = {}
        tab_names = ["히트맵", "플로우", "이벤트 빈도", "이벤트 시간분포", "통계"]
        
        # 탭 버튼들을 담을 프레임
        tab_group_frame = ttk.Frame(tab_button_frame)
        tab_group_frame.pack(side=tk.LEFT, padx=15, pady=15)
        

        
        for i, name in enumerate(tab_names):
            btn = ttk.Button(tab_group_frame, text=name, 
                           style='TButton',
                           command=lambda n=name: self.switch_tab(n))
            btn.pack(side=tk.LEFT, padx=(0, 4), pady=2)
            self.tab_buttons[name] = btn
        
        # 저장 버튼
        save_button_frame = ttk.Frame(tab_button_frame)
        save_button_frame.pack(side=tk.RIGHT, padx=15, pady=15)
        
        self.save_all_pdf_button = ttk.Button(save_button_frame, text="현재설정 기준 모든 시각화 이미지 PDF로 저장", 
                                             style='Save.TButton',
                                             command=self.save_all_visualizations_as_pdf)
        self.save_all_pdf_button.pack(side=tk.RIGHT)
        
        self.save_button = ttk.Button(save_button_frame, text="현재 시각화 이미지 저장", 
                                    style='Save.TButton',
                                    command=self.save_current_visualization)
        self.save_button.pack(side=tk.RIGHT, padx=(0, 15))
        
        # 탭 콘텐츠 영역
        self.tab_content_frame = ttk.Frame(tab_container)
        self.tab_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 탭 콘텐츠들
        self.tab_contents = {}
        self.create_heatmap_tab()
        self.create_flow_tab()
        self.create_layer_freq_tab()
        self.create_layer_time_tab()
        self.create_statistics_tab()
        
        # 기본 탭 설정
        self.current_tab = "히트맵"
        self.show_tab_content("히트맵")
        self.highlight_current_tab()
    
    def create_heatmap_tab(self):
        """히트맵 탭 생성"""
        heatmap_frame = ttk.Frame(self.tab_content_frame)
        self.tab_contents["히트맵"] = heatmap_frame
        
        # 그래프 프레임
        self.heatmap_graph_frame = ttk.Frame(heatmap_frame)
        self.heatmap_graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # matplotlib figure 생성 (여백 축소)
        self.heatmap_fig = Figure(figsize=(16, 3.5))
        self.heatmap_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)
        self.heatmap_canvas = FigureCanvasTkAgg(self.heatmap_fig, self.heatmap_graph_frame)
        self.heatmap_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 네비게이션 툴바
        heatmap_toolbar = NavigationToolbar2Tk(self.heatmap_canvas, self.heatmap_graph_frame)
        heatmap_toolbar.update()
    
    def create_flow_tab(self):
        """플로우 시각화 탭 생성"""
        flow_frame = ttk.Frame(self.tab_content_frame)
        self.tab_contents["플로우"] = flow_frame
        
        # 그래프 프레임
        self.flow_graph_frame = ttk.Frame(flow_frame)
        self.flow_graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # matplotlib figure 생성 (여백 축소)
        self.flow_fig = Figure(figsize=(16, 3.5))
        self.flow_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)
        self.flow_canvas = FigureCanvasTkAgg(self.flow_fig, self.flow_graph_frame)
        self.flow_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 네비게이션 툴바
        flow_toolbar = NavigationToolbar2Tk(self.flow_canvas, self.flow_graph_frame)
        flow_toolbar.update()
    
    def create_layer_freq_tab(self):
        """레이어별 이벤트 빈도 탭 생성"""
        layer_freq_frame = ttk.Frame(self.tab_content_frame)
        self.tab_contents["이벤트 빈도"] = layer_freq_frame
        
        # 그래프 프레임
        self.layer_freq_graph_frame = ttk.Frame(layer_freq_frame)
        self.layer_freq_graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # matplotlib figure 생성
        self.layer_freq_fig = Figure(figsize=(16, 8))
        self.layer_freq_canvas = FigureCanvasTkAgg(self.layer_freq_fig, self.layer_freq_graph_frame)
        self.layer_freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 네비게이션 툴바
        layer_freq_toolbar = NavigationToolbar2Tk(self.layer_freq_canvas, self.layer_freq_graph_frame)
        layer_freq_toolbar.update()
    
    def create_layer_time_tab(self):
        """레이어별 이벤트 시간 분포 탭 생성"""
        layer_time_frame = ttk.Frame(self.tab_content_frame)
        self.tab_contents["이벤트 시간분포"] = layer_time_frame
        
        # 그래프 프레임
        self.layer_time_graph_frame = ttk.Frame(layer_time_frame)
        self.layer_time_graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # matplotlib figure 생성
        self.layer_time_fig = Figure(figsize=(16, 8))
        self.layer_time_canvas = FigureCanvasTkAgg(self.layer_time_fig, self.layer_time_graph_frame)
        self.layer_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 네비게이션 툴바
        layer_time_toolbar = NavigationToolbar2Tk(self.layer_time_canvas, self.layer_time_graph_frame)
        layer_time_toolbar.update()
    
    def create_statistics_tab(self):
        """통계 탭 생성"""
        stats_frame = ttk.Frame(self.tab_content_frame)
        self.tab_contents["통계"] = stats_frame
        
        # 통계 표시 프레임
        self.stats_text_frame = ttk.Frame(stats_frame)
        self.stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스크롤바가 있는 텍스트 위젯
        stats_scrollbar = ttk.Scrollbar(self.stats_text_frame)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(self.stats_text_frame, wrap=tk.WORD, yscrollcommand=stats_scrollbar.set,
                                 font=('Arial', 10), bg='white', fg='black',
                                 padx=10, pady=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        stats_scrollbar.config(command=self.stats_text.yview)
        
        # 초기 메시지 설정
        self.stats_text.insert(tk.END, "데이터를 선택하고 필터를 적용하면 통계가 표시됩니다.")
    
    def on_time_range_change(self):
        """시간 범위 슬라이더 값이 변경될 때 호출되는 콜백"""
        start_sec, end_sec = self.time_range_slider.get_values()
        
        start_ms = start_sec * 1000
        end_ms = end_sec * 1000
        
        self.start_time_var.set(start_ms)
        self.end_time_var.set(end_ms)
        
        # 시간 범위 표시 라벨 업데이트
        self.update_time_range_display(start_sec, end_sec)
        
        if self.selected_files:
            self.apply_filter_auto()
    
    def update_time_range_display(self, start_sec, end_sec):
        """시간 범위 표시 라벨 업데이트"""
        start_min = int(start_sec // 60)
        start_sec_remainder = int(start_sec % 60)
        end_min = int(end_sec // 60)
        end_sec_remainder = int(end_sec % 60)
        
        range_text = f"{start_min:02d}:{start_sec_remainder:02d} ~ {end_min:02d}:{end_sec_remainder:02d}"
        
        if hasattr(self, 'time_range_display'):
            self.time_range_display.config(text=range_text)
    
    def apply_filter_auto(self):
        """자동 필터 적용"""
        if not self.selected_files or not hasattr(self, 'data'):
            return
        
        try:
            combined_data = self.load_and_combine_data()
            if combined_data is None:
                return
            
            filtered_data = self._apply_time_and_layer_filters(combined_data)
            self.filtered_data = filtered_data
            
            # HWK 이벤트 추출 및 슬라이더에 설정
            self._extract_and_set_hwk_events(combined_data)
            
            # 필터링된 데이터에서 이벤트 타입별로 구분
            filtered_hwk = filtered_data[
                filtered_data['Layer Name'].str.contains('HWK', case=False, na=False)
            ]
            filtered_swipe = filtered_data[
                filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
            # 터치 이벤트는 HWK와 SWIPE를 제외한 나머지 (플리킹 시작점 제외)
            # 원본 데이터를 전달하여 정확한 플리킹 단위 계산
            filtered_touch = self._get_filtered_touch_data_without_flick_starts(filtered_data, combined_data)
            
            hwk_count = len(filtered_hwk)
            flick_count = self._count_flick_events(filtered_data, combined_data)  # 원본 데이터 기준으로 플리킹 단위 카운트
            touch_count = len(filtered_touch)
            total_filtered = len(filtered_data)
            
            if total_filtered == 0:
                self.info_label.config(text="❌ 필터 조건에 맞는 데이터가 없습니다.\n다른 필터 조건을 시도해주세요.")
            else:
                layer_filter = self.layer_filter.get().strip()
                filter_info = (
                    f"📊 필터 적용 완료!\n"
                    f"• 👆 터치 이벤트: {touch_count:,}개\n"
                    f"• 🔄 플리킹 이벤트: {flick_count:,}개 (1개 단위)\n"
                    f"• 🎮 HWK 이벤트: {hwk_count:,}개\n"
                    f"• 필터된 이벤트: {total_filtered:,}개"
                )
                if layer_filter:
                    exclude_keywords = [keyword.strip() for keyword in layer_filter.split(',') if keyword.strip()]
                    if len(exclude_keywords) == 1:
                        filter_info += f"\n• 제외 필터: '{exclude_keywords[0]}' 포함 이벤트 제외"
                    else:
                        filter_info += f"\n• 제외 필터: {', '.join(exclude_keywords)} 포함 이벤트 제외"
                self.info_label.config(text=filter_info)
                
                self.update_current_visualization()
                
        except Exception as e:
            logger.error(f"자동 필터 적용 중 오류: {str(e)}")
    
    def _apply_time_and_layer_filters(self, combined_data):
        """시간 및 레이어 필터를 적용하는 공통 로직"""
        try:
            start_time = self.start_time_var.get()
            end_time = self.end_time_var.get()
            
            filtered_data = combined_data[
                (combined_data['Time(ms)'] >= start_time) & 
                (combined_data['Time(ms)'] <= end_time)
            ]
            
            # HWK 이벤트는 시각화에서 표시되어야 하므로 제외하지 않음
            # (이전에는 HWK 이벤트를 제외했지만, 사용자가 볼 수 있도록 유지)
            
            # 레이어 필터링 (제외 필터)
            layer_filter = self.layer_filter.get().strip()
            if layer_filter:
                try:
                    # 콤마로 구분된 키워드들을 분리
                    exclude_keywords = [keyword.strip() for keyword in layer_filter.split(',') if keyword.strip()]
                    
                    if exclude_keywords:
                        # 각 키워드가 포함된 이벤트를 제외
                        for keyword in exclude_keywords:
                            filtered_data = filtered_data[
                                ~filtered_data['Layer Name'].str.contains(keyword, case=False, na=False)
                            ]
                except Exception as e:
                    logger.error(f"레이어 필터링 오류: {str(e)}")
            
            return filtered_data
                
        except Exception as e:
            logger.error(f"필터 적용 중 오류: {str(e)}")
            return combined_data
    
    def _get_flick_start_points(self, filtered_data, original_data=None):
        """플리킹 시작점들을 찾아서 반환 - 플리킹 단위로 그룹화"""
        try:
            # 원본 데이터가 제공된 경우 원본에서 플리킹 단위를 계산
            if original_data is not None:
                data_to_analyze = original_data
                logger.info(f"원본 데이터에서 플리킹 단위 계산: {len(original_data)} 행")
            else:
                data_to_analyze = filtered_data
                logger.info(f"필터된 데이터에서 플리킹 단위 계산: {len(filtered_data)} 행")
            
            # SWIPE 이벤트들을 시간순으로 정렬
            swipe_events = data_to_analyze[
                data_to_analyze['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ].sort_values('Time(ms)')
            
            logger.info(f"SWIPE 이벤트 발견: {len(swipe_events)}개")
            
            flick_start_points = set()
            flick_end_points = set()  # 플리킹 종료점 (SWIPE 이벤트)
            flick_units_info = []  # 플리킹 단위 상세 정보
            
            for _, swipe_row in swipe_events.iterrows():
                current_time = swipe_row['Time(ms)']
                
                # 현재 SWIPE 이벤트보다 이전의 가장 가까운 터치 이벤트 찾기
                prev_touch = data_to_analyze[
                    (data_to_analyze['Time(ms)'] < current_time) & 
                    (~data_to_analyze['Layer Name'].str.contains('SWIPE', case=False, na=False))
                ].sort_values('Time(ms)', ascending=False)
                
                if len(prev_touch) > 0:
                    start_point = prev_touch.iloc[0]
                    # 플리킹 시작점의 인덱스를 저장
                    flick_start_points.add(start_point.name)
                    # 플리킹 종료점(SWIPE 이벤트)의 인덱스도 저장
                    flick_end_points.add(swipe_row.name)
                    
                    # 플리킹 단위 정보 저장 (시간 범위 포함)
                    flick_units_info.append({
                        'start_time': start_point['Time(ms)'],
                        'end_time': swipe_row['Time(ms)'],
                        'start_index': start_point.name,
                        'end_index': swipe_row.name,
                        'start_layer': start_point['Layer Name'],
                        'end_layer': swipe_row['Layer Name']
                    })
                    
                    logger.info(f"플리킹 단위 발견: 시작점 {start_point['Layer Name']} ({start_point['Time(ms)']}ms) -> 종료점 {swipe_row['Layer Name']} ({swipe_row['Time(ms)']}ms)")
            
            # 플리킹 단위 정보를 저장 (시작점과 종료점을 매핑)
            self.flick_units = {
                'start_points': flick_start_points,
                'end_points': flick_end_points,
                'total_flicks': len(flick_start_points),
                'units_info': flick_units_info
            }
            
            logger.info(f"총 {len(flick_start_points)}개의 플리킹 단위 계산 완료")
            return flick_start_points
            
        except Exception as e:
            logger.error(f"플리킹 시작점 찾기 실패: {str(e)}")
            return set()
    
    def _get_filtered_touch_data(self, filtered_data, original_data=None):
        """플리킹 시작점과 SWIPE 이벤트를 제외한 터치 데이터 반환 - 플리킹 단위로 처리"""
        try:
            # 원본 데이터에서 플리킹 단위를 먼저 계산
            if original_data is not None:
                self._get_flick_start_points(filtered_data, original_data)
            
            # 플리킹 시작점들 찾기
            flick_start_points = self._get_flick_start_points(filtered_data, original_data)
            
            # 일반 터치 데이터 (HWK, SWIPE 제외)
            touch_data = filtered_data[
                ~(filtered_data['Layer Name'].str.contains('HWK', case=False, na=False) |
                  filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
            ]
            
            # 플리킹 시작점들을 제외 (원본 데이터 기준으로 계산된 시작점들)
            if flick_start_points:
                touch_data = touch_data[~touch_data.index.isin(flick_start_points)]
            
            return touch_data
            
        except Exception as e:
            logger.error(f"터치 데이터 필터링 실패: {str(e)}")
            # 오류 발생 시 기존 방식으로 반환
            return filtered_data[
                ~(filtered_data['Layer Name'].str.contains('HWK', case=False, na=False) |
                  filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
            ]
    
    def _count_flick_events(self, filtered_data, original_data=None):
        """플리킹 이벤트를 1개 단위로 카운트 - 원본 데이터 기준"""
        try:
            # 원본 데이터에서 플리킹 단위를 먼저 계산
            if original_data is not None:
                self._get_flick_start_points(filtered_data, original_data)
            
            if not hasattr(self, 'flick_units'):
                self._get_flick_start_points(filtered_data, original_data)
            
            # 현재 필터링된 데이터에서 실제로 존재하는 SWIPE 이벤트 확인
            current_swipe_events = filtered_data[
                filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
            current_swipe_times = set(current_swipe_events['Time(ms)'].tolist())
            
            # 원본의 플리킹 단위 중에서 현재 필터링된 데이터에 SWIPE 이벤트가 존재하는 것만 유효한 플리킹으로 간주
            valid_flick_count = 0
            if 'units_info' in self.flick_units:
                for flick_unit in self.flick_units['units_info']:
                    if flick_unit['end_time'] in current_swipe_times:
                        valid_flick_count += 1
            
            logger.info(f"유효한 플리킹 이벤트 수: {valid_flick_count}개 (전체: {self.flick_units.get('total_flicks', 0)}개)")
            
            # 유효한 플리킹 단위 수 반환
            return valid_flick_count
            
        except Exception as e:
            logger.error(f"플리킹 이벤트 카운팅 실패: {str(e)}")
            # 기존 방식으로 SWIPE 이벤트 수 반환
            swipe_data = filtered_data[
                filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
            return len(swipe_data)
    
    def _get_filtered_touch_data_without_flick_starts(self, filtered_data, original_data=None):
        """플리킹 시작점을 제외한 터치 데이터만 반환 - 모든 카운트에서 사용"""
        try:
            # 원본 데이터에서 플리킹 단위를 먼저 계산
            if original_data is not None:
                self._get_flick_start_points(filtered_data, original_data)
            
            # 일반 터치 데이터 (HWK, SWIPE 제외)
            touch_data = filtered_data[
                ~(filtered_data['Layer Name'].str.contains('HWK', case=False, na=False) |
                  filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
            ]
            
            logger.info(f"필터링 전 터치 데이터: {len(touch_data)}개")
            
            # 플리킹 시작점들을 제외 (원본 데이터 기준으로 계산된 시작점들)
            if hasattr(self, 'flick_units') and 'units_info' in self.flick_units and self.flick_units['units_info']:
                # 현재 필터링된 데이터에서 실제로 존재하는 SWIPE 이벤트 확인
                current_swipe_events = filtered_data[
                    filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                current_swipe_times = set(current_swipe_events['Time(ms)'].tolist())
                
                logger.info(f"현재 필터링된 데이터의 SWIPE 이벤트: {len(current_swipe_events)}개")
                
                # 모든 플리킹 시작점을 제외 (SWIPE가 존재하든 안하든 상관없이)
                # 이유: 플리킹 시작점은 항상 플리킹 단위의 일부이므로 터치 이벤트로 카운트하면 안됨
                # SWIPE를 필터링하면 모든 플리킹 관련 이벤트가 제외되어야 함
                flick_start_identifiers = set()
                
                for flick_unit in self.flick_units['units_info']:
                    # 시간을 10ms 단위로 반올림하여 정확한 매칭
                    time_key = round(flick_unit['start_time'] / 10) * 10
                    layer_key = str(flick_unit['start_layer']).strip()
                    identifier = f"{time_key}_{layer_key}"
                    flick_start_identifiers.add(identifier)
                    
                    # SWIPE가 존재하는지 여부에 따라 로그 메시지 구분
                    if flick_unit['end_time'] in current_swipe_times:
                        logger.info(f"유효한 플리킹 시작점 제외: {identifier} (시간: {flick_unit['start_time']}ms, 레이어: {flick_unit['start_layer']}) - SWIPE 이벤트 존재하지만 터치로 카운트하지 않음")
                    else:
                        logger.info(f"필터링된 플리킹 단위 시작점 제외: {identifier} (시간: {flick_unit['start_time']}ms, 레이어: {flick_unit['start_layer']}) - SWIPE 이벤트 없음")
                
                logger.info(f"총 {len(flick_start_identifiers)}개의 플리킹 시작점 제외 (모든 플리킹 시작점은 터치로 카운트하지 않음)")
                
                # 필터링된 터치 데이터에서 모든 플리킹 시작점 제외
                filtered_touch_without_flick_starts = []
                excluded_count = 0
                
                for _, row in touch_data.iterrows():
                    # 현재 행의 식별자 생성
                    current_time_key = round(row['Time(ms)'] / 10) * 10
                    current_layer_key = str(row['Layer Name']).strip()
                    current_identifier = f"{current_time_key}_{current_layer_key}"
                    
                    # 플리킹 시작점이 아니면 포함
                    if current_identifier not in flick_start_identifiers:
                        filtered_touch_without_flick_starts.append(row)
                    else:
                        excluded_count += 1
                        # SWIPE가 존재하는지 여부에 따라 로그 메시지 구분
                        if any(flick_unit['end_time'] in current_swipe_times for flick_unit in self.flick_units['units_info'] 
                               if round(flick_unit['start_time'] / 10) * 10 == current_time_key and str(flick_unit['start_layer']).strip() == current_layer_key):
                            logger.info(f"유효한 플리킹 시작점 제외: {current_identifier} (시간: {row['Time(ms)']}ms, 레이어: {row['Layer Name']})")
                        else:
                            logger.info(f"필터링된 플리킹 시작점 제외: {current_identifier} (시간: {row['Time(ms)']}ms, 레이어: {row['Layer Name']})")
                
                logger.info(f"플리킹 시작점 제외 완료: {excluded_count}개 제외, {len(filtered_touch_without_flick_starts)}개 남음")
                
                # DataFrame으로 변환하여 touch_data 업데이트
                if filtered_touch_without_flick_starts:
                    touch_data = pd.DataFrame(filtered_touch_without_flick_starts)
                    logger.info(f"최종 터치 데이터: {len(touch_data)}개 (플리킹 시작점 제외 후)")
                else:
                    touch_data = pd.DataFrame(columns=touch_data.columns)
                    logger.info(f"최종 터치 데이터: 0개 (모든 터치가 플리킹 시작점이므로)")
            else:
                # 플리킹 단위 정보가 없으면 원본 데이터에서 계산
                if original_data is not None:
                    logger.info("플리킹 단위 정보가 없어 원본 데이터에서 계산")
                    self._get_flick_start_points(filtered_data, original_data)
                    
                    # 다시 플리킹 단위 정보 확인
                    if hasattr(self, 'flick_units') and 'units_info' in self.flick_units and self.flick_units['units_info']:
                        # 현재 필터링된 데이터에서 실제로 존재하는 SWIPE 이벤트 확인
                        current_swipe_events = filtered_data[
                            filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                        ]
                        current_swipe_times = set(current_swipe_events['Time(ms)'].tolist())
                        
                        logger.info(f"재계산 후 현재 필터링된 데이터의 SWIPE 이벤트: {len(current_swipe_events)}개")
                        
                        # 모든 플리킹 시작점을 제외
                        flick_start_identifiers = set()
                        
                        for flick_unit in self.flick_units['units_info']:
                            time_key = round(flick_unit['start_time'] / 10) * 10
                            layer_key = str(flick_unit['start_layer']).strip()
                            identifier = f"{time_key}_{layer_key}"
                            flick_start_identifiers.add(identifier)
                            
                            if flick_unit['end_time'] in current_swipe_times:
                                logger.info(f"재계산 후 유효한 플리킹 시작점 제외: {identifier} (시간: {flick_unit['start_time']}ms, 레이어: {flick_unit['start_layer']})")
                            else:
                                logger.info(f"재계산 후 필터링된 플리킹 단위 시작점 제외: {identifier} (시간: {flick_unit['start_time']}ms, 레이어: {flick_unit['start_layer']})")
                        
                        logger.info(f"재계산 후 총 {len(flick_start_identifiers)}개의 플리킹 시작점 제외")
                        
                        # 필터링된 터치 데이터에서 모든 플리킹 시작점 제외
                        filtered_touch_without_flick_starts = []
                        excluded_count = 0
                        
                        for _, row in touch_data.iterrows():
                            current_time_key = round(row['Time(ms)'] / 10) * 10
                            current_layer_key = str(row['Layer Name']).strip()
                            current_identifier = f"{current_time_key}_{current_layer_key}"
                            
                            if current_identifier not in flick_start_identifiers:
                                filtered_touch_without_flick_starts.append(row)
                            else:
                                excluded_count += 1
                        
                        logger.info(f"재계산 후 플리킹 시작점 제외 완료: {excluded_count}개 제외, {len(filtered_touch_without_flick_starts)}개 남음")
                        
                        # DataFrame으로 변환하여 touch_data 업데이트
                        if filtered_touch_without_flick_starts:
                            touch_data = pd.DataFrame(filtered_touch_without_flick_starts)
                            logger.info(f"재계산 후 최종 터치 데이터: {len(touch_data)}개 (플리킹 시작점 제외 후)")
                        else:
                            touch_data = pd.DataFrame(columns=touch_data.columns)
                            logger.info(f"재계산 후 최종 터치 데이터: 0개 (모든 터치가 플리킹 시작점이므로)")
                    else:
                        logger.info("재계산 후에도 플리킹 단위 정보를 찾을 수 없음")
                        # 플리킹 단위 정보가 없어도 원본 데이터에서 플리킹 시작점을 찾아서 제외
                        if original_data is not None:
                            logger.info("원본 데이터에서 직접 플리킹 시작점 찾기")
                            # 원본 데이터에서 SWIPE 이벤트 찾기
                            original_swipe_events = original_data[
                                original_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                            ]
                            
                            if len(original_swipe_events) > 0:
                                # 원본 데이터에서 플리킹 시작점 찾기
                                flick_start_identifiers = set()
                                
                                for _, swipe_row in original_swipe_events.iterrows():
                                    swipe_time = swipe_row['Time(ms)']
                                    # SWIPE 이벤트 직전의 터치 이벤트 찾기 (10ms 이내)
                                    for _, touch_row in touch_data.iterrows():
                                        touch_time = touch_row['Time(ms)']
                                        if 0 < (swipe_time - touch_time) <= 10:  # 10ms 이내의 직전 터치
                                            time_key = round(touch_time / 10) * 10
                                            layer_key = str(touch_row['Layer Name']).strip()
                                            identifier = f"{time_key}_{layer_key}"
                                            flick_start_identifiers.add(identifier)
                                            logger.info(f"직접 찾은 플리킹 시작점 제외: {identifier} (시간: {touch_time}ms, 레이어: {touch_row['Layer Name']})")
                                
                                # 찾은 플리킹 시작점 제외
                                if flick_start_identifiers:
                                    filtered_touch_without_flick_starts = []
                                    excluded_count = 0
                                    
                                    for _, row in touch_data.iterrows():
                                        current_time_key = round(row['Time(ms)'] / 10) * 10
                                        current_layer_key = str(row['Layer Name']).strip()
                                        current_identifier = f"{current_time_key}_{current_layer_key}"
                                        
                                        if current_identifier not in flick_start_identifiers:
                                            filtered_touch_without_flick_starts.append(row)
                                        else:
                                            excluded_count += 1
                                    
                                    logger.info(f"직접 찾은 플리킹 시작점 제외 완료: {excluded_count}개 제외, {len(filtered_touch_without_flick_starts)}개 남음")
                                    
                                    if filtered_touch_without_flick_starts:
                                        touch_data = pd.DataFrame(filtered_touch_without_flick_starts)
                                        logger.info(f"직접 찾은 플리킹 시작점 제외 후 최종 터치 데이터: {len(touch_data)}개")
                                    else:
                                        touch_data = pd.DataFrame(columns=touch_data.columns)
                                        logger.info(f"직접 찾은 플리킹 시작점 제외 후 최종 터치 데이터: 0개")
                                else:
                                    logger.info("직접 찾은 플리킹 시작점이 없음")
                            else:
                                logger.info("원본 데이터에 SWIPE 이벤트가 없음")
                else:
                    logger.info("원본 데이터가 없어 시작점 제외를 건너뜀")
            
            return touch_data
            
        except Exception as e:
            logger.error(f"터치 데이터 필터링 실패: {str(e)}")
            # 오류 발생 시 기존 방식으로 반환
            return filtered_data[
                ~(filtered_data['Layer Name'].str.contains('HWK', case=False, na=False) |
                  filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
            ]
    
    def _extract_and_set_hwk_events(self, combined_data):
        """HWK 이벤트와 SWIPE 이벤트를 추출하고 슬라이더에 설정"""
        try:
            hwk_data = combined_data[
                combined_data['Layer Name'].str.contains('HWK', case=False, na=False)
            ]
            swipe_data = combined_data[
                combined_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
            
            hwk_events = []
            for _, row in hwk_data.iterrows():
                try:
                    event_time = row['Time(ms)'] / 1000
                    layer_name = str(row['Layer Name'])
                
                    if 'boost' in layer_name.lower():
                        event_type = 'HWK_boost'
                    elif 'magma' in layer_name.lower():
                        event_type = 'HWK_magma'
                    elif 'drive' in layer_name.lower():
                        event_type = 'HWK_drive'
                    else:
                        event_type = 'HWK_unknown'
                
                    hwk_events.append({
                        'time': event_time,
                        'type': event_type
                    })
                except Exception as e:
                    logger.warning(f"HWK 이벤트 처리 중 오류: {str(e)}")
                    continue
            
            # SWIPE 이벤트도 HWK 이벤트와 함께 처리
            for _, row in swipe_data.iterrows():
                try:
                    event_time = row['Time(ms)'] / 1000
                    layer_name = str(row['Layer Name'])
                
                    if 'swipe_up' in layer_name.lower():
                        event_type = 'SWIPE_UP'
                    elif 'swipe_down' in layer_name.lower():
                        event_type = 'SWIPE_DOWN'
                    elif 'swipe_left' in layer_name.lower():
                        event_type = 'SWIPE_LEFT'
                    elif 'swipe_right' in layer_name.lower():
                        event_type = 'SWIPE_RIGHT'
                    else:
                        event_type = 'SWIPE_UNKNOWN'
                
                    hwk_events.append({
                        'time': event_time,
                        'type': event_type
                    })
                except Exception as e:
                    logger.warning(f"SWIPE 이벤트 처리 중 오류: {str(e)}")
                    continue
            
            if hasattr(self, 'time_range_slider'):
                self.time_range_slider.set_hwk_events(hwk_events)
                
        except Exception as e:
            logger.error(f"이벤트 추출 중 오류: {str(e)}")
    
    def show_all_data(self):
        """필터링 리셋 - 모든 필터를 초기화하고 전체 데이터 표시"""
        if not self.selected_files:
            messagebox.showwarning("경고", "사용자와 Task를 선택하세요.")
            return
        
        try:
            # 레이어 필터 초기화
            self.layer_filter.delete(0, tk.END)
            
            combined_data = self.load_and_combine_data()
            if combined_data is None:
                messagebox.showwarning("경고", "선택된 파일에서 데이터를 읽을 수 없습니다.\n파일 형식이나 권한을 확인해주세요.")
                if hasattr(self, 'info_label'):
                    self.info_label.config(text="데이터 로드 실패. 파일을 확인해주세요.")
                return
            
            # 시간 범위 계산 및 슬라이더 업데이트
            if len(combined_data) > 0:
                min_time_ms = combined_data['Time(ms)'].min()
                max_time_ms = combined_data['Time(ms)'].max()
                
                min_time_sec = 0
                max_time_sec = max_time_ms / 1000
                
                # 슬라이더 범위 업데이트
                self.time_range_slider.set_range(min_time_sec, max_time_sec)
                
                # 슬라이더 값을 전체 범위로 설정
                self.time_range_slider.start_var.set(min_time_sec)
                self.time_range_slider.end_var.set(max_time_sec)
                self.time_range_slider.draw_slider()
                self.time_range_slider.update_range_label()
                
                # 시간 변수 업데이트
                self.start_time_var.set(min_time_ms)
                self.end_time_var.set(max_time_ms)
                
                # 시간 범위 표시 라벨 업데이트
                self.update_time_range_display(min_time_sec, max_time_sec)
                
                # HWK 이벤트 추출 및 슬라이더에 즉시 설정
                self._extract_and_set_hwk_events(combined_data)
                
                # 슬라이더를 다시 그려서 HWK 이벤트를 즉시 표시
                self.time_range_slider.draw_slider()
                
                # 이벤트 타입별 개수 계산 - 플리킹 이벤트를 1개 단위로 처리
                hwk_data = combined_data[
                    combined_data['Layer Name'].str.contains('HWK', case=False, na=False)
                ]
                touch_data = self._get_filtered_touch_data_without_flick_starts(combined_data, combined_data)
                
                hwk_count = len(hwk_data)
                flick_count = self._count_flick_events(combined_data, combined_data)  # 원본 데이터 기준으로 플리킹 단위 카운트
                touch_count = len(touch_data)
                total_points = len(combined_data)
                
                self.filtered_data = combined_data
                
                # HWK 이벤트 슬라이더 표시 개수 확인
                hwk_events_count = len(self.time_range_slider.hwk_events) if hasattr(self.time_range_slider, 'hwk_events') else 0
                
                # 정보 업데이트 (이벤트 타입별 정보 포함) - 플리킹 단위로 표시
                data_info = (
                    f"📊 데이터 로드 완료!\n"
                    f"• 👆 터치 이벤트: {touch_count:,}개\n"
                    f"• 🔄 플리킹 이벤트: {flick_count:,}개 (1개 단위)\n"
                    f"• 🎮 HWK 이벤트: {hwk_count}개\n"
                    f"• 전체 이벤트: {total_points:,}개"
                )
                self.info_label.config(text=data_info)
                
                # 성공 로그
                logger.info(f"데이터 로드 성공: {total_points} 포인트, {max_time_sec:.1f}초")
                
                self.update_current_visualization()
            else:
                self.info_label.config(text="❌ 표시할 데이터가 없습니다.\n데이터 파일을 선택해주세요.")
                
        except pd.errors.EmptyDataError:
            logger.error("CSV 파일이 비어있습니다")
            messagebox.showerror("데이터 오류", "선택된 CSV 파일이 비어있습니다.")
            self.info_label.config(text="❌ 데이터 파일이 비어있습니다.\n다른 파일을 선택해주세요.")
        except pd.errors.ParserError as e:
            logger.error(f"CSV 파싱 오류: {str(e)}")
            messagebox.showerror("파일 형식 오류", "CSV 파일 형식이 올바르지 않습니다.\n파일 형식을 확인해주세요.")
            self.info_label.config(text="❌ 파일 형식 오류.\nCSV 파일 형식을 확인해주세요.")
        except MemoryError:
            logger.error("메모리 부족으로 데이터 로드 실패")
            messagebox.showerror("메모리 오류", "메모리가 부족합니다.\n더 적은 양의 데이터를 선택해주세요.")
            self.info_label.config(text="⚠️ 메모리 부족.\n데이터 양을 줄여주세요.")
        except Exception as e:
            logger.error(f"전체 데이터 표시 중 오류: {str(e)}")
            messagebox.showerror("오류", f"데이터 처리 중 오류가 발생했습니다:\n{str(e)}")
            self.info_label.config(text="❌ 데이터 처리 오류가 발생했습니다.\n다시 시도해주세요.")
    
    def clear_filters(self):
        """필터를 초기화"""
        try:
            # 레이어 필터 초기화
            if hasattr(self, 'layer_filter'):
                self.layer_filter.delete(0, tk.END)
            
            # 시간 범위를 전체 범위로 초기화
            if hasattr(self, 'time_range_slider') and hasattr(self, 'current_data'):
                if self.current_data is not None and len(self.current_data) > 0:
                    # 전체 시간 범위로 재설정
                    min_time_ms = self.current_data['Time(ms)'].min()
                    max_time_ms = self.current_data['Time(ms)'].max()
                    
                    min_time_sec = min_time_ms / 1000.0
                    max_time_sec = max_time_ms / 1000.0
                    
                    # 슬라이더 범위 재설정
                    self.time_range_slider.from_ = min_time_sec
                    self.time_range_slider.to = max_time_sec
                    self.time_range_slider.start_var.set(min_time_sec)
                    self.time_range_slider.end_var.set(max_time_sec)
                    self.time_range_slider.draw_slider()
                    
                    # 시간 변수 업데이트
                    self.start_time_var.set(min_time_ms)
                    self.end_time_var.set(max_time_ms)
                    
                    # 시간 표시 업데이트
                    self.update_time_range_display(min_time_sec, max_time_sec)
            
            # 정보 라벨 업데이트
            self.info_label.config(text="🔄 필터가 초기화되었습니다.\n필터링이 리셋되었습니다.")
            
            # 자동 필터 적용
            if hasattr(self, 'selected_files') and self.selected_files:
                self.apply_filter_auto()
            
            logger.info("필터 초기화 완료")
            
        except Exception as e:
            logger.error(f"필터 초기화 중 오류: {str(e)}")
            messagebox.showerror("오류", f"필터 초기화 중 오류가 발생했습니다: {str(e)}")
    

    
    def switch_tab(self, tab_name):
        """탭 전환"""
        self.current_tab = tab_name
        self.show_tab_content(tab_name)
        
        if hasattr(self, 'tab_buttons') and self.tab_buttons:
            self.highlight_current_tab()
        
        # 탭 전환 시 자동으로 해당 시각화 생성
        if tab_name == "히트맵":
            self.root.after(100, self.create_heatmap)
        elif tab_name == "플로우":
            self.root.after(100, self.create_flow)
        elif tab_name == "이벤트 빈도":
            self.root.after(100, self.create_layer_freq)
        elif tab_name == "이벤트 시간분포":
            self.root.after(100, self.create_layer_time)
        elif tab_name == "통계":
            self.root.after(100, self.update_statistics)
    
    def highlight_current_tab(self):
        """현재 탭 버튼 강조 표시"""
        if not hasattr(self, 'tab_buttons') or not self.tab_buttons:
            return
            
        for name, btn in self.tab_buttons.items():
            try:
                if name == self.current_tab:
                    btn.configure(style='SelectedData.TButton')
                else:
                    btn.configure(style='TButton')
            except tk.TclError:
                # 버튼이 이미 삭제된 경우 무시
                continue
    
    def update_current_visualization(self):
        """현재 탭의 시각화를 즉각적으로 업데이트"""
        if not hasattr(self, 'current_tab'):
            return
        
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.clear_all_visualizations()
            return
            
        if self.current_tab == "히트맵":
            self.create_heatmap()
        elif self.current_tab == "플로우":
            self.create_flow()
        elif self.current_tab == "이벤트 빈도":
            self.create_layer_freq()
        elif self.current_tab == "이벤트 시간분포":
            self.create_layer_time()
        elif self.current_tab == "통계":
            self.update_statistics()
    
    def clear_all_visualizations(self):
        """모든 시각화를 초기화하여 이전 결과를 제거"""
        try:
            # 히트맵 초기화
            if hasattr(self, 'heatmap_fig'):
                self.heatmap_fig.clear()
                ax = self.heatmap_fig.add_subplot(111)
                ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                if hasattr(self, 'heatmap_canvas'):
                    self.heatmap_canvas.draw()
            
            # 플로우 초기화
            if hasattr(self, 'flow_fig'):
                self.flow_fig.clear()
                ax = self.flow_fig.add_subplot(111)
                ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                if hasattr(self, 'flow_canvas'):
                    self.flow_canvas.draw()
            
            # 레이어 분석 초기화
            if hasattr(self, 'layer_freq_fig'):
                self.layer_freq_fig.clear()
                ax = self.layer_freq_fig.add_subplot(111)
                ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                if hasattr(self, 'layer_freq_canvas'):
                    self.layer_freq_canvas.draw()
            
            # 시간 분석 초기화
            if hasattr(self, 'layer_time_fig'):
                self.layer_time_fig.clear()
                ax = self.layer_time_fig.add_subplot(111)
                ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                if hasattr(self, 'layer_time_canvas'):
                    self.layer_time_canvas.draw()
            
            # 통계 초기화
            if hasattr(self, 'stats_text'):
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, "데이터가 없습니다.\n사용자와 Task를 선택해주세요.")
                
        except Exception as e:
            logger.error(f"시각화 초기화 중 오류: {str(e)}")
    
    # 히트맵 생성 메서드들 (기존 로직을 그대로 유지하되 최적화)
    def create_heatmap(self):
        """히트맵 생성"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.heatmap_fig.clear()
            ax = self.heatmap_fig.add_subplot(111)
            ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.heatmap_canvas.draw()
            return
        
        # 이벤트 타입별 데이터 추출
        try:
            # 원본 데이터에서 플리킹 단위를 계산하여 정확한 터치 데이터 추출
            original_data = None
            for user_data in self.data.values():
                for task_data in user_data.values():
                    if len(task_data) > 0:
                        original_data = task_data
                        break
                if original_data is not None:
                    break
            
            touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
            swipe_data = self.filtered_data[
                self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
        except Exception as e:
            logger.error(f"이벤트 필터링 실패: {str(e)}")
            touch_data = self.filtered_data
            swipe_data = pd.DataFrame()
        
        try:
            self.heatmap_fig.clear()
            
            # 배경을 투명하게 설정
            self.heatmap_fig.patch.set_alpha(0.0)
            
            # 여백 축소
            self.heatmap_fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.15)
            
            # 터치 좌표 추출
            x_coords = touch_data['TouchX'].values
            y_coords = touch_data['TouchY'].values
            
            # 히트맵 생성
            ax = self.heatmap_fig.add_subplot(111)
            
            # 히트맵 데이터 준비
            if len(x_coords) > 0:
                try:
                    # 적응적 bins 크기로 성능 최적화 (셀 크기를 약 1.5배로 세분화)
                    data_density = len(x_coords) // 1000 + 1
                    bins_x = min(133, max(53, data_density * 27))   # 가로 블럭 개수 약 1.5배 증가
                    bins_y = min(27, max(13, data_density * 5))     # 세로 블럭 개수 약 1.5배 증가
                    
                    heatmap_data, xedges, yedges = np.histogram2d(x_coords, y_coords, 
                                                                 bins=[bins_x, bins_y], 
                                                                 range=[[0, self.screen_width], [0, self.screen_height]])
                
                    # 히트맵 표시 (메모리 효율성 개선)
                    heatmap_data_masked = heatmap_data.T
                    heatmap_data_masked = np.where(heatmap_data_masked == 0, np.nan, heatmap_data_masked)
                
                    im = ax.imshow(heatmap_data_masked, origin='upper', 
                                  extent=[0, self.screen_width, self.screen_height, 0],
                                  aspect='auto', cmap='RdYlGn_r', alpha=0.7)
                except Exception as e:
                    logger.error(f"히트맵 데이터 생성 실패: {str(e)}")
                    im = None
            else:
                im = None
                # 터치 데이터가 없을 때 안내 메시지
                ax.text(0.5, 0.5, '터치 이벤트가 없습니다.\n필터 조건을 확인해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12, color='gray')
            
            # 배경 이미지 추가
            if self.background_image_path and os.path.exists(self.background_image_path):
                try:
                    img = Image.open(self.background_image_path)
                    img_resized = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                    ax.imshow(img_resized, extent=[0, self.screen_width, self.screen_height, 0], 
                             alpha=0.8, zorder=0)
                except FileNotFoundError:
                    logger.warning(f"배경 이미지 파일을 찾을 수 없습니다: {self.background_image_path}")
                    self.background_image_path = ""  # 잘못된 경로 초기화
                except PIL.UnidentifiedImageError:
                    logger.error(f"지원되지 않는 이미지 형식: {self.background_image_path}")
                    self.background_image_path = ""
                except MemoryError:
                    logger.error("이미지가 너무 커서 메모리 부족")
                    self.background_image_path = ""
                except Exception as e:
                    logger.error(f"배경 이미지 로드 실패: {str(e)}")
                    self.background_image_path = ""
            
            # 히트맵을 배경 이미지 위에 표시
            if im is not None:
                im.set_zorder(1)
                
                # 가로형 컬러바 추가 (정수 눈금, 크기 축소)
                cbar = self.heatmap_fig.colorbar(im, ax=ax, orientation='horizontal', 
                                                shrink=0.4, aspect=40, pad=0.05)
                cbar.set_label('터치 빈도', fontsize=8)
                cbar.ax.tick_params(labelsize=6)
                
                # 컬러바 배경을 투명하게 설정
                cbar.ax.set_facecolor('none')
                cbar.outline.set_alpha(0.0)
                
                # 정수 눈금 설정
                max_freq = int(np.nanmax(heatmap_data_masked)) if not np.isnan(np.nanmax(heatmap_data_masked)) else 1
                if max_freq > 0:
                    ticks = np.linspace(0, max_freq, min(6, max_freq + 1))
                    cbar.set_ticks(ticks)
                    cbar.set_ticklabels([str(int(tick)) for tick in ticks])
            
            # 화면 경계 설정
            ax.set_xlim(0, self.screen_width)
            ax.set_ylim(self.screen_height, 0)
            
            # 축 배경을 투명하게 설정
            ax.set_facecolor('none')
            
            # 터치 좌표 점들 추가
            if len(x_coords) > 0:
                # 터치 포인트 표시 (원형)
                ax.scatter(x_coords, y_coords, c='white', s=20, alpha=0.8, zorder=3, 
                          edgecolors='black', linewidth=1.0)
            
            # 플리킹 화살표 추가
            if len(swipe_data) > 0:
                try:
                    # 플리킹 이벤트를 시간순으로 정렬
                    swipe_data_sorted = swipe_data.sort_values('Time(ms)')
                    
                    for idx, row in swipe_data_sorted.iterrows():
                        # 플리킹 종료점 (SWIPE 이벤트 좌표)
                        end_x = row['TouchX']
                        end_y = row['TouchY']
                        layer_name = str(row['Layer Name']).lower()
                        
                        # 플리킹 시작점 찾기 (SWIPE 직전 좌표)
                        current_time = row['Time(ms)']
                        # 현재 SWIPE 이벤트보다 이전의 가장 가까운 터치 이벤트 찾기
                        prev_touch = self.filtered_data[
                            (self.filtered_data['Time(ms)'] < current_time) & 
                            (~self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
                        ].sort_values('Time(ms)', ascending=False)
                        
                        if len(prev_touch) > 0:
                            start_x = prev_touch.iloc[0]['TouchX']
                            start_y = prev_touch.iloc[0]['TouchY']
                            
                            # 화살표 색상 결정 (방향에 관계없이 통일)
                            arrow_color = '#06b6d4'  # 시안블루로 플리킹 이벤트 통일
                            
                            # 두께감 있는 화살표 그리기
                            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                                       arrowprops=dict(arrowstyle='->', color=arrow_color, 
                                                     lw=4, alpha=0.8, shrinkA=0, shrinkB=0))
                            
                except Exception as e:
                    logger.error(f"플리킹 화살표 그리기 실패: {str(e)}")
            
            # 축 눈금과 라벨 숨기기
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')
            
            # 제목 추가
            ax.set_title('터치 히트맵 + 플리킹 화살표 (좌표 기반)', fontsize=12, pad=10)
            
            self.heatmap_canvas.draw()
            
        except Exception as e:
            logger.error(f"히트맵 생성 중 오류: {str(e)}")
            messagebox.showerror("오류", f"히트맵 생성 중 오류가 발생했습니다: {str(e)}")
            self.info_label.config(text="❌ 히트맵 생성 중 오류가 발생했습니다.\n다시 시도해주세요.")
    

    
    def create_flow(self):
        """플로우 시각화 생성"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.flow_fig.clear()
            ax = self.flow_fig.add_subplot(111)
            ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.flow_canvas.draw()
            return
        
        # 이벤트 타입별 데이터 추출
        try:
            # 원본 데이터에서 플리킹 단위를 계산하여 정확한 터치 데이터 추출
            original_data = None
            for user_data in self.data.values():
                for task_data in user_data.values():
                    if len(task_data) > 0:
                        original_data = task_data
                        break
                if original_data is not None:
                    break
            
            touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
            swipe_data = self.filtered_data[
                self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
        except Exception as e:
            logger.error(f"이벤트 필터링 실패: {str(e)}")
            touch_data = self.filtered_data
            swipe_data = pd.DataFrame()
        
        try:
            self.flow_fig.clear()
            
            # 배경을 투명하게 설정
            self.flow_fig.patch.set_alpha(0.0)
            
            # 여백 설정 (히트맵과 동일하게 통일)
            self.flow_fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.15)
            
            ax = self.flow_fig.add_subplot(111)
            
            # 터치 좌표 추출
            x_coords = touch_data['TouchX'].values
            y_coords = touch_data['TouchY'].values
            
            # 배경 이미지 추가 (투명도 감소로 가시성 향상)
            if self.background_image_path and os.path.exists(self.background_image_path):
                try:
                    img = Image.open(self.background_image_path)
                    img_resized = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                    ax.imshow(img_resized, extent=[0, self.screen_width, self.screen_height, 0], 
                             alpha=0.25, zorder=0)  # 투명도 감소
                except Exception as e:
                    logger.error(f"배경 이미지 로드 실패: {str(e)}")
            
            # 터치 순서 색상 팔레트 생성
            colors = plt.cm.plasma(np.linspace(0, 1, len(x_coords))) if len(x_coords) > 0 else []
            
            # 터치 데이터가 없을 때 안내 메시지
            if len(x_coords) == 0:
                ax.text(0.5, 0.5, '터치 이벤트가 없습니다.\n필터 조건을 확인해주세요.', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12, color='gray')
            
            # 연결선 그리기 (터치 순서 색상 적용)
            if len(x_coords) > 1:
                try:
                    # 각 선분을 개별적으로 그려서 색상 변화 적용 (선 굵기 축소)
                    for i in range(len(x_coords) - 1):
                        # 선분의 시작점 색상 사용
                        segment_color = colors[i]
                        ax.plot([x_coords[i], x_coords[i+1]], [y_coords[i], y_coords[i+1]], 
                               color=segment_color, alpha=0.9, linewidth=1.5, zorder=2)
                except Exception as e:
                    logger.error(f"연결선 그리기 실패: {str(e)}")
            
            # 터치 포인트 그리기 (터치 이벤트만 표시)
            if len(x_coords) > 0:
                try:
                    # 터치 포인트 표시 (원형)
                    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                        ax.scatter(x, y, c=[colors[i]], s=20, alpha=0.8, 
                                  edgecolors='black', linewidth=1.0, zorder=3)
                        
                        # 번호 표시 (처음 20개만)
                        if i < 20:
                            circle = plt.Circle((x, y), 20, facecolor='white', edgecolor='#1f2937', 
                                              linewidth=1, alpha=0.95, zorder=4)
                            ax.add_patch(circle)
                            ax.text(x, y, str(i+1), ha='center', va='center', 
                                   fontsize=11, fontweight='bold', color=colors[i], zorder=5)
                    
                    # 화살표 추가 개선 (처음 10개만으로 제한)
                    for i in range(min(10, len(x_coords) - 1)):
                        try:
                            dx = x_coords[i+1] - x_coords[i]
                            dy = y_coords[i+1] - y_coords[i]
                            
                            arrow_length = min(60, np.sqrt(dx**2 + dy**2) * 0.4)
                            if arrow_length > 8:
                                # 터치 순서 색상을 화살표에 적용
                                ax.arrow(x_coords[i], y_coords[i], 
                                        dx * arrow_length / np.sqrt(dx**2 + dy**2), 
                                        dy * arrow_length / np.sqrt(dx**2 + dy**2), 
                                        head_width=15, head_length=20, fc=colors[i], ec=colors[i], 
                                        alpha=0.9, linewidth=3, zorder=4)
                        except Exception as e:
                            logger.warning(f"화살표 그리기 실패 (인덱스 {i}): {str(e)}")
                            continue
                except Exception as e:
                    logger.error(f"터치 포인트 그리기 실패: {str(e)}")
            
            # 플리킹 화살표 추가
            if len(swipe_data) > 0:
                try:
                    # 플리킹 이벤트를 시간순으로 정렬
                    swipe_data_sorted = swipe_data.sort_values('Time(ms)')
                    
                    for idx, row in swipe_data_sorted.iterrows():
                        # 플리킹 종료점 (SWIPE 이벤트 좌표)
                        end_x = row['TouchX']
                        end_y = row['TouchY']
                        layer_name = str(row['Layer Name']).lower()
                        
                        # 플리킹 시작점 찾기 (SWIPE 직전 좌표)
                        current_time = row['Time(ms)']
                        # 현재 SWIPE 이벤트보다 이전의 가장 가까운 터치 이벤트 찾기
                        prev_touch = self.filtered_data[
                            (self.filtered_data['Time(ms)'] < current_time) & 
                            (~self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False))
                        ].sort_values('Time(ms)', ascending=False)
                        
                        if len(prev_touch) > 0:
                            start_x = prev_touch.iloc[0]['TouchX']
                            start_y = prev_touch.iloc[0]['TouchY']
                            
                            # 화살표 색상 결정 (방향에 관계없이 통일)
                            arrow_color = '#06b6d4'  # 시안블루로 플리킹 이벤트 통일
                            
                            # 두께감 있는 화살표 그리기 (히트맵과 동일한 두께)
                            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                                       arrowprops=dict(arrowstyle='->', color=arrow_color, 
                                                     lw=4, alpha=0.8, shrinkA=0, shrinkB=0))
                            
                except Exception as e:
                    logger.error(f"플리킹 화살표 그리기 실패: {str(e)}")
            
            # 화면 경계 설정 (히트맵과 동일한 방식으로 통일)
            ax.set_xlim(0, self.screen_width)
            ax.set_ylim(self.screen_height, 0)
            
            # 축 배경을 투명하게 설정
            ax.set_facecolor('none')
            
            # 축 눈금과 라벨 숨기기
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')
            
            # 제목 추가
            ax.set_title('터치 플로우 + 플리킹 화살표 (좌표 기반)', fontsize=12, pad=10)
            
            # 플로우 범례 추가 (히트맵과 동일한 스타일)
            if len(x_coords) > 0:
                try:
                    # 시간 순서에 따른 색상 변화를 보여주는 범례
                    norm = plt.Normalize(0, len(x_coords) - 1)
                    sm = plt.cm.ScalarMappable(cmap=plt.cm.plasma, norm=norm)
                    sm.set_array([])
                    
                    # 히트맵과 동일한 스타일의 가로형 컬러바
                    cbar = self.flow_fig.colorbar(sm, ax=ax, orientation='horizontal', 
                                                shrink=0.4, aspect=40, pad=0.05)
                    cbar.set_label('터치 순서', fontsize=8)
                    cbar.ax.tick_params(labelsize=6)
                    
                    # 컬러바 배경을 투명하게 설정
                    cbar.ax.set_facecolor('none')
                    cbar.outline.set_alpha(0.0)
                    
                    # 눈금 설정 (처음, 중간, 마지막)
                    if len(x_coords) > 1:
                        ticks = [0, len(x_coords) // 2, len(x_coords) - 1]
                        tick_labels = ['시작', '중간', '끝']
                        cbar.set_ticks(ticks)
                        cbar.set_ticklabels(tick_labels)
                    else:
                        cbar.set_ticks([0])
                        cbar.set_ticklabels(['시작'])
                        
                except Exception as e:
                    logger.error(f"플로우 범례 생성 실패: {str(e)}")
            
            self.flow_canvas.draw()
            
        except Exception as e:
            logger.error(f"플로우 생성 중 오류: {str(e)}")
            messagebox.showerror("오류", f"플로우 생성 중 오류가 발생했습니다: {str(e)}")
            self.info_label.config(text="❌ 플로우 생성 중 오류가 발생했습니다.\n다시 시도해주세요.")
    
    def create_layer_freq(self):
        """이벤트 빈도 생성"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.layer_freq_fig.clear()
            ax = self.layer_freq_fig.add_subplot(111)
            ax.text(0.5, 0.5, '데이터가 없습니다.\n데이터 파일을 선택하고 필터를 적용해주세요.', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.layer_freq_canvas.draw()
            return
        
        try:
            self.layer_freq_fig.clear()
            
            # 배경을 투명하게 설정
            self.layer_freq_fig.patch.set_alpha(0.0)
            
            ax = self.layer_freq_fig.add_subplot(111)
            
            # 축 배경을 투명하게 설정
            ax.set_facecolor('none')
            
            if len(self.filtered_data) > 0:
                # 플리킹 시작점을 제외한 데이터 준비
                # 원본 데이터에서 플리킹 단위를 계산하여 정확한 터치 데이터 추출
                original_data = None
                for user_data in self.data.values():
                    for task_data in user_data.values():
                        if len(task_data) > 0:
                            original_data = task_data
                            break
                    if original_data is not None:
                        break
                
                filtered_touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
                hwk_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('HWK', case=False, na=False)
                ]
                swipe_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                
                # 모든 데이터를 하나로 합치기 (플리킹 시작점 제외된 터치 + HWK + SWIPE)
                combined_filtered_data = pd.concat([filtered_touch_data, hwk_data, swipe_data])
                
                # 레이어별 빈도 계산 (시간분포와 동일한 순서 사용)
                layer_freq_data = []
                layer_labels = []
                layer_colors = []
                
                for layer in combined_filtered_data['Layer Name'].unique():
                    layer_count = len(combined_filtered_data[combined_filtered_data['Layer Name'] == layer])
                    if layer_count > 0:
                        layer_freq_data.append(layer_count)
                        layer_labels.append(layer)
                        event_type = self.get_event_type(layer)
                        layer_colors.append(self.get_event_color(event_type))
                
                if layer_freq_data:
                    # 가로 막대 그래프
                    bars = ax.barh(range(len(layer_freq_data)), layer_freq_data, color=layer_colors)
                    ax.set_yticks(range(len(layer_freq_data)))
                    ax.set_yticklabels(layer_labels, fontsize=7, rotation=45, ha='right')
                    ax.set_xlabel('이벤트 횟수', fontsize=8)
                    ax.set_title('이벤트 빈도', fontsize=10, pad=8)
                    
                    # x축 눈금을 정수로만 표시
                    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
                    
                    # 그리드 추가 (숫자가 표시된 눈금에만)
                    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
                    
                    # 범례 추가
                    legend_elements = [
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('HWK'), label='HWK'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('SWIPE'), label='플리킹'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('AREA'), label='AREA'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('BTN'), label='BTN'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('OTHER'), label='OTHER')
                    ]
                    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=6)
                    
                    # 범례 배경을 투명하게 설정
                    legend.get_frame().set_facecolor('none')
                    legend.get_frame().set_alpha(0.0)
                else:
                    ax.text(0.5, 0.5, '표시할 이벤트가 없습니다.\n필터 조건을 확인해주세요.', ha='center', va='center', transform=ax.transAxes, fontsize=10)
                    ax.set_title('이벤트 빈도', fontsize=10, pad=8)
            else:
                ax.text(0.5, 0.5, '데이터가 없습니다.\n사용자와 Task를 선택해주세요.', ha='center', va='center', transform=ax.transAxes, fontsize=10)
                ax.set_title('이벤트 빈도', fontsize=10, pad=8)
            
            self.layer_freq_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("오류", f"이벤트 빈도 생성 중 오류가 발생했습니다: {str(e)}")
            self.info_label.config(text="❌ 이벤트 빈도 생성 중 오류가 발생했습니다.\n다시 시도해주세요.")
    
    def create_layer_time(self):
        """레이어별 이벤트 시간 분포 생성"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.layer_time_fig.clear()
            ax = self.layer_time_fig.add_subplot(111)
            ax.text(0.5, 0.5, '데이터가 없습니다.\n데이터 파일을 선택하고 필터를 적용해주세요.', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.layer_time_canvas.draw()
            return
        
        try:
            self.layer_time_fig.clear()
            
            # 배경을 투명하게 설정
            self.layer_time_fig.patch.set_alpha(0.0)
            
            ax = self.layer_time_fig.add_subplot(111)
            
            # 축 배경을 투명하게 설정
            ax.set_facecolor('none')
            
            if len(self.filtered_data) > 0:
                # 플리킹 시작점을 제외한 데이터 준비
                # 원본 데이터에서 플리킹 단위를 계산하여 정확한 터치 데이터 추출
                original_data = None
                for user_data in self.data.values():
                    for task_data in user_data.values():
                        if len(task_data) > 0:
                            original_data = task_data
                            break
                    if original_data is not None:
                        break
                
                filtered_touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
                hwk_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('HWK', case=False, na=False)
                ]
                swipe_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                
                # 모든 데이터를 하나로 합치기 (플리킹 시작점 제외된 터치 + HWK + SWIPE)
                combined_filtered_data = pd.concat([filtered_touch_data, hwk_data, swipe_data])
                
                # 시간을 초 단위로 변환
                time_data = combined_filtered_data.copy()
                time_data['Time_sec'] = time_data['Time(ms)'] / 1000
                
                # 레이어별 시간 분포 박스플롯
                layer_time_data = []
                layer_labels = []
                layer_colors = []
                
                for layer in time_data['Layer Name'].unique():
                    layer_data = time_data[time_data['Layer Name'] == layer]['Time_sec']
                    if len(layer_data) > 0:
                        layer_time_data.append(layer_data.values)
                        layer_labels.append(layer)
                        event_type = self.get_event_type(layer)
                        layer_colors.append(self.get_event_color(event_type))
                
                if layer_time_data:
                    # 가로 박스플롯
                    bp = ax.boxplot(layer_time_data, tick_labels=layer_labels, patch_artist=True, vert=False)
                    
                    # 박스 색상 설정
                    for patch, color in zip(bp['boxes'], layer_colors):
                        patch.set_facecolor(color)
                        patch.set_alpha(0.7)
                    
                    ax.set_title('이벤트 시간분포', fontsize=10, pad=8)
                    ax.set_ylabel('레이어', fontsize=8)
                    ax.set_xlabel('시간 (초)', fontsize=8)
                    ax.set_yticklabels(layer_labels, fontsize=7, rotation=45, ha='right')
                    
                    # 시간 범위 필터 설정값 가져오기
                    start_sec, end_sec = self.time_range_slider.get_values()
                    
                    # x축 범위를 시간 범위 필터와 동일하게 설정
                    x_min = start_sec
                    x_max = end_sec
                    time_range = x_max - x_min
                    
                    # x축 범위 설정
                    ax.set_xlim(x_min, x_max)
                    
                    # 모든 1초 단위 눈금 생성
                    all_ticks = np.arange(int(x_min), int(x_max) + 1, 1)
                    ax.set_xticks(all_ticks)
                    
                    # 시간 범위에 따라 숫자 표시 간격 결정
                    if time_range <= 10:  # 10초 이하: 1초 단위
                        label_interval = 1
                    elif time_range <= 50:  # 50초 이하: 5초 단위
                        label_interval = 5
                    else:  # 50초 초과: 10초 단위
                        label_interval = 10
                    
                    # 숫자 라벨 생성 (간격에 따라 선택적으로 표시)
                    x_labels = []
                    for tick in all_ticks:
                        if tick % label_interval == 0:
                            x_labels.append(str(int(tick)))
                        else:
                            x_labels.append('')
                    
                    ax.set_xticklabels(x_labels, fontsize=7)
                    
                    # 기본 그리드 추가 (모든 1초 단위 눈금)
                    ax.grid(axis='x', alpha=0.2, linestyle='--', linewidth=0.3)
                    
                    # 5초 단위 그리드를 약간 진하게 추가
                    if time_range > 10:  # 10초 초과일 때만 5초 단위 그리드 추가
                        five_sec_ticks = [tick for tick in all_ticks if tick % 5 == 0]
                        if five_sec_ticks:
                            ax.vlines(five_sec_ticks, ymin=0, ymax=len(layer_labels), 
                                    colors='gray', alpha=0.35, linestyle='-', linewidth=0.7)
                    
                    # 범례 추가
                    legend_elements = [
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('HWK'), alpha=0.7, label='HWK'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('SWIPE'), alpha=0.7, label='플리킹'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('AREA'), alpha=0.7, label='AREA'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('BTN'), alpha=0.7, label='BTN'),
                        plt.Rectangle((0,0),1,1, facecolor=self.get_event_color('OTHER'), alpha=0.7, label='OTHER')
                    ]
                    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=6)
                    
                    # 범례 배경을 투명하게 설정
                    legend.get_frame().set_facecolor('none')
                    legend.get_frame().set_alpha(0.0)
                    
                else:
                    ax.text(0.5, 0.5, '표시할 이벤트가 없습니다.\n필터 조건을 확인해주세요.', ha='center', va='center', transform=ax.transAxes, fontsize=10)
                    ax.set_title('이벤트 시간분포', fontsize=10, pad=8)
            
            self.layer_time_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("오류", f"이벤트 시간분포 생성 중 오류가 발생했습니다: {str(e)}")
            self.info_label.config(text="❌ 이벤트 시간분포 생성 중 오류가 발생했습니다.\n다시 시도해주세요.")
    
    def update_statistics(self):
        """통계 정보 업데이트"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "데이터가 없습니다.\n사용자와 Task를 선택해주세요.")
            return
        
        try:
            self.stats_text.delete(1.0, tk.END)
            
            # 이벤트 타입별 분리
            hwk_data = self.filtered_data[
                self.filtered_data['Layer Name'].str.contains('HWK', case=False, na=False)
            ]
            
            # 원본 데이터에서 플리킹 단위를 계산하기 위해 원본 데이터 찾기
            # 필터링과 동일한 방식으로 combined_data 가져오기
            original_data = None
            try:
                # load_and_combine_data()와 동일한 로직으로 원본 데이터 결합
                combined_data = self.load_and_combine_data()
                if combined_data is not None:
                    original_data = combined_data
                    logger.info(f"통계 탭: 원본 데이터 결합 완료 - {len(combined_data)} 행")
                else:
                    logger.warning("통계 탭: load_and_combine_data()에서 None 반환")
            except Exception as e:
                logger.error(f"통계 탭: 원본 데이터 결합 중 오류: {str(e)}")
            
            # 원본 데이터가 없으면 fallback으로 기존 방식 사용
            if original_data is None and hasattr(self, 'data') and self.data:
                logger.info("통계 탭: fallback으로 기존 방식 사용")
                for user_data in self.data.values():
                    if isinstance(user_data, dict):
                        for task_data in user_data.values():
                            if isinstance(task_data, pd.DataFrame) and len(task_data) > 0:
                                original_data = task_data
                                break
                        if original_data is not None:
                            break
            
            # 원본 데이터가 없으면 필터된 데이터 사용
            if original_data is None:
                original_data = self.filtered_data
                logger.warning("통계 탭: 원본 데이터를 찾을 수 없어 필터된 데이터 사용")
            
            # 통계 탭에서도 다른 시각화와 동일한 로직 사용
            # 플리킹 단위 정보를 먼저 계산 (원본 데이터 기준)
            if not hasattr(self, 'flick_units') or not self.flick_units:
                self._get_flick_start_points(self.filtered_data, original_data)
            
            # 플리킹 단위 정보가 제대로 계산되었는지 확인
            if not hasattr(self, 'flick_units') or not self.flick_units or 'units_info' not in self.flick_units:
                logger.warning("통계 탭: 플리킹 단위 정보를 찾을 수 없어 다시 계산")
                self._get_flick_start_points(self.filtered_data, original_data)
            
            # 플리킹 시작점이 제외된 터치 데이터 가져오기
            touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
            
            # 디버깅: 터치 데이터 상태 확인
            logger.info(f"통계 탭: 터치 데이터 상태 - 원본: {len(self.filtered_data[~(self.filtered_data['Layer Name'].str.contains('HWK|SWIPE', case=False, na=False))])}개, 플리킹 시작점 제외 후: {len(touch_data)}개")
            
            # SWIPE 데이터 추출 (필터링된 데이터에서)
            swipe_data = self.filtered_data[
                self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
            ]
            
            # 전체 통계 (플리킹 시작점 제외된 실제 이벤트 수)
            # 플리킹 시작점이 제외된 실제 터치 이벤트 + HWK + SWIPE
            actual_total_events = len(touch_data) + len(hwk_data) + len(swipe_data)
            
            hwk_count = len(hwk_data)
            flick_count = self._count_flick_events(self.filtered_data, original_data)  # 원본 데이터 기준으로 플리킹 단위 카운트
            touch_count = len(touch_data)
            swipe_count = len(swipe_data)
            
            # 고유 레이어 수도 플리킹 시작점이 제외된 실제 데이터 기준으로 계산
            # 실제 이벤트 데이터를 합쳐서 고유 레이어 수 계산
            actual_event_data = pd.concat([touch_data, hwk_data, swipe_data])
            unique_layers = actual_event_data['Layer Name'].nunique()
            
            # 전체 이벤트 수는 플리킹 시작점이 제외된 실제 이벤트 수로 사용
            total_events = actual_total_events
            
            # 디버깅을 위한 로그 추가
            logger.info(f"통계 계산 - 터치: {touch_count}개, HWK: {hwk_count}개, SWIPE: {swipe_count}개, 총: {total_events}개")
            
            # 시간 통계
            time_stats = self.filtered_data['Time(ms)'].describe()
            total_time_seconds = (self.filtered_data['Time(ms)'].max() - self.filtered_data['Time(ms)'].min()) / 1000
            
            # 통계 텍스트 생성
            stats_text = f"""
=== 이벤트 분석 통계 ===

📊 전체 이벤트 정보:
• 총 이벤트 수: {total_events:,}개
• 고유 레이어 수: {unique_layers}개
• 총 소요 시간: {total_time_seconds:.2f}초

🎯 이벤트 타입별 분포:
• 터치 이벤트: {touch_count:,}개 ({touch_count/total_events*100:.1f}%)
• 플리킹 이벤트: {flick_count:,}개 ({flick_count/total_events*100:.1f}%) (1개 단위)
• HWK 이벤트: {hwk_count:,}개 ({hwk_count/total_events*100:.1f}%)

⏰ 시간 분석:
• 최초 이벤트: {self.filtered_data['Time(ms)'].min() / 1000:.2f}초
• 마지막 이벤트: {self.filtered_data['Time(ms)'].max() / 1000:.2f}초
• 평균 이벤트 간격: {time_stats['mean'] / 1000:.2f}초
"""
            
            # 터치 이벤트 분석 (플리킹 시작점 제외)
            if len(touch_data) > 0:
                x_stats = touch_data['TouchX'].describe()
                y_stats = touch_data['TouchY'].describe()
                
                stats_text += f"""
👆 터치 이벤트 분석 (플리킹 시작점 제외):
• 터치 밀도: {touch_count / total_time_seconds:.2f} 터치/초
• X좌표 범위: {x_stats['min']:.0f} ~ {x_stats['max']:.0f} (평균: {x_stats['mean']:.1f})
• Y좌표 범위: {y_stats['min']:.0f} ~ {y_stats['max']:.0f} (평균: {y_stats['mean']:.1f})
"""
            
            # HWK 이벤트 분석
            if len(hwk_data) > 0:
                hwk_types = {}
                for _, row in hwk_data.iterrows():
                    layer_name = str(row['Layer Name']).lower()
                    if 'boost' in layer_name:
                        hwk_type = 'HWK_boost'
                    elif 'magma' in layer_name:
                        hwk_type = 'HWK_magma'
                    elif 'drive' in layer_name:
                        hwk_type = 'HWK_drive'
                    else:
                        hwk_type = 'HWK_unknown'
                    
                    if hwk_type not in hwk_types:
                        hwk_types[hwk_type] = 0
                    hwk_types[hwk_type] += 1
                
                stats_text += f"""
🎮 HWK 이벤트 분석 (게임 특화):
• HWK 밀도: {hwk_count / total_time_seconds:.2f} HWK/초
• 전체 이벤트 대비 HWK 비율: {hwk_count/total_events*100:.1f}%

🎯 HWK 타입별 분포:
"""
                
                for hwk_type, count in hwk_types.items():
                    percentage = (count / hwk_count) * 100
                    hwk_emoji = {
                        'HWK_boost': '🚀',
                        'HWK_magma': '🔥',
                        'HWK_drive': '🏎️',
                        'HWK_unknown': '❓'
                    }.get(hwk_type, '🎮')
                    stats_text += f"• {hwk_emoji} {hwk_type}: {count}회 ({percentage:.1f}%)\n"
            
            # 플리킹 이벤트 분석
            if flick_count > 0:
                # SWIPE 데이터에서 방향별 분포 계산
                swipe_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                
                swipe_types = {}
                for _, row in swipe_data.iterrows():
                    layer_name = str(row['Layer Name']).lower()
                    if 'swipe_up' in layer_name:
                        swipe_type = 'SWIPE_UP'
                    elif 'swipe_down' in layer_name:
                        swipe_type = 'SWIPE_DOWN'
                    elif 'swipe_left' in layer_name:
                        swipe_type = 'SWIPE_LEFT'
                    elif 'swipe_right' in layer_name:
                        swipe_type = 'SWIPE_RIGHT'
                    else:
                        swipe_type = 'SWIPE_UNKNOWN'
                    
                    if swipe_type not in swipe_types:
                        swipe_types[swipe_type] = 0
                    swipe_types[swipe_type] += 1
                
                stats_text += f"""
🔄 플리킹 이벤트 분석 (1개 단위):
• 플리킹 밀도: {flick_count / total_time_seconds:.2f} 플리킹/초
• 터치 대비 플리킹 비율: {flick_count/(touch_count+flick_count)*100:.1f}%

🎯 플리킹 방향별 분포:
"""
                
                for swipe_type, count in swipe_types.items():
                    percentage = (count / len(swipe_data)) * 100
                    direction_emoji = {
                        'SWIPE_UP': '⬆️',
                        'SWIPE_DOWN': '⬇️', 
                        'SWIPE_LEFT': '⬅️',
                        'SWIPE_RIGHT': '➡️',
                        'SWIPE_UNKNOWN': '↔️'
                    }.get(swipe_type, '❓')
                    stats_text += f"• {direction_emoji} {swipe_type}: {count}회 ({percentage:.1f}%)\n"
            
            # 레이어별 통계 (터치 이벤트만, 플리킹 시작점 제외)
            if len(touch_data) > 0:
                touch_layer_stats = touch_data['Layer Name'].value_counts()
                
                stats_text += f"""
🎯 터치 레이어별 분포 (플리킹 시작점 제외):
"""
                
                for layer, count in touch_layer_stats.head(10).items():
                    percentage = (count / touch_count) * 100
                    stats_text += f"• 📍 {layer}: {count}회 ({percentage:.1f}%)\n"
                
                if len(touch_layer_stats) > 10:
                    stats_text += f"• ... 기타 {len(touch_layer_stats) - 10}개 레이어\n"
            
            # 플리킹 레이어별 통계
            if flick_count > 0:
                # SWIPE 데이터에서 레이어별 분포 계산
                swipe_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                swipe_layer_stats = swipe_data['Layer Name'].value_counts()
                
                stats_text += f"""
🎯 플리킹 레이어별 분포 (1개 단위):
"""
                
                for layer, count in swipe_layer_stats.head(5).items():
                    percentage = (count / len(swipe_data)) * 100
                    stats_text += f"• 🔄 {layer}: {count}회 ({percentage:.1f}%)\n"
                
                if len(swipe_layer_stats) > 5:
                    stats_text += f"• ... 기타 {len(swipe_layer_stats) - 5}개 레이어\n"
            
            self.stats_text.insert(tk.END, stats_text)
                
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"통계 생성 중 오류가 발생했습니다: {str(e)}")
    
    def get_event_type(self, layer_name):
        """레이어 이름을 기반으로 이벤트 타입을 분류"""
        layer_name_lower = layer_name.lower()
        
        if 'hwk' in layer_name_lower:
            return 'HWK'
        elif 'swipe' in layer_name_lower:
            return 'SWIPE'
        elif 'area' in layer_name_lower:
            return 'AREA'
        elif 'btn' in layer_name_lower or 'button' in layer_name_lower:
            return 'BTN'
        else:
            return 'OTHER'
    
    def get_event_color(self, event_type):
        """이벤트 타입에 따른 색상 반환"""
        color_map = {
            'HWK': '#a855f7',  # 자주색으로 HWK 이벤트 통일
            'SWIPE': '#06b6d4',  # 시안블루로 플리킹 이벤트 통일
            'AREA': '#f59e0b',
            'BTN': '#10b981',
            'OTHER': '#22c55e'  # 연두색으로 OTHER 이벤트 구분
        }
        return color_map.get(event_type, '#6b7280')
    
    def save_current_visualization(self):
        """현재 선택된 시각화를 저장"""
        if not hasattr(self, 'current_tab'):
            messagebox.showwarning("경고", "선택된 시각화가 없습니다.")
            return
        
        # 현재 탭에 따른 figure 결정
        fig = None
        viz_type_name = ""
        
        if self.current_tab == "히트맵":
            fig = self.heatmap_fig
            viz_type_name = "히트맵"
        elif self.current_tab == "플로우":
            fig = self.flow_fig
            viz_type_name = "플로우"
        elif self.current_tab == "이벤트 빈도":
            fig = self.layer_freq_fig
            viz_type_name = "이벤트빈도"
        elif self.current_tab == "이벤트 시간분포":
            fig = self.layer_time_fig
            viz_type_name = "이벤트시간분포"
        else:
            messagebox.showwarning("경고", "통계 탭은 저장할 수 없습니다.")
            return
        
        if fig is None:
            messagebox.showwarning("경고", "먼저 시각화를 생성하세요.")
            return
        
        # 선택된 사용자와 태스크 정보 가져오기
        if not self.selected_users:
            selected_users = "선택안됨"
        else:
            # 전체 사용자 목록 가져오기
            all_users = set(self.get_user_list())
            
            # 모든 사용자가 선택되었는지 확인 (개별 선택 또는 "모든 사용자" 버튼)
            if (self.selected_users == all_users or 
                len(self.selected_users) == len(all_users)):
                selected_users = "모든사용자"
                logger.info(f"모든 사용자 선택됨: {len(self.selected_users)}명")
            else:
                selected_users = "_".join(sorted(self.selected_users))
                logger.info(f"일부 사용자 선택됨: {list(self.selected_users)}")
        
        # 선택된 task 확인
        selected_tasks = set()
        for task_num, btn in self.task_buttons.items():
            try:
                if btn.cget('style') == 'SelectedData.TButton':
                    selected_tasks.add(task_num)
            except tk.TclError:
                # 버튼이 이미 삭제된 경우 무시
                continue
        
        selected_task = "_".join([f"Task{num}" for num in sorted(selected_tasks)]) if selected_tasks else "선택안됨"
        
        # 파일명 생성
        filename = f"{viz_type_name}_{selected_task}_{selected_users}.png"
        logger.info(f"생성된 파일명: {filename}")
        
        # output_results 폴더에 저장
        output_dir = ensure_output_dir()
        
        # 파일명 중복 확인 및 숫자 추가
        base_filename = filename
        counter = 1
        while os.path.exists(os.path.join(output_dir, filename)):
            name_without_ext = base_filename[:-4]
            filename = f"{name_without_ext}_{counter}.png"
            counter += 1
        
        file_path = os.path.join(output_dir, filename)
        
        try:
            # 배경을 투명하게 저장 (transparent=True)
            fig.savefig(file_path, dpi=300, bbox_inches='tight', transparent=True)
            messagebox.showinfo("성공", f"파일이 저장되었습니다:\n{file_path}")
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 중 오류 발생: {str(e)}")
    
    def save_all_visualizations_as_pdf(self):
        """현재 설정 기준으로 모든 시각화를 PDF로 저장"""
        if not hasattr(self, 'filtered_data') or self.filtered_data is None or len(self.filtered_data) == 0:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.\n먼저 사용자와 Task를 선택하세요.")
            return
        
        try:
            # 선택된 사용자와 태스크 정보 가져오기
            if not self.selected_users:
                selected_users = "선택안됨"
            else:
                # 전체 사용자 목록 가져오기
                all_users = set(self.get_user_list())
                
                # 모든 사용자가 선택되었는지 확인
                if (self.selected_users == all_users or 
                    len(self.selected_users) == len(all_users)):
                    selected_users = "모든사용자"
                else:
                    selected_users = "_".join(sorted(self.selected_users))
            
            # 선택된 task 확인
            selected_tasks = set()
            for task_num, btn in self.task_buttons.items():
                try:
                    if btn.cget('style') == 'SelectedData.TButton':
                        selected_tasks.add(task_num)
                except tk.TclError:
                    continue
            
            selected_task = "_".join([f"Task{num}" for num in sorted(selected_tasks)]) if selected_tasks else "선택안됨"
            
            # 파일명 생성
            filename = f"모든시각화_{selected_task}_{selected_users}.pdf"
            
            # output_results 폴더에 저장
            output_dir = ensure_output_dir()
            
            # 파일명 중복 확인 및 숫자 추가
            base_filename = filename
            counter = 1
            while os.path.exists(os.path.join(output_dir, filename)):
                name_without_ext = base_filename[:-4]
                filename = f"{name_without_ext}_{counter}.pdf"
                counter += 1
            
            file_path = os.path.join(output_dir, filename)
            
            # PDF 생성을 위한 Figure 객체들 준비
            figures_to_save = []
            figure_names = []
            
            # 히트맵
            if hasattr(self, 'heatmap_fig') and self.heatmap_fig:
                # 히트맵 새로 생성
                self.create_heatmap()
                figures_to_save.append(self.heatmap_fig)
                figure_names.append("히트맵")
            
            # 플로우
            if hasattr(self, 'flow_fig') and self.flow_fig:
                # 플로우 새로 생성
                self.create_flow()
                figures_to_save.append(self.flow_fig)
                figure_names.append("플로우")
            
            # 이벤트 빈도
            if hasattr(self, 'layer_freq_fig') and self.layer_freq_fig:
                # 이벤트 빈도 새로 생성
                self.create_layer_freq()
                figures_to_save.append(self.layer_freq_fig)
                figure_names.append("이벤트 빈도")
            
            # 이벤트 시간분포
            if hasattr(self, 'layer_time_fig') and self.layer_time_fig:
                # 이벤트 시간분포 새로 생성
                self.create_layer_time()
                figures_to_save.append(self.layer_time_fig)
                figure_names.append("이벤트 시간분포")
            
            if not figures_to_save:
                messagebox.showwarning("경고", "저장할 시각화가 없습니다.")
                return
            
            # PDF 저장
            from matplotlib.backends.backend_pdf import PdfPages
            
            # 통일된 페이지 크기 설정 (16:9 비율, 축소된 크기)
            page_width = 8.0   # 인치 단위
            page_height = 4.5  # 16:9 비율
            dpi = 150  # DPI 축소로 파일 크기 감소
            
            with PdfPages(file_path) as pdf:
                # 각 시각화를 PDF 페이지로 저장
                for i, fig in enumerate(figures_to_save):
                    # 페이지 제목 설정 (사용자명 제거)
                    fig.suptitle(f"{figure_names[i]} - {selected_task}", 
                               fontsize=12, y=0.95)
                    
                    # 통일된 크기로 설정
                    fig.set_size_inches(page_width, page_height)
                    
                    # 여백 설정 (좌우상하 여백 추가)
                    fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.12)
                    
                    # PDF에 페이지 추가 (여백 포함하여 저장)
                    pdf.savefig(fig, bbox_inches='tight', dpi=dpi, 
                              pad_inches=0.3)  # 추가 여백
                    
                    # 제목 제거 (원래 상태로 복원)
                    if hasattr(fig, 'suptitle'):
                        fig.suptitle("")
                
                # 통계 정보 페이지 추가
                if hasattr(self, 'filtered_data') and self.filtered_data is not None:
                    self._add_statistics_page_to_pdf(pdf, selected_task, selected_users, page_width, page_height, dpi)
            
            # 성공 메시지
            saved_count = len(figures_to_save)
            messagebox.showinfo("성공", 
                              f"모든 시각화가 PDF로 저장되었습니다!\n\n"
                              f"파일: {file_path}\n"
                              f"저장된 시각화: {saved_count}개\n"
                              f"• {', '.join(figure_names)}")
            
            logger.info(f"모든 시각화 PDF 저장 완료: {file_path}, {saved_count}개 시각화")
            
        except ImportError:
            messagebox.showerror("오류", "PDF 저장을 위해 matplotlib.backends.backend_pdf가 필요합니다.")
        except Exception as e:
            logger.error(f"PDF 저장 중 오류: {str(e)}")
            messagebox.showerror("오류", f"PDF 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _add_statistics_page_to_pdf(self, pdf, selected_task, selected_users, page_width, page_height, dpi):
        """PDF에 통계 정보 페이지 추가"""
        try:
            # 통계 데이터 준비
            hwk_data = self.filtered_data[
                self.filtered_data['Layer Name'].str.contains('HWK', case=False, na=False)
            ]
            
            # 원본 데이터에서 플리킹 단위를 계산하기 위해 원본 데이터 찾기
            original_data = None
            if hasattr(self, 'data') and self.data:
                # data는 원본 데이터의 딕셔너리
                for user_data in self.data.values():
                    if isinstance(user_data, dict):
                        for task_data in user_data.values():
                            if isinstance(task_data, pd.DataFrame) and len(task_data) > 0:
                                original_data = task_data
                                break
                        if original_data is not None:
                            break
            
            # 원본 데이터가 없으면 필터된 데이터 사용
            if original_data is None:
                original_data = self.filtered_data
            
            touch_data = self._get_filtered_touch_data_without_flick_starts(self.filtered_data, original_data)
            
            # 기본 통계 계산
            total_events = len(self.filtered_data)
            hwk_count = len(hwk_data)
            flick_count = self._count_flick_events(self.filtered_data, original_data)  # 원본 데이터 기준으로 플리킹 단위 카운트
            touch_count = len(touch_data)
            total_time_seconds = (self.filtered_data['Time(ms)'].max() - self.filtered_data['Time(ms)'].min()) / 1000
            
            # 통계 페이지 생성
            fig, ax = plt.subplots(figsize=(page_width, page_height))
            fig.suptitle(f"통계 정보 - {selected_task}", fontsize=12, y=0.95)
            
            # 여백 설정
            fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.12)
            
            # 통계 텍스트 생성
            stats_text = f"""
📊 분석 통계 요약

📈 전체 이벤트 정보:
• 총 이벤트 수: {total_events:,}개
• 총 소요 시간: {total_time_seconds:.2f}초
• 평균 이벤트 밀도: {total_events/total_time_seconds:.2f} 이벤트/초

🎯 이벤트 타입별 분포:
• 터치 이벤트: {touch_count:,}개 ({touch_count/total_events*100:.1f}%)
• 플리킹 이벤트: {flick_count:,}개 ({flick_count/total_events*100:.1f}%) (1개 단위)
• HWK 이벤트: {hwk_count:,}개 ({hwk_count/total_events*100:.1f}%)

⏰ 시간 분석:
• 최초 이벤트: {self.filtered_data['Time(ms)'].min() / 1000:.2f}초
• 마지막 이벤트: {self.filtered_data['Time(ms)'].max() / 1000:.2f}초
• 평균 이벤트 간격: {self.filtered_data['Time(ms)'].describe()['mean'] / 1000:.2f}초
"""
            
            # 터치 이벤트 상세 분석
            if len(touch_data) > 0:
                x_stats = touch_data['TouchX'].describe()
                y_stats = touch_data['TouchY'].describe()
                stats_text += f"""

👆 터치 이벤트 분석:
• 터치 밀도: {touch_count / total_time_seconds:.2f} 터치/초
• X좌표 범위: {x_stats['min']:.0f} ~ {x_stats['max']:.0f} (평균: {x_stats['mean']:.1f})
• Y좌표 범위: {y_stats['min']:.0f} ~ {y_stats['max']:.0f} (평균: {y_stats['mean']:.1f})
"""
            
            # HWK 이벤트 상세 분석
            if len(hwk_data) > 0:
                hwk_types = {}
                for _, row in hwk_data.iterrows():
                    layer_name = str(row['Layer Name']).lower()
                    if 'boost' in layer_name:
                        hwk_type = 'HWK_boost'
                    elif 'magma' in layer_name:
                        hwk_type = 'HWK_magma'
                    elif 'drive' in layer_name:
                        hwk_type = 'HWK_drive'
                    else:
                        hwk_type = 'HWK_unknown'
                    
                    if hwk_type not in hwk_types:
                        hwk_types[hwk_type] = 0
                    hwk_types[hwk_type] += 1
                
                stats_text += f"""

🎮 HWK 이벤트 분석:
• HWK 밀도: {hwk_count / total_time_seconds:.2f} HWK/초
• 전체 이벤트 대비 HWK 비율: {hwk_count/total_events*100:.1f}%

🎯 HWK 타입별 분포:
"""
                
                for hwk_type, count in hwk_types.items():
                    percentage = (count / hwk_count) * 100
                    hwk_emoji = {
                        'HWK_boost': '🚀',
                        'HWK_magma': '🔥',
                        'HWK_drive': '🏎️',
                        'HWK_unknown': '❓'
                    }.get(hwk_type, '🎮')
                    stats_text += f"• {hwk_emoji} {hwk_type}: {count}회 ({percentage:.1f}%)\n"
            
            # 플리킹 이벤트 상세 분석
            if flick_count > 0:
                # SWIPE 데이터에서 방향별 분포 계산
                swipe_data = self.filtered_data[
                    self.filtered_data['Layer Name'].str.contains('SWIPE', case=False, na=False)
                ]
                
                swipe_types = {}
                for _, row in swipe_data.iterrows():
                    layer_name = str(row['Layer Name']).lower()
                    if 'swipe_up' in layer_name:
                        swipe_type = 'SWIPE_UP'
                    elif 'swipe_down' in layer_name:
                        swipe_type = 'SWIPE_DOWN'
                    elif 'swipe_left' in layer_name:
                        swipe_type = 'SWIPE_LEFT'
                    elif 'swipe_right' in layer_name:
                        swipe_type = 'SWIPE_RIGHT'
                    else:
                        swipe_type = 'SWIPE_UNKNOWN'
                    
                    if swipe_type not in swipe_types:
                        swipe_types[swipe_type] = 0
                    swipe_types[swipe_type] += 1
                
                stats_text += f"""

🔄 플리킹 이벤트 분석 (1개 단위):
• 플리킹 밀도: {flick_count / total_time_seconds:.2f} 플리킹/초
• 터치 대비 플리킹 비율: {flick_count/(touch_count+flick_count)*100:.1f}%

🎯 플리킹 방향별 분포:
"""
                
                for swipe_type, count in swipe_types.items():
                    percentage = (count / len(swipe_data)) * 100
                    direction_emoji = {
                        'SWIPE_UP': '⬆️',
                        'SWIPE_DOWN': '⬇️', 
                        'SWIPE_LEFT': '⬅️',
                        'SWIPE_RIGHT': '➡️',
                        'SWIPE_UNKNOWN': '↔️'
                    }.get(swipe_type, '❓')
                    stats_text += f"• {direction_emoji} {swipe_type}: {count}회 ({percentage:.1f}%)\n"
            
            # 통계 텍스트를 그래프에 표시
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', horizontalalignment='left',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
            
            # 축 숨기기
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # PDF에 통계 페이지 추가
            pdf.savefig(fig, bbox_inches='tight', dpi=dpi, pad_inches=0.3)
            
            # 메모리 정리
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"통계 페이지 생성 중 오류: {str(e)}")
    
    def _setup_memory_monitoring(self) -> None:
        """메모리 사용량 모니터링 설정 (디버그 모드)"""
        try:
            import psutil
            self._monitor_memory()
        except ImportError:
            logger.debug("psutil이 설치되지 않아 메모리 모니터링을 건너뜁니다.")
    
    def _monitor_memory(self) -> None:
        """메모리 사용량 모니터링"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            logger.debug(f"현재 메모리 사용량: {memory_mb:.1f} MB")
            
            # 캐시 크기 정보
            if hasattr(self, '_data_cache'):
                cache_size = len(self._data_cache)
                logger.debug(f"데이터 캐시 크기: {cache_size}개 파일")
            
            # 5초마다 모니터링
            self.root.after(5000, self._monitor_memory)
        except Exception:
            pass  # 메모리 모니터링 실패는 무시
    
    def cleanup_resources(self) -> None:
        """리소스 정리"""
        try:
            # 캐시 클리어
            if hasattr(self, 'clear_cache'):
                self.clear_cache()
            
            # matplotlib 메모리 클리어
            plt.close('all')
            
            # 데이터 클리어
            if hasattr(self, 'data'):
                self.data.clear()
            
            if hasattr(self, 'filtered_data'):
                self.filtered_data = None
            
            logger.info("리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {str(e)}")


# 추가 메서드들 (InteractiveVisualizer 클래스에 추가됨)
def show_quick_help(self):
    """간단한 도움말 표시"""
    help_text = """🎯 dflux_InteractiveAnalyzer 사용법

1️⃣ 사용자 선택: 데이터가 있는 사용자를 클릭하세요
2️⃣ Task 선택: Task 1~10 중 원하는 번호를 선택하세요  
3️⃣ 배경 이미지: 왼쪽에서 원하는 배경을 선택하세요 (선택사항)
4️⃣ 시각화 확인: 히트맵, 플로우, 통계 탭에서 결과를 확인하세요
5️⃣ 저장: 저장 버튼으로 이미지를 저장하세요

💡 유용한 팁:
• 회색으로 표시된 사용자는 데이터가 없습니다
• 시간 슬라이더로 특정 구간만 분석할 수 있습니다
• Ctrl+S를 눌러 빠르게 저장할 수 있습니다
• 레이어 필터로 특정 UI 요소만 분석 가능합니다

📁 데이터 준비:
data_log/{사용자명}/ 폴더에 CSV 파일을 넣어주세요."""
    
    messagebox.showinfo("사용법 안내", help_text)


def get_user_file_count(self, user):
    """특정 사용자의 CSV 파일 개수 반환"""
    return self.data_manager.get_user_file_count(user)


def setup_keyboard_shortcuts(self):
    """키보드 단축키 설정"""
    # 저장 단축키
    self.root.bind('<Control-s>', lambda e: self.save_current_visualization())
    self.root.bind('<Control-S>', lambda e: self.save_current_visualization())
    
    # 도움말 단축키
    self.root.bind('<F1>', lambda e: self.show_quick_help())
    self.root.bind('<Control-h>', lambda e: self.show_quick_help())
    
    # 새로고침 단축키
    self.root.bind('<F5>', lambda e: self.refresh_data())
    
    # 종료 단축키
    self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    # 숫자키로 Task 선택 (1-9, 0은 Task 10)
    for i in range(1, 10):
        self.root.bind(f'<Key-{i}>', lambda e, task=i: self.select_task_by_key(task))
    self.root.bind('<Key-0>', lambda e: self.select_task_by_key(10))


def refresh_data(self):
    """데이터 새로고침"""
    try:
        # 기존 데이터 클리어
        self.data.clear()
        self.filtered_data = None
        
        # 사용자 목록 다시 로드
        users = self.get_user_list()
        
        # UI 업데이트 (사용자 버튼 다시 생성은 복잡하므로 메시지만)
        messagebox.showinfo("새로고침 완료", f"{len(users)}명의 사용자를 다시 로드했습니다.")
        
    except Exception as e:
        logger.error(f"데이터 새로고침 오류: {e}")


def select_task_by_key(self, task_num):
    """키보드로 Task 선택"""
    try:
        if hasattr(self, 'task_buttons') and task_num in self.task_buttons:
            # Task 버튼이 존재하면 클릭 시뮬레이션
            self.task_buttons[task_num].invoke()
        else:
            logger.warning(f"Task {task_num} 버튼을 찾을 수 없습니다")
    except Exception as e:
        logger.error(f"키보드 Task 선택 오류: {e}")


# InteractiveVisualizer 클래스에 이 메서드들을 추가해야 합니다
InteractiveVisualizer.show_quick_help = show_quick_help
InteractiveVisualizer.get_user_file_count = get_user_file_count
InteractiveVisualizer.setup_keyboard_shortcuts = setup_keyboard_shortcuts
InteractiveVisualizer.refresh_data = refresh_data
InteractiveVisualizer.select_task_by_key = select_task_by_key
