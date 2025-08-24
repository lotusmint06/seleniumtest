"""
기본 연결 테스트
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def test_basic_chrome_connection():
    """기본 Chrome 연결 테스트"""
    try:
        # Chrome 옵션 설정
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # ChromeDriver 설치 및 서비스 생성
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        
        # WebDriver 생성
        driver = webdriver.Chrome(service=service, options=options)
        
        # 간단한 테스트
        driver.get("https://www.google.com")
        assert "Google" in driver.title
        
        # 드라이버 종료
        driver.quit()
        
        print("✅ 기본 Chrome 연결 테스트 성공")
        
    except Exception as e:
        print(f"❌ 기본 Chrome 연결 테스트 실패: {e}")
        raise


def test_selenium_import():
    """Selenium import 테스트"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        print("✅ Selenium import 성공")
    except ImportError as e:
        print(f"❌ Selenium import 실패: {e}")
        raise


def test_webdriver_manager():
    """WebDriver Manager 테스트"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✅ WebDriver Manager 성공: {driver_path}")
    except Exception as e:
        print(f"❌ WebDriver Manager 실패: {e}")
        raise


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main([__file__, "-v"])
