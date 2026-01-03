pipeline {
    agent { label 'docker-agent' } 
    
    environment {
        DOCKER_HUB_ID = "soo1278" 
        APP_NAME = "news-reader-be"
        DOCKER_CREDS = credentials('docker-hub-login')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Docker') {
            steps {
                container('docker') {
                    script {
                        echo "🐳 도커 빌드 및 푸시 시작"
                        sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
                        sh "docker build -t $DOCKER_HUB_ID/$APP_NAME:${BUILD_NUMBER} ."
                        sh "docker build -t $DOCKER_HUB_ID/$APP_NAME:latest ."
                        sh "docker push $DOCKER_HUB_ID/$APP_NAME:${BUILD_NUMBER}"
                        sh "docker push $DOCKER_HUB_ID/$APP_NAME:latest"

                        echo "디스크 용량 확보를 위해 로컬 이미지를 삭제합니다..."

                        sh "docker rmi $DOCKER_HUB_ID/$APP_NAME:${BUILD_NUMBER}"
                        sh "docker rmi $DOCKER_HUB_ID/$APP_NAME:latest"

                        sh "docker image prune -f"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                container('kubectl') {
                    script {
                        echo "🚀 K3s 배포 시작..."
                        
                        sh "kubectl apply -f k8s/postgres.yaml"
                        sh "sleep 5"
                        sh "kubectl apply -f k8s/backend.yaml"
                        
                        sh "kubectl rollout restart deployment/news-reader-api"
                        sh "kubectl rollout restart deployment/news-reader-worker"
                    }
                }
            }
        }
    }
}