#!/bin/bash

# Jenkins 환경용 Selenium 테스트 실행 스크립트
# Jenkins CI/CD 파이프라인에서 사용하기 위해 최적화되었습니다.
# sudo 권한 없이 실행 가능합니다.

set -e

echo "🚀 Jenkins 환경용 Selenium 테스트 실행"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Jenkins 환경 확인
check_jenkins_environment() {
    log_info "Jenkins 환경 확인 중..."
    
    # Jenkins 환경 변수 확인
    if [[ -n "$JENKINS_URL" ]] || [[ -n "$BUILD_NUMBER" ]] || [[ "$(whoami)" == "jenkins" ]]; then
        log_success "Jenkins 환경 감지됨"
        export JENKINS_MODE=true
        log_info "BUILD_NUMBER: ${BUILD_NUMBER:-N/A}"
        log_info "WORKSPACE: ${WORKSPACE:-$(pwd)}"
    else
        log_warning "Jenkins 환경이 아닙니다. 일반 모드로 실행합니다."
        export JENKINS_MODE=false
    fi
}

# 시스템 의존성 확인 (sudo 없이)
check_dependencies() {
    log_info "시스템 의존성 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않았습니다. 시스템 관리자에게 문의하세요."
        exit 1
    fi
    
    # pip 확인
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3가 설치되지 않았습니다. 시스템 관리자에게 문의하세요."
        exit 1
    fi
    
    # Chrome 확인
    if ! command -v google-chrome &> /dev/null; then
        log_warning "Chrome이 설치되지 않았습니다. 시스템 관리자에게 설치를 요청하세요."
        log_info "Chrome 설치 명령어: sudo apt install google-chrome-stable"
    else
        log_success "Chrome 확인됨: $(google-chrome --version)"
    fi
    
    # Xvfb 확인
    if ! command -v Xvfb &> /dev/null; then
        log_warning "Xvfb가 설치되지 않았습니다. 시스템 관리자에게 설치를 요청하세요."
        log_info "Xvfb 설치 명령어: sudo apt install xvfb"
    else
        log_success "Xvfb 확인됨"
    fi
    
    log_success "의존성 확인 완료"
}

# Python 환경 설정
setup_python_environment() {
    log_info "Python 환경 설정 중..."
    
    if [[ "$JENKINS_MODE" == "true" ]]; then
        # Jenkins 환경에서는 시스템 Python 사용
        log_info "Jenkins 모드: 시스템 Python 사용"
        
        # pip 업그레이드
        python3 -m pip install --upgrade pip --user
        
        # 패키지 설치 (사용자 디렉토리에)
        python3 -m pip install --user -r requirements.txt
        
        # PATH 설정
        export PATH="$HOME/.local/bin:$PATH"
        
        log_success "시스템 Python 환경 설정 완료"
    else
        # 일반 환경에서는 가상환경 사용
        log_info "일반 모드: 가상환경 사용"
        
        # 가상환경 생성 (권한 확인 후)
        if [[ ! -d "venv" ]]; then
            if [[ -w "." ]]; then
                python3 -m venv venv
                log_success "가상환경 생성 완료"
            else
                log_error "현재 디렉토리에 쓰기 권한이 없습니다"
                exit 1
            fi
        fi
        
        # 가상환경 활성화
        source venv/bin/activate
        pip install -r requirements.txt
        
        log_success "가상환경 설정 완료"
    fi
}

# 환경 변수 설정
setup_environment() {
    log_info "환경 변수 설정 중..."
    
    # 기본 환경 변수
    export HEADLESS=true
    export BROWSER=chrome
    export DISPLAY=:99
    
    # Jenkins 특별 설정
    if [[ "$JENKINS_MODE" == "true" ]]; then
        export PYTHONPATH="${PYTHONPATH}:${PWD}"
        export CHROME_OPTIONS="--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-extensions --disable-plugins --disable-images --disable-javascript --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-features=TranslateUI --disable-ipc-flooding-protection"
        
        # Jenkins 워크스페이스 설정
        if [[ -n "$WORKSPACE" ]]; then
            cd "$WORKSPACE"
        fi
    fi
    
    # Ubuntu 환경 설정 파일 로드
    if [[ -f "env.ubuntu" ]]; then
        export $(cat env.ubuntu | grep -v '^#' | xargs)
    fi
    
    log_success "환경 변수 설정 완료"
}

