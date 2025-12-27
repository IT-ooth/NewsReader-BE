pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Deploy') {
            steps {
                script {
                    // sh "docker rm -f news-reader-be || true"
                    // sh "docker build -t news-reader-be:latest ."
                    // sh "docker run -d --name news-reader-be -p 8000:8000 news-reader-be:latest"
                    sh "docker compose down || true"
                    sh "docker compose up --build -d"
                }
            }
        }

        stage('Cleanup') {
            steps {
                // 사용하지 않는 빌드 찌꺼기 이미지 삭제
                sh "docker image prune -f"
            }
        }
    }

    post {
        success {
            echo "Successfully deployed NewsReader-BE!"
        }
        failure {
            echo "Deployment failed. Please check the logs."
        }
    }
}