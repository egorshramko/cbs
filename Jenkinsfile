pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage ('Start') {
            steps {
                echo 'Jenkins pipeline started'
            }
        }
    }
}