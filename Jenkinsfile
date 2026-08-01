pipeline {
    agent any
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
                    -t registry.local.home:5000/cbs-frontend:develop \
                    ./cbs-frontend
                '''
            }
        }
    }
}