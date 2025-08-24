"""
Firefox 테스트
"""
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


def test_firefox_connection():
    """Firefox 연결 테스트"""
    try:
        # Firefox 옵션 설정
        options = Options()
        options.add_argument('--headless')
        
        # GeckoDriver 설치 및 서비스 생성
        driver_path = GeckoDriverManager().install()
        service = Service(driver_path)
        
        # WebDriver 생성
        driver = webdriver.Firefox(service=service, options=options)
        
        # 간단한 테스트
        driver.get("https://www.google.com")
        assert "Google" in driver.title
        
        # 드라이버 종료
        driver.quit()
        
        print("✅ Firefox 연결 테스트 성공")
        
    except Exception as e:
        print(f"❌ Firefox 연결 테스트 실패: {e}")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
