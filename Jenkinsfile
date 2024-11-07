pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockercred')
        DOCKER_IMAGE = 'rajnages/my-flask-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/rajnages/flask-app.git'
        GIT_BRANCH = 'main'
        SONAR_PROJECT_KEY = 'sonar'
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                cleanWs()
                git branch: "${GIT_BRANCH}",
                    url: "${GIT_REPO}"
            }
        }
        
        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'SonarScanner'
            }
            steps {
                withSonarQubeEnv(credentialsId: 'sonar', installationName: 'SonarScanner') {
                    sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.projectName='Flask Application' \
                        -Dsonar.projectVersion='1.0' \
                        -Dsonar.sources=. \
                        -Dsonar.sourceEncoding=UTF-8 \
                        -Dsonar.exclusions=**/*.pyc,**/*.pyo,**/__pycache__/**,**/tests/**,**/venv/**,.git/**,.github/**
                    """
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    try {
                        timeout(time: 2, unit: 'MINUTES') {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                echo "Quality Gate failed: ${qg.status}"
                                currentBuild.result = 'UNSTABLE'
                            }
                        }
                    } catch (Exception e) {
                        echo "Quality Gate timed out or failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Login to DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockercred', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                        sh "echo \$DOCKERHUB_PASSWORD | docker login -u \$DOCKERHUB_USERNAME --password-stdin"
                    }
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    sh """
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                script {
                    sh """
                        docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop
                        docker container ls -a -fname=flask-container -q | xargs -r docker container rm
                        docker run -d -p 5000:5000 --name flask-container ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        max_retries=6
                        counter=0
                        until curl -s -f http://44.211.197.232:5000/ > /dev/null || [ $counter -eq $max_retries ]
                        do
                            counter=$((counter+1))
                            echo "Waiting for application to start... (Attempt: $counter/$max_retries)"
                            sleep 5
                        done
                        
                        if [ $counter -eq $max_retries ]; then
                            echo "Health check failed after $max_retries attempts"
                            exit 1
                        fi
                        
                        echo "Application is healthy!"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded! Application deployed successfully.'
        }
        failure {
            echo 'Pipeline failed! Check the logs for details.'
        }
        always {
            sh 'docker logout'
            cleanWs()
        }
    }
}