#!/bin/bash

# Ubuntu 서버용 Selenium 테스트 실행 스크립트
# 헤드리스 모드로 최적화되어 있습니다.

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 Ubuntu 서버용 Selenium 테스트 실행"
echo "=========================================="

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

# 시스템 체크
check_system() {
    log_info "시스템 환경 확인 중..."
    
    # OS 확인
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Linux 환경 확인됨"
    else
        log_error "Linux 환경이 아닙니다: $OSTYPE"
        exit 1
    fi
    
    # Python 확인
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python 확인됨: $PYTHON_VERSION"
    else
        log_error "Python3가 설치되지 않았습니다"
        exit 1
    fi
    
    # Chrome 확인
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version)
        log_success "Chrome 확인됨: $CHROME_VERSION"
    else
        log_warning "Chrome이 설치되지 않았습니다. 설치를 권장합니다."
    fi
    
    # 가상환경 확인
    if [[ -d "venv" ]]; then
        log_success "가상환경 확인됨"
    else
        log_warning "가상환경이 없습니다. 생성합니다..."
        python3 -m venv venv
        log_success "가상환경 생성 완료"
    fi
}

# 가상환경 활성화
activate_venv() {
    log_info "가상환경 활성화 중..."
    source venv/bin/activate
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log_success "가상환경 활성화됨: $VIRTUAL_ENV"
    else
        log_error "가상환경 활성화 실패"
        exit 1
    fi
}

# 패키지 설치
install_packages() {
    log_info "필요한 패키지 설치 중..."
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "패키지 설치 완료"
    else
        log_error "requirements.txt 파일을 찾을 수 없습니다"
        exit 1
    fi
}

# 환경 변수 설정
setup_environment() {
    log_info "Ubuntu 서버 환경 변수 설정 중..."
    
    # Ubuntu 환경 설정 파일이 있으면 사용
    if [[ -f "env.ubuntu" ]]; then
        export $(cat env.ubuntu | grep -v '^#' | xargs)
        log_success "Ubuntu 환경 설정 로드됨"
    fi
    
    # 기본 헤드리스 모드 설정
    export HEADLESS=true
    export BROWSER=chrome
    
    # 메모리 최적화 설정
    export CHROME_OPTIONS="--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-extensions --disable-plugins --disable-images --disable-javascript"
    
    log_success "환경 변수 설정 완료"
}

# 테스트 실행
run_tests() {
    log_info "테스트 실행 중..."
    
    # 명령행 인수 처리
    TEST_PATH="tests/"
    BROWSER="chrome"
    HEADLESS=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --browser=*)
                BROWSER="${1#*=}"
                shift
                ;;
            --headless)
                HEADLESS=true
                shift
                ;;
            --test-path=*)
                TEST_PATH="${1#*=}"
                shift
                ;;
            *)
                TEST_PATH="$1"
                shift
                ;;
        esac
    done
    
    # 환경 변수 설정
    export BROWSER=$BROWSER
    export HEADLESS=$HEADLESS
    
    # 테스트 실행
    python -m pytest $TEST_PATH \
        -v \
        --html=reports/report.html \
        --self-contained-html \
        --tb=short \
        --disable-warnings
    
    if [[ $? -eq 0 ]]; then
        log_success "테스트 실행 완료"
    else
        log_error "테스트 실행 실패"
        exit 1
    fi
}

# 결과 정리
cleanup() {
    log_info "정리 작업 중..."
    
    # 오래된 스크린샷 정리 (7일 이상)
    find reports/screenshots -name "*.png" -mtime +7 -delete 2>/dev/null || true
    
    # 오래된 로그 정리 (30일 이상)
    find . -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "정리 작업 완료"
}

# 메인 실행
main() {
    echo "시작 시간: $(date)"
    
    check_system
    activate_venv
    install_packages
    setup_environment
    run_tests "$@"
    cleanup
    
    echo "완료 시간: $(date)"
    log_success "모든 작업이 완료되었습니다!"
    
    # 리포트 위치 안내
    if [[ -f "reports/report.html" ]]; then
        echo ""
        echo "📊 테스트 리포트: reports/report.html"
        echo "📸 스크린샷: reports/screenshots/"
    fi
}

# 스크립트 실행
main "$@"
