pipeline {
    agent any
    environment {
        REGISTRY = "registry.local.home:5000"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Start') {
            steps {
                echo 'Jenkins pipeline started'
            }
        }
        stage('Build frontend') {
            steps {
                sh 'pwd'
                sh '''
                    docker build \
                    -t ${REGISTRY}/cbs-frontend:develop \
                    cbs-frontend
                '''
            }
        }
        stage('Push frontend') {
            steps {
                sh '''
                    docker push \
                    ${REGISTRY}/cbs-frontend:develop
                '''
            }
        }
    }
}