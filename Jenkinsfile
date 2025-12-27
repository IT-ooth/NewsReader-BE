pipeline {
    agent any

    tools {
        dockerTool 'my-docker'
    }
    
    environment {
        // 프로젝트 경로 설정
        PROJECT_DIR = "2025_SecurityCurator"
    }

    stages {
        stage('Checkout') {
            steps {
                // 소스 코드 가져오기
                checkout scm
            }
        }

        stage('Build & Deploy') {
            steps {
                script {
                    // 1. 기존 컨테이너 중지 및 최신 이미지 빌드 후 실행
                    // -d: 백그라운드 실행, --build: 이미지 강제 재빌드
                    sh "docker compose up --build -d"
                }
            }
        }

        stage('Cleanup') {
            steps {
                // 사용하지 않는 오래된 이미지 정리 (용량 관리)
                sh "docker image prune -f"
            }
        }
    }

    post {
        success {
            echo "Successfully deployed Security Curator!"
        }
        failure {
            echo "Deployment failed. Please check the logs."
        }
    }
}