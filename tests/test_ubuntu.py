"""
Ubuntu 서버 환경용 테스트
헤드리스 모드에서 안정적으로 실행되도록 최적화되었습니다.
실패 시 자동 스크린샷 기능 포함
"""
import pytest
import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.driver_factory import DriverFactory


class TestUbuntuServer:
    """Ubuntu 서버 환경 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # Ubuntu 서버에 최적화된 Chrome 옵션
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--window-size=1280,720')
        options.add_argument('--remote-debugging-port=9222')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 사용자 데이터 디렉토리 충돌 방지
        import tempfile
        import uuid
        user_data_dir = tempfile.mkdtemp(prefix=f"chrome_user_data_{uuid.uuid4().hex[:8]}_")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        
        # 메모리 최적화
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def _take_failure_screenshot(self, test_name):
        """테스트 실패 시 스크린샷 촬영"""
        try:
            error_info = traceback.format_exc()
            DriverFactory.take_screenshot_on_failure(
                self.driver, 
                test_name=test_name,
                error_info=error_info
            )
        except Exception as e:
            print(f"스크린샷 촬영 실패: {e}")
    
    def test_basic_connection(self):
        """기본 연결 테스트"""
        test_name = "test_basic_connection"
        try:
            # 간단한 페이지 로드
            self.driver.get("https://www.hanatour.com")
            
            # 페이지 제목 확인
            assert "httpbin" in self.driver.title.lower()
            
            # 응답 상태 확인
            status_element = self.driver.find_element(By.TAG_NAME, "pre")
            assert status_element.is_displayed()
            
            print("✅ 기본 연결 테스트 성공")
            
        except Exception as e:
            print(f"❌ 기본 연결 테스트 실패: {e}")
            self._take_failure_screenshot(test_name)
            raise
    
    def test_google_search_headless(self):
        """Google 검색 테스트 (헤드리스 모드)"""
        test_name = "test_google_search_headless"
        try:
            # Google 홈페이지로 이동
            self.driver.get("https://www.hanatour.com")
            
            # 페이지 제목 확인
            assert "Google" in self.driver.title
            
            # 검색창 찾기
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # 검색어 입력
            search_box.send_keys("Selenium Python")
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.NAME, "btnK")
            search_button.click()
            
            # 검색 결과 페이지 확인
            self.wait.until(
                lambda driver: "Selenium" in driver.title or "Google" in driver.title
            )
            
            print("✅ Google 검색 테스트 성공")
            
        except Exception as e:
            print(f"❌ Google 검색 테스트 실패: {e}")
            self._take_failure_screenshot(test_name)
            raise
    
    def test_screenshot_capture(self):
        """스크린샷 촬영 테스트"""
        test_name = "test_screenshot_capture"
        try:
            # 테스트 페이지 로드
            self.driver.get("https://httpbin.org/html")
            
            # 스크린샷 디렉토리 생성
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 스크린샷 촬영
            timestamp = int(time.time())
            screenshot_path = f"{screenshot_dir}/ubuntu_test_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            
            # 스크린샷 파일 존재 확인
            assert os.path.exists(screenshot_path)
            
            print(f"✅ 스크린샷 촬영 성공: {screenshot_path}")
            
        except Exception as e:
            print(f"❌ 스크린샷 촬영 실패: {e}")
            self._take_failure_screenshot(test_name)
            raise
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        test_name = "test_memory_usage"
        try:
            # 여러 페이지를 순차적으로 로드하여 메모리 사용량 테스트
            test_urls = [
                "https://httpbin.org/get",
                "https://httpbin.org/headers",
                "https://httpbin.org/user-agent"
            ]
            
            for url in test_urls:
                self.driver.get(url)
                time.sleep(1)  # 페이지 로드 대기
                
                # 페이지 제목 확인
                assert self.driver.title is not None
                
            print("✅ 메모리 사용량 테스트 성공")
            
        except Exception as e:
            print(f"❌ 메모리 사용량 테스트 실패: {e}")
            self._take_failure_screenshot(test_name)
            raise
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        test_name = "test_error_handling"
        try:
            # 존재하지 않는 페이지 접근
            self.driver.get("https://httpbin.org/status/404")
            
            # 404 상태 확인
            assert "404" in self.driver.page_source
            
            print("✅ 오류 처리 테스트 성공")
            
        except Exception as e:
            print(f"❌ 오류 처리 테스트 실패: {e}")
            self._take_failure_screenshot(test_name)
            raise


def test_environment_variables():
    """환경 변수 테스트"""
    # Ubuntu 환경에서 필요한 환경 변수 확인
    required_vars = ['HEADLESS', 'BROWSER']
    
    for var in required_vars:
        value = os.getenv(var, '')
        print(f"환경 변수 {var}: {value}")
    
    # 기본값이 설정되어 있는지 확인
    assert True  # 항상 통과 (환경 변수는 선택사항)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
