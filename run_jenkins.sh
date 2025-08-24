#!/bin/bash

# Jenkins 환경용 Selenium 테스트 실행 스크립트
# 가상 디스플레이 없이 헤드리스 모드로 실행

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Jenkins 환경 감지
is_jenkins() {
    [ -n "$JENKINS_URL" ] || [ -n "$BUILD_NUMBER" ] || [ -d "/var/lib/jenkins" ]
}

# 시스템 의존성 확인
check_dependencies() {
    log_info "시스템 의존성 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않았습니다."
        log_info "시스템 관리자에게 다음 명령어로 설치를 요청하세요:"
        log_info "sudo apt update && sudo apt install python3 python3-pip"
        return 1
    fi
    
    # pip 확인
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3가 설치되지 않았습니다."
        log_info "시스템 관리자에게 다음 명령어로 설치를 요청하세요:"
        log_info "sudo apt install python3-pip"
        return 1
    fi
    
    # Chrome 확인
    if ! command -v google-chrome &> /dev/null; then
        log_warning "Chrome이 설치되지 않았습니다."
        log_info "시스템 관리자에게 다음 명령어로 설치를 요청하세요:"
        log_info "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
        log_info "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
        log_info "sudo apt update && sudo apt install google-chrome-stable"
    fi
    
    log_success "시스템 의존성 확인 완료"
}

# Python 환경 설정
setup_python_environment() {
    log_info "Python 가상환경 설정 중..."
    
    # 가상환경 생성
    if [ ! -d "venv" ]; then
        log_info "가상환경 생성 중..."
        python3 -m venv venv
    fi
    
    # 가상환경 활성화 (Jenkins 호환 방식)
    if is_jenkins; then
        log_info "Jenkins 환경에서 가상환경 활성화 중..."
        . venv/bin/activate
    else
        log_info "일반 환경에서 가상환경 활성화 중..."
        . venv/bin/activate
    fi
    
    # pip 업그레이드
    log_info "pip 업그레이드 중..."
    pip install --upgrade pip
    
    # 의존성 설치
    log_info "Python 패키지 설치 중..."
    pip install -r requirements.txt
    
    log_success "Python 환경 설정 완료"
}

# 환경 설정
setup_environment() {
    log_info "환경 설정 중..."
    
    # 환경 변수 설정
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    export DISPLAY=":99"
    
    # Chrome 옵션 설정
    export CHROME_OPTIONS="--headless,--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-extensions,--disable-plugins,--disable-images,--disable-javascript,--disable-background-timer-throttling,--disable-backgrounding-occluded-windows,--disable-renderer-backgrounding,--disable-features=TranslateUI,--disable-ipc-flooding-protection"
    
    # 디렉토리 생성
    mkdir -p reports/screenshots
    mkdir -p logs
    
    log_success "환경 설정 완료"
}

# 테스트 실행
run_tests() {
    log_info "Selenium 테스트 실행 중..."
    
    # 가상환경 활성화 확인
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "가상환경이 활성화되지 않았습니다. 다시 활성화합니다."
        . venv/bin/activate
    fi
    
    # 테스트 실행
    python -m pytest tests/ \
        -v \
        --html=reports/report.html \
        --self-contained-html \
        --tb=short \
        --disable-warnings \
        --junitxml=reports/junit.xml \
        --capture=no
    
    if [ $? -eq 0 ]; then
        log_success "모든 테스트가 성공적으로 완료되었습니다!"
    else
        log_error "일부 테스트가 실패했습니다."
        return 1
    fi
}

# 정리 작업
cleanup() {
    log_info "정리 작업 중..."
    
    # 가상환경 비활성화
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    # 프로세스 정리
    pkill -f chrome || true
    pkill -f chromedriver || true
    
    log_success "정리 작업 완료"
}

# 메인 실행 함수
main() {
    log_info "Jenkins Selenium 테스트 시작"
    log_info "작업 디렉토리: $(pwd)"
    log_info "Python 버전: $(python3 --version)"
    
    # 의존성 확인
    check_dependencies
    
    # Python 환경 설정
    setup_python_environment
    
    # 환경 설정
    setup_environment
    
    # 테스트 실행
    run_tests
    
    # 정리 작업
    cleanup
    
    log_success "Jenkins Selenium 테스트 완료"
}

# 스크립트 실행
main "$@"
