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
        
        stage('SonarQube Analysis & Quality Gate') {
            steps {
                script {
                    try {
                        // Start SonarQube analysis
                        withSonarQubeEnv(credentialsId: 'sonar', installationName: 'SonarScanner') {
                            sh """
                                ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.projectName='Flask Application' \
                                -Dsonar.projectVersion='1.0' \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.sourceEncoding=UTF-8 \
                                -Dsonar.exclusions=**/*.pyc,**/*.pyo,**/__pycache__/**,**/tests/**,**/venv/**,.git/**,.github/**
                            """
                        }
                        
                        // Start next stages while SonarQube processes
                        parallel(
                            qualityGate: {
                                timeout(time: 5, unit: 'MINUTES') {
                                    def qg = waitForQualityGate()
                                    if (qg.status != 'OK') {
                                        echo "Quality Gate failed: ${qg.status}"
                                        currentBuild.result = 'UNSTABLE'
                                    }
                                }
                            },
                            buildImage: {
                                // Start building Docker image while waiting for Quality Gate
                                sh """
                                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                                """
                            }
                        )
                    } catch (Exception e) {
                        echo "SonarQube analysis or Quality Gate failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                        // Continue pipeline
                    }
                }
            }
        }
        
        stage('Login to DockerHub') {
            steps {
                script {
                    try {
                        sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                    } catch (Exception e) {
                        error "Failed to login to DockerHub: ${e.message}"
                    }
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    try {
                        sh """
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                            docker push ${DOCKER_IMAGE}:latest
                        """
                    } catch (Exception e) {
                        error "Failed to push Docker image: ${e.message}"
                    }
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                script {
                    try {
                        sh '''
                            docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop
                            docker container ls -a -fname=flask-container -q | xargs -r docker container rm
                            docker run -d -p 5000:5000 --name flask-container ${DOCKER_IMAGE}:${DOCKER_TAG}
                        '''
                    } catch (Exception e) {
                        error "Failed to deploy container: ${e.message}"
                    }
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    try {
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
                    } catch (Exception e) {
                        error "Health check failed: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        success {
            script {
                try {
                    echo 'Pipeline succeeded! Application deployed successfully.'
                    slackSend(
                        color: 'good',
                        message: """
                            ✅ Build #${BUILD_NUMBER} - Success!
                            🐳 Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}
                            🌐 Application URL: http://44.211.197.232:5000
                        """
                    )
                } catch (Exception e) {
                    echo "Failed to send success notification: ${e.message}"
                }
            }
        }
        failure {
            script {
                try {
                    echo 'Pipeline failed! Check the logs for details.'
                    slackSend(
                        color: 'danger',
                        message: """
                            ❌ Build #${BUILD_NUMBER} - Failed!
                            🔍 Check Jenkins logs for details: ${BUILD_URL}console
                        """
                    )
                } catch (Exception e) {
                    echo "Failed to send failure notification: ${e.message}"
                }
            }
        }
        always {
            script {
                try {
                    sh 'docker logout'
                    cleanWs()
                } catch (Exception e) {
                    echo "Cleanup failed: ${e.message}"
                }
            }
        }
    }
}