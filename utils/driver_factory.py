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


class DriverFactory:
    """WebDriver 생성을 담당하는 팩토리 클래스"""
    
    @staticmethod
    def get_driver(browser=None, headless=None):
        """
        지정된 브라우저의 WebDriver 인스턴스를 반환합니다.
        
        Args:
            browser (str): 브라우저 타입 ('chrome', 'firefox', 'edge')
            headless (bool): 헤드리스 모드 여부
            
        Returns:
            WebDriver: 설정된 WebDriver 인스턴스
        """
        browser = browser or TestConfig.BROWSER
        headless = headless if headless is not None else TestConfig.HEADLESS
        
        if browser == 'chrome':
            return DriverFactory._create_chrome_driver(headless)
        elif browser == 'firefox':
            return DriverFactory._create_firefox_driver(headless)
        elif browser == 'edge':
            return DriverFactory._create_edge_driver(headless)
        else:
            raise ValueError(f"지원하지 않는 브라우저: {browser}")
    
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
        
        # 시스템에 설치된 ChromeDriver를 우선적으로 사용
        try:
            driver = webdriver.Chrome(options=options)
            DriverFactory._configure_driver(driver)
            return driver
        except Exception as e:
            print(f"시스템 ChromeDriver 실패: {e}")
            # 대안: ChromeDriverManager 사용
            try:
                driver_path = ChromeDriverManager().install()
                service = ChromeService(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                DriverFactory._configure_driver(driver)
                return driver
            except Exception as e2:
                print(f"ChromeDriverManager도 실패: {e2}")
                raise
    
    @staticmethod
    def _create_firefox_driver(headless=False):
        """Firefox WebDriver 생성"""
        options = TestConfig.get_browser_options()
        if headless:
            options.add_argument('--headless')
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        DriverFactory._configure_driver(driver)
        return driver
    
    @staticmethod
    def _create_edge_driver(headless=False):
        """Edge WebDriver 생성"""
        from selenium.webdriver.edge.options import Options
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument(f'--window-size={TestConfig.WINDOW_WIDTH},{TestConfig.WINDOW_HEIGHT}')
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        DriverFactory._configure_driver(driver)
        return driver
    
    @staticmethod
    def _configure_driver(driver):
        """WebDriver 공통 설정"""
        driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
        driver.set_page_load_timeout(TestConfig.PAGE_LOAD_TIMEOUT)
        driver.maximize_window()
    
    @staticmethod
    def quit_driver(driver):
        """WebDriver 종료"""
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"드라이버 종료 중 오류 발생: {e}")