# 가상 디스플레이 시작
start_virtual_display() {
    log_info "가상 디스플레이 시작 중..."
    
    # Xvfb가 설치되어 있는지 확인
    if ! command -v Xvfb &> /dev/null; then
        log_warning "Xvfb가 설치되지 않았습니다. 가상 디스플레이를 시작할 수 없습니다."
        log_info "시스템 관리자에게 다음 명령어로 설치를 요청하세요:"
        log_info "sudo apt install xvfb"
        return 1
    fi
    
    # 기존 Xvfb 프로세스 종료
    pkill Xvfb 2>/dev/null || true
    
    # 새로운 가상 디스플레이 시작
    Xvfb :99 -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
    export DISPLAY=:99
    
    # 디스플레이 준비 대기
    sleep 3
    
    log_success "가상 디스플레이 시작 완료"
}

# 테스트 실행
run_tests() {
    log_info "테스트 실행 중..."
    
    # 테스트 디렉토리 생성
    mkdir -p reports/screenshots
    
    # 테스트 실행
    if [[ "$JENKINS_MODE" == "true" ]]; then
        # Jenkins 환경에서는 python3 직접 사용
        python3 -m pytest tests/ \
            -v \
            --html=reports/report.html \
            --self-contained-html \
            --tb=short \
            --disable-warnings \
            --junitxml=reports/junit.xml
    else
        # 일반 환경에서는 가상환경의 python 사용
        python -m pytest tests/ \
            -v \
            --html=reports/report.html \
            --self-contained-html \
            --tb=short \
            --disable-warnings
    fi
    
    TEST_EXIT_CODE=$?
    
    if [[ $TEST_EXIT_CODE -eq 0 ]]; then
        log_success "테스트 실행 완료"
    else
        log_error "테스트 실행 실패 (종료 코드: $TEST_EXIT_CODE)"
    fi
    
    return $TEST_EXIT_CODE
}

# 결과 정리
cleanup() {
    log_info "정리 작업 중..."
    
    # 가상 디스플레이 정리
    pkill Xvfb 2>/dev/null || true
    
    # 오래된 파일 정리
    find reports/screenshots -name "*.png" -mtime +7 -delete 2>/dev/null || true
    find . -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "정리 작업 완료"
}

# Jenkins 아티팩트 설정
setup_jenkins_artifacts() {
    if [[ "$JENKINS_MODE" == "true" ]]; then
        log_info "Jenkins 아티팩트 설정 중..."
        
        # 테스트 결과를 Jenkins에서 접근 가능하도록 설정
        if [[ -f "reports/report.html" ]]; then
            echo "📊 HTML 리포트: reports/report.html"
        fi
        
        if [[ -f "reports/junit.xml" ]]; then
            echo "📋 JUnit 리포트: reports/junit.xml"
        fi
        
        # 스크린샷 디렉토리 확인
        if [[ -d "reports/screenshots" ]]; then
            SCREENSHOT_COUNT=$(find reports/screenshots -name "*.png" | wc -l)
            echo "📸 스크린샷 개수: $SCREENSHOT_COUNT"
        fi
        
        log_success "Jenkins 아티팩트 설정 완료"
    fi
}

# 메인 실행
main() {
    echo "시작 시간: $(date)"
    echo "작업 디렉토리: $(pwd)"
    
    check_jenkins_environment
    check_dependencies
    setup_python_environment
    setup_environment
    start_virtual_display
    run_tests
    TEST_RESULT=$?
    cleanup
    setup_jenkins_artifacts
    
    echo "완료 시간: $(date)"
    
    if [[ $TEST_RESULT -eq 0 ]]; then
        log_success "모든 작업이 성공적으로 완료되었습니다!"
    else
        log_error "작업이 실패했습니다 (종료 코드: $TEST_RESULT)"
    fi
    
    exit $TEST_RESULT
}

# 스크립트 실행
main "$@"
