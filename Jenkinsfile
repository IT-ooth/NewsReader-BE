pipeline {
    agent { label 'docker-agent' } // 이전에 설정한 도커 가능한 에이전트
    
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
                        // 1. 도커 로그인
                        sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
                        
                        // 2. 이미지 빌드 (API와 Worker가 같은 코드 베이스이므로 하나만 빌드)
                        sh "docker build -t $DOCKER_HUB_ID/$APP_NAME:${BUILD_NUMBER} ."
                        sh "docker build -t $DOCKER_HUB_ID/$APP_NAME:latest ."
                        
                        // 3. 이미지 푸시
                        sh "docker push $DOCKER_HUB_ID/$APP_NAME:${BUILD_NUMBER}"
                        sh "docker push $DOCKER_HUB_ID/$APP_NAME:latest"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                container('docker') {
                    script {
                        // 1. YAML 파일 내의 이미지 태그를 최신 빌드 번호로 교체 (선택 사항, latest 쓸거면 생략 가능)
                        // 여기서는 간단하게 latest를 쓰되, rollout restart로 강제 재배포합니다.
                        
                        // 2. K3s에 배포 적용
                        // (젠킨스 에이전트가 로컬 K3s 클러스터에 접근 가능하다고 가정)
                        // 만약 권한 에러가 나면 'kubectl' 설정이 필요합니다.
                        
                        sh "kubectl apply -f k8s/postgres.yaml"
                        // DB가 뜰 때까지 살짝 대기 (선택)
                        sh "sleep 5" 
                        sh "kubectl apply -f k8s/backend.yaml"
                        
                        // 3. 강제로 최신 이미지로 재시작 (latest 태그일 때 중요)
                        sh "kubectl rollout restart deployment/news-reader-api"
                        sh "kubectl rollout restart deployment/news-reader-worker"
                    }
                }
            }
        }
    }
}