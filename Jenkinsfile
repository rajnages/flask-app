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
        
        stage('Code Analysis') {
            parallel {
                stage('SonarQube Analysis') {
                    environment {
                        scannerHome = tool 'SonarScanner'
                    }
                    steps {
                        withSonarQubeEnv('sonar') {
                            sh """
                                ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.projectName='Flask Application' \
                                -Dsonar.projectVersion='1.0' \
                                -Dsonar.sources=. \
                                -Dsonar.sourceEncoding=UTF-8 \
                                -Dsonar.language=python \
                                -Dsonar.python.version=3 \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.exclusions=**/*.pyc,**/*.pyo,**/__pycache__/**,**/tests/**,**/venv/**,.git/**,.github/**
                            """
                        }
                    }
                }
                
                stage('Lint Check') {
                    steps {
                        sh '''
                            python -m pip install flake8
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                        '''
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    python -m pip install bandit
                    bandit -r . -f json -o bandit-report.json || true
                '''
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    python -m pip install pytest pytest-cov
                    python -m pytest --cov=. --cov-report=xml
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Scan Docker Image') {
            steps {
                sh """
                    docker scan ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                """
            }
        }
        
        stage('Login to DockerHub') {
            steps {
                script {
                    sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                script {
                    sh 'docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop'
                    sh 'docker container ls -a -fname=flask-container -q | xargs -r docker container rm'
                    sh "docker run -d -p 5000:5000 --name flask-container ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        sleep 10
                        curl -f http://localhost:5000/health || exit 1
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded! Application deployed successfully.'
            slackSend(color: 'good', message: "Build #${BUILD_NUMBER} - Success!")
        }
        failure {
            echo 'Pipeline failed! Check the logs for details.'
            slackSend(color: 'danger', message: "Build #${BUILD_NUMBER} - Failed!")
        }
        always {
            sh 'docker logout'
            cleanWs()
            junit '**/test-results/*.xml'
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'coverage',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}