#!/bin/bash

# Jenkins 환경에서 ChromeDriver 설치 스크립트
# sudo 권한 없이 실행 가능

set -e

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

# ChromeDriver 설치
install_chromedriver() {
    log_info "ChromeDriver 설치 시작..."
    
    # 작업 디렉토리 생성
    CHROMEDRIVER_DIR="$HOME/chromedriver"
    mkdir -p "$CHROMEDRIVER_DIR"
    cd "$CHROMEDRIVER_DIR"
    
    # Chrome 버전 확인
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        log_info "Chrome 버전: $CHROME_VERSION"
    else
        log_warning "Chrome이 설치되지 않았습니다. 최신 ChromeDriver를 다운로드합니다."
        CHROME_VERSION="latest"
    fi
    
    # ChromeDriver 다운로드
    if [ "$CHROME_VERSION" != "latest" ]; then
        # 특정 버전 다운로드
        MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)
        log_info "ChromeDriver 버전 $MAJOR_VERSION 다운로드 중..."
        
        # ChromeDriver 다운로드 URL
        CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION"
        CHROMEDRIVER_VERSION=$(curl -s "$CHROMEDRIVER_URL")
        
        if [ -z "$CHROMEDRIVER_VERSION" ]; then
            log_warning "특정 버전을 찾을 수 없습니다. 최신 버전을 다운로드합니다."
            CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        fi
    else
        # 최신 버전 다운로드
        log_info "최신 ChromeDriver 다운로드 중..."
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
    fi
    
    log_info "ChromeDriver 버전: $CHROMEDRIVER_VERSION"
    
    # 아키텍처 확인
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        PLATFORM="linux64"
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        PLATFORM="linux64"  # ChromeDriver는 ARM64도 linux64로 제공
    else
        log_error "지원하지 않는 아키텍처: $ARCH"
        exit 1
    fi
    
    # ChromeDriver 다운로드
    DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_$PLATFORM.zip"
    log_info "다운로드 URL: $DOWNLOAD_URL"
    
    # 기존 파일 정리
    rm -f chromedriver_*.zip
    rm -f chromedriver
    
    # 다운로드
    if curl -L -o "chromedriver_$PLATFORM.zip" "$DOWNLOAD_URL"; then
        log_success "ChromeDriver 다운로드 완료"
    else
        log_error "ChromeDriver 다운로드 실패"
        exit 1
    fi
    
    # 압축 해제
    if unzip -q "chromedriver_$PLATFORM.zip"; then
        log_success "ChromeDriver 압축 해제 완료"
    else
        log_error "ChromeDriver 압축 해제 실패"
        exit 1
    fi
    
    # 실행 권한 부여
    chmod +x chromedriver
    
    # 설치 확인
    if ./chromedriver --version; then
        log_success "ChromeDriver 설치 완료"
        log_info "ChromeDriver 경로: $CHROMEDRIVER_DIR/chromedriver"
        
        # PATH에 추가
        echo "export PATH=\"$CHROMEDRIVER_DIR:\$PATH\"" >> ~/.bashrc
        export PATH="$CHROMEDRIVER_DIR:$PATH"
        
        log_info "PATH에 ChromeDriver 경로가 추가되었습니다."
    else
        log_error "ChromeDriver 설치 실패"
        exit 1
    fi
}

# webdriver-manager 캐시 정리
cleanup_wdm_cache() {
    log_info "webdriver-manager 캐시 정리 중..."
    
    WDM_CACHE="$HOME/.wdm"
    if [ -d "$WDM_CACHE" ]; then
        rm -rf "$WDM_CACHE"
        log_success "webdriver-manager 캐시 정리 완료"
    else
        log_info "webdriver-manager 캐시가 없습니다."
    fi
}

# 메인 실행
main() {
    log_info "ChromeDriver 설치 스크립트 시작"
    log_info "작업 디렉토리: $(pwd)"
    log_info "사용자: $(whoami)"
    
    # webdriver-manager 캐시 정리
    cleanup_wdm_cache
    
    # ChromeDriver 설치
    install_chromedriver
    
    log_success "ChromeDriver 설치 완료!"
    log_info "이제 Selenium 테스트를 실행할 수 있습니다."
}

# 스크립트 실행
main "$@"
