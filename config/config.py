"""
Selenium 테스트 설정 파일
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class TestConfig:
    """테스트 설정 클래스"""
    
    # 기본 URL
    BASE_URL = os.getenv('BASE_URL', 'https://www.hanatour.com')
    
    # 브라우저 설정
    BROWSER = os.getenv('BROWSER', 'chrome').lower()
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    # 타임아웃 설정 (초)
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '20'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    # 윈도우 크기
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1920'))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '1080'))
    
    # 스크린샷 설정
    SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'reports/screenshots')
    
    # 테스트 데이터
    TEST_USERNAME = os.getenv('TEST_USERNAME', 'test_user')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'test_password')
    
    @classmethod
    def get_browser_options(cls):
        """브라우저별 옵션 반환"""
        if cls.BROWSER == 'chrome':
            from selenium.webdriver.chrome.options import Options
            options = Options()
            if cls.HEADLESS:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--window-size={cls.WINDOW_WIDTH},{cls.WINDOW_HEIGHT}')
            return options
        elif cls.BROWSER == 'firefox':
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if cls.HEADLESS:
                options.add_argument('--headless')
            return options
        else:
            raise ValueError(f"지원하지 않는 브라우저: {cls.BROWSER}")
