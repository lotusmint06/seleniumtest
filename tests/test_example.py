"""
Selenium 테스트 예제
"""
import pytest
from selenium.webdriver.common.by import By
from utils.driver_factory import DriverFactory
from pages.base_page import BasePage
from config.config import TestConfig


class TestGoogleSearch:
    """Google 검색 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.driver = DriverFactory.get_driver()
        self.base_page = BasePage(self.driver)
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        DriverFactory.quit_driver(self.driver)
    
    def test_google_search(self):
        """Google 검색 기능 테스트"""
        # Google 홈페이지로 이동
        self.base_page.navigate_to(TestConfig.BASE_URL)
        
        # 페이지 제목 확인
        assert "Google" in self.base_page.get_title()
        
        # 검색창 찾기 및 검색어 입력
        search_box = (By.NAME, "q")
        self.base_page.input_text(search_box, "Selenium Python")
        
        # 검색 버튼 클릭
        search_button = (By.NAME, "btnK")
        self.base_page.click_element(search_button)
        
        # 검색 결과 페이지에서 제목 확인
        assert "Selenium" in self.base_page.get_title() or "Google" in self.base_page.get_title()
        
        # 검색 결과가 있는지 확인 (여러 가능한 선택자 시도)
        possible_selectors = [
            (By.ID, "search"),
            (By.ID, "rso"),
            (By.CLASS_NAME, "g"),
            (By.CSS_SELECTOR, "[data-sokoban-container]")
        ]
        
        results_found = False
        for selector in possible_selectors:
            if self.base_page.is_element_present(selector, timeout=5):
                results_found = True
                break
        
        assert results_found, "검색 결과를 찾을 수 없습니다"
    
    def test_google_page_title(self):
        """Google 페이지 제목 테스트"""
        # Google 홈페이지로 이동
        self.base_page.navigate_to(TestConfig.BASE_URL)
        
        # 페이지 제목이 "Google"을 포함하는지 확인
        title = self.base_page.get_title()
        assert "Google" in title
    
    def test_google_search_suggestions(self):
        """Google 검색 제안 기능 테스트"""
        # Google 홈페이지로 이동
        self.base_page.navigate_to(TestConfig.BASE_URL)
        
        # 검색창에 텍스트 입력
        search_box = (By.NAME, "q")
        self.base_page.input_text(search_box, "Python")
        
        # 검색 제안이 나타날 때까지 대기
        suggestions = (By.CLASS_NAME, "UUbT9")
        if self.base_page.is_element_visible(suggestions, timeout=5):
            # 제안 목록이 비어있지 않은지 확인
            suggestion_items = self.base_page.find_elements((By.CSS_SELECTOR, ".UUbT9 .sbct"))
            assert len(suggestion_items) > 0
    
    def test_google_lucky_search(self):
        """Google I'm Feeling Lucky 버튼 테스트"""
        # Google 홈페이지로 이동
        self.base_page.navigate_to(TestConfig.BASE_URL)
        
        # 검색창에 텍스트 입력
        search_box = (By.NAME, "q")
        self.base_page.input_text(search_box, "Python")
        
        # I'm Feeling Lucky 버튼 클릭
        lucky_button = (By.NAME, "btnI")
        self.base_page.click_element(lucky_button)
        
        # 검색 결과 페이지로 이동했는지 확인
        current_url = self.base_page.get_current_url()
        assert current_url != TestConfig.BASE_URL


class TestBasicNavigation:
    """기본 네비게이션 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.driver = DriverFactory.get_driver()
        self.base_page = BasePage(self.driver)
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        DriverFactory.quit_driver(self.driver)
    
    def test_page_navigation(self):
        """페이지 네비게이션 테스트"""
        # 첫 번째 페이지로 이동
        self.base_page.navigate_to("https://www.python.org")
        assert "Python" in self.base_page.get_title()
        
        # 두 번째 페이지로 이동
        self.base_page.navigate_to("https://www.selenium.dev")
        assert "Selenium" in self.base_page.get_title()
        
        # 뒤로 가기
        self.base_page.go_back()
        assert "Python" in self.base_page.get_title()
        
        # 앞으로 가기
        self.base_page.go_forward()
        assert "Selenium" in self.base_page.get_title()
    
    def test_screenshot_capture(self):
        """스크린샷 촬영 테스트"""
        # 페이지로 이동
        self.base_page.navigate_to("https://www.python.org")
        
        # 스크린샷 촬영
        screenshot_path = self.base_page.take_screenshot("python_org.png")
        
        # 스크린샷 파일이 생성되었는지 확인
        import os
        assert os.path.exists(screenshot_path)
    
    def test_scroll_functionality(self):
        """스크롤 기능 테스트"""
        # 긴 페이지로 이동
        self.base_page.navigate_to("https://www.python.org")
        
        # 페이지 하단으로 스크롤
        self.base_page.scroll_to_bottom()
        
        # 페이지 상단으로 스크롤
        self.base_page.scroll_to_top()
        
        # 페이지 새로고침
        self.base_page.refresh_page()
        
        # 페이지가 정상적으로 로드되었는지 확인
        assert "Python" in self.base_page.get_title()


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    pytest.main([__file__, "-v"])
