"""
WebDriver 팩토리 클래스
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.config import TestConfig
import os
import time
import traceback


class DriverFactory:
    """WebDriver 팩토리 클래스"""
    
    @staticmethod
    def get_driver(browser=None, headless=None):
        """WebDriver 인스턴스 생성"""
        browser = browser or TestConfig.BROWSER
        headless = headless if headless is not None else TestConfig.HEADLESS
        
        if browser == 'chrome':
            driver = DriverFactory._create_chrome_driver(headless)
        elif browser == 'firefox':
            driver = DriverFactory._create_firefox_driver(headless)
        elif browser == 'edge':
            driver = DriverFactory._create_edge_driver(headless)
        else:
            raise ValueError(f"지원하지 않는 브라우저: {browser}")
        
        DriverFactory._configure_driver(driver)
        return driver
    
    @staticmethod
    def _create_chrome_driver(headless=False):
        """Chrome WebDriver 생성"""
        options = TestConfig.get_browser_options()
        if headless:
            options.add_argument('--headless')

        # 추가 Chrome 옵션
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 사용자 데이터 디렉토리 충돌 방지
        import tempfile
        import uuid
        user_data_dir = tempfile.mkdtemp(prefix=f"chrome_user_data_{uuid.uuid4().hex[:8]}_")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')

        # 시스템에 설치된 ChromeDriver를 우선적으로 사용
        try:
            driver = webdriver.Chrome(options=options)
            DriverFactory._configure_driver(driver)
            return driver
        except Exception as e:
            print(f"시스템 ChromeDriver 실패: {e}")
            # 대안: ChromeDriverManager 사용 (캐시 정리 포함)
            try:
                # webdriver-manager 캐시 정리
                import os
                import shutil
                wdm_cache_dir = os.path.expanduser("~/.wdm")
                if os.path.exists(wdm_cache_dir):
                    print(f"webdriver-manager 캐시 정리 중: {wdm_cache_dir}")
                    shutil.rmtree(wdm_cache_dir)
                
                # ChromeDriverManager로 새로 다운로드
                driver_path = ChromeDriverManager().install()
                
                # 실제 chromedriver 실행 파일 확인
                if os.path.isdir(driver_path):
                    # 디렉토리인 경우 chromedriver 파일 찾기
                    for root, dirs, files in os.walk(driver_path):
                        for file in files:
                            if file == 'chromedriver' or file.startswith('chromedriver-'):
                                driver_path = os.path.join(root, file)
                                break
                        if driver_path != ChromeDriverManager().install():
                            break
                
                # 실행 권한 부여
                if os.path.exists(driver_path):
                    os.chmod(driver_path, 0o755)
                    print(f"ChromeDriver 경로: {driver_path}")
                
                service = ChromeService(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                DriverFactory._configure_driver(driver)
                return driver
            except Exception as e2:
                print(f"ChromeDriverManager도 실패: {e2}")
                # 마지막 대안: 직접 chromedriver 경로 시도
                try:
                    # 일반적인 chromedriver 경로들 시도
                    possible_paths = [
                        '/usr/bin/chromedriver',
                        '/usr/local/bin/chromedriver',
                        '/snap/bin/chromedriver',
                        'chromedriver'
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path) and os.access(path, os.X_OK):
                            print(f"직접 ChromeDriver 사용: {path}")
                            service = ChromeService(path)
                            driver = webdriver.Chrome(service=service, options=options)
                            DriverFactory._configure_driver(driver)
                            return driver
                    
                    raise Exception("사용 가능한 ChromeDriver를 찾을 수 없습니다")
                except Exception as e3:
                    print(f"직접 ChromeDriver 시도도 실패: {e3}")
                    raise
    
    @staticmethod
    def _create_firefox_driver(headless=False):
        """Firefox WebDriver 생성"""
        options = TestConfig.get_browser_options()
        if headless:
            options.add_argument('--headless')
        
        try:
            driver = webdriver.Firefox(options=options)
            DriverFactory._configure_driver(driver)
            return driver
        except Exception as e:
            print(f"시스템 GeckoDriver 실패: {e}")
            # 대안: GeckoDriverManager 사용
            try:
                driver_path = GeckoDriverManager().install()
                service = FirefoxService(driver_path)
                driver = webdriver.Firefox(service=service, options=options)
                DriverFactory._configure_driver(driver)
                return driver
            except Exception as e2:
                print(f"GeckoDriverManager도 실패: {e2}")
                raise
    
    @staticmethod
    def _create_edge_driver(headless=False):
        """Edge WebDriver 생성"""
        options = TestConfig.get_browser_options()
        if headless:
            options.add_argument('--headless')
        
        try:
            driver = webdriver.Edge(options=options)
            DriverFactory._configure_driver(driver)
            return driver
        except Exception as e:
            print(f"시스템 EdgeDriver 실패: {e}")
            # 대안: EdgeChromiumDriverManager 사용
            try:
                driver_path = EdgeChromiumDriverManager().install()
                service = EdgeService(driver_path)
                driver = webdriver.Edge(service=service, options=options)
                DriverFactory._configure_driver(driver)
                return driver
            except Exception as e2:
                print(f"EdgeChromiumDriverManager도 실패: {e2}")
                raise
    
    @staticmethod
    def _configure_driver(driver):
        """WebDriver 설정"""
        driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
        driver.set_page_load_timeout(TestConfig.PAGE_LOAD_TIMEOUT)
        driver.set_window_size(TestConfig.WINDOW_WIDTH, TestConfig.WINDOW_HEIGHT)
    
    @staticmethod
    def quit_driver(driver):
        """WebDriver 종료"""
        if driver:
            try:
                # 임시 사용자 데이터 디렉토리 정리
                if hasattr(driver, 'options') and driver.options:
                    for argument in driver.options.arguments:
                        if argument.startswith('--user-data-dir='):
                            import shutil
                            import os
                            user_data_dir = argument.split('=', 1)[1]
                            if os.path.exists(user_data_dir):
                                try:
                                    shutil.rmtree(user_data_dir)
                                    print(f"임시 디렉토리 정리됨: {user_data_dir}")
                                except Exception as e:
                                    print(f"임시 디렉토리 정리 실패: {e}")
                            break
                
                driver.quit()
            except Exception as e:
                print(f"드라이버 종료 중 오류: {e}")
    
    @staticmethod
    def take_screenshot_on_failure(driver, test_name=None, error_info=None):
        """테스트 실패 시 스크린샷 촬영"""
        try:
            # 스크린샷 디렉토리 생성
            screenshot_dir = TestConfig.SCREENSHOT_DIR
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 파일명 생성
            timestamp = int(time.time())
            test_name = test_name or f"test_{timestamp}"
            filename = f"failure_{test_name}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            # 스크린샷 촬영
            driver.save_screenshot(filepath)
            
            # 오류 정보 로그 파일 생성
            log_filename = f"failure_{test_name}_{timestamp}.log"
            log_filepath = os.path.join(screenshot_dir, log_filename)
            
            with open(log_filepath, 'w', encoding='utf-8') as f:
                f.write(f"테스트 실패 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"테스트명: {test_name}\n")
                f.write(f"현재 URL: {driver.current_url}\n")
                f.write(f"페이지 제목: {driver.title}\n")
                if error_info:
                    f.write(f"오류 정보:\n{error_info}\n")
                f.write(f"스크린샷 파일: {filepath}\n")
            
            print(f"❌ 테스트 실패 스크린샷 저장: {filepath}")
            print(f"❌ 오류 로그 저장: {log_filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"스크린샷 촬영 실패: {e}")
            return None
