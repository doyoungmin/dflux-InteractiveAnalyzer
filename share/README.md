# dflux_InteractiveAnalyzer - 독립 실행 버전

이 폴더는 윈도우와 맥 모두에서 독립적으로 실행할 수 있는 dflux_InteractiveAnalyzer 프로그램입니다.

## 🚀 빠른 시작

### Windows에서 실행
```bash
# Python이 설치되어 있는 경우
python main.py

# 또는 실행 파일로 실행
dflux_InteractiveAnalyzer.exe
```

### macOS에서 실행
```bash
# Python이 설치되어 있는 경우
python3 main.py

# 또는 실행 파일로 실행
./dflux_InteractiveAnalyzer
```

## 📁 폴더 구조

```
share/
├── main.py                    # 메인 실행 파일
├── interactive_visualizer.py  # 메인 GUI 애플리케이션
├── base_visualizer.py        # 기본 시각화 클래스
├── config/
│   └── settings.py           # 설정 파일
├── src/
│   └── touch_analyzer/       # 핵심 모듈
│       ├── core/             # 핵심 기능
│       └── utils/            # 유틸리티
├── requirements.txt           # Python 의존성
├── setup.py                  # 설치 스크립트
├── run.bat                   # Windows 실행 스크립트
├── run.sh                    # macOS/Linux 실행 스크립트
└── README.md                 # 이 파일
```

## 🔧 설치 및 실행

### 1. Python 환경 확인
```bash
# Python 버전 확인 (3.8 이상 필요)
python --version
# 또는
python3 --version
```

### 2. 의존성 설치
```bash
# Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

### 3. 프로그램 실행
```bash
# Windows
python main.py

# macOS/Linux
python3 main.py
```

## 📊 기능

- **터치 이벤트 분석**: 터치 좌표, 빈도, 패턴 분석
- **플리킹 이벤트 분석**: 스와이프 동작과 시작점 분석
- **HWK 이벤트 분석**: 게임 특화 하드웨어 키 이벤트
- **시각화**: 히트맵, 플로우, 빈도, 시간분포 그래프
- **필터링**: 시간 범위, 레이어, 사용자별 필터링
- **통계**: 상세한 이벤트 통계 및 분석

## 🎯 사용법

1. **데이터 로드**: 사용자와 Task 선택
2. **필터 적용**: 시간 범위 및 레이어 필터 설정
3. **시각화 확인**: 다양한 탭에서 분석 결과 확인
4. **결과 저장**: 이미지 또는 PDF로 결과 저장

## 🔧 설정

`config/settings.py` 파일에서 다음 설정을 변경할 수 있습니다:

- 화면 해상도
- 메모리 임계값
- 캐시 설정
- 성능 옵션

## 🐛 문제 해결

### Python 오류
```bash
# 의존성 재설치
pip install --upgrade -r requirements.txt
```

### 메모리 부족
- `config/settings.py`에서 메모리 임계값 조정
- 데이터 파일 크기 확인

### 실행 파일 오류
- Python 환경 확인
- 필요한 라이브러리 설치 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.8 이상)
2. 필요한 라이브러리 설치
3. 데이터 파일 형식
4. 시스템 메모리

## 🔄 업데이트

새 버전이 있을 때:
1. 기존 폴더 백업
2. 새 파일로 교체
3. 의존성 재설치: `pip install -r requirements.txt`

---

**버전**: 2.0 (최적화 버전)
**최종 업데이트**: 2024년 12월

