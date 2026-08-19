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

        stage('Prepare Version') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
                echo "Build version: ${IMAGE_TAG}"
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
                    -t ${REGISTRY}/cbs-frontend:${IMAGE_TAG} \
                    cbs-frontend
                '''
            }
        }

        stage('Build backend') {
            steps {
                sh '''
                    docker build \
                    -t ${REGISTRY}/cbs-backend:${IMAGE_TAG} \
                    cbs-backend
                '''
            }
        }

        stage('Push frontend') {
            steps {
                sh '''
                    docker push \
                    ${REGISTRY}/cbs-frontend:${IMAGE_TAG}
                '''
            }
        }

        stage('Push backend') {
            steps {
                sh '''
                    docker push \
                    ${REGISTRY}/cbs-backend:${IMAGE_TAG}
                '''
            }
        }

        stage('Copy compose to DEV') {
            steps {
                sshagent(['dev-ssh-key']) {
                    sh '''
                    scp compose/compose.dev.yaml \
                    root@dev.local.home:/opt/cbs/compose.yaml
                    '''
                }
            }
        }

        stage('Copy env to DEV') {
            steps {
                withCredentials([file(credentialsId: 'dev-env-file', variable: 'ENV_FILE')]) {
                    sh '''
                        cp $ENV_FILE .env.dev
                    '''
                    sh '''
                        echo "IMAGE_TAG=${IMAGE_TAG}" >> .env.dev
                    '''
                    sshagent(['dev-ssh-key']) {
                        sh '''
                        scp .env.dev \
                        root@dev.local.home:/opt/cbs/.env
                        '''
                    }
                }
                
            }
        }

        stage('Deploy DEV') {
            steps {
                sshagent(['dev-ssh-key']) {
                    sh '''
                    ssh root@dev.local.home "
                        cd /opt/cbs &&
                        docker compose pull &&
                        docker compose up -d
                    "
                    '''
                }
            }
        }

    }
}