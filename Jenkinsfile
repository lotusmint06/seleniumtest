pipeline {
    agent any
    
    environment {
        // 환경 변수 설정
        PYTHON_VERSION = '3.8'
        DISPLAY = ':99'
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
        
        stage('Setup Environment') {
            steps {
                echo '⚙️ 환경 설정 중...'
                script {
                    // 시스템 패키지 업데이트
                    sh '''
                        sudo apt update
                        sudo apt install -y python3 python3-pip python3-venv xvfb
                    '''
                    
                    // Chrome 설치 확인
                    sh '''
                        if ! command -v google-chrome &> /dev/null; then
                            echo "Chrome 설치 중..."
                            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
                            sudo apt update
                            sudo apt install -y google-chrome-stable
                        fi
                    '''
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '📦 의존성 설치 중...'
                script {
                    // Python 패키지 설치 (사용자 디렉토리에)
                    sh '''
                        python3 -m pip install --upgrade pip --user
                        python3 -m pip install --user -r requirements.txt
                        export PATH="$HOME/.local/bin:$PATH"
                    '''
                }
            }
        }
        
        stage('Start Virtual Display') {
            steps {
                echo '🖥️ 가상 디스플레이 시작 중...'
                script {
                    // 기존 Xvfb 프로세스 종료
                    sh 'pkill Xvfb 2>/dev/null || true'
                    
                    // 새로운 가상 디스플레이 시작
                    sh '''
                        Xvfb :99 -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
                        export DISPLAY=:99
                        sleep 3
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
                    
                    // 테스트 실행
                    sh '''
                        export PYTHONPATH="${PYTHONPATH}:${PWD}"
                        export PATH="$HOME/.local/bin:$PATH"
                        
                        python3 -m pytest tests/ \
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
                    // 가상 디스플레이 정리
                    sh 'pkill Xvfb 2>/dev/null || true'
                    
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
        
        cleanup {
            echo '🧹 최종 정리 중...'
            // 가상 디스플레이 강제 종료
            sh 'pkill -f Xvfb 2>/dev/null || true'
        }
    }
}
