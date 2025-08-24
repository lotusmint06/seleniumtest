"""
pytest 설정 파일
테스트 실패 시 자동 스크린샷 기능 포함
"""
import pytest
import os
import time
import traceback
from utils.driver_factory import DriverFactory


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 결과를 가로채서 실패 시 스크린샷 촬영"""
    outcome = yield
    report = outcome.get_result()
    
    # 테스트가 실패했고, WebDriver가 있는 경우에만 스크린샷 촬영
    if report.when == "call" and report.failed:
        try:
            # 테스트 클래스에서 driver 인스턴스 찾기
            driver = None
            if hasattr(item, 'funcargs'):
                # fixture에서 driver 찾기
                for fixture_name, fixture_value in item.funcargs.items():
                    if hasattr(fixture_value, 'save_screenshot'):
                        driver = fixture_value
                        break
            
            # 클래스 인스턴스에서 driver 찾기
            if not driver and hasattr(item, 'instance'):
                if hasattr(item.instance, 'driver'):
                    driver = item.instance.driver
            
            if driver:
                # 테스트 이름 생성
                test_name = f"{item.module.__name__}.{item.name}"
                
                # 오류 정보 수집
                error_info = ""
                if hasattr(report, 'longrepr'):
                    error_info = str(report.longrepr)
                
                # 스크린샷 촬영
                screenshot_path = DriverFactory.take_screenshot_on_failure(
                    driver=driver,
                    test_name=test_name,
                    error_info=error_info
                )
                
                if screenshot_path:
                    print(f"📸 실패 스크린샷 저장됨: {screenshot_path}")
                    
        except Exception as e:
            print(f"스크린샷 촬영 중 오류: {e}")


@pytest.fixture(scope="function")
def driver():
    """WebDriver fixture - 각 테스트마다 새로운 드라이버 제공"""
    driver = None
    try:
        driver = DriverFactory.get_driver()
        yield driver
    finally:
        if driver:
            DriverFactory.quit_driver(driver)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """테스트 환경 설정"""
    # 스크린샷 디렉토리 생성
    screenshot_dir = "reports/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print(f"📁 스크린샷 디렉토리 준비: {screenshot_dir}")
    
    yield
    
    print("🧹 테스트 환경 정리 완료")


def pytest_configure(config):
    """pytest 설정"""
    # 커스텀 마커 등록
    config.addinivalue_line(
        "markers", "screenshot: 테스트 실패 시 스크린샷 촬영"
    )


def pytest_collection_modifyitems(config, items):
    """테스트 아이템 수정"""
    for item in items:
        # 모든 테스트에 screenshot 마커 추가
        item.add_marker(pytest.mark.screenshot)
