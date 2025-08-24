"""
Page Object Model의 기본 클래스
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import TestConfig
import os
import time


class BasePage:
    """모든 페이지 객체의 기본 클래스"""
    
    def __init__(self, driver):
        """
        BasePage 초기화
        
        Args:
            driver: WebDriver 인스턴스
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, TestConfig.EXPLICIT_WAIT)
    
    def navigate_to(self, url):
        """
        지정된 URL로 이동
        
        Args:
            url (str): 이동할 URL
        """
        self.driver.get(url)
    
    def get_title(self):
        """페이지 제목 반환"""
        return self.driver.title
    
    def get_current_url(self):
        """현재 URL 반환"""
        return self.driver.current_url
    
    def find_element(self, locator, timeout=None):
        """
        요소 찾기
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
            
        Returns:
            WebElement: 찾은 요소
        """
        wait_time = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator, timeout=None):
        """
        여러 요소 찾기
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
            
        Returns:
            list: 찾은 요소들의 리스트
        """
        wait_time = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.presence_of_all_elements_located(locator))
    
    def click_element(self, locator, timeout=None):
        """
        요소 클릭
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
        """
        element = self.find_element(locator, timeout)
        self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def input_text(self, locator, text, timeout=None):
        """
        텍스트 입력
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            text (str): 입력할 텍스트
            timeout (int): 대기 시간 (초)
        """
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator, timeout=None):
        """
        요소의 텍스트 가져오기
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
            
        Returns:
            str: 요소의 텍스트
        """
        element = self.find_element(locator, timeout)
        return element.text
    
    def is_element_present(self, locator, timeout=None):
        """
        요소 존재 여부 확인
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 요소 존재 여부
        """
        try:
            self.find_element(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def is_element_visible(self, locator, timeout=None):
        """
        요소 가시성 확인
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 요소 가시성
        """
        try:
            wait_time = timeout or TestConfig.EXPLICIT_WAIT
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_visible(self, locator, timeout=None):
        """
        요소가 보일 때까지 대기
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
            timeout (int): 대기 시간 (초)
        """
        wait_time = timeout or TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        wait.until(EC.visibility_of_element_located(locator))
    
    def take_screenshot(self, filename=None):
        """
        스크린샷 촬영
        
        Args:
            filename (str): 파일명 (기본값: timestamp)
            
        Returns:
            str: 스크린샷 파일 경로
        """
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        # 스크린샷 디렉토리 생성
        screenshot_dir = TestConfig.SCREENSHOT_DIR
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, filename)
        self.driver.save_screenshot(filepath)
        return filepath
    
    def scroll_to_element(self, locator):
        """
        요소로 스크롤
        
        Args:
            locator (tuple): (By, value) 형태의 로케이터
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def scroll_to_bottom(self):
        """페이지 하단으로 스크롤"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_to_top(self):
        """페이지 상단으로 스크롤"""
        self.driver.execute_script("window.scrollTo(0, 0);")
    
    def refresh_page(self):
        """페이지 새로고침"""
        self.driver.refresh()
    
    def go_back(self):
        """뒤로 가기"""
        self.driver.back()
    
    def go_forward(self):
        """앞으로 가기"""
        self.driver.forward()
