pipeline {
    agent { label 'docker-agent' } 

    environment {
        DOCKER_HUB_ID = "soo1278" 
        APP_NAME = "news-reader-be"
        IMAGE_NAME = "${DOCKER_HUB_ID}/${APP_NAME}"
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
                        echo "🐳 도커 빌드 시작: 버전 ${BUILD_NUMBER}"
                        sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
                        
                        // 빌드 번호를 태그로 사용하여 "고유한 이미지" 생성
                        sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                        sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest"
                        
                        sh "docker push ${IMAGE_NAME}:${BUILD_NUMBER}"
                        sh "docker push ${IMAGE_NAME}:latest"

                        sh "docker rmi ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest"
                        sh "docker image prune -f"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                container('kubectl') {
                    script {
                        echo "🚀 K3s 인프라 및 앱 업데이트..."
                        
                        // 1. 모든 YAML 적용 (DB, Service, Ingress 등 변경사항 반영)
                        sh "kubectl apply -f k8s/"

                        // 2. 고유 태그(${BUILD_NUMBER})를 사용하여 배포 업데이트 강제 수행
                        // 이렇게 하면 K8s는 이미지가 확실히 바뀌었음을 인지하고 즉시 새 Pod를 띄웁니다.
                        def apps = [
                            [deploy: "news-reader-api", container: "api"],
                            [deploy: "news-reader-worker", container: "worker"],
                            [deploy: "news-reader-analyzer", container: "analyzer"]
                        ]
                        
                        apps.each { app ->
                            echo "Updating ${app.deploy} to version ${BUILD_NUMBER}..."
                            sh "kubectl set image deployment/${app.deploy} ${app.container}=${IMAGE_NAME}:${BUILD_NUMBER}"
                        }

                        // 3. 배포가 완전히 끝날 때까지 대기 (Health Check)
                        apps.each { app ->
                            sh "kubectl rollout status deployment/${app.deploy} --timeout=2m"
                        }
                        
                        echo "✅ 모든 서비스 배포 완료!"
                    }
                }
            }
        }
    }
}