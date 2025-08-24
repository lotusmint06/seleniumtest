#!/usr/bin/env python3
"""
Selenium 테스트 실행 스크립트
"""
import sys
import os
import subprocess
from pathlib import Path


def install_requirements():
    """필요한 패키지 설치"""
    print("📦 필요한 패키지를 설치합니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 패키지 설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False
    return True


def run_tests(test_path=None, browser=None, headless=False):
    """테스트 실행"""
    print("🚀 테스트를 실행합니다...")
    
    # 환경 변수 설정
    env = os.environ.copy()
    if browser:
        env['BROWSER'] = browser
    if headless:
        env['HEADLESS'] = 'true'
    
    # pytest 명령어 구성
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    cmd.extend([
        "-v",
        "--html=reports/report.html",
        "--self-contained-html"
    ])
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print("✅ 테스트 실행 완료")
        print("📊 리포트: reports/report.html")
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실행 실패: {e}")
        return False
    
    return True


def main():
    """메인 함수"""
    print("🎯 Selenium 테스트 프로젝트")
    print("=" * 50)
    
    # 명령행 인수 처리
    test_path = None
    browser = None
    headless = False
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--browser="):
                browser = arg.split("=")[1]
            elif arg.startswith("--headless"):
                headless = True
            elif not arg.startswith("--"):
                test_path = arg
    
    # requirements.txt가 있는지 확인
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt 파일을 찾을 수 없습니다.")
        return 1
    
    # 패키지 설치
    if not install_requirements():
        return 1
    
    # 테스트 실행
    if not run_tests(test_path, browser, headless):
        return 1
    
    print("🎉 모든 작업이 완료되었습니다!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
