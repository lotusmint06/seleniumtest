#!/bin/bash

# Jenkins Execute Shell에서 직접 실행할 수 있는 명령어들
# 이 파일의 내용을 Jenkins Execute Shell에 복사해서 사용하세요

set -e

echo "🚀 Jenkins Selenium 테스트 시작"
echo "=========================================="

# 1. 가상환경 생성 (Jenkins 호환 방식)
echo "📦 가상환경 생성 중..."
python3 -m venv venv

# 2. 가상환경 활성화 (Jenkins 호환 방식)
echo "🔧 가상환경 활성화 중..."
. venv/bin/activate

# 3. pip 업그레이드
echo "⬆️ pip 업그레이드 중..."
pip install --upgrade pip

# 4. 의존성 설치
echo "📚 패키지 설치 중..."
pip install -r requirements.txt

# 5. 환경 변수 설정
echo "⚙️ 환경 설정 중..."
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export CHROME_OPTIONS="--headless,--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-extensions,--disable-plugins,--disable-images,--disable-javascript,--disable-background-timer-throttling,--disable-backgrounding-occluded-windows,--disable-renderer-backgrounding,--disable-features=TranslateUI,--disable-ipc-flooding-protection"

# 6. 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p reports/screenshots
mkdir -p logs

# 7. 테스트 실행
echo "🧪 테스트 실행 중..."
python -m pytest tests/ \
    -v \
    --html=reports/report.html \
    --self-contained-html \
    --tb=short \
    --disable-warnings \
    --junitxml=reports/junit.xml \
    --capture=no

# 8. 결과 확인
echo "📊 테스트 결과 확인 중..."
if [ -f "reports/report.html" ]; then
    echo "✅ HTML 리포트 생성됨: reports/report.html"
fi

if [ -f "reports/junit.xml" ]; then
    echo "✅ JUnit 리포트 생성됨: reports/junit.xml"
fi

# 9. 스크린샷 개수 확인
if [ -d "reports/screenshots" ]; then
    SCREENSHOT_COUNT=$(find reports/screenshots -name "*.png" | wc -l)
    echo "📸 스크린샷 개수: $SCREENSHOT_COUNT"
fi

# 10. 정리
echo "🧹 정리 작업 중..."
pkill -f chrome || true
pkill -f chromedriver || true

echo "✅ Jenkins Selenium 테스트 완료"
