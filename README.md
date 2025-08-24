# Selenium 테스트 프로젝트

이 프로젝트는 Python과 Selenium을 사용한 웹 자동화 테스트 프로젝트입니다.

## 설치 방법

### macOS/Linux (로컬 환경)

1. 가상환경 생성 (권장):
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

### Ubuntu 서버 환경

1. 시스템 패키지 업데이트:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Python 및 pip 설치:
```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. Chrome 브라우저 설치:
```bash
# Chrome 저장소 추가
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Chrome 설치
sudo apt update
sudo apt install google-chrome-stable -y
```

4. 필수 시스템 라이브러리 설치:
```bash
sudo apt install -y \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    xorg \
    openbox \
    x11-xserver-utils
```

5. 프로젝트 설정:
```bash
# 프로젝트 디렉토리로 이동
cd seleniumtest

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## 프로젝트 구조

```
seleniumtest/
├── requirements.txt          # Python 패키지 의존성
├── README.md                # 프로젝트 설명서
├── config/                  # 설정 파일들
│   └── config.py
├── tests/                   # 테스트 파일들
│   ├── __init__.py
│   └── test_example.py
├── pages/                   # Page Object Model
│   ├── __init__.py
│   └── base_page.py
├── utils/                   # 유틸리티 함수들
│   ├── __init__.py
│   └── driver_factory.py
└── reports/                 # 테스트 결과 리포트
```

## 사용 방법

### 기본 테스트 실행
```bash
python -m pytest tests/
```

### 헤드리스 모드 실행 (Ubuntu 서버 권장)
```bash
# 환경 변수로 헤드리스 모드 설정
export HEADLESS=true
python run_tests.py --headless

# 또는 직접 pytest 사용
python -m pytest tests/ --headless
```

### HTML 리포트 생성
```bash
python -m pytest tests/ --html=reports/report.html
```

### 특정 테스트 실행
```bash
python -m pytest tests/test_example.py::test_function_name
```

### Ubuntu 서버에서 실행 스크립트 사용
```bash
# 헤드리스 모드로 전체 테스트 실행
python run_tests.py --headless

# 특정 브라우저로 실행
python run_tests.py --browser=firefox --headless

# 특정 테스트 파일만 실행
python run_tests.py tests/test_simple.py --headless
```

## 주요 기능

- WebDriver 자동 관리 (webdriver-manager)
- Page Object Model 패턴
- HTML 테스트 리포트 생성
- 환경 설정 관리
- 크로스 브라우저 테스트 지원
- **Ubuntu 서버 환경 최적화**

## 브라우저 지원

- Chrome (Ubuntu 서버에서 권장)
- Firefox
- Safari
- Edge

## Ubuntu 서버 환경 특별 고려사항

### 1. 헤드리스 모드 필수
Ubuntu 서버에는 GUI가 없으므로 반드시 헤드리스 모드로 실행해야 합니다:
```bash
export HEADLESS=true
```

### 2. 메모리 사용량 최적화
서버 환경에서는 메모리 사용량을 최소화하는 것이 좋습니다:
```bash
# Chrome 옵션에 추가
--disable-dev-shm-usage
--no-sandbox
--disable-gpu
--disable-extensions
```

### 3. 로그 관리
서버 환경에서는 로그를 파일로 저장하는 것이 좋습니다:
```bash
python run_tests.py --headless > test.log 2>&1
```

### 4. 스케줄링
cron을 사용하여 정기적으로 테스트를 실행할 수 있습니다:
```bash
# crontab -e
0 2 * * * cd /path/to/seleniumtest && source venv/bin/activate && python run_tests.py --headless
```
