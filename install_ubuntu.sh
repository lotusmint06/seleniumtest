#!/bin/bash

# Ubuntu 서버용 Selenium 테스트 환경 자동 설치 스크립트

set -e

echo "🚀 Ubuntu 서버용 Selenium 테스트 환경 설치"
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

# 시스템 업데이트
update_system() {
    log_info "시스템 패키지 업데이트 중..."
    sudo apt update && sudo apt upgrade -y
    log_success "시스템 업데이트 완료"
}

# Python 설치
install_python() {
    log_info "Python 및 pip 설치 중..."
    sudo apt install -y python3 python3-pip python3-venv
    log_success "Python 설치 완료: $(python3 --version)"
}

# Chrome 설치
install_chrome() {
    log_info "Chrome 브라우저 설치 중..."
    
    # Chrome 저장소 추가
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # Chrome 설치
    sudo apt update
    sudo apt install -y google-chrome-stable
    
    log_success "Chrome 설치 완료: $(google-chrome --version)"
}

# 필수 라이브러리 설치
install_libraries() {
    log_info "필수 시스템 라이브러리 설치 중..."
    sudo apt install -y \
        xvfb \
        libxi6 \
        libgconf-2-4 \
        default-jdk \
        xorg \
        openbox \
        x11-xserver-utils \
        curl \
        wget \
        unzip
    log_success "라이브러리 설치 완료"
}

# Docker 설치 (선택사항)
install_docker() {
    read -p "Docker를 설치하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Docker 설치 중..."
        
        # Docker 저장소 추가
        sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Docker 설치
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io
        
        # 현재 사용자를 docker 그룹에 추가
        sudo usermod -aG docker $USER
        
        log_success "Docker 설치 완료"
        log_warning "Docker 그룹에 사용자가 추가되었습니다. 로그아웃 후 다시 로그인하세요."
    fi
}

# 프로젝트 설정
setup_project() {
    log_info "프로젝트 설정 중..."
    
    # 가상환경 생성
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log_success "가상환경 생성 완료"
    fi
    
    # 가상환경 활성화
    source venv/bin/activate
    
    # 패키지 설치
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "Python 패키지 설치 완료"
    fi
    
    # 디렉토리 생성
    mkdir -p reports/screenshots logs
    log_success "디렉토리 생성 완료"
}

# 환경 설정
setup_environment() {
    log_info "환경 설정 중..."
    
    # Ubuntu 환경 설정 파일 복사
    if [[ -f "env.ubuntu" ]]; then
        cp env.ubuntu .env
        log_success "환경 설정 파일 복사 완료"
    fi
    
    # 실행 권한 부여
    chmod +x run_ubuntu.sh
    chmod +x run_tests.py
    log_success "실행 권한 설정 완료"
}

# 테스트 실행
test_installation() {
    log_info "설치 테스트 중..."
    
    # 가상환경 활성화
    source venv/bin/activate
    
    # 간단한 테스트 실행
    python -m pytest tests/test_simple.py::test_imports -v
    
    if [[ $? -eq 0 ]]; then
        log_success "설치 테스트 성공"
    else
        log_error "설치 테스트 실패"
        return 1
    fi
}

# 사용법 안내
show_usage() {
    echo ""
    echo "🎉 설치가 완료되었습니다!"
    echo ""
    echo "📋 사용 방법:"
    echo "1. 전체 테스트 실행:"
    echo "   ./run_ubuntu.sh"
    echo ""
    echo "2. 특정 테스트 실행:"
    echo "   ./run_ubuntu.sh tests/test_simple.py"
    echo ""
    echo "3. Docker 사용 (Docker 설치 시):"
    echo "   docker-compose up"
    echo ""
    echo "4. 웹으로 결과 확인 (Docker 사용 시):"
    echo "   docker-compose --profile web up"
    echo "   브라우저에서 http://localhost:8080 접속"
    echo ""
    echo "📊 테스트 결과:"
    echo "   - HTML 리포트: reports/report.html"
    echo "   - 스크린샷: reports/screenshots/"
    echo "   - 로그: logs/"
    echo ""
}

# 메인 실행
main() {
    echo "시작 시간: $(date)"
    
    update_system
    install_python
    install_chrome
    install_libraries
    install_docker
    setup_project
    setup_environment
    test_installation
    show_usage
    
    echo "완료 시간: $(date)"
    log_success "모든 설치가 완료되었습니다!"
}

# 스크립트 실행
main "$@"
