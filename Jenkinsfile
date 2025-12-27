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
                    // 1. 기존에 실행 중인 컨테이너가 있다면 강제로 끄고 삭제 (에러 방지)
                    // 컨테이너 이름은 'news-reader-be'로 정했습니다.
                    sh "docker rm -f news-reader-be || true"

                    // 2. 이미지 빌드 (-t 뒤에 이미지 이름을 정합니다)
                    sh "docker build -t news-reader-be:latest ."

                    // 3. 컨테이너 실행
                    // -p 8000:8000 (호스트포트:컨테이너포트) - 프로젝트 포트에 맞춰 수정하세요.
                    sh "docker run -d --name news-reader-be -p 8000:8000 news-reader-be:latest"
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