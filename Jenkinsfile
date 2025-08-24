pipeline {
    agent any
    
    environment {
        // 환경 변수 설정
        PYTHON_VERSION = '3.8'
        HEADLESS = 'true'
        BROWSER = 'chrome'
    }
    
    options {
        // 빌드 옵션
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔍 코드 체크아웃 중...'
                checkout scm
            }
        }
        
        stage('Check Dependencies') {
            steps {
                echo '🔍 시스템 의존성 확인 중...'
                script {
                    // 필수 도구들 확인
                    sh '''
                        echo "Python3 확인:"
                        python3 --version || { echo "❌ Python3가 설치되지 않았습니다"; exit 1; }
                        
                        echo "pip3 확인:"
                        pip3 --version || { echo "❌ pip3가 설치되지 않았습니다"; exit 1; }
                        
                        echo "Chrome 확인:"
                        google-chrome --version || { echo "⚠️ Chrome이 설치되지 않았습니다. 시스템 관리자에게 설치를 요청하세요"; }
                    '''
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo '🐍 가상환경 설정 중...'
                script {
                    // 가상환경 생성 및 활성화
                    sh '''
                        # 가상환경 생성
                        python3 -m venv venv
                        
                        # 가상환경 활성화
                        source venv/bin/activate
                        
                        # pip 업그레이드
                        pip install --upgrade pip
                        
                        # 패키지 설치
                        pip install -r requirements.txt
                        
                        echo "가상환경 설정 완료"
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 테스트 실행 중...'
                script {
                    // 테스트 디렉토리 생성
                    sh 'mkdir -p reports/screenshots'
                    
                    // 테스트 실행 (가상환경 사용)
                    sh '''
                        # 가상환경 활성화
                        source venv/bin/activate
                        
                        # 환경 변수 설정
                        export PYTHONPATH="${PYTHONPATH}:${PWD}"
                        
                        # 테스트 실행
                        python -m pytest tests/ \
                            -v \
                            --html=reports/report.html \
                            --self-contained-html \
                            --tb=short \
                            --disable-warnings \
                            --junitxml=reports/junit.xml
                    '''
                }
            }
            post {
                always {
                    echo '📊 테스트 결과 수집 중...'
                    // JUnit 테스트 결과 수집
                    junit 'reports/junit.xml'
                    
                    // HTML 리포트 아카이브
                    archiveArtifacts artifacts: 'reports/report.html', fingerprint: true
                    
                    // 스크린샷 아카이브
                    archiveArtifacts artifacts: 'reports/screenshots/*.png', fingerprint: true
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                echo '🧹 정리 작업 중...'
                script {
                    // 오래된 파일 정리
                    sh '''
                        find reports/screenshots -name "*.png" -mtime +7 -delete 2>/dev/null || true
                        find . -name "*.log" -mtime +30 -delete 2>/dev/null || true
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📋 빌드 완료'
            
            // 테스트 결과 요약
            script {
                if (fileExists('reports/report.html')) {
                    echo '✅ HTML 리포트 생성됨: reports/report.html'
                }
                
                if (fileExists('reports/junit.xml')) {
                    echo '✅ JUnit 리포트 생성됨: reports/junit.xml'
                }
                
                if (fileExists('reports/screenshots')) {
                    def screenshotCount = sh(
                        script: 'find reports/screenshots -name "*.png" | wc -l',
                        returnStdout: true
                    ).trim()
                    echo "📸 스크린샷 개수: $screenshotCount"
                }
            }
        }
        
        success {
            echo '🎉 빌드 성공!'
        }
        
        failure {
            echo '❌ 빌드 실패!'
            
            // 실패 시 로그 수집
            script {
                if (fileExists('reports/')) {
                    archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
                }
            }
        }
    }
}
