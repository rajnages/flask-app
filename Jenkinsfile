pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockercred')
        DOCKER_IMAGE = 'rajnages/my-flask-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/rajnages/flask-app.git'
        GIT_BRANCH = 'main'
        TRIVY_SEVERITY = 'HIGH,CRITICAL'  // Set severity levels
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                cleanWs()
                git branch: "${GIT_BRANCH}",
                    url: "${GIT_REPO}"
            }
        }
        
        stage('Parallel Tasks') {
            parallel {
                stage('SonarQube Analysis') {
                    steps {
                        script {
                            def scannerHome = tool 'SonarScanner'
                            withSonarQubeEnv(credentialsId: 'sonar', installationName: 'SonarScanner') {
                                sh """
                                    ${scannerHome}/bin/sonar-scanner \
                                    -Dsonar.projectKey=sonar \
                                    -Dsonar.projectName='Flask Application' \
                                    -Dsonar.projectVersion='1.0' \
                                    -Dsonar.sources=. \
                                    -Dsonar.sourceEncoding=UTF-8
                                """
                            }
                        }
                    }
                }
                
                stage('Build & Push Docker') {
                    steps {
                        script {
                            // Build Image
                            sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                            
                            // Login and Push
                            withCredentials([usernamePassword(credentialsId: 'dockercred', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                                sh """
                                    echo \$DOCKERHUB_PASSWORD | docker login -u \$DOCKERHUB_USERNAME --password-stdin
                                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                                    docker push ${DOCKER_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    // Create results directory
                    sh 'mkdir -p trivy-results'
                    
                    // Download Trivy DB with retry mechanism
                    sh '''
                        max_retries=3
                        counter=0
                        until trivy image --download-db-only || [ $counter -eq $max_retries ]
                        do
                            counter=$((counter+1))
                            echo "Retrying Trivy DB download... Attempt: $counter/$max_retries"
                            sleep 10
                        done
                    '''
                    
                    // Run Trivy scan with cache
                    sh """
                        trivy image \
                            --cache-dir /var/lib/trivy \
                            --format template \
                            --template '@/usr/local/share/trivy/templates/html.tpl' \
                            --output trivy-results/scan.html \
                            --severity \${TRIVY_SEVERITY} \
                            --no-progress \
                            --ignore-unfixed \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                    
                    // Generate JSON report for processing
                    sh """
                        trivy image \
                            --cache-dir /var/lib/trivy \
                            --format json \
                            --output trivy-results/scan.json \
                            --severity \${TRIVY_SEVERITY} \
                            --no-progress \
                            --ignore-unfixed \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                    
                    // Archive the results
                    archiveArtifacts artifacts: 'trivy-results/**/*'
                }
            }
        }
        
        stage('Deploy & Health Check') {
            steps {
                script {
                    // Deploy
                    sh """
                        docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop
                        docker container ls -a -fname=flask-container -q | xargs -r docker container rm
                        docker run -d -p 5000:5000 --name flask-container ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                    
                    // Quick Health Check
                    sh '''
                        max_retries=3
                        counter=0
                        until curl -s -f http://44.211.197.232:5000/ > /dev/null || [ $counter -eq $max_retries ]
                        do
                            counter=$((counter+1))
                            echo "Health check attempt: $counter/$max_retries"
                            sleep 3
                        done
                        
                        if [ $counter -eq $max_retries ]; then
                            echo "Health check failed"
                            exit 1
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo "Security scan passed successfully!"
        }
        failure {
            echo "Security scan failed! Check the Trivy scan results."
        }
        always {
            sh '''
                docker logout
                docker system prune -f
            '''
            cleanWs()
        }
    }
}